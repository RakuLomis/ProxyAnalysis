"""Trusted adapters strip query identity before any numerical predictor call."""
from .common import *


def common_query(role, path):
    d = package(path, role, 'common-query-pre')
    values = t(d[HIST].to_numpy())
    route = d[['query_key', 'content_token']].copy()
    route.insert(0, 'row', np.arange(len(d)))
    return values, route


def anonymous_fit(role, path):
    d = package(path, role, 'anonymous-fit')
    need(set(d) == {'content_token', 'fit_mass', *HIST}, 'Anonymous fit schema')
    need(np.allclose(d.fit_mass, 1/48, atol=1e-15, rtol=0), 'Equal fit mass')
    # No common visit key; the two returned groupings remain independent.
    return t(d[HIST].to_numpy()), d.content_token.to_numpy()


def score_post(role, path, route):
    d = package(path, role, 'C-score')
    need(d.query_key.is_unique and set(d.query_key) == set(route.query_key), 'Score key mismatch')
    d = d.set_index('query_key').loc[route.query_key].reset_index()
    need(d.content_token.tolist() == route.content_token.tolist(), 'Score content mismatch')
    return t(d[HIST].to_numpy())
