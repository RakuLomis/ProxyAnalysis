"""Command line entry point for inspectable pipeline stages."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import platform
import sys
from typing import Sequence

from . import __version__
from .config import FeatureConfig
from .inventory import InventoryScanner, inventory_summary
from .indexing.traffictracer import aggregate_index_audits, audit_session_indexes
from .pipeline.extract_packets import CaptureSource, write_packet_events
from .indexing.identities import build_entity_descriptors
from .pipeline.analyze_entity import analyze_entity_capture
from .features.core import extract_core_entity_features
from .features.pairwise import extract_pairwise_features
from .indexing.pairs import build_exclusive_pairs
from .features.web import extract_web_features
from .features.hysteria2 import extract_hysteria2_window_features
from .indexing.hysteria2 import build_hysteria2_carrier_windows
from .pipeline.batch import process_dataset, process_session
from .pipeline.export_ml import export_ml_tables, validate_ml_tables
from .quality.reports import build_quality_report
from .modeling.datasets import build_dual_track_datasets
from .modeling.baselines import run_all_protocol_baselines
from .modeling.statistics import analyze_transformation_track
from .modeling.evaluation import run_formal_tabular_evaluation
from .alignment.build import (
    build_page_aligned_protocol_features,
    build_url_aligned_pair_features,
    build_url_connection_index,
)
from .alignment.quality import validate_aligned_datasets
from .statistical.marts import build_statistical_marts
from .statistical.page import run_page_statistics
from .statistical.resource import run_resource_statistics
from .statistical.sensitivity import run_sensitivity_analysis
from .statistical.reporting import finalize_statistical_analysis


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="proxy-analysis")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("env", help="show the active Python environment")

    config_parser = subparsers.add_parser("config-check", help="validate feature config")
    config_parser.add_argument("path", type=Path)

    inventory_parser = subparsers.add_parser("inventory", help="scan dataset manifests")
    inventory_parser.add_argument("dataset_root", type=Path)
    inventory_parser.add_argument("--output", type=Path)

    audit_parser = subparsers.add_parser("index-audit", help="audit TrafficTracer indexes")
    audit_parser.add_argument("dataset_root", type=Path)
    audit_parser.add_argument("--output", type=Path)

    extract_parser = subparsers.add_parser(
        "extract-capture", help="write raw packet events for one PCAPNG artifact"
    )
    extract_parser.add_argument("input", type=Path)
    extract_parser.add_argument("output", type=Path)
    extract_parser.add_argument("--protocol", required=True)
    extract_parser.add_argument("--session-id", required=True)
    extract_parser.add_argument("--artifact-id", required=True)
    extract_parser.add_argument("--side", choices=("pre", "post"), required=True)
    extract_parser.add_argument("--config", type=Path, default=Path("configs/feature-defaults.yaml"))

    entity_parser = subparsers.add_parser(
        "entity-audit", help="build deduplicated pre/outer/carrier capture identities"
    )
    entity_parser.add_argument("dataset_root", type=Path)
    entity_parser.add_argument("--output", type=Path)

    feature_parser = subparsers.add_parser(
        "extract-entity-features", help="extract core features for one indexed entity"
    )
    feature_parser.add_argument("session_path", type=Path)
    feature_parser.add_argument("output", type=Path)
    feature_parser.add_argument("--protocol", required=True)
    feature_parser.add_argument("--entity-id", required=True)
    feature_parser.add_argument("--side", choices=("pre", "post"), required=True)
    feature_parser.add_argument("--config", type=Path, default=Path("configs/feature-defaults.yaml"))

    pair_parser = subparsers.add_parser(
        "extract-pair-features", help="extract pre/post features for one exclusive pair"
    )
    pair_parser.add_argument("session_path", type=Path)
    pair_parser.add_argument("output", type=Path)
    pair_parser.add_argument("--protocol", choices=("VLESS", "SHADOWSOCKS"), required=True)
    pair_parser.add_argument("--connection-id", required=True)
    pair_parser.add_argument("--config", type=Path, default=Path("configs/feature-defaults.yaml"))

    web_parser = subparsers.add_parser(
        "extract-web-features", help="extract URL/host concurrency and multiplexing"
    )
    web_parser.add_argument("session_path", type=Path)
    web_parser.add_argument("output", type=Path)
    web_parser.add_argument("--protocol", required=True)

    hy2_parser = subparsers.add_parser(
        "extract-hy2-window-features",
        help="extract aggregate-inner/shared-carrier dual-window features",
    )
    hy2_parser.add_argument("session_path", type=Path)
    hy2_parser.add_argument("output", type=Path)
    hy2_parser.add_argument("--carrier-id", required=True)
    hy2_parser.add_argument("--config", type=Path, default=Path("configs/feature-defaults.yaml"))

    batch_parser = subparsers.add_parser(
        "run-dataset", help="checkpointed feature extraction over dataset sessions"
    )
    batch_parser.add_argument("dataset_root", type=Path)
    batch_parser.add_argument("output_root", type=Path)
    batch_parser.add_argument("--protocol", action="append", dest="protocols")
    batch_parser.add_argument("--session-id", action="append", dest="session_ids")
    batch_parser.add_argument("--limit", type=int)
    batch_parser.add_argument("--force", action="store_true")
    batch_parser.add_argument("--config", type=Path, default=Path("configs/feature-defaults.yaml"))

    export_parser = subparsers.add_parser(
        "export-ml", help="flatten numeric features and add deterministic group splits"
    )
    export_parser.add_argument("feature_root", type=Path)
    export_parser.add_argument("output_root", type=Path)
    export_parser.add_argument("--seed", default="proxy-analysis-v1")

    validate_export_parser = subparsers.add_parser(
        "validate-ml", help="validate ML table types and group split isolation"
    )
    validate_export_parser.add_argument("output_root", type=Path)
    validate_export_parser.add_argument("--output", type=Path)

    quality_parser = subparsers.add_parser(
        "quality-report", help="run feature invariants and dataset quality gates"
    )
    quality_parser.add_argument("feature_root", type=Path)
    quality_parser.add_argument("--session-id", action="append", default=None)
    quality_parser.add_argument("--output", type=Path)

    dual_parser = subparsers.add_parser(
        "build-dual-track", help="build frozen transformation and protocol datasets"
    )
    dual_parser.add_argument("ml_root", type=Path)
    dual_parser.add_argument("output_root", type=Path)

    baseline_parser = subparsers.add_parser(
        "run-protocol-baselines", help="run site-isolated Track B baselines"
    )
    baseline_parser.add_argument("dataset_root", type=Path)
    baseline_parser.add_argument("output_root", type=Path)
    baseline_parser.add_argument("--seed", type=int, default=20260901)

    stats_parser = subparsers.add_parser(
        "analyze-transformations", help="run session-weighted Track A statistics"
    )
    stats_parser.add_argument("dataset", type=Path)
    stats_parser.add_argument("output", type=Path)
    stats_parser.add_argument("--seed", type=int, default=20260901)
    stats_parser.add_argument("--bootstrap-repetitions", type=int, default=2000)

    formal_parser = subparsers.add_parser(
        "evaluate-tabular", help="run repeated nested site-group CV and ablations"
    )
    formal_parser.add_argument("dataset_root", type=Path)
    formal_parser.add_argument("output_root", type=Path)
    formal_parser.add_argument("--seed", type=int, default=20260901)
    formal_parser.add_argument("--outer-splits", type=int, default=5)
    formal_parser.add_argument("--outer-repeats", type=int, default=5)
    formal_parser.add_argument("--inner-splits", type=int, default=4)

    url_index_parser = subparsers.add_parser(
        "build-url-index", help="build request-level URL/connection/entity index"
    )
    url_index_parser.add_argument("dataset_root", type=Path)
    url_index_parser.add_argument("output", type=Path)
    url_index_parser.add_argument("--registry", type=Path)

    url_pair_parser = subparsers.add_parser(
        "build-url-pairs", help="join URL incidences to processed pre/post features"
    )
    url_pair_parser.add_argument("url_index", type=Path)
    url_pair_parser.add_argument("ml_root", type=Path)
    url_pair_parser.add_argument("experiment_root", type=Path)
    url_pair_parser.add_argument("output", type=Path)

    page_parser = subparsers.add_parser(
        "build-page-protocol", help="aggregate unique proxy entities by target URL and protocol"
    )
    page_parser.add_argument("url_index", type=Path)
    page_parser.add_argument("ml_root", type=Path)
    page_parser.add_argument("output", type=Path)

    aligned_quality_parser = subparsers.add_parser(
        "validate-aligned", help="validate aligned tables and write lineage manifest"
    )
    aligned_quality_parser.add_argument("aligned_root", type=Path)
    aligned_quality_parser.add_argument("--registry", type=Path)

    statistical_mart_parser = subparsers.add_parser(
        "build-statistical-marts", help="freeze statistical cohorts and coverage audit"
    )
    statistical_mart_parser.add_argument("aligned_root", type=Path)
    statistical_mart_parser.add_argument("output_root", type=Path)
    statistical_mart_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/statistical-analysis.yaml"),
    )

    page_statistics_parser = subparsers.add_parser(
        "run-page-statistics", help="run Q1/Q2 paired page-level statistics"
    )
    page_statistics_parser.add_argument("marts_root", type=Path)
    page_statistics_parser.add_argument("output_root", type=Path)
    page_statistics_parser.add_argument(
        "--config", type=Path, default=Path("configs/statistical-analysis.yaml")
    )

    resource_statistics_parser = subparsers.add_parser(
        "run-resource-statistics", help="run URL/host strict and weighted statistics"
    )
    resource_statistics_parser.add_argument("marts_root", type=Path)
    resource_statistics_parser.add_argument("output_root", type=Path)
    resource_statistics_parser.add_argument(
        "--config", type=Path, default=Path("configs/statistical-analysis.yaml")
    )

    sensitivity_parser = subparsers.add_parser(
        "run-statistical-sensitivity", help="run pre-registered direction robustness checks"
    )
    sensitivity_parser.add_argument("marts_root", type=Path)
    sensitivity_parser.add_argument("output_root", type=Path)
    sensitivity_parser.add_argument(
        "--config", type=Path, default=Path("configs/statistical-analysis.yaml")
    )

    finalize_statistics_parser = subparsers.add_parser(
        "finalize-statistics", help="write statistical figures, tables, quality, and manifest"
    )
    finalize_statistics_parser.add_argument("output_root", type=Path)
    finalize_statistics_parser.add_argument("--interpretation-addendum", type=Path)
    finalize_statistics_parser.add_argument(
        "--config", type=Path, default=Path("configs/statistical-analysis.yaml")
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "env":
        print(
            json.dumps(
                {
                    "python": sys.executable,
                    "python_version": platform.python_version(),
                    "platform": platform.platform(),
                    "package_version": __version__,
                },
                indent=2,
            )
        )
        return 0
    if args.command == "config-check":
        config = FeatureConfig.load(args.path)
        print(json.dumps({"schema_version": config.schema_version, "sha256": config.sha256}))
        return 0
    if args.command == "inventory":
        sessions = InventoryScanner(args.dataset_root).scan()
        result = {
            "summary": inventory_summary(sessions),
            "sessions": [asdict(session) for session in sessions],
        }
        rendered = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
        print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
        return 0 if result["summary"]["sessions_with_errors"] == 0 else 2
    if args.command == "index-audit":
        sessions = InventoryScanner(args.dataset_root).scan()
        audits = [
            audit_session_indexes(session.session_path, session.protocol_dataset)
            for session in sessions
        ]
        result = {
            "summary": aggregate_index_audits(audits),
            "sessions": [audit.to_dict() for audit in audits],
        }
        rendered = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
        print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
        failures = sum(
            result["summary"]["totals"][field]
            for field in (
                "request_connection_orphans",
                "pcap_connection_orphans",
                "connection_request_orphans",
                "duplicate_connection_ids",
                "duplicate_request_occurrence_ids",
            )
        )
        return 0 if failures == 0 else 2
    if args.command == "extract-capture":
        config = FeatureConfig.load(args.config)
        threshold = int(config.values["offload"]["suspected_ip_len_above_bytes"])
        source = CaptureSource(
            dataset_protocol=args.protocol,
            session_id=args.session_id,
            source_artifact_id=args.artifact_id,
            source_path=args.input,
            capture_side=args.side,
        )
        summary = write_packet_events(
            source, args.output, offload_ip_len_threshold=threshold
        )
        summary["feature_schema_version"] = config.schema_version
        summary["feature_config_sha256"] = config.sha256
        print(json.dumps(summary, indent=2))
        return 0 if summary["decode_failed_count"] == 0 else 2
    if args.command == "entity-audit":
        sessions = InventoryScanner(args.dataset_root).scan()
        rows = []
        for session in sessions:
            descriptors = build_entity_descriptors(
                session.session_path, session.protocol_dataset
            )
            rows.append(
                {
                    "session_id": session.session_id,
                    "protocol_dataset": session.protocol_dataset,
                    "descriptor_count": len(descriptors),
                    "pre_logical_connections": sum(
                        item.capture_side == "pre" for item in descriptors
                    ),
                    "post_outer_connections": sum(
                        item.entity_level == "outer_connection" for item in descriptors
                    ),
                    "post_carriers": sum(
                        item.entity_level == "carrier" for item in descriptors
                    ),
                    "shared_logical_bindings": sum(
                        len(item.logical_connection_ids)
                        for item in descriptors
                        if item.entity_level == "carrier"
                    ),
                }
            )
        protocols = sorted({row["protocol_dataset"] for row in rows})
        summary = {
            "session_count": len(rows),
            "descriptor_count": sum(row["descriptor_count"] for row in rows),
            "by_protocol": {
                protocol: {
                    key: sum(row[key] for row in rows if row["protocol_dataset"] == protocol)
                    for key in (
                        "descriptor_count",
                        "pre_logical_connections",
                        "post_outer_connections",
                        "post_carriers",
                        "shared_logical_bindings",
                    )
                }
                for protocol in protocols
            },
        }
        result = {"summary": summary, "sessions": rows}
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if args.command == "extract-entity-features":
        config = FeatureConfig.load(args.config)
        matches = [
            item
            for item in build_entity_descriptors(args.session_path, args.protocol)
            if item.entity_id == args.entity_id and item.capture_side == args.side
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected exactly one descriptor, found {len(matches)} for "
                f"{args.entity_id}/{args.side}"
            )
        analysis = analyze_entity_capture(matches[0])
        features = extract_core_entity_features(analysis, config)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(features, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "entity_id": features["entity_id"],
                    "packet_count": features["packet_count"],
                    "unknown_direction_count": features["unknown_direction_count"],
                    "output": str(args.output),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if features["unknown_direction_count"] == 0 else 2
    if args.command == "extract-pair-features":
        config = FeatureConfig.load(args.config)
        matches = [
            item
            for item in build_exclusive_pairs(args.session_path, args.protocol)
            if item.connection_id == args.connection_id
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected exactly one exclusive pair, found {len(matches)} for "
                f"{args.connection_id}"
            )
        pair = matches[0]
        pre = analyze_entity_capture(pair.pre)
        post = analyze_entity_capture(pair.post)
        features = extract_pairwise_features(pre, post, config)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(features, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        summary = {
            "connection_id": pair.connection_id,
            "pre_packets": pre.packet_count,
            "post_packets": post.packet_count,
            "pre_transport": pair.pre.transport_protocol,
            "post_transport": pair.post.transport_protocol,
            "output": str(args.output),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if pre.unknown_direction_count + post.unknown_direction_count == 0 else 2
    if args.command == "extract-web-features":
        features = extract_web_features(args.session_path, args.protocol)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(features, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "session_id": features["session_id"],
                    "request_count": features["request_count"],
                    "connection_count": features["connection_count"],
                    "carrier_count": len(features["carrier_features"]),
                    "output": str(args.output),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "extract-hy2-window-features":
        config = FeatureConfig.load(args.config)
        matches = [
            item
            for item in build_hysteria2_carrier_windows(args.session_path)
            if item.carrier_id == args.carrier_id
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected exactly one Hysteria2 carrier window, found {len(matches)}"
            )
        features = extract_hysteria2_window_features(matches[0], config)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(features, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "carrier_id": features["carrier_id"],
                    "logical_connection_count": features["logical_connection_count"],
                    "inner_packet_count": features["inner_packet_count"],
                    "carrier_full_packet_count": features["carrier_full_packet_count"],
                    "output": str(args.output),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "run-dataset":
        config = FeatureConfig.load(args.config)

        def show_progress(index, total, session, result):
            print(
                f"[{index}/{total}] {session.protocol_dataset}/{session.target_domain} "
                f"state={result['state']} skipped={result.get('skipped', False)}",
                flush=True,
            )

        results = process_dataset(
            args.dataset_root,
            args.output_root,
            config,
            protocols=args.protocols,
            session_ids=args.session_ids,
            limit=args.limit,
            force=args.force,
            progress=show_progress,
        )
        summary = {
            "session_count": len(results),
            "completed": sum(item["state"] == "complete" for item in results),
            "skipped": sum(bool(item.get("skipped")) for item in results),
            "entity_records": sum(item.get("entity_record_count", 0) for item in results),
            "exclusive_pair_records": sum(
                item.get("exclusive_pair_record_count", 0) for item in results
            ),
            "hysteria2_window_records": sum(
                item.get("hysteria2_window_record_count", 0) for item in results
            ),
        }
        print(json.dumps(summary, indent=2))
        return 0
    if args.command == "export-ml":
        counts = export_ml_tables(args.feature_root, args.output_root, seed=args.seed)
        print(json.dumps(counts, indent=2))
        return 0
    if args.command == "validate-ml":
        report = validate_ml_tables(args.output_root)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        print(
            json.dumps(
                {
                    "state": report["state"],
                    "error_count": report["error_count"],
                    "tables": report["tables"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if report["state"] == "passed" else 2
    if args.command == "quality-report":
        report = build_quality_report(args.feature_root, expected_session_ids=args.session_id)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        print(
            json.dumps(
                {
                    key: report[key]
                    for key in (
                        "state",
                        "session_count",
                        "record_counts",
                        "error_count",
                        "warning_count",
                    )
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if report["state"] == "passed" else 2
    if args.command == "build-dual-track":
        manifest = build_dual_track_datasets(args.ml_root, args.output_root)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    if args.command == "run-protocol-baselines":
        summary = run_all_protocol_baselines(
            args.dataset_root, args.output_root, seed=args.seed
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if args.command == "analyze-transformations":
        report = analyze_transformation_track(
            args.dataset,
            args.output,
            seed=args.seed,
            bootstrap_repetitions=args.bootstrap_repetitions,
        )
        significant = sum(
            metric["omnibus_kruskal_wallis"] is not None
            and metric["omnibus_kruskal_wallis"].get("qvalue_bh_across_metrics", 1) < 0.05
            for metric in report["metrics"].values()
        )
        print(
            json.dumps(
                {
                    "metric_count": len(report["metrics"]),
                    "significant_omnibus_bh_005": significant,
                    "output": str(args.output),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "evaluate-tabular":
        report = run_formal_tabular_evaluation(
            args.dataset_root,
            args.output_root,
            seed=args.seed,
            outer_splits=args.outer_splits,
            outer_repeats=args.outer_repeats,
            inner_splits=args.inner_splits,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    if args.command == "build-url-index":
        summary = build_url_connection_index(args.dataset_root, args.output, registry=args.registry)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if args.command == "build-url-pairs":
        summary = build_url_aligned_pair_features(
            args.url_index, args.ml_root, args.experiment_root, args.output
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if args.command == "build-page-protocol":
        summary = build_page_aligned_protocol_features(
            args.url_index, args.ml_root, args.output
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if args.command == "validate-aligned":
        report = validate_aligned_datasets(args.aligned_root, registry=args.registry)
        print(
            json.dumps(
                {
                    "state": report["state"],
                    "error_count": report["error_count"],
                    "warning_count": report["warning_count"],
                    "tables": report["tables"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if report["state"] == "passed" else 2
    if args.command == "build-statistical-marts":
        audit = build_statistical_marts(
            args.aligned_root, args.output_root, args.config
        )
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        return 0
    if args.command == "run-page-statistics":
        report = run_page_statistics(args.marts_root, args.output_root, args.config)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    if args.command == "run-resource-statistics":
        report = run_resource_statistics(
            args.marts_root, args.output_root, args.config
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    if args.command == "run-statistical-sensitivity":
        report = run_sensitivity_analysis(
            args.marts_root, args.output_root, args.config
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    if args.command == "finalize-statistics":
        report = finalize_statistical_analysis(args.output_root, args.config, interpretation_addendum=args.interpretation_addendum)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["state"] == "passed" else 2
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
