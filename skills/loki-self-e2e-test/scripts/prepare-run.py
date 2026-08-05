#!/usr/bin/env python3
"""Atomically allocate one local Loki E2E report directory and failure-safe skeleton."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[3]
REPORT_ROOT = PACKAGE_ROOT / "e2e-runs"
ID_PATTERN = re.compile(r"^(?P<ordinal>[0-9]+)-e2e-")
SLUG_PATTERN = re.compile(r"[^a-z0-9]+")
ALLOWED_BASELINES = {"raw-demand", "analysis-ready", "product-implemented"}
ALLOWED_QA_OUTCOMES = {"approve", "disapprove"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--behavior-slug", required=True)
    parser.add_argument("--behavior-under-test", required=True)
    parser.add_argument("--baseline", required=True, choices=sorted(ALLOWED_BASELINES))
    parser.add_argument(
        "--manual-qa-outcome", required=True, choices=sorted(ALLOWED_QA_OUTCOMES)
    )
    return parser.parse_args()


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def normalize_slug(raw: str) -> str:
    slug = SLUG_PATTERN.sub("-", raw.lower()).strip("-")
    return slug[:64] or "loki-self-e2e-test"


def assert_package_root() -> None:
    required = (PACKAGE_ROOT / "manifest.yaml", PACKAGE_ROOT / "AGENTS.md")
    if not all(path.is_file() for path in required):
        raise SystemExit("resolved script location is not the Loki package root")
    probe = "e2e-runs/.self-e2e-ignore-probe"
    checked = subprocess.run(
        ["git", "-C", str(PACKAGE_ROOT), "check-ignore", "-q", "--", probe],
        check=False,
    )
    if checked.returncode != 0:
        raise SystemExit("e2e-runs/ is not ignored by the Loki package Git rules")


def next_ordinal() -> int:
    maximum = 0
    if REPORT_ROOT.is_dir():
        for child in REPORT_ROOT.iterdir():
            if not child.is_dir():
                continue
            match = ID_PATTERN.match(child.name)
            if match:
                maximum = max(maximum, int(match.group("ordinal")))
    return maximum + 1


def allocate(slug: str) -> tuple[str, Path]:
    REPORT_ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    while True:
        ordinal = next_ordinal()
        prefix = f"{ordinal:03d}"
        timestamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
        execution_id = f"{prefix}-e2e-{timestamp}-{slug}"
        report_dir = REPORT_ROOT / execution_id
        try:
            os.mkdir(report_dir, mode=0o700)
        except FileExistsError:
            continue
        return execution_id, report_dir


def initial_result(
    *,
    execution_id: str,
    input_dir: str,
    behavior: str,
    baseline: str,
    qa_outcome: str,
) -> str:
    ordinal = int(execution_id.split("-", 1)[0])
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    return f"""---
e2e_execution_id: {yaml_string(execution_id)}
ordinal: {ordinal}
status: "failed"
started_at: {yaml_string(now)}
finished_at: {yaml_string(now)}
behavior_under_test: {yaml_string(behavior)}
baseline: {yaml_string(baseline)}
baseline_ref: "unavailable"
loki_source_root: {yaml_string(str(PACKAGE_ROOT))}
loki_source_fingerprint_before: "unavailable"
loki_source_fingerprint_after: "unavailable"
manual_qa_outcome: {yaml_string(qa_outcome)}
loki_run_id: null
loki_execution_id: null
plan_directory: null
final_plan_status: "unavailable"
postflight: "not-run"
failure_code: "E2E-INCOMPLETE"
---

# Loki self E2E result

## Summary

Run allocated. Execution has not reached a terminal oracle.

## Normalized Request

- Input directory: {yaml_string(input_dir)}
- Behavior: {yaml_string(behavior)}
- Baseline: {baseline}
- Manual QA outcome: {qa_outcome}

## Baseline And Installation

not-run

## Command Timeline

not-run

## Interactions

none

## State And Administrative Evidence

not-run

## Postflight

not-run

## Failure Details

`E2E-INCOMPLETE`: the run was allocated but has not been finalized.

## Reproduction

Invoke `$loki-self-e2e-test` again with the recorded input directory to create a new clean run.
"""


def main() -> int:
    args = parse_args()
    assert_package_root()
    execution_id, report_dir = allocate(normalize_slug(args.behavior_slug))
    for name in ("commands", "snapshots", "attachments"):
        (report_dir / name).mkdir(mode=0o700)
    result_path = report_dir / "result.md"
    result_path.write_text(
        initial_result(
            execution_id=execution_id,
            input_dir=args.input_dir,
            behavior=args.behavior_under_test,
            baseline=args.baseline,
            qa_outcome=args.manual_qa_outcome,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "e2e_execution_id": execution_id,
                "report_dir": str(report_dir),
                "result_path": str(result_path),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
