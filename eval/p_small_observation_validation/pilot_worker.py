"""O1 physical-only worker. No labels, pair registry, browser or pre input."""
from collections import Counter
from dataclasses import asdict
import hashlib
import time
from pathlib import Path

from .common import io_path
from .packages import validate_worker_package
from proxy_analysis.parsing.pcapng import PcapNgReader
from proxy_analysis.observation.physical_tcp import Endpoint, EndpointDecoder
from proxy_analysis.observation.window_stats import summarize, FEATURES
from proxy_analysis.observation.visit_histogram import aggregate


class ReadBudget:
    def __init__(self, paths, limit):
        self.allowed = {str(Path(p).resolve()): int(size) for p, size in paths}
        self.limit = int(limit)
        self.opened = set()
        self.bytes = 0
        if sum(self.allowed.values()) != self.limit:
            raise ValueError("budget_manifest_mismatch")

    def authorize(self, path):
        p = str(Path(path).resolve())
        if p not in self.allowed or Path(p).name != "phys.pcap":
            raise PermissionError("unregistered_raw_input")
        if p in self.opened:
            raise PermissionError("second_raw_pass_forbidden")
        if io_path(p).stat().st_size != self.allowed[p]:
            raise ValueError("raw_size_changed")
        self.opened.add(p)
        return self.allowed[p]


class HashingReader:
    def __init__(self, stream, budget, expected):
        self.stream, self.budget, self.expected = stream, budget, expected
        self.size = 0
        self.hash = hashlib.sha256()

    def read(self, n=-1):
        value = self.stream.read(n)
        self.size += len(value)
        self.budget.bytes += len(value)
        if self.size > self.expected or self.budget.bytes > self.budget.limit:
            raise PermissionError("raw_read_budget_exceeded")
        self.hash.update(value)
        return value


def lifecycle_guard(epoch):
    """Do not merge same-ISN reincarnation into a terminated socket silently."""
    terminal = False
    fins = set()
    for p in epoch.packets:
        if terminal and p.flags & 2 and not p.flags & 16:
            epoch.reasons.add("bare_syn_after_terminal_same_isn_ambiguous")
        if p.flags & 1:
            fins.add(p.direction)
        terminal |= bool(p.flags & 4) or fins == {1, -1}


def digest(value):
    return hashlib.sha256(repr(value).encode()).hexdigest()


def extract(package, budget):
    validate_worker_package(package)
    if len(package["windows"]) != 1 or package["windows"][0]["version"] != "O1":
        raise PermissionError("pilot_is_O1_only")
    w = package["windows"][0]
    if w["coverage_verified"]:
        raise PermissionError("O2_coverage_not_authorized")
    start, end = w["start_ns"], w["end_ns"]
    path, token = package["physical_path"], package["visit_token"]
    expected = budget.authorize(path)
    before = io_path(path).stat()
    decoder = EndpointDecoder([Endpoint(**e) for e in package["endpoints"]], start, end)
    minimum, maximum, raw_count = None, None, 0
    started = time.monotonic()
    parse_error = None
    with io_path(path).open("rb") as source:
        stream = HashingReader(source, budget, expected)
        reader = PcapNgReader(stream)
        try:
            for rec in reader:
                raw_count += 1
                minimum = rec.timestamp_ns if minimum is None else min(minimum, rec.timestamp_ns)
                maximum = rec.timestamp_ns if maximum is None else max(maximum, rec.timestamp_ns)
                decoder.feed(rec)
        except Exception as exc:
            parse_error = type(exc).__name__ + ":" + str(exc)
        # Finish hashing in the same open pass on a parser failure, not a reread.
        if parse_error:
            for _ in iter(lambda: stream.read(1 << 20), b""):
                pass
    after = io_path(path).stat()
    es, failures = decoder.finish()
    if parse_error:
        failures.append("capture_parse_failure")
    if stream.size != expected or (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        failures.append("raw_input_changed_or_incomplete_read")
    assert raw_count == decoder.counts["raw_records"]
    assert sum(len(e.packets) for e in es) == len(decoder.packets)
    connections, events, duplicate_evidence = [], [], []
    witnesses = set()
    for e in es:
        lifecycle_guard(e)
        s = summarize(e, start, end)
        ps = [p for p in e.packets if start <= p.timestamp_ns < end]
        positive = [p for p in ps if p.payload_length]
        reference = {"W_up": sum(p.payload_length for p in positive if p.direction == 1),
                     "W_down": sum(p.payload_length for p in positive if p.direction == -1),
                     "P_up": sum(p.direction == 1 for p in positive),
                     "P_down": sum(p.direction == -1 for p in positive),
                     "FR_packet_runs": sum(j == 0 or p.direction != positive[j-1].direction
                                           for j, p in enumerate(positive))}
        assert all(s["statistics"][k] == value for k, value in reference.items())
        for suffix in ("up", "down"):
            direction = 1 if suffix == "up" else -1
            assert sum(v["new_bytes"] for v in s["new_byte_events"] if v["direction"] == direction) == s["statistics"]["U_"+suffix]
        instance = digest((e.key, e.ordinal, sorted(e.syn.items()), e.packets[0].timestamp_ns))
        connection = {"visit_token": token, "instance_token": instance, "socket_token": digest(e.key),
                      "epoch_token": s["epoch_token"], "epoch_ordinal": e.ordinal,
                      "first_ns": e.packets[0].timestamp_ns, "last_ns": e.packets[-1].timestamp_ns,
                      "syn_token": digest(sorted(e.syn.items())), "bare_syn_observed": e.bare_syn_observed,
                      "terminated": e.terminated, "rst": e.rst, "fin_directions": sorted(e.fins),
                      "window_packet_count": len(ps), "nonempty": s["nonempty"], "valid": s["valid"],
                      "reasons": s["reasons"], "statistics": s["statistics"]}
        connections.append(connection)
        for v in s["new_byte_events"]:
            events.append({"visit_token": token, "instance_token": instance, **v})
        for p in e.packets:
            witness = digest((e.key, p.timestamp_ns, p.fingerprint))
            if witness not in witnesses:
                duplicate_evidence.append({"visit_token": token, "instance_token": instance, "witness": witness})
                witnesses.add(witness)
    # True here means only the explicitly accepted OLD conditional window.
    # Independent fixed-window coverage is a separate false flag, never inferred.
    a = aggregate(connections, coverage_verified=True, failures=failures)
    a.update(visit_token=token, window_version="O1", old_conditional_window_accepted=True,
             independent_fixed_window_coverage_verified=False, classifier_eligible=False,
             technically_valid_nonempty_connections=sum(c["nonempty"] and c["valid"] for c in connections))
    counters = dict(decoder.counts)
    audit = {"visit_token": token, "file_bytes": expected, "bytes_read": stream.size,
             "sha256": stream.hash.hexdigest(), "raw_open_count": 1, "parse_error": parse_error,
             "raw_records": raw_count, "first_packet_ns": minimum, "last_packet_ns": maximum,
             "window_packet_span_enclosed": minimum is not None and minimum <= start and maximum >= end,
             "packet_span_is_not_capture_continuity_proof": True,
             "interfaces": [asdict(i) for i in reader.interfaces], "decoder_counts": counters,
             "fragment_counts": dict(decoder.fragments.stats), "failures": sorted(set(failures)),
             "partition_verified": True, "independent_counters_verified": True,
             "payload_saved": False, "elapsed_seconds": time.monotonic()-started}
    return {"audit": audit, "visit": a, "connections": connections, "events": events,
            "duplicate_evidence": duplicate_evidence}
