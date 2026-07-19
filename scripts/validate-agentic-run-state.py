#!/usr/bin/env python3
"""Validate current and legacy Loki agentic XML run state."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


RESOLVED_GATE_STATUSES = {"resolved", "answered", "accepted", "none", "not_applicable"}
NON_WRITER_MODES = {"", "none", "read-only", "readonly", "proposal", "report"}
KNOWLEDGE_CAPTURE_STATES = {
    "captured",
    "partial",
    "failed",
    "unsupported",
    "skipped-nonmaterial",
}
EVIDENCE_SCHEMAS = {"2", "3", "4"}
TERMINAL_RUN_STATUSES = {"completed", "blocked", "failed", "pending-human-validation"}
CURRENT_RUN_STATUSES = TERMINAL_RUN_STATUSES | {"draft", "running"}


def text(element: ET.Element | None) -> str:
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def child_text(parent: ET.Element, path: str) -> str:
    return text(parent.find(path))


def non_empty_children(parent: ET.Element, path: str) -> list[str]:
    return [text(child) for child in parent.findall(path) if text(child)]


def parse_boolean(raw: str) -> bool | None:
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    return None


def knowledge_record(
    element: ET.Element,
    label: str,
    failures: list[str],
    *,
    run_id: str = "",
    agent_run_id: str = "",
    handoff_id: str = "",
) -> dict[str, str | bool | None]:
    record: dict[str, str | bool | None] = {
        "capture_id": child_text(element, "capture_id"),
        "run_id": child_text(element, "run_id") or run_id,
        "agent_run_id": child_text(element, "agent_run_id") or agent_run_id,
        "handoff_id": child_text(element, "handoff_id") or handoff_id,
        "material": parse_boolean(child_text(element, "material")),
        "target_entry": child_text(element, "target_entry"),
        "state": child_text(element, "state"),
        "reason": child_text(element, "reason"),
        "minimum_next_path": child_text(element, "minimum_next_path"),
    }
    for field in ("capture_id", "run_id", "agent_run_id", "handoff_id", "target_entry"):
        if not record[field]:
            failures.append(f"{label}: knowledge capture missing {field}")
    if record["material"] is None:
        failures.append(f"{label}: knowledge material must be true or false")
    if record["state"] not in KNOWLEDGE_CAPTURE_STATES:
        failures.append(f"{label}: invalid execution knowledge state {record['state']!r}")
    if record["state"] == "skipped-nonmaterial" and record["material"] is not False:
        failures.append(f"{label}: skipped-nonmaterial requires material=false")
    if record["state"] != "captured" and (
        not record["reason"] or not record["minimum_next_path"]
    ):
        failures.append(f"{label}: degraded knowledge state requires reason and minimum_next_path")
    return record


def validate_knowledge_entry_file(path: Path) -> list[str]:
    validator_path = Path(__file__).with_name("validate-execution-knowledge.py")
    spec = importlib.util.spec_from_file_location("loki_execution_knowledge_validator", validator_path)
    if spec is None or spec.loader is None:
        return [f"{path}: execution-knowledge validator cannot be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate(path)


def parse_xml_file(path: Path) -> ET.Element:
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"{path}: XML parse error: {exc}") from exc


def parse_all_xml(run_dir: Path) -> dict[Path, ET.Element]:
    xml_paths = sorted(run_dir.rglob("*.xml"))
    if not xml_paths:
        raise ValueError(f"{run_dir}: no XML state files found")
    return {path: parse_xml_file(path) for path in xml_paths}


def validate_selected_agents(root: ET.Element, label: str, failures: list[str]) -> None:
    for selected in root.findall(".//selected_agent"):
        name = selected.attrib.get("name", child_text(selected, "agent_name")) or "<unnamed>"
        if not child_text(selected, "selection_reason"):
            failures.append(f"{label}: selected agent {name} missing selection_reason")


def validate_decision_gates(root: ET.Element, label: str, failures: list[str]) -> None:
    for gate in root.findall(".//decision_gate"):
        category = child_text(gate, "category") or gate.attrib.get("category", "")
        status = (child_text(gate, "status") or gate.attrib.get("status", "")).lower()
        if category == "must_ask_now" and status not in RESOLVED_GATE_STATUSES:
            gate_id = gate.attrib.get("id", child_text(gate, "id")) or "<missing-id>"
            failures.append(f"{label}: unresolved must_ask_now gate {gate_id}")


def validate_manifest_handoffs(root: ET.Element, failures: list[str]) -> dict[str, str]:
    seen_agent_runs: set[str] = set()
    seen_handoffs: set[str] = set()
    parents: dict[str, str] = {}
    for handoff in root.findall(".//handoff"):
        agent_run_id = child_text(handoff, "agent_run_id")
        handoff_id = child_text(handoff, "handoff_id")
        if not agent_run_id:
            failures.append("agentic-run-manifest.xml: handoff missing agent_run_id")
        elif agent_run_id in seen_agent_runs:
            failures.append(
                f"agentic-run-manifest.xml: duplicate handoff agent_run_id {agent_run_id}"
            )
        else:
            seen_agent_runs.add(agent_run_id)

        if not handoff_id:
            failures.append("agentic-run-manifest.xml: handoff missing handoff_id")
        elif handoff_id in seen_handoffs:
            failures.append(
                f"agentic-run-manifest.xml: duplicate handoff_id {handoff_id}"
            )
        else:
            seen_handoffs.add(handoff_id)
        if root.get("schema_version") in {"2", "3"}:
            evidence_id = child_text(handoff, "evidence_id")
            evidence_path = child_text(handoff, "evidence_manifest_path")
            if not evidence_id or not evidence_path:
                failures.append("agentic-run-manifest.xml: v2 handoff missing evidence lineage")
        parent = child_text(handoff, "depends_on_handoff_id")
        if parent and handoff_id:
            parents[handoff_id] = parent
    for handoff_id in parents:
        visited: set[str] = set()
        current = handoff_id
        while current in parents:
            if current in visited:
                failures.append(f"agentic-run-manifest.xml: cyclic handoff lineage at {current}")
                break
            visited.add(current)
            current = parents[current]
    return {child_text(h, "handoff_id"): child_text(h, "agent_run_id") for h in root.findall(".//handoff")}


def validate_report(
    path: Path, root: ET.Element, failures: list[str]
) -> tuple[str, str, list[str], dict[str, str | bool | None] | None]:
    agent_run_id = child_text(root, "identity/agent_run_id")
    handoff_id = child_text(root, "identity/handoff_id")
    owner = child_text(root, "identity/owner")
    group_id = child_text(root, "identity/parallel_group_id")
    write_mode = child_text(root, "write_contract/write_mode").lower()
    target_files = non_empty_children(root, "write_contract/target_files/target_file")
    allowed_writes = non_empty_children(root, "write_contract/allowed_writes/allowed_write")
    validators = root.findall("validators/validator")
    gates = root.findall("gates/gate")

    if not agent_run_id:
        failures.append(f"{path}: missing identity/agent_run_id")
    if not handoff_id:
        failures.append(f"{path}: missing identity/handoff_id")
    if not child_text(root, "selection/selection_reason"):
        failures.append(f"{path}: missing selection/selection_reason")
    schema_version = root.get("schema_version", "")
    if schema_version in EVIDENCE_SCHEMAS:
        for field in ("evidence_manifest_path", "evidence_status", "capture_trigger", "capture_target"):
            if not child_text(root, f"evidence/{field}"):
                failures.append(f"{path}: schema {schema_version} missing evidence/{field}")
    if schema_version == "4":
        knowledge = root.find("execution_knowledge")
        if knowledge is None:
            failures.append(f"{path}: schema 4 missing execution_knowledge")
            knowledge_record_value = None
        else:
            knowledge_record_value = knowledge_record(
                knowledge,
                str(path),
                failures,
                run_id=child_text(root, "identity/run_id"),
                agent_run_id=agent_run_id,
                handoff_id=handoff_id,
            )
    else:
        knowledge_record_value = None
    if root.find("freshness_signature") is None:
        failures.append(f"{path}: missing freshness_signature")

    if write_mode not in NON_WRITER_MODES:
        if not owner:
            failures.append(f"{path}: writer missing identity/owner")
        if not target_files:
            failures.append(f"{path}: writer missing target_files")
        if not allowed_writes:
            failures.append(f"{path}: writer missing allowed_writes")
        if not validators:
            failures.append(f"{path}: writer missing validators")
        if not gates:
            failures.append(f"{path}: writer missing gates")

    completion = root.find("completion")
    if completion is None:
        failures.append(f"{path}: missing completion")
    else:
        if not child_text(completion, "status"):
            failures.append(f"{path}: completion missing status")
        if not child_text(completion, "report_path"):
            failures.append(f"{path}: completion missing report_path")
        if not non_empty_children(completion, "evidence/item"):
            failures.append(f"{path}: completion missing evidence item")

    return agent_run_id, group_id, target_files, knowledge_record_value


def validate_reports(
    roots: dict[Path, ET.Element], run_dir: Path, failures: list[str], manifest_handoffs: dict[str, str]
) -> dict[str, dict[str, str | bool | None]]:
    seen_agent_runs: set[str] = set()
    seen_handoffs: set[str] = set()
    target_files_by_group: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    report_roots = {
        path: root for path, root in roots.items() if root.tag == "agent_run_report"
    }
    if not report_roots:
        if manifest_handoffs:
            failures.append(f"{run_dir}: no agent_run_report XML files found")
        return {}

    knowledge_records: dict[str, dict[str, str | bool | None]] = {}

    for path, root in report_roots.items():
        agent_run_id = child_text(root, "identity/agent_run_id")
        handoff_id = child_text(root, "identity/handoff_id")
        if agent_run_id:
            if agent_run_id in seen_agent_runs:
                failures.append(f"{path}: duplicate agent_run_id {agent_run_id}")
            seen_agent_runs.add(agent_run_id)
        if handoff_id:
            if handoff_id in seen_handoffs:
                failures.append(f"{path}: duplicate handoff_id {handoff_id}")
            seen_handoffs.add(handoff_id)

        report_agent_run_id, group_id, target_files, report_knowledge = validate_report(
            path, root, failures
        )
        if root.get("schema_version") in EVIDENCE_SCHEMAS and handoff_id:
            expected_agent_run = manifest_handoffs.get(handoff_id)
            if expected_agent_run != report_agent_run_id:
                failures.append(f"{path}: handoff correlation does not match manifest")
        if group_id:
            for target_file in target_files:
                target_files_by_group[group_id][target_file].append(report_agent_run_id)
        if report_knowledge:
            capture_id = str(report_knowledge["capture_id"])
            if capture_id in knowledge_records:
                failures.append(f"{path}: duplicate report knowledge capture_id {capture_id}")
            knowledge_records[capture_id] = report_knowledge

    for group_id, files in target_files_by_group.items():
        for target_file, agent_runs in files.items():
            unique_runs = sorted({run for run in agent_runs if run})
            if len(unique_runs) > 1:
                failures.append(
                    "parallel target conflict: "
                    f"group {group_id} target {target_file} used by "
                    + ", ".join(unique_runs)
                )
    return knowledge_records


def validate_digest(
    roots: dict[Path, ET.Element], failures: list[str]
) -> tuple[str, str, str, dict[str, dict[str, str | bool | None]]]:
    digest_roots = [(path, root) for path, root in roots.items() if root.tag == "agentic_run_digest"]
    if not digest_roots:
        return "", "", "", {}
    if len(digest_roots) > 1:
        failures.append("multiple agentic_run_digest XML files found")
    path, root = digest_roots[0]
    schema_version = root.get("schema_version", "")
    digest_run_id = child_text(root, "digest/run_id")
    digest_status = child_text(root, "digest/status").lower()
    if schema_version != "3":
        return digest_run_id, schema_version, digest_status, {}
    if digest_status not in CURRENT_RUN_STATUSES:
        failures.append(f"{path}: invalid schema-3 digest status {digest_status!r}")
    records: dict[str, dict[str, str | bool | None]] = {}
    for capture in root.findall("execution_knowledge_captures/capture"):
        record = knowledge_record(
            capture, str(path), failures, run_id=child_text(root, "digest/run_id")
        )
        capture_id = str(record["capture_id"])
        if capture_id in records:
            failures.append(f"{path}: duplicate digest capture_id {capture_id}")
        records[capture_id] = record
    return digest_run_id, schema_version, digest_status, records


def compare_capture_records(
    source_name: str,
    expected: dict[str, str | bool | None],
    actual: dict[str, str | bool | None],
    failures: list[str],
) -> None:
    for field in ("capture_id", "run_id", "agent_run_id", "handoff_id", "material", "target_entry", "state"):
        if expected.get(field) != actual.get(field):
            failures.append(
                f"execution knowledge mismatch in {source_name} for capture "
                f"{expected.get('capture_id')}: {field} expected {expected.get(field)!r}, "
                f"got {actual.get(field)!r}"
            )
    if expected.get("state") != "captured":
        for field in ("reason", "minimum_next_path"):
            if expected.get(field) != actual.get(field):
                failures.append(
                    f"execution knowledge mismatch in {source_name} for capture "
                    f"{expected.get('capture_id')}: {field} expected "
                    f"{expected.get(field)!r}, got {actual.get(field)!r}"
                )


def validate_current_knowledge_lineage(
    run_dir: Path,
    run_id: str,
    manifest_records: dict[str, dict[str, str | bool | None]],
    report_records: dict[str, dict[str, str | bool | None]],
    digest_run_id: str,
    digest_schema: str,
    digest_status: str,
    digest_records: dict[str, dict[str, str | bool | None]],
    digest_required: bool,
    run_status: str,
    failures: list[str],
) -> None:
    if digest_required and digest_schema != "3":
        failures.append(f"{run_dir}: terminal schema-3 run requires agentic_run_digest schema 3")
    if digest_run_id and digest_run_id != run_id:
        failures.append(f"{run_dir}: digest run_id does not match manifest run_id")
    if digest_required and digest_status != run_status:
        failures.append(f"{run_dir}: terminal digest status does not match manifest run status")

    for capture_id, manifest_record in manifest_records.items():
        report_record = report_records.get(capture_id)
        if report_record is None:
            failures.append(f"{run_dir}: capture {capture_id} missing schema-4 report record")
        else:
            compare_capture_records("report", manifest_record, report_record, failures)
        if digest_run_id:
            digest_record = digest_records.get(capture_id)
            if digest_record is None:
                failures.append(f"{run_dir}: capture {capture_id} missing schema-3 digest record")
            else:
                compare_capture_records("digest", manifest_record, digest_record, failures)

        if manifest_record.get("state") != "captured":
            continue
        target_raw = str(manifest_record.get("target_entry") or "")
        target = Path(target_raw)
        target = target.resolve() if target.is_absolute() else (run_dir / target).resolve()
        if not target.is_file():
            failures.append(f"{run_dir}: captured target does not exist: {target_raw}")
            continue
        for failure in validate_knowledge_entry_file(target):
            failures.append(f"captured entry invalid: {failure}")
        try:
            entry = parse_xml_file(target)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        entry_values: dict[str, str | bool | None] = {
            "capture_id": child_text(entry, "identity/capture_id"),
            "run_id": child_text(entry, "identity/run_id"),
            "agent_run_id": child_text(entry, "identity/agent_run_id"),
            "handoff_id": child_text(entry, "identity/handoff_id"),
            "material": parse_boolean(child_text(entry, "materiality/material")),
            "target_entry": child_text(entry, "lineage/target_entry"),
            "state": child_text(entry, "capture/state"),
        }
        declared_run_raw = child_text(entry, "identity/run_directory")
        declared_run_path = Path(declared_run_raw)
        if declared_run_path.is_absolute():
            declared_run = declared_run_path.resolve()
        else:
            declared_run = (target.resolve().parents[2] / declared_run_path).resolve()
        if declared_run != run_dir.resolve():
            failures.append(
                f"captured entry {capture_id}: identity/run_directory does not match actual run_dir"
            )
        compare_capture_records("entry", manifest_record, entry_values, failures)

    extra_reports = sorted(set(report_records) - set(manifest_records))
    extra_digests = sorted(set(digest_records) - set(manifest_records))
    if extra_reports:
        failures.append(f"{run_dir}: report capture IDs absent from manifest: {', '.join(extra_reports)}")
    if extra_digests:
        failures.append(f"{run_dir}: digest capture IDs absent from manifest: {', '.join(extra_digests)}")


def validate_run_dir(run_dir: Path) -> list[str]:
    failures: list[str] = []
    roots = parse_all_xml(run_dir)
    manifest_records: dict[str, dict[str, str | bool | None]] = {}
    current_schema = False
    run_id = ""
    digest_required = False
    run_status = ""

    manifest_path = run_dir / "agentic-run-manifest.xml"
    manifest = roots.get(manifest_path)
    if manifest is None:
        failures.append(f"{manifest_path}: required run manifest is missing")
    else:
        if manifest.find("freshness_signature") is None:
            failures.append(f"{manifest_path}: missing freshness_signature")
        validate_selected_agents(manifest, str(manifest_path), failures)
        manifest_handoffs = validate_manifest_handoffs(manifest, failures)
        if manifest.get("schema_version") == "3":
            current_schema = True
            run_id = child_text(manifest, "run/run_id")
            run_status = child_text(manifest, "run/status").lower()
            if run_status not in CURRENT_RUN_STATUSES:
                failures.append(f"{manifest_path}: invalid schema-3 run/status {run_status!r}")
            digest_required = run_status in TERMINAL_RUN_STATUSES
            if not run_id:
                failures.append(f"{manifest_path}: schema 3 missing run/run_id")
            policy = manifest.find("execution_knowledge_policy")
            if policy is None:
                failures.append(f"{manifest_path}: schema 3 missing execution_knowledge_policy")
            elif child_text(policy, "promotion_owner") != "loki-continuous-improvement":
                failures.append(f"{manifest_path}: invalid execution knowledge promotion owner")
            seen_targets: set[str] = set()
            for capture in manifest.findall("execution_knowledge_captures/capture"):
                record = knowledge_record(
                    capture, str(manifest_path), failures, run_id=run_id
                )
                capture_id = str(record["capture_id"])
                target = str(record["target_entry"])
                target_path = Path(target)
                target_path = (
                    target_path.resolve()
                    if target_path.is_absolute()
                    else (run_dir / target_path).resolve()
                )
                expected_target = (
                    run_dir.resolve()
                    / "execution-knowledge"
                    / "entries"
                    / f"{capture_id}.xml"
                )
                if target_path != expected_target:
                    failures.append(
                        f"{manifest_path}: capture {capture_id} target must resolve exactly inside actual run_dir"
                    )
                if capture_id in manifest_records:
                    failures.append(f"{manifest_path}: duplicate capture_id {capture_id!r}")
                manifest_records[capture_id] = record
                if not target or target in seen_targets:
                    failures.append(f"{manifest_path}: missing or duplicate knowledge target {target!r}")
                seen_targets.add(target)
    if manifest is None:
        manifest_handoffs = {}

    for path, root in roots.items():
        validate_decision_gates(root, str(path), failures)
        if root.tag == "agentic_analysis_manifest":
            validate_selected_agents(root, str(path), failures)

    report_records = validate_reports(roots, run_dir, failures, manifest_handoffs)
    digest_run_id, digest_schema, digest_status, digest_records = validate_digest(
        roots, failures
    )
    if current_schema:
        validate_current_knowledge_lineage(
            run_dir,
            run_id,
            manifest_records,
            report_records,
            digest_run_id,
            digest_schema,
            digest_status,
            digest_records,
            digest_required,
            run_status,
            failures,
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate current and legacy Loki agentic XML run state."
    )
    parser.add_argument("run_dir", help="Directory containing agentic-run-manifest.xml")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        print(f"error: run directory does not exist: {run_dir}", file=sys.stderr)
        return 1

    try:
        failures = validate_run_dir(run_dir)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("agentic run-state validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("agentic run-state validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
