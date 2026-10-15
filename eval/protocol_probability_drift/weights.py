"""Content -> visit -> pair equal mass, with explicitly separate flow weighting."""
import numpy as np


def mass(frame, mode='hierarchical'):
    if mode == 'flow_equal':
        return np.ones(len(frame), dtype=np.float64)
    if mode != 'hierarchical':
        raise ValueError(mode)
    visits = frame[['content_id', 'session_id']].drop_duplicates()
    repetitions = visits.groupby('content_id').session_id.nunique()
    counts = frame.groupby('session_id').size()
    return (1 / (frame.content_id.map(repetitions).to_numpy(dtype=float)
                 * frame.session_id.map(counts).to_numpy(dtype=float)))


def normalized(frame, mode='hierarchical'):
    w = mass(frame, mode)
    return w / w.sum()

