"""Content-grouped outer and teacher splits with auditable donor exclusions."""
from collections import defaultdict
import hashlib

import numpy as np


def outer_assignment(rows, seed):
    grouped=defaultdict(set)
    owners={}
    for r in rows:
        if r['content_id'] in owners and owners[r['content_id']]!=r['label_id']:
            raise ValueError('Content belongs to multiple labels')
        owners[r['content_id']]=r['label_id']; grouped[r['label_id']].add(r['content_id'])
    assignment={}
    for label, contents in sorted(grouped.items()):
        if len(contents)!=5: raise ValueError('Exactly five contents required')
        local=int.from_bytes(hashlib.sha256(f'{seed}:{label}'.encode()).digest()[:8])
        for fold, content in enumerate(np.random.default_rng(local).permutation(sorted(contents))):
            assignment[str(content)]=fold
    return assignment


def disjoint(*parts):
    for part in parts:
        if len({r['session_id'] for r in part})!=len(part): raise ValueError('Duplicate session')
    for i, a in enumerate(parts):
        for b in parts[i+1:]:
            for key in ('session_id','content_id'):
                if {r[key] for r in a}&{r[key] for r in b}: raise ValueError(f'Overlap: {key}')


def teacher_assignment(train, scheme):
    choices=((0,1),(0,2),(0,3))
    grouped=defaultdict(set)
    for r in train: grouped[r['label_id']].add(r['content_id'])
    assignment={}
    for label, content_set in sorted(grouped.items()):
        contents=sorted(content_set)
        if len(contents)!=4: raise ValueError('Teacher requires four training contents per label')
        for i,c in enumerate(contents): assignment[c]=int(i not in choices[scheme])
    return assignment


def donors(rows, teacher_groups, mode='cross_content', seed=0):
    groups=defaultdict(list)
    for i,r in enumerate(rows):
        key=(r['label_id'],r['protocol'],teacher_groups[r['content_id']],
             r['repetition'] if mode=='cross_content' else r['content_id'])
        groups[key].append(i)
    result=list(range(len(rows)))
    for key,indices in sorted(groups.items()):
        indices=sorted(indices,key=lambda i:rows[i]['session_id'])
        if mode=='cross_content':
            if len(indices)!=2 or rows[indices[0]]['content_id']==rows[indices[1]]['content_id']:
                raise ValueError('Cross-content matching requires two distinct content observations per round')
            proposed=indices[::-1]
        elif mode=='within_content':
            if len(indices)!=4: raise ValueError('Within-content control requires four repetitions')
            local=int.from_bytes(hashlib.sha256(repr((seed,key)).encode()).digest()[:8])
            rng=np.random.default_rng(local)
            while True:
                proposed=rng.permutation(indices).tolist()
                if all(a!=b for a,b in zip(indices,proposed)): break
        else: raise ValueError('Unknown mismatch type')
        for receiver,donor in zip(indices,proposed): result[receiver]=donor
    validate_donors(rows,teacher_groups,result,mode)
    return np.asarray(result)


def validate_donors(rows, teacher_groups, mapping, mode):
    if sorted(mapping)!=list(range(len(rows))): raise ValueError('Not a bijection')
    for i,j in enumerate(mapping):
        a,b=rows[i],rows[j]
        if i==j: raise ValueError('Mismatch fixed point')
        if (a['label_id'],a['protocol'],teacher_groups[a['content_id']])!=(b['label_id'],b['protocol'],teacher_groups[b['content_id']]):
            raise ValueError('Cross-label/protocol/teacher-partition donor')
        if mode=='cross_content' and (a['content_id']==b['content_id'] or a['repetition']!=b['repetition']):
            raise ValueError('Wrong cross-content matching')
        if mode=='within_content' and a['content_id']!=b['content_id']:
            raise ValueError('Wrong within-content matching')
