import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location('extend_verify', Path(__file__).resolve().parents[2] / 'eval/extend_calibration/verify_extraction.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_recount_global_vs_connection_runs():
    frame = pd.DataFrame({'logical_id':['a','b','a','b'], 'timestamp_ns':[1,2,3,4],
        'raw_packet_ordinal':[1,2,3,4], 'direction':[1,1,1,-1], 'new_bytes':[3,4,5,6]})
    assert np.array_equal(module.recount(frame, 'new_bytes'), [12,6,3,1,1,1])
    assert np.array_equal(module.recount(frame, 'new_bytes', True), [12,6,3,1,2,1])


def test_recount_tie_order_and_duplicates():
    frame = pd.DataFrame({'timestamp_ns':[2,2,1], 'raw_packet_ordinal':[3,2,1],
        'direction':[1,-1,1], 'payload_bytes':[10,20,30]})
    assert np.array_equal(module.recount(frame, 'payload_bytes'), [40,20,2,1,2,1])
    with pytest.raises(AssertionError):
        module.recount(pd.concat([frame,frame.iloc[:1]]), 'payload_bytes')


def test_recount_empty():
    assert np.array_equal(module.recount(pd.DataFrame(), 'new_bytes', True), np.zeros(6))
