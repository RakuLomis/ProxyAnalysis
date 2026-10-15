"""Frozen E1 supervision schedule, repeated after Adam reset at step1000."""
import numpy as np


def supervised_schedule(frame, seed, steps=1000):
    rng = np.random.default_rng(seed); groups = {}
    for (p, y), g in frame.groupby(['deployment', 'label_id']):
        c = sorted(g.group_id.unique()); assert len(c) == 4; rng.shuffle(c)
        groups[p, y] = [g.index[g.group_id.eq(v)].to_numpy() for v in c]
    result = np.stack([np.concatenate([groups[k][s%4] for k in sorted(groups)]) for s in range(steps)])
    assert result.shape == (steps, 120)
    assert np.bincount(result.ravel(), minlength=len(frame)).tolist() == [steps//4]*len(frame)
    return result


def independent_schedule(post, pre, schedule):
    blocks = []
    for ix in schedule[:4]:
        keys = set(zip(post.iloc[ix].deployment, post.iloc[ix].group_id))
        blocks.append(np.array([i for i, k in enumerate(zip(pre.deployment, pre.group_id)) if k in keys]))
    result = np.stack([blocks[s%4] for s in range(len(schedule))])
    assert result.shape == schedule.shape
    assert np.bincount(result.ravel(), minlength=len(pre)).tolist() == [len(schedule)//4]*len(pre)
    return result


def routing(post, pre, ip, ia, group=False):
    if not group: return np.repeat(np.eye(120, dtype=np.float32)[None], 4, axis=0)
    rows = []
    for bp, ba in zip(ip[:4], ia[:4]):
        kp = list(zip(post.iloc[bp].deployment, post.iloc[bp].group_id))
        ka = list(zip(pre.iloc[ba].deployment, pre.iloc[ba].group_id))
        m = np.array([[x == y for y in ka] for x in kp], dtype=np.float32)/4
        assert np.all(m.sum(1) == 1) and np.all((m > 0).sum(1) == 4)
        rows.append(m)
    return np.stack(rows)
