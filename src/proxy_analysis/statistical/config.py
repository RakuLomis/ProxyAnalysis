"""Frozen configuration and metric dictionary for statistical analysis."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml


PROTOCOLS = {"HYSTERIA2", "SHADOWSOCKS", "VLESS"}


@dataclass(frozen=True)
class MetricSpec:
    metric_id: str
    family: str
    transform: str
    protocols: tuple[str, ...]
    practical_threshold: str
    pre_column: str | None = None
    post_column: str | None = None
    delta_column: str | None = None
    distance_column: str | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "MetricSpec":
        protocols = tuple(str(item) for item in value.get("protocols", ()))
        if not protocols or not set(protocols).issubset(PROTOCOLS):
            raise ValueError(f"invalid protocols for metric {value.get('id')}: {protocols}")
        columns = {
            name: value.get(name)
            for name in ("pre_column", "post_column", "delta_column", "distance_column")
        }
        if columns["distance_column"]:
            if columns["pre_column"] or columns["post_column"]:
                raise ValueError(f"distance metric cannot also define pre/post: {value.get('id')}")
        elif not columns["pre_column"] or not columns["post_column"]:
            raise ValueError(f"paired metric requires pre_column and post_column: {value.get('id')}")
        return cls(
            metric_id=str(value["id"]),
            family=str(value["family"]),
            transform=str(value["transform"]),
            protocols=protocols,
            practical_threshold=str(value["practical_threshold"]),
            **columns,
        )

    @property
    def columns(self) -> tuple[str, ...]:
        return tuple(
            str(value)
            for value in (
                self.pre_column,
                self.post_column,
                self.delta_column,
                self.distance_column,
            )
            if value
        )


@dataclass(frozen=True)
class StatisticalConfig:
    schema_version: int
    implementation_version: int
    seed: int
    bootstrap_repetitions: int
    permutation_repetitions: int
    confidence_level: float
    fdr_alpha: float
    minimum_paired_clusters: int
    url_protocol_policy: Mapping[str, Mapping[str, str]]
    interpretation_policy: Mapping[str, Mapping[str, Any]]
    cohorts: Mapping[str, Mapping[str, Any]]
    practical_thresholds: Mapping[str, float]
    metrics: tuple[MetricSpec, ...]
    sha256: str

    @classmethod
    def load(cls, path: Path | str) -> "StatisticalConfig":
        source = Path(path)
        raw = yaml.safe_load(source.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("statistical config must be a mapping")
        canonical = json.dumps(raw, sort_keys=True, separators=(",", ":"))
        metrics = tuple(MetricSpec.from_mapping(item) for item in raw.get("metrics", ()))
        ids = [item.metric_id for item in metrics]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("metric ids must be present and unique")
        thresholds = {
            str(key): float(value)
            for key, value in raw.get("practical_thresholds", {}).items()
        }
        unknown_thresholds = {
            metric.practical_threshold for metric in metrics
        } - set(thresholds)
        if unknown_thresholds:
            raise ValueError(f"unknown practical thresholds: {sorted(unknown_thresholds)}")
        confidence = float(raw["confidence_level"])
        fdr = float(raw["fdr_alpha"])
        if not 0 < confidence < 1 or not 0 < fdr < 1:
            raise ValueError("confidence_level and fdr_alpha must be between zero and one")
        return cls(
            schema_version=int(raw["schema_version"]),
            implementation_version=int(raw["implementation_version"]),
            seed=int(raw["seed"]),
            bootstrap_repetitions=int(raw["bootstrap_repetitions"]),
            permutation_repetitions=int(raw["permutation_repetitions"]),
            confidence_level=confidence,
            fdr_alpha=fdr,
            minimum_paired_clusters=int(raw["minimum_paired_clusters"]),
            url_protocol_policy=raw["url_protocol_policy"],
            interpretation_policy=raw["interpretation_policy"],
            cohorts=raw["cohorts"],
            practical_thresholds=thresholds,
            metrics=metrics,
            sha256=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        )

    def validate_page_columns(self, columns: set[str]) -> None:
        missing = sorted(
            {column for metric in self.metrics for column in metric.columns} - columns
        )
        if missing:
            raise ValueError(f"configured metric columns missing from page table: {missing}")
