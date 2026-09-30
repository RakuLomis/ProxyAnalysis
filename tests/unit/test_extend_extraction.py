from collections import defaultdict

from proxy_analysis.extend_calibration.extraction import mapping_add, summarize, valid_window


def test_global_runs_are_not_summed_across_connections():
    rows = [dict(timestamp_ns=1, raw_packet_ordinal=1, direction=1, payload_bytes=10, entity_id='a'),
            dict(timestamp_ns=2, raw_packet_ordinal=2, direction=1, payload_bytes=10, entity_id='b'),
            dict(timestamp_ns=3, raw_packet_ordinal=3, direction=-1, payload_bytes=20, entity_id='a')]
    assert summarize(rows) == dict(W_up=20,W_down=20,P_up=2,P_down=1,R_up=1,R_down=1)
    assert valid_window(summarize(rows))


def test_carrier_duplicates_do_not_multiply_mapping():
    mapping = defaultdict(set)
    flow = dict(network='tcp',src_ip='a',src_port=1,dst_ip='b',dst_port=2)
    assert mapping_add(mapping,flow,'carrier')
    assert mapping_add(mapping,flow,'carrier')
    assert len(mapping[('tcp','a',1,'b',2)]) == 1
    mapping_add(mapping,flow,'other')
    assert len(mapping[('tcp','a',1,'b',2)]) == 2


def test_zero_events_and_bad_runs_fail():
    assert not valid_window(summarize([]))
    s = dict(W_up=10,W_down=0,P_up=1,P_down=0,R_up=1,R_down=0)
    assert valid_window(s)
    s['R_up'] = 3
    assert not valid_window(s)


def test_tie_break_is_raw_ordinal_and_nonpositive_not_counted():
    rows = [dict(timestamp_ns=1,raw_packet_ordinal=2,direction=-1,payload_bytes=1),
            dict(timestamp_ns=1,raw_packet_ordinal=1,direction=1,payload_bytes=1),
            dict(timestamp_ns=2,raw_packet_ordinal=3,direction=1,payload_bytes=0)]
    assert summarize(rows)['R_up'] == 1
    assert summarize(rows)['P_up'] == 1
