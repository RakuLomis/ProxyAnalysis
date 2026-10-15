"""Q07-Q09 cache-only pair features, with exact frozen T-summary replay."""
import numpy as np
import pandas as pd
from common import OUT, EXTRACT, FEATURES, FAMILIES, read, write, require, checkpoint
from weights import mass


def event_summary(events, entity, byte_field):
    events = events.sort_values(['timestamp_ns', 'raw_packet_ordinal'], kind='stable').copy()
    require(events.direction.isin([-1, 1]).all() and events[byte_field].gt(0).all(),
            'Invalid direction or nonpositive event')
    previous = events.groupby(entity, sort=False).direction.shift()
    events['run'] = events.direction.ne(previous).astype('int64')
    table = events.groupby([entity, 'direction']).agg(
        bytes=(byte_field, 'sum'), count=(byte_field, 'size'), runs=('run', 'sum'))
    result = {}
    for ident, frame in events.groupby(entity, sort=False):
        record = {}
        for direction, suffix in [(1, 'up'), (-1, 'down')]:
            if (ident, direction) in table.index:
                v = table.loc[(ident, direction)]
                record.update({f'{name}_{suffix}': int(v[name]) for name in ['bytes', 'count', 'runs']})
            else:
                record.update({f'{name}_{suffix}': 0 for name in ['bytes', 'count', 'runs']})
        record.update(first_direction=int(frame.iloc[0].direction), last_direction=int(frame.iloc[-1].direction))
        result[ident] = record
    return result


def run():
    require(not (OUT / 'features/features-complete.json').exists(), 'Features already completed')
    pairs = pd.read_parquet(OUT / 'cohorts/pairs.parquet')
    rows, missing = [], []
    t_keys = {'U': 'bytes', 'E': 'count', 'R': 'runs'}
    for visit_index, (sid, visit) in enumerate(pairs.groupby('session_id', sort=True)):
        folder = EXTRACT / 'sessions' / sid
        frozen = {p['logical_id']: p for p in read(folder / 'T-pairs.json') if p['common_valid_nonempty']}
        ledger = pd.read_parquet(folder / 'T-direction-ledger.parquet')
        t = pd.read_parquet(folder / 'T-newbyte-events.parquet')
        packet, unique = {}, {}
        for side in ['pre', 'post']:
            packet[side] = event_summary(pd.read_parquet(folder / (side + '-W-events.parquet')), 'entity_id', 'payload_bytes')
            unique[side] = event_summary(t[t.side.eq(side)], 'logical_id', 'new_bytes')
        for _, p in visit.iterrows():
            record = p.to_dict()
            for side in ['pre', 'post']:
                ident = p.logical_id if side == 'pre' else p.carrier_id
                if ident not in packet[side] or p.logical_id not in unique[side]:
                    missing.append({'pair_id': p.pair_id, 'side': side, 'reason': 'event_identity_missing'})
                    continue
                a, b = packet[side][ident], unique[side][p.logical_id]
                for prefix, key in t_keys.items():
                    for d in ['up', 'down']:
                        require(b[f'{key}_{d}'] == frozen[p.logical_id]['summaries'][side][f'{prefix}_{d}'],
                                'Newbyte summary replay differs from frozen pair')
                for d in ['up', 'down']:
                    w, pp, u, ee = a[f'bytes_{d}'], a[f'count_{d}'], b[f'bytes_{d}'], b[f'count_{d}']
                    require(0 <= u <= w and 0 <= ee <= pp, 'Observed/unique side relation violated')
                    require(0 <= b[f'runs_{d}'] <= ee <= u, 'Unique run/event/byte constraint violated')
                    record.update({f'{side}_W_{d}': w, f'{side}_P_{d}': pp,
                                   f'{side}_U_{d}': u, f'{side}_E_{d}': ee,
                                   f'{side}_R_unique_{d}': b[f'runs_{d}'],
                                   f'{side}_R_packet_{d}': a[f'runs_{d}'],
                                   f'{side}_observed_repeat_bytes_{d}': w - u})
                runs = a['runs_up'] + a['runs_down']
                nonempty = a['count_up'] + a['count_down']
                require(runs >= 1 and abs(a['runs_up'] - a['runs_down']) <= 1, 'Packet FR constraint violated')
                record.update({f'{side}_FR_packet_runs': runs, f'{side}_FR_packet_switches': runs - 1,
                               f'{side}_FR_switch_fraction': (runs - 1) / (nonempty - 1) if nonempty > 1 else np.nan,
                               f'{side}_FR_run_per_packet': runs / nonempty,
                               f'{side}_R_unique_zero_runs': b['runs_up'] + b['runs_down'],
                               f'{side}_packet_first_direction': a['first_direction'],
                               f'{side}_packet_last_direction': a['last_direction']})
                lr = ledger[ledger.logical_id.eq(p.logical_id) & ledger.side.eq(side)]
                require(len(lr) == 2 and lr.valid.all(), 'Direction qualification replay failed')
                record[f'{side}_closed_contiguous_both_directions'] = bool(lr.closed_contiguous.all())
            record['closed_contiguous_all_four'] = bool(record.get('pre_closed_contiguous_both_directions', False)
                                                        and record.get('post_closed_contiguous_both_directions', False))
            rows.append(record)
        if visit_index % 40 == 0:
            print('feature visits', visit_index + 1, '/ 480', flush=True)
    write(OUT / 'features/missingness.json', {'records': missing, 'count': len(missing), 'zeros_imputed': 0})
    require(not missing, 'Missing required cache fields: stop for user confirmation; members not changed')
    frame = pd.DataFrame(rows)
    require(len(frame) == 23566, 'Members changed')
    native = [side + '_' + f for side in ['pre', 'post'] for f in FEATURES]
    require(not frame[native].isna().any().any(), 'Required feature missing')
    frame['content_visit_flow_mass'] = 0.0
    for _, g in frame.groupby('protocol'):
        frame.loc[g.index, 'content_visit_flow_mass'] = mass(g)
    require(frame.groupby(['protocol', 'content_id']).content_visit_flow_mass.sum().sub(1).abs().max() < 1e-12,
            'Content mass is not one')
    (OUT / 'features').mkdir(exist_ok=True)
    frame.to_parquet(OUT / 'features/paired-flow-features.parquet', index=False)
    write(OUT / 'manifests/feature-schema.json', {'families': FAMILIES, 'features': FEATURES,
          'numeric_inputs': ['pre_' + f for f in FEATURES], 'target_columns': ['post_' + f for f in FEATURES],
          'FR_packet_runs': 'positive payload direction runs incl retransmissions; nonempty 1+switches',
          'R_unique_zero_runs': 'positive newly observed TCP bytes arrival direction runs; zero threshold',
          'ordering': ['timestamp_ns', 'raw_packet_ordinal'], 'up_direction': 1, 'down_direction': -1,
          'post_only_attack_interface': False, 'test_pre_offline_measurement_allowed': True,
          'classifier_fitted': False, 'metadata_numeric_inputs': [], 'raw_captures_opened': 0})
    write(OUT / 'features/features-complete.json', {'rows': len(frame), 'missing_required': 0,
           'T_replay_exact': True, 'member_set_unchanged': True, 'content_weights_verified': True})
    checkpoint('Q10_features_complete', {'pairs': len(frame), 'missing': 0})
    print('All ten features complete; exact T replay; no missing or removed pairs', flush=True)


if __name__ == '__main__':
    run()
