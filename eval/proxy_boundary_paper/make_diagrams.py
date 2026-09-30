"""Generate editable uncompressed draw.io diagrams; export using draw.io desktop."""
from pathlib import Path
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parents[2]/'docs/paper/proxy-boundary-correspondence/figures/source'

def diagram(name,nodes,edges):
    doc=ET.Element('mxfile',host='app.diagrams.net',type='device')
    page=ET.SubElement(doc,'diagram',id=name,name=name)
    model=ET.SubElement(page,'mxGraphModel',dx='1100',dy='500',grid='1',gridSize='10',page='0',math='0',shadow='0')
    root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
    for id,text,x,y,w,h,color in nodes:
        cell=ET.SubElement(root,'mxCell',id=id,value=text,style=f'rounded=1;whiteSpace=wrap;html=0;fillColor={color};strokeColor=#476378;fontSize=17;fontFamily=Helvetica;',vertex='1',parent='1')
        ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
    for i,(src,dst,label,dashed) in enumerate(edges):
        ports=''
        if src=='split':
            ports={'pre':'exitX=1;exitY=0.08;entryX=0;entryY=0.5;','post':'exitX=1;exitY=0.6;entryX=0;entryY=0.5;','test':'exitX=0.5;exitY=1;entryX=0;entryY=0.5;'}[dst]
        cell=ET.SubElement(root,'mxCell',id=f'e{i}',value=label,style=f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;fontSize=14;fontFamily=Helvetica;strokeColor=#476378;dashed={int(dashed)};'+ports,edge='1',parent='1',source=src,target=dst)
        ET.SubElement(cell,'mxGeometry',relative='1',**{'as':'geometry'})
    OUT.mkdir(parents=True,exist_ok=True)
    ET.indent(doc);ET.ElementTree(doc).write(OUT/(name+'.drawio'),encoding='utf-8',xml_declaration=True)

diagram('observation-boundary',[
 ('pre','Indexed pre observation\n(proxy-session entrance)',20,30,245,75,'#DAE8FC'),
 ('proxy','Observed proxy deployment\nSS or VLESS',330,30,245,75,'#E1D5E7'),
 ('post','Indexed post observation\n(paired exit scope)',650,30,245,75,'#DAE8FC'),
 ('train','Development only\nPaired statistics + labels\nContent-disjoint fitting',20,195,265,95,'#D5E8D4'),
 ('fit','Frozen adapter +\nsource classifier',360,195,240,95,'#D5E8D4'),
 ('infer','Prediction interface\npost vector only',680,195,240,95,'#D5E8D4'),
 ('audit','Evaluation only: held-out pre + labels\nNo feedback into prediction or selection',230,370,510,65,'#FFF2CC')],
 [('pre','proxy','traffic',False),('proxy','post','traffic',False),('pre','train','training partition',True),('train','fit','fit',False),('fit','infer','fixed',False),('post','infer','held-out post',False),('infer','audit','sealed predictions',True)])

diagram('calibration-framework',[
 ('split','Split by content first\n\nAll repeats, sides and\nparent connections move together',20,35,270,245,'#FFF2CC'),
 ('pre','Training pre + labels\nFit source scaler and h-minus\nFreeze W and intercept',355,20,270,100,'#DAE8FC'),
 ('post','Training post\nFit post preprocessing',355,170,270,80,'#DAE8FC'),
 ('target','Training targets\nF: same visit\nG: cyclic same-content donor\nH: content-deployment center',700,25,280,140,'#E1D5E7'),
 ('map','Fit diagonal affine adapter\nStatistical + decision loss\n298 parameters; lambda = 1',700,220,280,95,'#D5E8D4'),
 ('test','Held-out post only\nTraining-fitted preprocessing',355,365,270,80,'#DAE8FC'),
 ('out','Frozen adapter then h-minus\nActivity probabilities',700,365,280,80,'#D5E8D4')],
 [('split','pre','train',False),('split','post','train',False),('pre','target','pre coordinates',False),('target','map','targets and frozen W',False),('post','map','inputs',False),('split','test','held-out contents',True),('test','out','post vector',False),('map','out','frozen parameters',False)])
print('Two editable draw.io sources generated.')
