"""Default is metadata and synthetic tests; no implicit pilot/full/raw access."""
import argparse
from pathlib import Path
from .common import *


def main():
    parser = argparse.ArgumentParser(__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--metadata-only", action="store_true")
    modes.add_argument("--tests-only", action="store_true")
    modes.add_argument("--pilot", action="store_true")
    modes.add_argument("--full", action="store_true")
    parser.add_argument("--out", type=Path,
                        default=ROOT / "outputs/p-small-observation-validation-20261010/run-01")
    args = parser.parse_args()
    if args.pilot or args.full:
        parser.error("PCAP execution not authorized by this entry: complete A06/A17 and register evidence first")
    from . import tests
    if args.tests_only:
        result = tests.run()
        print(result["log"])
        raise SystemExit(0 if result["passed"] else 1)
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / "outputs/p-small-observation-validation-20261010")
    if out.exists():
        parser.error("registered run is read-only; choose a new run path")
    out.mkdir(parents=True)
    print("metadata run:", str(out), flush=True)
    try:
        result = tests.run()
        write(out, "manifests/engineering-tests.json", result)
        assert result["passed"], "synthetic_engineering_tests_failed"
        print("synthetic tests:", result["tests"], "passed", flush=True)
        from . import inventory, windows
        parents, pilot = inventory.run(out)
        summary = windows.run(out, parents, pilot)
        sources = source_lock()
        write(out, "manifests/source-lock.json", sources)
        write(out, "manifests/access-log.json", ACCESS)
        state = {"version": "POV-A-metadata-v1", **timestamp(), "new_classifier_fits": 0,
             "real_model_inferences": 0, "PCAP_reads": 0, "PCAP_bytes_read": 0,
             "test_pre_reads": 0, "target_U_training_numeric_packages_read": 0,
             "metadata_preflight_passed": True, "synthetic_engineering_passed": True,
             "O2_qualified": False, "pilot_completed": False, "full_extraction_completed": False,
             "stage_A_complete": False, "stage_B_started": False, "stage_C_started": False,
             "stop_gate": "A06_timing_endpoint_and_PCAP_budget_confirmation",
             "source_sha256": sources, "summary": summary}
        write(out, "progress.json", state)
        from . import report, verify
        report.run(out, state)
        check = verify.run(out)
        write(out, "verification.json", check)
        print(json.dumps({"out": str(out), "metadata_preflight_passed": check["passed"],
                          "stop_gate": state["stop_gate"], **summary}, ensure_ascii=False, indent=2))
    except BaseException as exc:
        write(out, "failure.json", {"type": type(exc).__name__, "error": str(exc),
             "PCAP_reads": 0, "classifier_fits": 0, "automatic_retry": False, **timestamp()})
        raise


if __name__ == "__main__":
    main()
