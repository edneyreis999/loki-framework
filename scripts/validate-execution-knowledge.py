#!/usr/bin/env python3
"""Validate provider-neutral Loki execution-knowledge schema-v1 entries."""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


CAPTURE_STATES = {
    "captured",
    "partial",
    "failed",
    "unsupported",
    "skipped-nonmaterial",
}
DEGRADED_STATES = CAPTURE_STATES - {"captured"}
CLAIM_TYPES = {"fact", "inference", "hypothesis", "decision", "error", "friction"}
CONFIDENCE_VALUES = {"low", "medium", "high", "unknown"}
ALLOWED_SOURCE_TYPES = {
    "completion-record",
    "evidence-manifest",
    "build-report",
    "validator-record",
    "task-state",
}
RESOLUTION_STATUSES = {"resolved", "partial", "unresolved", "not-applicable"}
CAUSE_STATUSES = {"known", "suspected", "unknown"}
FORBIDDEN_MARKERS = (
    "chain-of-thought",
    "chain_of_thought",
    "private reasoning",
    "private_reasoning",
    "raw payload",
    "raw_payload",
    "full transcript",
    "full_transcript",
)


def value(element: ET.Element | None) -> str:
    return "" if element is None or element.text is None else element.text.strip()


def child(root: ET.Element, path: str) -> str:
    return value(root.find(path))


def parse_boolean(raw: str) -> bool | None:
    normalized = raw.lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


def contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def resolve_run_directory(path: Path, raw: str) -> Path | None:
    if not raw:
        return None
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate.resolve()
    # Relative declarations are interpreted from the containing run root.
    inferred_run_root = path.resolve().parents[2]
    return (inferred_run_root / candidate).resolve()


def resolve_from_run(raw: str, run_directory: Path) -> Path:
    candidate = Path(raw)
    return candidate.resolve() if candidate.is_absolute() else (run_directory / candidate).resolve()


def entry_paths(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(target.rglob("execution-knowledge/entries/*.xml"))
    raise ValueError(f"path does not exist: {target}")


def parse_entry(path: Path) -> ET.Element:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"{path}: XML parse error: {exc}") from exc
    if root.tag != "execution_knowledge_entry":
        raise ValueError(f"{path}: root must be execution_knowledge_entry")
    return root


def has_material_content(root: ET.Element) -> bool:
    if any(value(claim.find("statement")) for claim in root.findall("knowledge/claims/claim")):
        return True
    for attempt in root.findall("knowledge/attempts/attempt"):
        if child(attempt, "action") or child(attempt, "outcome"):
            return True
    for path in (
        "knowledge/resolution/statement",
        "knowledge/cause/statement",
        "knowledge/reuse_guidance",
        "knowledge/avoid_next_time",
    ):
        item = child(root, path).lower()
        if item and item not in {"none", "unknown", "not-applicable", "n/a"}:
            return True
    return False


