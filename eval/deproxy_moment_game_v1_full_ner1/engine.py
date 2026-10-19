"""Independent float64 Adam models, scheduled in eight CUDA graph streams."""
from common import *
from models import initial,objective,KEYS
from classifier import basis

class Engine:
    def __init__(self,data,jobs,heads,streams=True,states=None):
        require(0<len(jobs)<=32,'32-model upper bound')
        require(len({j['recipe']['lr'] for j in jobs})==1,'One learning rate per CUDA bucket required by contract')
        require(len({len(d['b']) for d in data})==1,'One row shape per CUDA bucket')
        self.data=data;self.jobs=jobs;self.q=basis();self.steps=0;self.graph=None
        self.states=[{k:torch.nn.Parameter(v.clone()) for k,v in (initial(h,j['seed']) if states is None else states[i]).items()} for i,(j,h) in enumerate(zip(jobs,heads))]
        self.streams=[torch.cuda.Stream() for _ in range(min(8,len(jobs)))] if streams else []
        self.optimizers=[];self.bad=torch.zeros(len(jobs),device='cuda',dtype=torch.bool)
        self.clips=torch.zeros(len(jobs),device='cuda',dtype=torch.int64)
        for s,j in zip(self.states,jobs):
            opt=torch.optim.Adam(list(s.values()),lr=j['recipe']['lr'],betas=(.9,.999),eps=1e-8,weight_decay=0,foreach=False,capturable=True)
            for p in s.values():
                p.grad=torch.zeros_like(p);st=opt.state[p]
                st['step']=torch.zeros((),device='cuda',dtype=torch.float32)
                st['exp_avg']=torch.zeros_like(p);st['exp_avg_sq']=torch.zeros_like(p)
            self.optimizers.append(opt)
        self.parts=None;self.values=None;self.norms=None

    def step(self):
        root=torch.cuda.current_stream();vals=[];parts=[];norms=[]
        for stream in self.streams:stream.wait_stream(root)
        for i,(s,d,j,opt) in enumerate(zip(self.states,self.data,self.jobs,self.optimizers)):
            stream=self.streams[i%len(self.streams)] if self.streams else root
            with torch.cuda.stream(stream):
                opt.zero_grad(set_to_none=False)
                value,part,_,_=objective(s,d,j['arm'],j['recipe'],self.q);value.backward()
                norm=sum(p.grad.square().sum() for p in s.values()).sqrt()
                factor=(5/norm.clamp_min(1e-30)).clamp_max(1)
                for p in s.values():p.grad.mul_(factor)
                opt.step();self.bad[i].logical_or_(~torch.isfinite(value)|~torch.isfinite(norm))
                vals.append(value.detach());parts.append(part.detach());norms.append(norm.detach())
        for stream in self.streams:root.wait_stream(stream)
        self.values=torch.stack(vals);self.parts=torch.stack(parts);self.norms=torch.stack(norms)
        self.clips.add_((self.norms>5).long())

    def healthy(self):
        require(not bool(self.bad.any()),'Nonfinite model loss/gradient; no fallback')
        require(all(bool(torch.isfinite(p).all()) for s in self.states for p in s.values()),'Nonfinite Adam parameter')

    def checkpoint(self):
        return dict(parameters=[{k:p.detach().clone() for k,p in s.items()} for s in self.states],
            gradients=[{k:p.grad.detach().clone() for k,p in s.items()} for s in self.states],
            adam=[{k:{name:value.detach().clone() for name,value in o.state[p].items()} for k,p in s.items()} for s,o in zip(self.states,self.optimizers)],
            clips=self.clips.detach().clone(),steps=self.steps)

    def restore(self,ck):
        with torch.no_grad():
            for i,(s,o) in enumerate(zip(self.states,self.optimizers)):
                for k,p in s.items():
                    p.copy_(ck['parameters'][i][k]);p.grad.copy_(ck['gradients'][i][k])
                    for name,value in ck['adam'][i][k].items():o.state[p][name].copy_(value)
            self.bad.zero_();self.clips.copy_(ck['clips']);self.steps=ck['steps']

    def capture(self):
        require(self.graph is None,'Double capture');ck=self.checkpoint()
        stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            for _ in range(3):self.step()
        torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize();self.restore(ck)
        graph=torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):self.step()
        torch.cuda.synchronize();self.restore(ck);self.graph=graph

    def advance(self,n):
        for i in range(n):
            if self.graph is None:self.step()
            else:self.graph.replay()
            self.steps+=1
        self.healthy()

    def diagnostics(self):
        from simplex import valid
        out=[]
        for i,(s,d,j) in enumerate(zip(self.states,self.data,self.jobs)):
            val,part,ahat,residual=objective(s,d,j['arm'],j['recipe'],self.q);valid(ahat)
            terms=[part[2],part[3],part[4]+part[5],part[6]+part[7],.1*part[8],part[9]]
            gs=[]
            for term in terms:
                if term.requires_grad:
                    g=torch.autograd.grad(term,list(s.values()),retain_graph=True,allow_unused=True)
                    gs.append(torch.cat([torch.zeros_like(p).flatten() if x is None else x.flatten() for x,p in zip(g,s.values())]))
                else:gs.append(torch.zeros(sum(p.numel() for p in s.values()),device='cuda',dtype=torch.float64))
            g=torch.stack(gs);norm=g.norm(dim=1);cos=(g@g.T)/(norm[:,None]*norm[None,:]).clamp_min(1e-30)
            log=dict(step=self.steps,objective=float(val),parts=cpu(part).tolist(),gradient_part_norms=cpu(norm).tolist(),gradient_cosines=cpu(cos).tolist(),
                clip_count=int(self.clips[i]),support_active=int((ahat>0).sum()),residual_norm=float(residual.norm()),
                generated_rank=int(torch.linalg.matrix_rank(ahat)),generated_std_error=float((((ahat-d['a'])/d['scale_A']).square().sum(1)*d['w']).sum()) if j['arm']!='F-G' else None,
                raw_target_error=float(((ahat-(d['target'] if 'target' in d else d['b'])).square().sum(1)*d['w']).sum()))
            logits=F.linear((ahat-d['mu_A'])/d['scale_A'],s['A'],s['c'])@self.q.T
            prob=logits.softmax(1);bad=prob.argmax(1)!=d['y']
            log['wrong_mass']=float(d['w'][bad].sum());log['wrong_confidence']=float((prob.max(1).values[bad]*d['w'][bad]).sum()/d['w'][bad].sum()) if bool(bad.any()) else None
            out.append(log)
        return out
