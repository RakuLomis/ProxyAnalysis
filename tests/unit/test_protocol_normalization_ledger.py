from dataclasses import replace
import random

import pytest

from proxy_analysis.sequences.tcp_state import TcpPacket, analyze_tcp_flow
from proxy_analysis.protocol_normalization.tcp_ledger import ledger, interval_union, conflicts
from proxy_analysis.protocol_normalization.byte_runs import merge_runs, multiscale


def packet(i, seq, size, direction=1, flags=16):
    return TcpPacket(str(i), i*1000, i, direction, seq, 0, flags, size)


def run(ps, payloads=None):
    if payloads is None:
        payloads = {p.packet_event_id: b'X'*p.payload_len for p in ps}
    return ledger(ps, analyze_tcp_flow(ps).segments, payloads)


def test_partial_overlap_full_repeat_and_union_identity():
    rows, events, _ = run([packet(1,100,10), packet(2,105,10), packet(3,100,10)])
    up = rows[0]
    assert up['observed_payload_bytes'] == 30
    assert up['unique_payload_bytes'] == 15
    assert up['duplicate_payload_bytes'] == 15
    assert up['exclude_full_retransmission_bytes'] == 20
    assert [x['new_payload_bytes'] for x in events] == [10,5]


def test_syn_and_fin_sequence_positions_not_payload():
    rows, _, _ = run([packet(1,100,5,flags=2),packet(2,106,0,flags=1)])
    assert rows[0]['unique_payload_bytes'] == 5
    assert rows[0]['closed_contiguous_capture_candidate']
    assert rows[0]['quality'] == 'Q1'  # TCP flags alone do not prove successful proxy relay.


def test_wrap_and_out_of_order():
    rows, _, _ = run([packet(1,2**32-4,8),packet(2,4,3),packet(3,2**32-2,4)])
    assert rows[0]['unique_payload_bytes'] == 11
    assert rows[0]['duplicate_payload_bytes'] == 4
    assert rows[0]['final_internal_gap_count'] == 0


def test_gap_not_filled_and_prefix_unknown():
    rows, _, _ = run([packet(1,100,3),packet(2,108,2)])
    assert rows[0]['unique_payload_bytes'] == 5
    assert rows[0]['final_internal_gap_bytes'] == 5
    assert not rows[0]['prefix_observed']


def test_conflicting_overlap_rejected():
    ps = [packet(1,100,3),packet(2,101,3)]
    rows, events, runs = run(ps, {'1':b'abc','2':b'ZZd'})
    assert rows[0]['quality'] == 'Q0'
    assert rows[0]['unique_payload_bytes'] is None
    assert not events and not runs


def test_epoch_reuse_rejected():
    rows, _, runs = run([packet(1,100,0,flags=2),packet(2,101,10),packet(3,500,0,flags=2)])
    assert rows[0]['sequence_epoch_ambiguous']
    assert rows[0]['unique_payload_bytes'] is None
    assert not runs


def test_half_space_ambiguity_rejected():
    rows, _, _ = run([packet(1,0,1),packet(2,2**31,1)])
    assert rows[0]['quality'] == 'Q0'


def test_resegmentation_and_repetition_byte_mass():
    a, _, _ = run([packet(1,100,100)])
    b, _, _ = run([packet(1,100,40),packet(2,140,60),packet(3,100,100)])
    assert a[0]['unique_payload_bytes'] == b[0]['unique_payload_bytes'] == 100


def test_curve_endpoint_and_two_directions():
    rows, _, runs = run([packet(1,100,10),packet(2,900,20,direction=-1),packet(3,110,2)])
    assert rows[0]['new_byte_curve_absolute'][-1] == 12
    assert rows[1]['new_byte_curve_absolute'][-1] == 20
    assert runs[0]['run_count'] == 3
    assert runs[1]['zero_run'] and runs[1]['retained_fraction'] == 0


def test_threshold_is_one_pass_simultaneous():
    r = multiscale([(1,30),(-1,1),(1,40)])[1]
    assert r['run_count'] == 0  # Do not delete middle first then join 30+40 and keep it.
    r = multiscale([(1,70),(-1,1),(1,80)])[1]
    assert r['run_count'] == 1 and r['retained_bytes'] == 150
    assert r['down_retained_fraction'] == 0


def test_empty_zero_byte_and_rst():
    rows, events, _ = run([packet(1,100,0,flags=4)])
    assert rows[0]['unique_payload_bytes'] == 0
    assert rows[0]['duplicate_fraction'] is None
    assert rows[0]['new_byte_curve_normalized'] is None
    assert not events
    assert 'rst_observed' in rows[0]['qualification_reasons']


def test_timestamp_tie_order():
    ps = [replace(packet(2,100,5),timestamp_ns=1),replace(packet(1,200,4,-1),timestamp_ns=1)]
    _, events, _ = run(ps)
    assert [e['direction'] for e in events] == [-1,1]


def test_independent_union_randomized():
    rng = random.Random(20260922)
    for _ in range(100):
        intervals = [(rng.randrange(200),rng.randrange(1,50)) for _ in range(20)]
        ps = [packet(i+1,start,size) for i,(start,size) in enumerate(intervals)]
        rows,_,_ = run(ps)
        expected = len({x for start,size in intervals for x in range(start,start+size)})
        assert rows[0]['unique_payload_bytes'] == expected


def test_capture_integrity_failure_does_not_export_unique():
    p = [packet(1,100,1)]
    rows, events, _ = ledger(p,analyze_tcp_flow(p).segments,{'1':b'x'},False)
    assert rows[0]['quality'] == 'Q0' and not events


def test_negative_unwrapped_positions_do_not_conflict_with_empty_reference():
    assert conflicts([(-10,b'abc'),(-9,b'bcde')]) == 0
    assert conflicts([(-10,b'abc'),(-9,b'XYde')]) == 1


def test_initial_capture_after_wrap_then_earlier_segment():
    rows,_,_ = run([packet(1,2,5),packet(2,2**32-2,4)])
    assert rows[0]['unique_payload_bytes'] == 9
    assert rows[0]['overlap_content_conflicts'] == 0
