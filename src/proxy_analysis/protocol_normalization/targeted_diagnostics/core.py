"""Reusable, fail-closed table operations for the approved targeted diagnostics."""
import numpy as np
import pandas as pd

PAIR = ['session_id', 'connection_id']
KEY = PAIR + ['direction']
META = ['batch', 'item_id', 'protocol', 'repetition', 'main_route']


def pair_ledger(ledger):
    assert not ledger.duplicated(KEY + ['side']).any(), 'duplicate side/direction key'
    assert set(ledger.side) == {'pre', 'post'}
    assert set(ledger.direction) <= {-1, 1}
    assert ledger.groupby(PAIR).size().eq(4).all(), 'missing side/direction'
    assert ledger.groupby(PAIR + ['side']).epoch_id.nunique().eq(1).all()
    assert ledger.loc[~ledger.observed_unique_valid, 'unique_payload_bytes'].isna().all()
    a = ledger[ledger.side == 'pre']; b = ledger[ledger.side == 'post']
    z = a.merge(b, on=KEY, suffixes=('_pre', '_post'), validate='one_to_one')
    for col in META:
        assert (z[col + '_pre'] == z[col + '_post']).all(), col
        z[col] = z[col + '_pre']
    z['S_valid'] = z.observed_unique_valid_pre & z.observed_unique_valid_post
    cpre = z.closed_contiguous_capture_candidate_pre
    cpost = z.closed_contiguous_capture_candidate_post
    z['S_both'] = z.S_valid & cpre & cpost
    z['S_all4'] = z.groupby(PAIR).S_both.transform('all')
    z['stratum'] = np.select([cpre & cpost, cpre, cpost], ['both', 'pre_only', 'post_only'], default='neither')
    z.loc[~z.S_valid, 'stratum'] = 'Q0_excluded'
    z['pre'] = z.unique_payload_bytes_pre
    z['post'] = z.unique_payload_bytes_post
    return contrast(z)


def contrast(z):
    z = z.copy()
    z['difference'] = z.post - z.pre
    z['ratio'] = z.post.div(z.pre.where(z.pre > 0))
    z['log_ratio'] = np.log(z.ratio.where(z.ratio > 0))
    z['zero_pre'] = z.pre.eq(0)
    z['zero_post'] = z.post.eq(0)
    return z


def reason_flags(row):
    return [name for name, flag in [
        ('prefix_unobserved', not row['prefix_observed']),
        ('suffix_unobserved', not row['suffix_observed']),
        ('internal_gaps', row['final_internal_gap_count'] > 0),
        ('rst', row['rst_count'] > 0),
        ('epoch_ambiguous', row['sequence_epoch_ambiguous']),
        ('overlap_conflict', row['overlap_content_conflicts'] > 0),
        ('Q0', not row['observed_unique_valid'])] if flag]


def cohorts(z):
    """Return explicit membership including empty subset visits, without zero filling."""
    pieces = []
    for name in ['S_valid', 'S_both', 'S_all4']:
        v = z[z[name]].copy(); v['cohort'] = name; pieces.append(v)
        if name != 'S_valid':
            keys = v[['session_id', 'direction']].drop_duplicates()
            same = z[z.S_valid].merge(keys, on=['session_id', 'direction'], validate='many_to_one')
            same['cohort'] = 'S_valid_on_' + name + '_visits'; pieces.append(same)
    return pd.concat(pieces, ignore_index=True)


def visits_and_items(rows):
    keys = ['batch', 'protocol', 'item_id', 'session_id', 'repetition', 'direction', 'cohort']
    visits = rows.groupby(keys, as_index=False).agg(pre=('pre', 'sum'), post=('post', 'sum'), pairs=('connection_id', 'size'))
    visits = contrast(visits)
    items = visits.groupby(['batch', 'protocol', 'item_id', 'direction', 'cohort'], as_index=False).agg(
        median_difference=('difference', 'median'), median_log_ratio=('log_ratio', 'median'),
        visits=('session_id', 'size'), zero_pre_visits=('zero_pre', 'sum'))
    return visits, items


def position(index, count):
    if count == 1: return 'singleton'
    if index == 0: return 'first'
    if index == count - 1: return 'last'
    return 'interior'


def size_bin(size):
    assert size > 0
    if size < 64: return '(0,64)'
    if size < 256: return '[64,256)'
    if size < 1024: return '[256,1024)'
    return '[1024,inf)'


def event_runs(events):
    """Reconstruct contiguous directions using exactly the old stable packet order."""
    events = events.sort_values(['relative_time_ns', 'packet_ordinal'], kind='stable')
    runs = []
    for i, e in enumerate(events.itertuples(index=False)):
        if e.new_payload_bytes <= 0: continue
        if not runs or runs[-1]['direction'] != e.direction:
            runs.append(dict(direction=int(e.direction), new_bytes=0, first_event=i, last_event=i,
                             first_time_ns=int(e.relative_time_ns), last_time_ns=int(e.relative_time_ns)))
        r = runs[-1]; r['new_bytes'] += int(e.new_payload_bytes)
        r['last_event'] = i; r['last_time_ns'] = int(e.relative_time_ns)
    total = sum(r['new_bytes'] for r in runs); acc = 0
    for i, r in enumerate(runs):
        r.update(run_index=i, run_count=len(runs), position=position(i, len(runs)),
                 normalized_run_position=i/(len(runs)-1) if len(runs)>1 else 0.,
                 cumulative_byte_start=acc/total, cumulative_byte_end=(acc+r['new_bytes'])/total,
                 size_bin=size_bin(r['new_bytes']))
        acc += r['new_bytes']
    return runs