def validate_entry(
    path: Path, root: ET.Element, failures: list[str], *, allow_staged: bool = False
) -> tuple[str, str]:
    label = str(path)
    if root.get("schema_version") != "1":
        failures.append(f"{label}: unsupported schema_version; expected 1")

    capture_id = child(root, "identity/capture_id")
    calling_workflow = child(root, "identity/calling_workflow")
    run_id = child(root, "identity/run_id")
    run_directory_raw = child(root, "identity/run_directory")
    target_entry = child(root, "lineage/target_entry")
    state = child(root, "capture/state")
    reason = child(root, "capture/reason")
    minimum_next_path = child(root, "capture/minimum_next_path")
    material = parse_boolean(child(root, "materiality/material"))
    material_reason = child(root, "materiality/reason")

    for field, field_value in (
        ("identity/capture_id", capture_id),
        ("identity/calling_workflow", calling_workflow),
        ("identity/run_id", run_id),
        ("identity/run_directory", run_directory_raw),
        ("lineage/target_entry", target_entry),
    ):
        if not field_value:
            failures.append(f"{label}: missing {field}")

    if state not in CAPTURE_STATES:
        failures.append(f"{label}: invalid capture state {state!r}")
    if material is None:
        failures.append(f"{label}: materiality/material must be true or false")
    if not material_reason:
        failures.append(f"{label}: missing materiality/reason")

    run_directory = resolve_run_directory(path, run_directory_raw)
    if run_directory is not None:
        expected_entry = (
            run_directory / "execution-knowledge" / "entries" / f"{capture_id}.xml"
        ).resolve()
        actual_entry = path.resolve()
        staged_entry = expected_entry.parent / f".{capture_id}.tmp"
        allowed_actuals = {expected_entry, staged_entry} if allow_staged else {expected_entry}
        if actual_entry not in allowed_actuals:
            failures.append(
                f"{label}: actual entry is not exactly <run_directory>/execution-knowledge/entries/<capture-id>.xml"
            )
        if target_entry:
            resolved_target = resolve_from_run(target_entry, run_directory)
            if resolved_target != expected_entry:
                failures.append(f"{label}: target_entry does not resolve to the exact expected entry")

    source_elements = root.findall("lineage/source_refs/source_ref")
    source_refs = [value(item) for item in source_elements if value(item)]
    if state == "captured":
        if material is not True:
            failures.append(f"{label}: captured requires material=true")
        if not source_refs:
            failures.append(f"{label}: captured requires at least one persisted source_ref")
        for source in source_elements:
            source_value = value(source)
            source_type = source.get("type", "")
            authorization = source.get("authorization", "")
            if source_type not in ALLOWED_SOURCE_TYPES:
                failures.append(f"{label}: invalid source_ref type {source_type!r}")
            if authorization != "run-contained":
                failures.append(f"{label}: source_ref authorization must be run-contained")
            if source_value and run_directory is not None:
                source_path = resolve_from_run(source_value, run_directory)
                if not contained(source_path, run_directory):
                    failures.append(f"{label}: source_ref escapes run_directory: {source_value}")
                elif not source_path.is_file():
                    failures.append(f"{label}: source_ref does not exist as a file: {source_value}")
        if not has_material_content(root):
            failures.append(f"{label}: captured requires material knowledge content")
    if state in DEGRADED_STATES:
        if not reason:
            failures.append(f"{label}: {state} requires capture/reason")
        if not minimum_next_path:
            failures.append(f"{label}: {state} requires capture/minimum_next_path")
    if state == "skipped-nonmaterial" and material is not False:
        failures.append(f"{label}: skipped-nonmaterial requires material=false")

    for claim in root.findall("knowledge/claims/claim"):
        claim_type = claim.get("type", "")
        confidence = claim.get("confidence", "")
        if claim_type not in CLAIM_TYPES:
            failures.append(f"{label}: invalid claim type {claim_type!r}")
        if confidence not in CONFIDENCE_VALUES:
            failures.append(f"{label}: invalid claim confidence {confidence!r}")
        if not child(claim, "statement"):
            failures.append(f"{label}: claim missing statement")
        if claim_type in {"inference", "hypothesis"} and not child(claim, "evidence_ref"):
            failures.append(f"{label}: {claim_type} requires evidence_ref")

    resolution = root.find("knowledge/resolution")
    if resolution is not None:
        if resolution.get("status", "") not in RESOLUTION_STATUSES:
            failures.append(f"{label}: invalid resolution status {resolution.get('status', '')!r}")
        if resolution.get("confidence", "") not in CONFIDENCE_VALUES:
            failures.append(f"{label}: invalid resolution confidence {resolution.get('confidence', '')!r}")
    cause = root.find("knowledge/cause")
    if cause is not None:
        if cause.get("status", "") not in CAUSE_STATUSES:
            failures.append(f"{label}: invalid cause status {cause.get('status', '')!r}")
        if cause.get("confidence", "") not in CONFIDENCE_VALUES:
            failures.append(f"{label}: invalid cause confidence {cause.get('confidence', '')!r}")

    if child(root, "security/sanitized").lower() != "true":
        failures.append(f"{label}: security/sanitized must be true")
    if child(root, "security/raw_payload_included").lower() != "false":
        failures.append(f"{label}: raw payload is forbidden")
    if child(root, "security/private_reasoning_included").lower() != "false":
        failures.append(f"{label}: private reasoning is forbidden")

    if child(root, "promotion/owner") != "loki-continuous-improvement":
        failures.append(f"{label}: promotion owner must be loki-continuous-improvement")
    promotion_status = child(root, "promotion/status").lower()
    if promotion_status != "unreviewed":
        failures.append(f"{label}: promotion/status must be exactly unreviewed")

    serialized = " ".join(part.strip() for part in root.itertext() if part.strip()).lower()
    for marker in FORBIDDEN_MARKERS:
        if marker in serialized:
            failures.append(f"{label}: forbidden raw/private marker {marker!r}")

    return capture_id, target_entry


def validate(target: Path, *, allow_staged: bool = False) -> list[str]:
    failures: list[str] = []
    paths = entry_paths(target)
    if not paths:
        return [f"{target}: no execution-knowledge entries found"]

    seen_capture_ids: dict[str, Path] = {}
    seen_targets: dict[str, Path] = {}
    for path in paths:
        try:
            root = parse_entry(path)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        capture_id, target_entry = validate_entry(
            path, root, failures, allow_staged=allow_staged
        )
        if capture_id:
            if capture_id in seen_capture_ids:
                failures.append(
                    f"{path}: duplicate capture_id {capture_id} also used by {seen_capture_ids[capture_id]}"
                )
            seen_capture_ids[capture_id] = path
        if target_entry:
            normalized = target_entry.replace("\\", "/")
            if normalized in seen_targets:
                failures.append(
                    f"{path}: duplicate target_entry {target_entry} also used by {seen_targets[normalized]}"
                )
            seen_targets[normalized] = path
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Allow only the exact sibling .<capture-id>.tmp before atomic publication",
    )
    parser.add_argument("target", help="Execution-knowledge XML entry or run directory")
    args = parser.parse_args()

    try:
        failures = validate(Path(args.target), allow_staged=args.staged)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("execution-knowledge validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("execution-knowledge validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
