"""Binary direction transition matrix and entropy."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


@dataclass(frozen=True, slots=True)
class TransitionFeatures:
    packet_count: int
    n_pp: int
    n_pm: int
    n_mp: int
    n_mm: int
    p_pp: float | None
    p_pm: float | None
    p_mp: float | None
    p_mm: float | None
    direction_entropy_bits: float | None
    transition_entropy_bits: float | None


def _entropy(probabilities: Iterable[float]) -> float:
    return -sum(value * math.log2(value) for value in probabilities if value > 0)


def transition_features(directions: Iterable[int]) -> TransitionFeatures:
    values = list(directions)
    if any(value not in (-1, 1) for value in values):
        raise ValueError("directions must contain only +1 and -1")
    n_pp = n_pm = n_mp = n_mm = 0
    for previous, current in zip(values, values[1:]):
        if previous == 1 and current == 1:
            n_pp += 1
        elif previous == 1 and current == -1:
            n_pm += 1
        elif previous == -1 and current == 1:
            n_mp += 1
        else:
            n_mm += 1
    plus_row = n_pp + n_pm
    minus_row = n_mp + n_mm
    p_pp = n_pp / plus_row if plus_row else None
    p_pm = n_pm / plus_row if plus_row else None
    p_mp = n_mp / minus_row if minus_row else None
    p_mm = n_mm / minus_row if minus_row else None

    if values:
        plus_fraction = values.count(1) / len(values)
        direction_entropy = _entropy((plus_fraction, 1 - plus_fraction))
    else:
        direction_entropy = None
    transition_count = plus_row + minus_row
    if transition_count:
        conditional = 0.0
        if plus_row:
            conditional += plus_row / transition_count * _entropy((p_pp or 0.0, p_pm or 0.0))
        if minus_row:
            conditional += minus_row / transition_count * _entropy((p_mp or 0.0, p_mm or 0.0))
    else:
        conditional = None
    return TransitionFeatures(
        len(values),
        n_pp,
        n_pm,
        n_mp,
        n_mm,
        p_pp,
        p_pm,
        p_mp,
        p_mm,
        direction_entropy,
        conditional,
    )

