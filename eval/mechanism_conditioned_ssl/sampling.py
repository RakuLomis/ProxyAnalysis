"""Label-free SSL content batches and separately authorized supervised schedule."""
import numpy as np
from common import digest


def ssl_schedule(frame, seed, steps=1000):
    assert 'label_id' not in frame and 'repetition' not in frame
    contents = np.array(sorted(frame.group_id.unique())); assert len(contents) == 24
    np.random.default_rng(seed).shuffle(contents)
    blocks = [np.flatnonzero(frame.group_id.isin(c).to_numpy()) for c in contents.reshape(4, 6)]
    assert all(len(ix) == 120 for ix in blocks)
    result = np.stack([blocks[s%4] for s in range(steps)])
    assert np.bincount(result.ravel(), minlength=len(frame)).tolist() == [steps//4]*len(frame)
    return result


def independent_schedule(post, pre, schedule):
    rows = []
    for ix in schedule[:4]:
        keys = set(zip(post.iloc[ix].deployment, post.iloc[ix].group_id))
        rows.append(np.array([i for i, k in enumerate(zip(pre.deployment, pre.group_id)) if k in keys]))
    assert all(len(r) == schedule.shape[1] for r in rows)
    result = np.stack([rows[s%4] for s in range(len(schedule))])
    assert np.bincount(result.ravel(), minlength=len(pre)).tolist() == [len(schedule)//4]*len(pre)
    return result


def supervised_schedule(frame, seed, steps=1000):
    rng = np.random.default_rng(seed); groups = {}
    for (p, y), g in frame.groupby(['deployment', 'label_id']):
        c = sorted(g.group_id.unique()); assert len(c) == 4; rng.shuffle(c)
        groups[p, y] = [g.index[g.group_id.eq(v)].to_numpy() for v in c]
    result = np.stack([np.concatenate([groups[k][s%4] for k in sorted(groups)]) for s in range(steps)])
    assert np.bincount(result.ravel(), minlength=len(frame)).tolist() == [steps//4]*len(frame)
    return result


def metadata_codes(frame, deployments, contents):
    return np.array([deployments.index(v) for v in frame.deployment]), np.array([contents.index(v) for v in frame.group_id])
