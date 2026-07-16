#!/usr/bin/env python3
"""Validate Loki agentic v2 run state."""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


RESOLVED_GATE_STATUSES = {"resolved", "answered", "accepted", "none", "not_applicable"}
NON_WRITER_MODES = {"", "none", "read-only", "readonly", "proposal", "report"}


def text(element: ET.Element | None) -> str:
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def child_text(parent: ET.Element, path: str) -> str:
    return text(parent.find(path))


def non_empty_children(parent: ET.Element, path: str) -> list[str]:
    return [text(child) for child in parent.findall(path) if text(child)]


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
        if root.get("schema_version") == "2":
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


def validate_report(path: Path, root: ET.Element, failures: list[str]) -> tuple[str, str, list[str]]:
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
    if root.get("schema_version") == "2":
        for field in ("evidence_manifest_path", "evidence_status", "capture_trigger", "capture_target"):
            if not child_text(root, f"evidence/{field}"):
                failures.append(f"{path}: v2 missing evidence/{field}")
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

    return agent_run_id, group_id, target_files


def validate_reports(
    roots: dict[Path, ET.Element], run_dir: Path, failures: list[str], manifest_handoffs: dict[str, str]
) -> None:
    seen_agent_runs: set[str] = set()
    seen_handoffs: set[str] = set()
    target_files_by_group: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    report_roots = {
        path: root for path, root in roots.items() if root.tag == "agent_run_report"
    }
    if not report_roots:
        failures.append(f"{run_dir}: no agent_run_report XML files found")
        return

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

        report_agent_run_id, group_id, target_files = validate_report(path, root, failures)
        if root.get("schema_version") == "2" and handoff_id:
            expected_agent_run = manifest_handoffs.get(handoff_id)
            if expected_agent_run != report_agent_run_id:
                failures.append(f"{path}: v2 handoff correlation does not match manifest")
        if group_id:
            for target_file in target_files:
                target_files_by_group[group_id][target_file].append(report_agent_run_id)

    for group_id, files in target_files_by_group.items():
        for target_file, agent_runs in files.items():
            unique_runs = sorted({run for run in agent_runs if run})
            if len(unique_runs) > 1:
                failures.append(
                    "parallel target conflict: "
                    f"group {group_id} target {target_file} used by "
                    + ", ".join(unique_runs)
                )


def validate_run_dir(run_dir: Path) -> list[str]:
    failures: list[str] = []
    roots = parse_all_xml(run_dir)

    manifest_path = run_dir / "agentic-run-manifest.xml"
    manifest = roots.get(manifest_path)
    if manifest is None:
        failures.append(f"{manifest_path}: required run manifest is missing")
    else:
        if manifest.find("freshness_signature") is None:
            failures.append(f"{manifest_path}: missing freshness_signature")
        validate_selected_agents(manifest, str(manifest_path), failures)
        manifest_handoffs = validate_manifest_handoffs(manifest, failures)
    if manifest is None:
        manifest_handoffs = {}

    for path, root in roots.items():
        validate_decision_gates(root, str(path), failures)
        if root.tag == "agentic_analysis_manifest":
            validate_selected_agents(root, str(path), failures)

    validate_reports(roots, run_dir, failures, manifest_handoffs)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Loki agentic v2 XML run state."
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
