"""Manifest-driven repeated experiment identities; retries are not replicates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..pathutils import filesystem_path


def read_json(path: Path) -> Any:
    return json.loads(Path(filesystem_path(path)).read_text(encoding="utf-8-sig"))


def ordered_attempts(run: dict, contexts: dict[str, dict]) -> list[tuple[int, str, dict]]:
    """One-based chronological attempt, independent of the selected attempt."""
    selected = run['session_ids']
    referenced = set(selected) | set(run.get('prior_session_ids', []))
    attempts = run.get('attempts') or []
    result = []
    if attempts:
        for attempt in attempts:
            ordinal = attempt.get('ordinal')
            if not isinstance(ordinal, int) or ordinal < 1:
                raise ValueError('invalid attempt ordinal')
            ids = attempt.get('session_ids', [])
            if len(ids) != 1:
                raise ValueError('expected one session per recorded attempt')
            if 'selected' in attempt and bool(attempt['selected']) != (ids == selected):
                raise ValueError('attempt selected flag contradicts selected session')
            result.append((ordinal, ids[0], attempt))
        if {sid for _, sid, _ in result} != referenced:
            raise ValueError('attempt list/reference mismatch')
        if run.get('selected_attempt') is not None:
            chosen = [sid for n, sid, _ in result if n == run['selected_attempt']]
            if chosen != selected:
                raise ValueError('selected_attempt contradicts selected session')
    else:
        for sid in referenced:
            number = contexts[sid].get('orchestration', {}).get('application_retry_attempt')
            if number is None and len(referenced) == 1:
                number = 0
            if not isinstance(number, int) or number < 0:
                raise ValueError('legacy attempt chronology unavailable')
            result.append((number + 1, sid, {}))
    if len({n for n, _, _ in result}) != len(result) or len({s for _, s, _ in result}) != len(result):
        raise ValueError('duplicate attempt ordinal/session')
    return sorted(result, key=lambda item: item[0])


def discover_runs(root: Path) -> list[dict[str, Any]]:
    root = Path(filesystem_path(root))
    pipeline = read_json(root / "pipeline-manifest.json")
    targets = {target["index"]: target for target in pipeline["targets"]}
    sessions = {}
    for path in sorted((root / "runs").glob("*/*/*/*/manifest.json")):
        manifest = read_json(path)
        sid = manifest["session_id"]
        if sid in sessions:
            raise ValueError(f"duplicate session id: {sid}")
        sessions[sid] = (path, manifest)
    rows = []
    seen_cells = set()
    seen_sessions = set()
    for run in pipeline["runs"]:
        target = targets[run["target_index"]]
        protocol = run["expected_protocol"].upper()
        if protocol not in {"VLESS", "SHADOWSOCKS", "HYSTERIA2"}:
            raise ValueError(f"unsupported protocol: {protocol}")
        cell = (run["target_index"], protocol, run["repetition_index"])
        if cell in seen_cells:
            raise ValueError(f"duplicate experiment cell: {cell}")
        seen_cells.add(cell)
        # Keep query, fragment, and interaction policy in activity identity.
        activity = hashlib.sha256(json.dumps(target, sort_keys=True).encode()).hexdigest()
        final_ids = run["session_ids"]
        if len(final_ids) != 1:
            raise ValueError(f"expected one final session per run: {run['run_id']}")
        referenced = set(final_ids) | set(run.get('prior_session_ids', []))
        if referenced - set(sessions):
            raise ValueError(f'missing referenced sessions: {referenced - set(sessions)}')
        contexts = {sid: read_json(sessions[sid][0].parent / 'raw/capture-context.json') for sid in referenced}
        for sid, context in contexts.items():
            orchestration = context.get('orchestration', {})
            for name, expected in (('run_id', run['run_id']), ('repetition_index', run['repetition_index']),
                                   ('target_index', run['target_index'])):
                if name in orchestration and orchestration[name] != expected:
                    raise ValueError(f'context mismatch {sid}: {name}')
        attempts = ordered_attempts(run, contexts)
        selected_ordinal = next(n for n, sid, _ in attempts if sid in final_ids)
        for ordinal, sid, attempt_metadata in attempts:
            if sid in seen_sessions:
                raise ValueError(f"session assigned more than once: {sid}")
            seen_sessions.add(sid)
            if sid not in sessions:
                raise ValueError(f"missing referenced session: {sid}")
            path, manifest = sessions[sid]
            context = contexts[sid]
            orchestration = context.get("orchestration", {})
            for name, expected in (("run_id", run["run_id"]),
                                   ("repetition_index", run["repetition_index"]),
                                   ("target_index", run["target_index"])):
                if name in orchestration and orchestration[name] != expected:
                    raise ValueError(f"context mismatch {sid}: {name}")
            rows.append({
                "pipeline_id": pipeline["pipeline_id"], "run_id": run["run_id"],
                "activity_id": activity, "target_index": run["target_index"],
                "target_domain": target["domain"], "target_url": target["url"],
                "protocol": protocol, "repetition": run["repetition_index"],
                "run_ordinal": run["ordinal"], "attempt": ordinal - 1,
                "chronological_attempt": ordinal, "selected_attempt": selected_ordinal,
                "is_selected": sid in final_ids,
                "target_key": f"{pipeline['pipeline_id']}:{run['target_index']}",
                "recorded_attempt": orchestration.get("application_retry_attempt"),
                "is_final": sid in final_ids, "is_first_attempt": ordinal == 1,
                "session_id": sid, "session_path": str(path.parent),
                "candidate_position": orchestration.get("candidate_position"),
                "started_at": manifest.get("started_at"),
                "completed_at": manifest.get("completed_at"),
                "cache_mode": context.get("cache_mode"),
                "profile_fingerprint": run.get("profile_fingerprint"),
                "observed_protocol": run.get("observed_protocol"),
                "traffictracer_version": manifest.get("component_versions", {}).get(
                    "traffictracer", {}).get("version"),
                "traffictracer_commit": manifest.get("component_versions", {}).get(
                    "traffictracer", {}).get("commit"),
                "quality_json": json.dumps(run["quality"] if sid in final_ids else attempt_metadata.get('quality', {}),
                                           ensure_ascii=False),
            })
    if set(sessions) != seen_sessions:
        raise ValueError(f"unregistered sessions: {sorted(set(sessions)-seen_sessions)}")
    return rows
