"""Strict, versioned configuration loading and hashing."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml


class ConfigError(ValueError):
    """Raised when a configuration violates the frozen contract."""


_EXPECTED_TOP_LEVEL = {
    "feature_schema_version",
    "lengths",
    "iat",
    "offload",
    "burst",
    "active_idle",
    "sequence",
    "cumulative_shape",
    "histograms",
    "ratios",
    "tcp",
    "privacy",
    "pairing",
    "splitting",
}


@dataclass(frozen=True, slots=True)
class FeatureConfig:
    """Validated feature configuration plus its canonical content hash."""

    values: Mapping[str, Any]
    sha256: str

    @property
    def schema_version(self) -> int:
        return int(self.values["feature_schema_version"])

    @property
    def epsilon(self) -> float:
        return float(self.values["ratios"]["epsilon"])

    @classmethod
    def load(cls, path: Path | str) -> "FeatureConfig":
        config_path = Path(path)
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ConfigError("feature configuration must be a mapping")
        _validate_feature_config(raw)
        canonical = json.dumps(raw, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(values=raw, sha256=digest)


def _require_mapping(parent: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"{key} must be a mapping")
    return value


def _positive_sorted_numbers(value: Any, name: str) -> None:
    if not isinstance(value, list) or not value:
        raise ConfigError(f"{name} must be a non-empty list")
    if any(not isinstance(item, (int, float)) or item < 0 for item in value):
        raise ConfigError(f"{name} must contain non-negative numbers")
    if any(left >= right for left, right in zip(value, value[1:])):
        raise ConfigError(f"{name} must be strictly increasing")


def _validate_feature_config(raw: Mapping[str, Any]) -> None:
    unknown = set(raw) - _EXPECTED_TOP_LEVEL
    missing = _EXPECTED_TOP_LEVEL - set(raw)
    if unknown:
        raise ConfigError(f"unknown top-level fields: {sorted(unknown)}")
    if missing:
        raise ConfigError(f"missing top-level fields: {sorted(missing)}")
    if raw["feature_schema_version"] != 1:
        raise ConfigError("only feature_schema_version=1 is currently supported")

    lengths = _require_mapping(raw, "lengths")
    if lengths.get("primary") != "transport_payload_len":
        raise ConfigError("v1 primary length must be transport_payload_len")
    if lengths.get("secondary") != "ip_total_len":
        raise ConfigError("v1 secondary length must be ip_total_len")

    offload = _require_mapping(raw, "offload")
    threshold = offload.get("suspected_ip_len_above_bytes")
    if not isinstance(threshold, int) or threshold <= 0:
        raise ConfigError("offload.suspected_ip_len_above_bytes must be a positive integer")

    burst = _require_mapping(raw, "burst")
    _positive_sorted_numbers(burst.get("time_gap_thresholds_ms"), "burst thresholds")
    active_idle = _require_mapping(raw, "active_idle")
    _positive_sorted_numbers(active_idle.get("thresholds_ms"), "active/idle thresholds")
    sequence = _require_mapping(raw, "sequence")
    _positive_sorted_numbers(sequence.get("prefix_lengths"), "sequence prefix lengths")

    shape = _require_mapping(raw, "cumulative_shape")
    if not isinstance(shape.get("grid_points"), int) or shape["grid_points"] < 2:
        raise ConfigError("cumulative_shape.grid_points must be an integer >= 2")
    if shape.get("interpolation") != "previous":
        raise ConfigError("v1 cumulative interpolation must be previous")

    histograms = _require_mapping(raw, "histograms")
    for key in (
        "transport_payload_len_edges_bytes",
        "ip_total_len_edges_bytes",
        "iat_edges_us",
    ):
        _positive_sorted_numbers(histograms.get(key), f"histograms.{key}")

    ratios = _require_mapping(raw, "ratios")
    epsilon = ratios.get("epsilon")
    if not isinstance(epsilon, (int, float)) or epsilon <= 0:
        raise ConfigError("ratios.epsilon must be positive")

    privacy = _require_mapping(raw, "privacy")
    if privacy.get("store_payload") is not False:
        raise ConfigError("v1 production configuration must not store payload")

    pairing = _require_mapping(raw, "pairing")
    if pairing.get("allow_hysteria2_logical_post") is not False:
        raise ConfigError("Hysteria2 logical-flow post pairing is forbidden")
    if pairing.get("js_log_base") != 2:
        raise ConfigError("v1 JS divergence must use log base 2")
    if not isinstance(pairing.get("low_power_min_samples"), int) or pairing[
        "low_power_min_samples"
    ] < 2:
        raise ConfigError("pairing.low_power_min_samples must be an integer >= 2")
    if pairing.get("wasserstein_iat_transform") != "log1p_us":
        raise ConfigError("v1 IAT Wasserstein transform must be log1p_us")
