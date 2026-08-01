#!/usr/bin/env python3
"""Validate current-only plan-knowledge lifecycle state and candidate v2."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

SHA256_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
RUN_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
PROBLEM_TYPES = {"error", "failure", "waste", "friction", "prevention"}
SEMANTIC_TYPES = {"architecture", "convention", "implemented-capability", "runtime-contract", "state-or-data-contract", "content-or-canon", "validation-pattern", "human-decision", *PROBLEM_TYPES}
GENERALIZABLE_TYPES = {"architecture", "convention", "runtime-contract", "state-or-data-contract", "validation-pattern", "prevention"}
ABSTRACTION_RESULTS = {"generalized", "local-with-rationale", "blocked-ambiguous"}
GENERALIZATION_CONFIDENCES = {"not-applicable", "low", "medium", "high"}
COUNTEREXAMPLE_RESULTS = {"none-observed", "bounded", "material-observed", "inconclusive"}
ABSTRACTION_REASON_CODES = {
    "generalized": {"reusable-invariant"},
    "local-with-rationale": {"content-or-canon", "explicitly-local-human-decision", "deliberate-exception", "material-counterexample", "no-reusable-invariant"},
    "blocked-ambiguous": {"insufficient-evidence", "conflicting-scope", "material-counterexample-needs-human"},
}
ACTIONS = {"promote", "noop-proven", "blocked-with-reason"}
RUN_STATES = {"proposed", "approved", "writing", "auditing", "completed", "completed-with-blockers"}
CANDIDATE_STATES = {"proposed", "approved", "writing", "auditing", "promoted", "noop-proven", "blocked-with-reason"}
TERMINAL_CANDIDATE_STATES = {"promoted", "noop-proven", "blocked-with-reason"}
CONTROL_STATES = {"pending", "passed", "failed"}
DISPOSITIONS = {"digested", "duplicate", "generated-noise", "unsupported", "blocked"}
DIAGNOSTIC_TYPES = {"missing", "changed", "added", "symlink", "escape", "tree-digest-drift", "managed-namespace-collision"}
SAFETY_PAIRS = {("recognized-text", "eligible"), ("blocked", "sensitive-name"), ("blocked", "binary-nul"), ("blocked", "unknown-schema"), ("blocked", "invalid-utf8")}
DESTINATION_WRITERS = {"package": "framework-artifact-writer", "consumer-docs": "catalogador", "consumer-operational-state": "technical-implementer"}
DESTINATION_SCOPES = {"package": "package", "consumer-docs": "consumer", "consumer-operational-state": "consumer"}
CANONICAL_FILES = {
    "source-manifest.xml": "source_manifest", "approved-roots.xml": "approved_roots",
    "file-processing-ledger.xml": "file_processing_ledger", "integrity-diagnostics.xml": "integrity_diagnostics",
    "knowledge-digest.xml": "knowledge_digest", "candidates.xml": "candidates",
    "approvals.xml": "approvals", "coverage.xml": "plan_knowledge_coverage",
}
ALL_CANONICAL_FILES = {"run-state.xml", *CANONICAL_FILES}
TEXT_ELEMENTS = {"intended_change", "source_instance", "resulting_statement", "applicability_signal", "exclusion", "none_observed_rationale", "rationale", "statement", "use_when", "question_text", "expected_claim", "comparison_evidence"}
BASE64_ELEMENTS = {"target_before_state", "target_after_state"}


class ValidationError(ValueError):
    """Closed schema or invariant failure."""


def _fail(message: str) -> None:
    raise ValidationError(message)


def _attrs(element: ET.Element, required: set[str], optional: set[str] = set()) -> None:
    missing = required - set(element.attrib)
    extra = set(element.attrib) - required - optional
    if missing: _fail(f"{element.tag}: missing attributes {sorted(missing)}")
    if extra: _fail(f"{element.tag}: unknown attributes {sorted(extra)}")
    if any(element.get(key, "") == "" for key in required): _fail(f"{element.tag}: required attributes must be non-empty")


def _closed_children(element: ET.Element, allowed: set[str]) -> None:
    unknown = {child.tag for child in element} - allowed
    if unknown: _fail(f"{element.tag}: unknown elements {sorted(unknown)}")


def _closed_text(root: ET.Element) -> None:
    for element in root.iter():
        if element.tail and element.tail.strip(): _fail(f"{element.tag}: non-whitespace tail is forbidden")
        if element.tag in TEXT_ELEMENTS:
            if list(element) or not (element.text or "").strip(): _fail(f"{element.tag}: explicit text must be non-empty and childless")
        elif element.tag in BASE64_ELEMENTS:
            if list(element): _fail(f"{element.tag}: base64 text must be childless")
        elif element.text and element.text.strip():
            _fail(f"{element.tag}: non-whitespace text is forbidden")


def _sha(value: str | None, locator: str) -> None:
    if value is None or not SHA256_RE.fullmatch(value): _fail(f"{locator}: invalid sha256 digest")


def _int(value: str | None, locator: str) -> int:
    try: parsed = int(value or "")
    except ValueError: _fail(f"{locator}: expected non-negative integer")
    if parsed < 0: _fail(f"{locator}: expected non-negative integer")
    return parsed


def _bool(value: str | None, locator: str) -> bool:
    if value not in {"true", "false"}: _fail(f"{locator}: expected true or false")
    return value == "true"


def _unique(values: list[str | None], locator: str) -> None:
    if any(not value for value in values) or len(values) != len(set(values)): _fail(f"{locator}: values must be non-empty and unique")


def _normalized_relative(value: str, locator: str) -> str:
    if not value or value.startswith("/") or value.endswith("/") or "\\" in value or "//" in value or any(part in {"", ".", ".."} for part in value.split("/")) or PurePosixPath(value).as_posix() != value:
        _fail(f"{locator}: path must be exact normalized root-relative POSIX")
    return value


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _canonical_bytes(element: ET.Element) -> bytes:
    raw = ET.tostring(element, encoding="unicode", short_empty_elements=True)
    return (ET.canonicalize(raw, strip_text=True) + "\n").encode()


def _candidate_digest(candidate: ET.Element) -> str:
    clone = copy.deepcopy(candidate); clone.attrib.pop("candidate_digest", None)
    return _digest(_canonical_bytes(clone).rstrip(b"\n"))


def _intent_digest(candidate: ET.Element, run_id: str) -> str:
    change = (candidate.findtext("intended_change") or "").strip()
    if not change or len(change) > 500 or "\n" in change or "\r" in change: _fail("intended_change must be one concise normalized line")
    projection = ET.Element("candidate_intent", {
        "schema_version": "1", "run_id": run_id, "candidate_id": candidate.get("candidate_id", ""),
        "destination_scope": candidate.get("destination_scope", ""), "root": candidate.get("root", ""),
        "target": candidate.get("target", ""), "action": candidate.get("action", ""),
        "target_before_digest": candidate.get("target_before_digest", ""),
        "target_before_exists": candidate.get("target_before_exists", ""),
    })
    ET.SubElement(projection, "intended_change").text = change
    gate = candidate.find("semantic_abstraction_gate")
    if gate is None or len(candidate.findall("semantic_abstraction_gate")) != 1: _fail("candidate v2 requires one semantic abstraction gate")
    projection.append(copy.deepcopy(gate))
    return _digest(_canonical_bytes(projection).rstrip(b"\n"))


def _lineage_locator(locator: str, lineage: set[str]) -> bool:
    if locator in lineage:
        return True
    return any(locator.startswith(path + "#") and locator[len(path) + 1:].strip() == locator[len(path) + 1:] and locator[len(path) + 1:] for path in lineage)


def _validate_semantic_abstraction_gate(candidate: ET.Element, lineage: set[str]) -> str:
    gates = candidate.findall("semantic_abstraction_gate")
    if len(gates) != 1: _fail("candidate v2 requires one semantic abstraction gate")
    gate = gates[0]
    children = list(candidate)
    lineage_element = candidate.find("source_lineage")
    unit = candidate.find("durable_knowledge_unit")
    if lineage_element is None or unit is None: _fail("semantic abstraction gate requires source lineage and durable knowledge unit")
    if children.index(gate) != children.index(lineage_element) + 1 or children.index(gate) > children.index(unit):
        _fail("semantic abstraction gate must immediately follow source lineage and precede target state and knowledge unit")
    for state_tag in ("target_before_state", "target_after_state"):
        state = candidate.find(state_tag)
        if state is not None and children.index(gate) > children.index(state):
            _fail("semantic abstraction gate must precede target state and knowledge unit")

    _attrs(gate, {"result", "generalization_confidence", "reason_code"})
    _closed_children(gate, {"source_instances", "resulting_statement", "applicability_signals", "exclusions", "generalization_evidence", "counterexample_check", "rationale"})
    expected_order = ["source_instances", "resulting_statement", "applicability_signals", "exclusions", "generalization_evidence", "counterexample_check", "rationale"]
    if [child.tag for child in gate] != expected_order: _fail("semantic abstraction gate child order or cardinality invalid")

    result = gate.get("result", "")
    confidence = gate.get("generalization_confidence", "")
    reason = gate.get("reason_code", "")
    if result not in ABSTRACTION_RESULTS or confidence not in GENERALIZATION_CONFIDENCES or reason not in ABSTRACTION_REASON_CODES.get(result, set()):
        _fail("semantic abstraction gate result, confidence or reason code invalid")

    instances = gate.find("source_instances"); statement = gate.find("resulting_statement"); signals = gate.find("applicability_signals")
    exclusions = gate.find("exclusions"); evidence = gate.find("generalization_evidence"); counterexample = gate.find("counterexample_check"); rationale = gate.find("rationale")
    assert None not in {instances, statement, signals, exclusions, evidence, counterexample, rationale}
    assert instances is not None and statement is not None and signals is not None and exclusions is not None and evidence is not None and counterexample is not None and rationale is not None

    _attrs(instances, set()); _closed_children(instances, {"source_instance"}); source_instances = instances.findall("source_instance")
    if not source_instances: _fail("semantic abstraction gate requires source instances")
    _unique([item.get("locator") for item in source_instances], "semantic abstraction source instance locators")
    for item in source_instances:
        _attrs(item, {"locator"})
        if not _lineage_locator(item.get("locator", ""), lineage): _fail("semantic abstraction source instance is outside source lineage")

    _attrs(statement, set())
    _attrs(signals, set()); _closed_children(signals, {"applicability_signal"}); applicability = signals.findall("applicability_signal")
    if not applicability: _fail("semantic abstraction gate requires applicability signals")
    for item in applicability: _attrs(item, set())

    _attrs(exclusions, {"status"})
    exclusion_status = exclusions.get("status")
    if exclusion_status == "observed":
        _closed_children(exclusions, {"exclusion"})
        if not exclusions.findall("exclusion"): _fail("observed exclusions require one or more exclusions")
        for item in exclusions.findall("exclusion"): _attrs(item, set())
    elif exclusion_status == "none-observed":
        _closed_children(exclusions, {"none_observed_rationale"})
        if len(exclusions.findall("none_observed_rationale")) != 1: _fail("none-observed exclusions require exactly one rationale")
        _attrs(exclusions.find("none_observed_rationale"), set())
    else:
        _fail("semantic abstraction exclusions status invalid")

    def validate_gate_refs(container: ET.Element, locator: str) -> None:
        refs = container.findall("evidence_ref")
        if not refs: _fail(f"{locator} requires evidence refs")
        _unique([item.get("locator") for item in refs], f"{locator} evidence refs")
        for item in refs:
            _attrs(item, {"locator"}); _closed_children(item, set())
            if not _lineage_locator(item.get("locator", ""), lineage): _fail(f"{locator} evidence is outside source lineage")

    _attrs(evidence, set()); _closed_children(evidence, {"evidence_ref"}); validate_gate_refs(evidence, "semantic abstraction generalization")
    _attrs(counterexample, {"result"}); _closed_children(counterexample, {"evidence_ref"}); validate_gate_refs(counterexample, "semantic abstraction counterexample")
    counterexample_result = counterexample.get("result", "")
    if counterexample_result not in COUNTEREXAMPLE_RESULTS: _fail("semantic abstraction counterexample result invalid")
    _attrs(rationale, set())

    knowledge_statement = unit.find("statement")
    if knowledge_statement is None or len(unit.findall("statement")) != 1 or (statement.text or "") != (knowledge_statement.text or ""):
        _fail("semantic abstraction resulting statement must exactly equal knowledge unit statement")
    if any(locator in (statement.text or "") for locator in lineage): _fail("lineage locators are forbidden in semantic statements")

    if result == "generalized":
        if candidate.get("type") not in GENERALIZABLE_TYPES: _fail("semantic abstraction generalized result requires eligible semantic type")
        if confidence not in {"medium", "high"} or counterexample_result not in {"none-observed", "bounded"}:
            _fail("semantic abstraction generalized transition invalid")
    elif result == "local-with-rationale":
        if confidence != "not-applicable" or counterexample_result not in {"none-observed", "bounded", "material-observed"}:
            _fail("semantic abstraction local transition invalid")
        if (reason == "material-counterexample") != (counterexample_result == "material-observed"):
            _fail("semantic abstraction local material counterexample binding invalid")
    else:
        if confidence != "low" or counterexample_result not in {"inconclusive", "material-observed"} or candidate.get("action") != "blocked-with-reason":
            _fail("semantic abstraction blocked transition invalid")
        if (reason == "material-counterexample-needs-human") != (counterexample_result == "material-observed"):
            _fail("semantic abstraction blocked counterexample reason invalid")
    if counterexample_result == "bounded" and exclusion_status != "observed": _fail("bounded counterexample requires observed exclusions")
    if counterexample_result == "inconclusive" and result != "blocked-ambiguous": _fail("inconclusive counterexample requires blocked ambiguity")
    return result


def _manifest_digest(files: list[ET.Element]) -> str:
    payload = "".join(f"{e.get('path')}\0{e.get('sha256')}\0{e.get('size')}\0{e.get('initial_family')}\0{e.get('safety')}\n" for e in sorted(files, key=lambda x: x.get("path", ""))).encode()
    return _digest(payload)


def _canonical_root(value: str, locator: str, exists: bool) -> Path:
    path = Path(value)
    if not path.is_absolute() or path.as_posix() != value: _fail(f"{locator}: root must be canonical absolute POSIX")
    resolved = path.resolve(strict=exists)
    if resolved.as_posix() != value or (exists and not resolved.is_dir()): _fail(f"{locator}: root must be canonical absolute POSIX directory")
    return resolved


def _reject_absolute_symlink_components(path: Path, locator: str) -> None:
    if not path.is_absolute(): _fail(f"{locator}: path must be absolute")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        try: mode = current.lstat().st_mode
        except FileNotFoundError as error: raise ValidationError(f"{locator}: path component does not exist: {current}") from error
        if stat.S_ISLNK(mode): _fail(f"{locator}: symlink component is forbidden: {current}")


def _decode_state(candidate: ET.Element, prefix: str) -> tuple[bytes, bool]:
    element = candidate.find(f"target_{prefix}_state")
    if element is None or len(candidate.findall(f"target_{prefix}_state")) != 1: _fail(f"candidate: exactly one target_{prefix}_state is required")
    _attrs(element, {"encoding"})
    if element.get("encoding") != "base64": _fail(f"target_{prefix}_state encoding must be base64")
    try: payload = base64.b64decode((element.text or "").strip(), validate=True)
    except (ValueError, base64.binascii.Error) as error: raise ValidationError(f"invalid target_{prefix}_state base64") from error
    digest_key, exists_key = f"target_{prefix}_digest", f"target_{prefix}_exists"
    _sha(candidate.get(digest_key), digest_key)
    exists = _bool(candidate.get(exists_key), exists_key)
    if _digest(payload) != candidate.get(digest_key): _fail(f"target {prefix} digest is stale")
    if not exists and payload: _fail(f"absent target requires empty {prefix} state")
    return payload, exists


def _reject_lexical_symlinks(root: Path, target: str) -> Path:
    current = root
    for part in target.split("/"):
        current = current / part
        try: mode = current.lstat().st_mode
        except FileNotFoundError: continue
        if stat.S_ISLNK(mode): _fail("target path contains a symlink component")
    resolved = current.resolve(strict=False)
    try: resolved.relative_to(root)
    except ValueError as error: raise ValidationError("candidate target escapes approved root") from error
    return resolved


def _validate_current_target(candidate: ET.Element, root: Path, before: tuple[bytes, bool], after: tuple[bytes, bool] | None) -> None:
    target = _normalized_relative(candidate.get("target", ""), "candidate.target")
    path = _reject_lexical_symlinks(root, target)
    lifecycle = candidate.get("lifecycle")
    expected = after if candidate.get("action") == "promote" and lifecycle in {"writing", "auditing", "promoted"} else before
    assert expected is not None
    payload, exists = expected
    if exists:
        if not path.is_file() or path.read_bytes() != payload: _fail("current target differs from lifecycle-selected persisted state")
    elif path.exists(): _fail("current target existence differs from lifecycle-selected persisted state")


def _validate_manifest(manifest: ET.Element) -> dict[str, ET.Element]:
    _attrs(manifest, {"schema_version", "run_id", "plan_path", "excluded_namespace", "source_tree_digest"})
    if manifest.get("schema_version") != "1" or manifest.get("excluded_namespace") != "continuous-improvement/": _fail("source_manifest header invalid")
    if not RUN_ID_RE.fullmatch(manifest.get("run_id", "")) or manifest.get("run_id") in {".", ".."}: _fail("unsafe run_id")
    _canonical_root(manifest.get("plan_path", ""), "source_manifest.plan_path", False); _sha(manifest.get("source_tree_digest"), "source_tree_digest")
    _closed_children(manifest, {"totals", "files"})
    totals, container = manifest.find("totals"), manifest.find("files")
    if totals is None or container is None or len(manifest.findall("totals")) != 1 or len(manifest.findall("files")) != 1: _fail("source_manifest requires totals and files")
    _attrs(totals, {"discovered_files", "discovered_bytes"}); _attrs(container, set()); _closed_children(container, {"file"})
    records: dict[str, ET.Element] = {}
    for item in container.findall("file"):
        _attrs(item, {"path", "sha256", "size", "initial_family", "safety"}); path = _normalized_relative(item.get("path", ""), "manifest.file")
        if path.startswith("continuous-improvement/"): _fail("excluded namespace in manifest")
        _sha(item.get("sha256"), path); _int(item.get("size"), path)
        if (item.get("initial_family"), item.get("safety")) not in SAFETY_PAIRS: _fail("invalid family/safety pair")
        if path in records: _fail("manifest paths must be unique")
        records[path] = item
    files = list(records.values())
    if _int(totals.get("discovered_files"), "discovered_files") != len(files) or _int(totals.get("discovered_bytes"), "discovered_bytes") != sum(_int(x.get("size"), "size") for x in files): _fail("manifest totals mismatch")
    if manifest.get("source_tree_digest") != _manifest_digest(files): _fail("source manifest tree digest is stale")
    return records


def _validate_current_source(manifest: ET.Element) -> None:
    path = Path(__file__).resolve().parent / "inventory-plan-directory.py"
    spec = importlib.util.spec_from_file_location("inventory_current", path)
    if spec is None or spec.loader is None: _fail("inventory module unavailable")
    module = importlib.util.module_from_spec(spec); prior = sys.dont_write_bytecode; sys.dont_write_bytecode = True
    try: spec.loader.exec_module(module); observed = module.inventory(Path(manifest.get("plan_path", "")), manifest.get("run_id", ""))
    finally: sys.dont_write_bytecode = prior
    if module.canonical_xml(observed) != module.canonical_xml(manifest): _fail("current source tree differs from immutable manifest")


def _validate_roots(container: ET.Element, authority: dict[str, Path] | None, live: bool) -> dict[str, Path]:
    _attrs(container, {"schema_version"}); _closed_children(container, {"approved_root"})
    if container.get("schema_version") != "1": _fail("approved_roots version invalid")
    roots: dict[str, Path] = {}
    for item in container.findall("approved_root"):
        _attrs(item, {"destination_scope", "scope", "root", "writer"}); scope = item.get("destination_scope", "")
        if scope not in DESTINATION_WRITERS or scope in roots: _fail("approved root scope unknown or duplicate")
        if item.get("writer") != DESTINATION_WRITERS[scope] or item.get("scope") != DESTINATION_SCOPES[scope]: _fail("approved root routing mismatch")
        roots[scope] = _canonical_root(item.get("root", ""), f"approved_root[{scope}]", live)
    if not roots: _fail("approved_roots must be non-empty")
    if live:
        if authority is None or set(authority) != set(roots): _fail("persisted roots disagree with caller authority")
        for scope, path in authority.items():
            if _canonical_root(path.as_posix(), f"authoritative_root[{scope}]", True) != roots[scope]: _fail("persisted root disagrees with caller authority")
    return roots


def validate_document(root: ET.Element, authoritative_roots: dict[str, Path] | None = None, authoritative_plan_path: Path | None = None, verify_current_filesystem: bool = True) -> None:
    _closed_text(root)
    for candidate in root.iter("continuous_improvement_candidate"):
        if candidate.get("schema_version") != "2": _fail("continuous_improvement_candidate v1 is current-only rejected")
    if root.tag != "plan_knowledge_run": _fail("root must be plan_knowledge_run")
    _attrs(root, {"schema_version", "run_id", "plan_directory_class", "retrospective_present"})
    if root.get("schema_version") != "1" or root.get("plan_directory_class") != "complete": _fail("plan_knowledge_run header invalid")
    _bool(root.get("retrospective_present"), "retrospective_present")
    expected = {"run_state", *CANONICAL_FILES.values()}; _closed_children(root, expected)
    if any(len(root.findall(tag)) != 1 for tag in expected): _fail("plan_knowledge_run requires each canonical section exactly once")
    run = root.find("run_state"); assert run is not None
    _attrs(run, {"schema_version", "run_id", "status", "resume_mode", "resume_stale", "source_tree_digest", "plan_directory_class", "retrospective_present"})
    if run.get("schema_version") != "1" or run.get("status") not in RUN_STATES or run.get("resume_mode") not in {"new", "resumed", "explicit-resume"} or _bool(run.get("resume_stale"), "resume_stale"): _fail("run_state header invalid")
    for field in ("run_id", "plan_directory_class", "retrospective_present"):
        if run.get(field) != root.get(field): _fail(f"run_state {field} disagrees with aggregate")
    _sha(run.get("source_tree_digest"), "run_state.source_tree_digest"); _closed_children(run, {"canonical_files"})
    canonical = run.find("canonical_files")
    if canonical is None or len(run.findall("canonical_files")) != 1: _fail("run_state requires canonical_files")
    _attrs(canonical, set()); _closed_children(canonical, {"file"}); refs = canonical.findall("file")
    _unique([x.get("path") for x in refs], "canonical file paths")
    if {x.get("path") for x in refs} != set(CANONICAL_FILES): _fail("run_state must bind exactly eight canonical files")
    for ref in refs:
        _attrs(ref, {"path", "sha256"}); _sha(ref.get("sha256"), "canonical file digest")
        section = root.find(CANONICAL_FILES[ref.get("path", "")]); assert section is not None
        if ref.get("sha256") != _digest(_canonical_bytes(section)): _fail("canonical file digest is stale")

    manifest = root.find("source_manifest"); assert manifest is not None
    records = _validate_manifest(manifest)
    if manifest.get("run_id") != root.get("run_id") or manifest.get("source_tree_digest") != run.get("source_tree_digest"): _fail("run/source identity drift")
    if verify_current_filesystem:
        if authoritative_plan_path is None or authoritative_plan_path.is_symlink(): _fail("authoritative plan_directory required and must not be symlink")
        approved_plan = _canonical_root(authoritative_plan_path.as_posix(), "authoritative plan_directory", True)
        _reject_absolute_symlink_components(approved_plan, "authoritative plan_directory")
        if approved_plan.as_posix() != manifest.get("plan_path"): _fail("plan_path disagrees with caller authority")
        _validate_current_source(manifest)
    roots_element = root.find("approved_roots"); assert roots_element is not None
    roots = _validate_roots(roots_element, authoritative_roots, verify_current_filesystem)

    ledger = root.find("file_processing_ledger"); assert ledger is not None
    _attrs(ledger, {"schema_version"}); _closed_children(ledger, {"file_result"})
    if ledger.get("schema_version") != "1": _fail("ledger version invalid")
    results = ledger.findall("file_result"); _unique([x.get("path") for x in results], "ledger paths")
    if {x.get("path") for x in results} != set(records): _fail("every manifest file requires one ledger result")
    result_by_path = {x.get("path", ""): x for x in results}; digested_batches: dict[str, str] = {}
    content_groups: dict[tuple[str | None, str | None], list[str]] = {}
    for path, record in records.items(): content_groups.setdefault((record.get("sha256"), record.get("size")), []).append(path)
    duplicate_leaders = {path: min(paths) for paths in content_groups.values() for path in paths}
    for path, item in result_by_path.items():
        disposition = item.get("disposition"); required = {"path", "disposition"}
        if disposition == "digested": required |= {"batch_id", "result_ref"}
        elif disposition == "duplicate": required |= {"duplicate_of"}
        elif disposition == "generated-noise": required |= {"rule_id", "reason"}
        elif disposition in {"unsupported", "blocked"}: required |= {"material", "reason"}
        else: _fail("invalid ledger disposition")
        _attrs(item, required)
        eligible = records[path].get("initial_family") == "recognized-text" and records[path].get("safety") == "eligible"
        if not eligible and disposition != "blocked": _fail("noneligible source must remain blocked")
        if disposition == "digested": digested_batches[path] = item.get("batch_id", "")
        elif disposition == "duplicate":
            leader = item.get("duplicate_of", "")
            if path == duplicate_leaders[path] or leader != duplicate_leaders[path]: _fail("duplicate must point directly to lexicographically smallest group leader")
        elif disposition in {"unsupported", "blocked"}: _bool(item.get("material"), f"ledger[{path}].material")
    def admissible(path: str, seen: set[str] | None = None) -> bool:
        seen = seen or set()
        if path in seen: return False
        seen.add(path); item = result_by_path[path]
        if item.get("disposition") == "digested": return records[path].get("safety") == "eligible"
        if item.get("disposition") == "duplicate": return admissible(item.get("duplicate_of", ""), seen)
        return False
    admissible_paths = {path for path in records if admissible(path)}
    material_unread = sum(item.get("disposition") in {"unsupported", "blocked"} and item.get("material") == "true" for item in results)

    diagnostics = root.find("integrity_diagnostics"); assert diagnostics is not None
    _attrs(diagnostics, {"schema_version", "status"}); _closed_children(diagnostics, {"diagnostic"})
    if diagnostics.get("schema_version") != "1" or diagnostics.get("status") not in {"pass", "blocked"}: _fail("diagnostics header invalid")
    for item in diagnostics.findall("diagnostic"):
        _attrs(item, {"type", "path", "reason"})
        if item.get("type") not in DIAGNOSTIC_TYPES: _fail("invalid diagnostic type")
    if (diagnostics.get("status") == "pass") != (not diagnostics.findall("diagnostic")): _fail("diagnostics status mismatch")
    if diagnostics.findall("diagnostic"): _fail("integrity diagnostics block validation")

    digest = root.find("knowledge_digest"); assert digest is not None
    _attrs(digest, {"schema_version", "reconciler"}); _closed_children(digest, {"digestion_batches", "claims", "implementation_deltas", "material_findings"})
    if digest.get("schema_version") != "1" or digest.get("reconciler") != "orchestrator-global": _fail("knowledge_digest header invalid")
    batches = digest.find("digestion_batches"); claims_box = digest.find("claims"); deltas_box = digest.find("implementation_deltas"); findings_box = digest.find("material_findings")
    if None in {batches, claims_box, deltas_box, findings_box}: _fail("knowledge_digest sections missing")
    assert batches is not None and claims_box is not None and deltas_box is not None and findings_box is not None
    for box, child in ((batches, "batch"), (claims_box, "claim"), (deltas_box, "implementation_delta"), (findings_box, "material_finding")): _attrs(box, set()); _closed_children(box, {child})
    batch_paths: list[str | None] = []; batch_map: dict[str, str] = {}; batch_ids = []
    for batch in batches.findall("batch"):
        _attrs(batch, {"batch_id"}); _closed_children(batch, {"file_ref"}); batch_ids.append(batch.get("batch_id"))
        for ref in batch.findall("file_ref"): _attrs(ref, {"path"}); batch_paths.append(ref.get("path")); batch_map[ref.get("path", "")] = batch.get("batch_id", "")
    _unique(batch_ids, "batch ids"); _unique(batch_paths, "batch file refs")
    if set(batch_paths) != set(digested_batches) or any(batch_map[p] != b for p, b in digested_batches.items()): _fail("digestion batch coverage mismatch")
    claims = claims_box.findall("claim"); deltas = deltas_box.findall("implementation_delta"); findings = findings_box.findall("material_finding")
    _unique([x.get("claim_id") for x in claims], "claim ids"); _unique([x.get("delta_id") for x in deltas], "delta ids"); _unique([x.get("finding_id") for x in findings], "finding ids")
    claim_by_id = {x.get("claim_id", ""): x for x in claims}
    for claim in claims:
        _attrs(claim, {"claim_id", "reconciliation", "source_ref"})
        if claim.get("reconciliation") not in {"confirmed", "not-implemented", "contradicted", "unvalidated"} or claim.get("source_ref") not in admissible_paths: _fail("claim reconciliation or provenance invalid")
    for delta in deltas:
        _attrs(delta, {"delta_id", "claim_id", "target"}); source_claim = claim_by_id.get(delta.get("claim_id", ""))
        if source_claim is None or source_claim.get("reconciliation") != "confirmed": _fail("implementation delta requires confirmed claim")
    for finding in findings:
        _attrs(finding, {"finding_id", "type", "scope", "source_ref"})
        if finding.get("type") not in SEMANTIC_TYPES or not finding.get("scope") or finding.get("source_ref") not in admissible_paths: _fail("material finding type, scope or provenance invalid")

    candidates_box = root.find("candidates"); assert candidates_box is not None
    _attrs(candidates_box, {"schema_version"}); _closed_children(candidates_box, {"continuous_improvement_candidate"})
    if candidates_box.get("schema_version") != "1": _fail("candidates version invalid")
    candidates = candidates_box.findall("continuous_improvement_candidate"); by_id: dict[str, ET.Element] = {}; covered_deltas: set[str] = set(); covered_findings: set[str] = set(); candidate_blockers = []; material_candidates: list[ET.Element] = []
    for candidate in candidates:
        common = {"schema_version", "candidate_id", "candidate_digest", "intent_digest", "lifecycle", "target_before_digest", "target_before_exists", "material", "type", "scope", "destination_scope", "root", "target", "writer", "action"}
        after_attrs = {"target_after_digest", "target_after_exists"} if candidate.get("action") == "promote" else set()
        _attrs(candidate, common | after_attrs)
        cid = candidate.get("candidate_id", ""); is_material = _bool(candidate.get("material"), f"candidate[{cid}].material")
        if is_material: material_candidates.append(candidate)
        by_id[cid] = candidate; action = candidate.get("action"); lifecycle = candidate.get("lifecycle")
        if action not in ACTIONS or lifecycle not in CANDIDATE_STATES: _fail("candidate action or lifecycle invalid")
        allowed_lifecycle = {"proposed", "approved", "writing", "auditing", "promoted", "blocked-with-reason"} if action == "promote" else {"proposed", "noop-proven", "blocked-with-reason"} if action == "noop-proven" else {"proposed", "blocked-with-reason"}
        if lifecycle not in allowed_lifecycle: _fail("candidate lifecycle disagrees with action")
        scope = candidate.get("destination_scope", "")
        if scope not in roots or candidate.get("writer") != DESTINATION_WRITERS[scope] or candidate.get("scope") != DESTINATION_SCOPES[scope]: _fail("candidate routing mismatch")
        croot = _canonical_root(candidate.get("root", ""), f"candidate[{cid}].root", verify_current_filesystem)
        if croot != roots[scope]: _fail("candidate root is not approved")
        _normalized_relative(candidate.get("target", ""), "candidate.target")
        _closed_children(candidate, {"intended_change", "source_lineage", "semantic_abstraction_gate", "target_before_state", "target_after_state", "durable_knowledge_unit", "root_cause", "approval", "validators", "gates", "promotion_evidence", "noop_evidence", "blocked_evidence", "residual_blockers"})
        if len(candidate.findall("intended_change")) != 1: _fail("candidate requires one intended_change")
        _attrs(candidate.find("intended_change"), set())
        lineage = candidate.find("source_lineage")
        if lineage is None or len(candidate.findall("source_lineage")) != 1: _fail("candidate requires source lineage")
        _attrs(lineage, set()); _closed_children(lineage, {"evidence_ref"}); refs = lineage.findall("evidence_ref"); _unique([x.get("locator") for x in refs], "lineage refs")
        if not refs or any(x.get("locator") not in admissible_paths for x in refs): _fail("candidate source lineage provenance invalid")
        for ref in refs: _attrs(ref, {"locator"})
        unit = candidate.find("durable_knowledge_unit")
        if unit is None or len(candidate.findall("durable_knowledge_unit")) != 1: _fail("candidate requires one durable knowledge unit")
        abstraction_result = _validate_semantic_abstraction_gate(candidate, {ref.get("locator", "") for ref in refs})
        _sha(candidate.get("intent_digest"), "intent_digest")
        if candidate.get("intent_digest") != _intent_digest(candidate, root.get("run_id", "")): _fail("candidate intent digest is stale")
        before = _decode_state(candidate, "before")
        after = _decode_state(candidate, "after") if action == "promote" else None
        if action != "promote" and candidate.find("target_after_state") is not None: _fail("non-promote candidate forbids target after state")
        if verify_current_filesystem: _validate_current_target(candidate, roots[scope], before, after)
        _attrs(unit, set()); _closed_children(unit, {"statement", "use_when", "evidence_refs", "covered_refs"})
        if len(unit.findall("statement")) != 1 or len(unit.findall("use_when")) != 1: _fail("knowledge unit text cardinality invalid")
        _attrs(unit.find("statement"), set()); _attrs(unit.find("use_when"), set())
        evidence = unit.find("evidence_refs"); covered = unit.find("covered_refs")
        if evidence is None or covered is None: _fail("knowledge unit refs missing")
        _attrs(evidence, set()); _closed_children(evidence, {"evidence_ref"}); erefs = evidence.findall("evidence_ref"); _unique([x.get("locator") for x in erefs], "evidence refs")
        if not erefs or any(x.get("locator") not in admissible_paths for x in erefs): _fail("candidate evidence provenance invalid")
        for ref in erefs: _attrs(ref, {"locator"})
        _attrs(covered, set()); _closed_children(covered, {"delta_ref", "finding_ref"}); crefs = list(covered); _unique([f"{x.tag}:{x.get('id')}" for x in crefs], "covered refs")
        if not crefs: _fail("candidate covered refs required")
        for ref in crefs:
            _attrs(ref, {"id"})
            if ref.tag == "delta_ref":
                if ref.get("id") not in {x.get("delta_id") for x in deltas}: _fail("unknown covered delta")
                if is_material: covered_deltas.add(ref.get("id", ""))
            else:
                if ref.get("id") not in {x.get("finding_id") for x in findings}: _fail("unknown covered finding")
                if is_material: covered_findings.add(ref.get("id", ""))
        roots_cause = candidate.findall("root_cause")
        if (candidate.get("type") in PROBLEM_TYPES) != (len(roots_cause) == 1): _fail("root_cause cardinality disagrees with type")
        if candidate.get("type") not in SEMANTIC_TYPES: _fail("unknown semantic type")
        if roots_cause: _attrs(roots_cause[0], {"problem", "cause", "prevention"}); _closed_children(roots_cause[0], set())
        approval = candidate.find("approval"); validators = candidate.find("validators"); gates = candidate.find("gates"); residual = candidate.find("residual_blockers")
        if None in {approval, validators, gates, residual}: _fail("candidate controls missing")
        assert approval is not None and validators is not None and gates is not None and residual is not None
        _attrs(approval, {"status", "approval_id"}); _attrs(validators, set()); _attrs(gates, set()); _attrs(residual, set())
        _closed_children(validators, {"validator"}); _closed_children(gates, {"gate"}); _closed_children(residual, {"blocker"})
        controls = validators.findall("validator") + gates.findall("gate")
        if not validators.findall("validator") or not gates.findall("gate"): _fail("validators and gates must be non-empty")
        for control in controls:
            _attrs(control, {"id", "status"})
            if control.get("status") not in CONTROL_STATES: _fail("control status invalid")
        _unique([x.get("id") for x in validators.findall("validator")], "validator ids"); _unique([x.get("id") for x in gates.findall("gate")], "gate ids")
        material_residual = False
        for blocker in residual.findall("blocker"): _attrs(blocker, {"material", "reason"}); material_residual |= _bool(blocker.get("material"), "residual blocker")
        if abstraction_result == "blocked-ambiguous" and (not material_residual or candidate.find("blocked_evidence") is None):
            _fail("blocked semantic abstraction requires blocking evidence and a material residual blocker")
        expected_approval = "pending" if action == "promote" and lifecycle == "proposed" else "approved" if action == "promote" else "not-required" if action == "noop-proven" else "rejected"
        if approval.get("status") != expected_approval: _fail("candidate approval status disagrees with lifecycle/action")
        evidence_tags = [tag for tag in ("promotion_evidence", "noop_evidence", "blocked_evidence") if candidate.find(tag) is not None]
        if len(evidence_tags) > 1: _fail("candidate action evidence cardinality invalid")
        for tag in evidence_tags:
            item = candidate.find(tag); assert item is not None; _attrs(item, {"mode", "status"}); _closed_children(item, set())
            if item.get("status") not in CONTROL_STATES: _fail("action evidence status invalid")
        if lifecycle == "promoted" and (evidence_tags != ["promotion_evidence"] or candidate.find("promotion_evidence").get("status") != "passed" or any(x.get("status") != "passed" for x in controls)): _fail("promoted candidate requires passed evidence and controls")
        if lifecycle == "noop-proven" and (evidence_tags != ["noop_evidence"] or candidate.find("noop_evidence").get("status") != "passed" or any(x.get("status") != "passed" for x in controls)): _fail("noop candidate requires passed evidence and controls")
        if lifecycle == "blocked-with-reason":
            if evidence_tags != ["blocked_evidence"] or candidate.find("blocked_evidence").get("status") != "passed" or not (material_residual or any(x.get("status") == "failed" for x in controls)): _fail("blocked candidate requires passed blocking evidence and blocker")
            candidate_blockers.append(cid)
        _sha(candidate.get("candidate_digest"), "candidate_digest")
        if candidate.get("candidate_digest") != _candidate_digest(candidate): _fail("candidate digest is stale")
    _unique([x.get("candidate_id") for x in candidates], "candidate ids")
    if {x.get("delta_id") for x in deltas} - covered_deltas: _fail("confirmed implementation delta lacks material candidate linkage")
    if {x.get("finding_id") for x in findings} - covered_findings: _fail("material finding lacks material candidate linkage")

    approvals = root.find("approvals"); assert approvals is not None
    _attrs(approvals, {"schema_version", "interaction_id"}); _closed_children(approvals, {"envelope"})
    if approvals.get("schema_version") != "1": _fail("approvals version invalid")
    envelopes = approvals.findall("envelope"); _unique([x.get("approval_id") for x in envelopes], "approval ids")
    if len(envelopes) != len(candidates): _fail("every candidate requires one envelope")
    for env in envelopes:
        _attrs(env, {"approval_id", "run_id", "candidate_id", "intent_digest", "destination_scope", "root", "target", "before_digest", "before_exists", "action", "status"})
        candidate = by_id.get(env.get("candidate_id", ""))
        if candidate is None or env.get("run_id") != root.get("run_id"): _fail("approval run/candidate binding invalid")
        mapping = {"intent_digest": "intent_digest", "destination_scope": "destination_scope", "root": "root", "target": "target", "before_digest": "target_before_digest", "before_exists": "target_before_exists", "action": "action"}
        if any(env.get(a) != candidate.get(b) for a, b in mapping.items()): _fail("approval immutable intent binding changed")
        approval = candidate.find("approval"); assert approval is not None
        if env.get("approval_id") != approval.get("approval_id") or env.get("status") != approval.get("status"): _fail("candidate/envelope approval mismatch")

    coverage = root.find("plan_knowledge_coverage"); assert coverage is not None
    _attrs(coverage, {"schema_version", "status", "plan_knowledge_independence", "lifecycle_validated", "deletion_readiness_claimed"})
    if coverage.get("schema_version") != "1": _fail("coverage version invalid")
    status_value = coverage.get("status"); independence = _bool(coverage.get("plan_knowledge_independence"), "independence")
    if status_value != run.get("status") or status_value not in RUN_STATES or _bool(coverage.get("lifecycle_validated"), "lifecycle") or _bool(coverage.get("deletion_readiness_claimed"), "deletion"): _fail("coverage lifecycle header invalid")
    _closed_children(coverage, {"source_coverage", "knowledge_coverage", "candidate_coverage", "recoverability", "durable_dependency", "blockers"})
    source = coverage.find("source_coverage"); knowledge = coverage.find("knowledge_coverage"); candidate_cov = coverage.find("candidate_coverage"); recovery = coverage.find("recoverability"); dependency = coverage.find("durable_dependency"); blockers = coverage.find("blockers")
    if None in {source, knowledge, candidate_cov, recovery, dependency, blockers}: _fail("coverage sections missing")
    assert source is not None and knowledge is not None and candidate_cov is not None and recovery is not None and dependency is not None and blockers is not None
    _attrs(source, {"manifest_files", "ledger_files", "accounted", "integrity", "material_unread"}); _attrs(knowledge, {"material_findings", "covered_findings", "claims", "reconciled_claims", "deltas", "disposed_deltas"}); _attrs(candidate_cov, {"material_candidates", "applied_or_noop", "blocked"}); _attrs(recovery, set()); _attrs(dependency, {"plan_refs", "run_namespace_refs"}); _attrs(blockers, set()); _closed_children(recovery, {"question"}); _closed_children(blockers, {"blocker"})
    if _int(source.get("manifest_files"), "manifest_files") != len(records) or _int(source.get("ledger_files"), "ledger_files") != len(results) or not _bool(source.get("accounted"), "accounted") or source.get("integrity") != "pass": _fail("source coverage mismatch")
    if _int(source.get("material_unread"), "material_unread") != material_unread: _fail("material_unread must be derived from ledger")
    if (_int(knowledge.get("material_findings"), "findings"), _int(knowledge.get("covered_findings"), "covered")) != (len(findings), len(covered_findings)) or (_int(knowledge.get("claims"), "claims"), _int(knowledge.get("reconciled_claims"), "reconciled")) != (len(claims), len(claims)) or (_int(knowledge.get("deltas"), "deltas"), _int(knowledge.get("disposed_deltas"), "disposed")) != (len(deltas), len(covered_deltas)): _fail("knowledge coverage mismatch")
    material = material_candidates
    applied = sum(x.get("lifecycle") in {"promoted", "noop-proven"} for x in material); blocked_count = sum(x.get("lifecycle") == "blocked-with-reason" for x in material)
    if (_int(candidate_cov.get("material_candidates"), "material candidates"), _int(candidate_cov.get("applied_or_noop"), "applied"), _int(candidate_cov.get("blocked"), "blocked")) != (len(material), applied, blocked_count): _fail("candidate coverage mismatch")
    questions = recovery.findall("question"); _unique([x.get("question_id") for x in questions], "question ids"); question_texts = [] ; recovered: set[str] = set(); recovery_failed = False
    for question in questions:
        _attrs(question, {"question_id", "librarian", "entrypoint", "result"}); _closed_children(question, {"question_text", "candidate_ref", "expected_claim", "comparison_evidence"})
        if len(question.findall("question_text")) != 1 or len(question.findall("comparison_evidence")) != 1: _fail("recoverability textual cardinality invalid")
        _attrs(question.find("question_text"), set())
        text = (question.findtext("question_text") or "").strip(); question_texts.append(text)
        refs = question.findall("candidate_ref"); claims_expected = question.findall("expected_claim"); _unique([x.get("id") for x in refs], "question candidate refs"); _unique([(x.text or "").strip() for x in claims_expected], "expected claims")
        if not refs or not claims_expected: _fail("recoverability candidates and expected claims required")
        for claim in claims_expected: _attrs(claim, set())
        for ref in refs:
            _attrs(ref, {"id"})
            if ref.get("id") not in by_id: _fail("unknown recovery candidate")
            recovered.add(ref.get("id", ""))
        librarian, entrypoint = question.get("librarian"), question.get("entrypoint")
        if (librarian, entrypoint) not in {("framework-knowledge-librarian", "manifest.yaml"), ("bibliotecario", "docs/index.xml")}: _fail("recoverability routing invalid")
        comparison = question.find("comparison_evidence"); assert comparison is not None; _attrs(comparison, {"status", "evidence_ref"})
        if question.get("result") not in {"pass", "fail", "inconclusive"} or comparison.get("status") != question.get("result"): _fail("recoverability comparison status invalid")
        recovery_failed |= question.get("result") != "pass"
    _unique(question_texts, "recovery questions")
    if {x.get("candidate_id") for x in material if x.get("lifecycle") in {"promoted", "noop-proven"}} - recovered: _fail("material terminal candidate lacks recoverability")
    material_coverage_blockers = []
    for blocker in blockers.findall("blocker"): _attrs(blocker, {"material", "reason"}); material_coverage_blockers += [blocker] if _bool(blocker.get("material"), "coverage blocker") else []
    if _int(dependency.get("plan_refs"), "plan_refs") or _int(dependency.get("run_namespace_refs"), "run refs"): _fail("durable target depends on transient plan state")
    lifecycles = {x.get("lifecycle") for x in candidates}
    if status_value == "proposed" and lifecycles != {"proposed"}: _fail("proposed run cardinality invalid")
    if status_value == "approved" and ("approved" not in lifecycles or not lifecycles <= {"approved", "noop-proven", "blocked-with-reason"}): _fail("approved run cardinality invalid")
    if status_value == "writing" and ("writing" not in lifecycles or not lifecycles <= {"approved", "writing", "noop-proven", "blocked-with-reason"}): _fail("writing run cardinality invalid")
    if status_value == "auditing" and ("auditing" not in lifecycles or not lifecycles <= {"approved", "writing", "auditing", *TERMINAL_CANDIDATE_STATES}): _fail("auditing run cardinality invalid")
    blockers_present = bool(material_unread or material_coverage_blockers or candidate_blockers or recovery_failed)
    if status_value not in {"completed", "completed-with-blockers"}:
        if independence: _fail("nonterminal run cannot claim independence")
    elif status_value == "completed":
        if lifecycles - {"promoted", "noop-proven"} or blockers_present or not independence: _fail("completed terminal truth invalid")
    else:
        if lifecycles - TERMINAL_CANDIDATE_STATES or not blockers_present or independence: _fail("completed-with-blockers terminal truth invalid")
    if independence and any(x.get("reconciliation") not in {"confirmed", "not-implemented"} for x in claims): _fail("independence requires conclusive reconciliation")


def _load_live_run(run_directory: Path, authoritative_plan_path: Path | None) -> ET.Element:
    if authoritative_plan_path is None: _fail("authoritative plan_directory is required for live run selection")
    approved_plan = _canonical_root(authoritative_plan_path.as_posix(), "authoritative plan_directory", True)
    _reject_absolute_symlink_components(approved_plan, "authoritative plan_directory")
    run_id = run_directory.name
    if not RUN_ID_RE.fullmatch(run_id) or run_id in {".", ".."}: _fail("live run path has unsafe run_id")
    expected = approved_plan / "continuous-improvement" / "runs" / run_id
    if run_directory.as_posix() != expected.as_posix(): _fail("live run path is not lexically bound to authoritative plan_directory")
    _reject_absolute_symlink_components(expected, "live run path")
    if expected.resolve(strict=True) != expected: _fail("live run path is not canonically bound to authoritative plan_directory")
    if not run_directory.is_dir(): _fail("live run path must be a regular directory")
    if {x.name for x in run_directory.iterdir()} != ALL_CANONICAL_FILES: _fail("live run directory must contain exactly nine canonical files")
    parsed: dict[str, ET.Element] = {}; raw: dict[str, bytes] = {}
    for name in ALL_CANONICAL_FILES:
        path = run_directory / name
        _reject_absolute_symlink_components(path, f"canonical run file {name}")
        if not path.is_file(): _fail(f"canonical run file is not regular: {name}")
        raw[name] = path.read_bytes(); parsed[name] = ET.fromstring(raw[name])
        if raw[name] != _canonical_bytes(parsed[name]): _fail(f"canonical run file bytes are not canonical: {name}")
    run = parsed["run-state.xml"]
    if run.tag != "run_state" or run_directory.name != run.get("run_id"): _fail("selected persisted run identity mismatch")
    root = ET.Element("plan_knowledge_run", {"schema_version": "1", "run_id": run.get("run_id", ""), "plan_directory_class": run.get("plan_directory_class", ""), "retrospective_present": run.get("retrospective_present", "")})
    root.append(run)
    for name, tag in CANONICAL_FILES.items():
        if parsed[name].tag != tag: _fail(f"canonical file root mismatch: {name}")
        root.append(parsed[name])
    return root


def validate_path(path: Path, roots: dict[str, Path] | None = None, plan: Path | None = None, fixture: bool = False) -> None:
    root = ET.parse(path).getroot() if fixture else _load_live_run(path, plan)
    validate_document(root, roots, plan, not fixture)


def _clone(root: ET.Element) -> ET.Element: return copy.deepcopy(root)


def _refresh_canonical_digests(root: ET.Element) -> None:
    canonical = root.find("./run_state/canonical_files")
    assert canonical is not None
    for ref in canonical.findall("file"):
        section = root.find(CANONICAL_FILES[ref.get("path", "")])
        assert section is not None
        ref.set("sha256", _digest(_canonical_bytes(section)))


def _refresh_candidate_bindings(root: ET.Element, candidate: ET.Element) -> None:
    intent = _intent_digest(candidate, root.get("run_id", ""))
    candidate.set("intent_digest", intent)
    envelope = root.find(f"./approvals/envelope[@candidate_id='{candidate.get('candidate_id')}']")
    if envelope is not None:
        envelope.set("intent_digest", intent)
        envelope.set("action", candidate.get("action", ""))
        approval = candidate.find("approval")
        if approval is not None: envelope.set("status", approval.get("status", ""))
    candidate.set("candidate_digest", _candidate_digest(candidate))
    _refresh_canonical_digests(root)


def _terminal_package(root: ET.Element) -> ET.Element:
    candidate = root.find("./candidates/continuous_improvement_candidate[@candidate_id='candidate-package']")
    assert candidate is not None
    return candidate


def _blocked_abstraction_case(terminal: ET.Element, reason: str, counterexample_result: str) -> ET.Element:
    case = _clone(terminal); candidate = _terminal_package(case); gate = candidate.find("semantic_abstraction_gate"); assert gate is not None
    candidate.set("action", "blocked-with-reason"); candidate.set("lifecycle", "blocked-with-reason")
    candidate.attrib.pop("target_after_digest"); candidate.attrib.pop("target_after_exists"); candidate.remove(candidate.find("target_after_state"))
    gate.set("result", "blocked-ambiguous"); gate.set("generalization_confidence", "low"); gate.set("reason_code", reason)
    counterexample = gate.find("counterexample_check"); assert counterexample is not None; counterexample.set("result", counterexample_result)
    approval = candidate.find("approval"); assert approval is not None; approval.set("status", "rejected")
    promotion = candidate.find("promotion_evidence"); assert promotion is not None
    blocked = ET.Element("blocked_evidence", {"mode": "semantic-abstraction-gate", "status": "passed"}); candidate.insert(list(candidate).index(promotion), blocked); candidate.remove(promotion)
    residual = candidate.find("residual_blockers"); assert residual is not None; ET.SubElement(residual, "blocker", {"material": "true", "reason": "semantic-abstraction-needs-human"})
    run = case.find("run_state"); coverage = case.find("plan_knowledge_coverage"); assert run is not None and coverage is not None
    run.set("status", "completed-with-blockers"); coverage.set("status", "completed-with-blockers"); coverage.set("plan_knowledge_independence", "false")
    candidate_coverage = coverage.find("candidate_coverage"); assert candidate_coverage is not None; candidate_coverage.set("applied_or_noop", "1"); candidate_coverage.set("blocked", "1")
    _refresh_candidate_bindings(case, candidate)
    return case


def _apply_abstraction_scenario(candidate: ET.Element, scenario: dict[str, object]) -> None:
    candidate.set("type", str(scenario["semantic_type"]))
    gate = candidate.find("semantic_abstraction_gate"); unit = candidate.find("durable_knowledge_unit"); assert gate is not None and unit is not None
    gate.set("result", str(scenario["result"])); gate.set("generalization_confidence", str(scenario["confidence"])); gate.set("reason_code", str(scenario["reason_code"]))
    source_instance = gate.find("source_instances/source_instance"); resulting_statement = gate.find("resulting_statement"); applicability = gate.find("applicability_signals/applicability_signal")
    evidence = gate.find("generalization_evidence/evidence_ref"); counterexample = gate.find("counterexample_check"); counterexample_evidence = gate.find("counterexample_check/evidence_ref"); rationale = gate.find("rationale"); statement = unit.find("statement")
    assert None not in {source_instance, resulting_statement, applicability, evidence, counterexample, counterexample_evidence, rationale, statement}
    assert source_instance is not None and resulting_statement is not None and applicability is not None and evidence is not None and counterexample is not None and counterexample_evidence is not None and rationale is not None and statement is not None
    source_instance.set("locator", str(scenario["source_locator"])); source_instance.text = str(scenario["source_instance"])
    resulting_statement.text = str(scenario["statement"]); statement.text = str(scenario["statement"]); applicability.text = str(scenario["applicability"])
    evidence.set("locator", str(scenario["evidence_locator"])); counterexample.set("result", str(scenario["counterexample_result"])); counterexample_evidence.set("locator", str(scenario["counterexample_locator"])); rationale.text = str(scenario["rationale"])
    exclusions = gate.find("exclusions"); assert exclusions is not None; exclusions.clear()
    observed_exclusions = list(scenario.get("exclusions", []))
    if observed_exclusions:
        exclusions.set("status", "observed")
        for value in observed_exclusions: ET.SubElement(exclusions, "exclusion").text = str(value)
    else:
        exclusions.set("status", "none-observed")
        ET.SubElement(exclusions, "none_observed_rationale").text = str(scenario["none_observed_rationale"])


def _scenario_input_summary(scenario: dict[str, object]) -> str:
    exclusions = scenario.get("exclusions") or [scenario.get("none_observed_rationale")]
    return "; ".join((
        f"type={scenario['semantic_type']}", f"gate={scenario['result']}/{scenario['confidence']}/{scenario['reason_code']}",
        f"source_instance={scenario['source_instance']}", f"statement={scenario['statement']}",
        f"applicability={scenario['applicability']}", f"exclusions={' | '.join(str(value) for value in exclusions)}",
        f"evidence={scenario['evidence_locator']}", f"counterexample={scenario['counterexample_result']}@{scenario['counterexample_locator']}",
        f"rationale={scenario['rationale']}",
    ))


def _expect_invalid(root: ET.Element, expected: str) -> None:
    try: validate_document(root, verify_current_filesystem=False)
    except ValidationError as error:
        if expected not in str(error): raise AssertionError(f"expected {expected!r}, got {error!r}") from error
    else: raise AssertionError(f"expected failure containing {expected!r}")


def self_test() -> None:
    fixture_dir = Path(__file__).resolve().parent.parent / "fixtures" / "plan-directory-intake"
    terminal = ET.parse(fixture_dir / "valid-plan-knowledge-run.xml").getroot(); proposed = ET.parse(fixture_dir / "valid-proposed-plan-knowledge-run.xml").getroot()
    validate_document(_clone(terminal), verify_current_filesystem=False); validate_document(_clone(proposed), verify_current_filesystem=False)
    _expect_invalid(ET.parse(fixture_dir / "invalid-candidate-v1.xml").getroot(), "candidate v1")

    scenario_rows: list[dict[str, object]] = []

    def observe_valid(scenario: dict[str, object], document: ET.Element) -> None:
        validate_document(document, verify_current_filesystem=False)
        candidate = document.find("./candidates/continuous_improvement_candidate"); assert candidate is not None
        observed = candidate.find("semantic_abstraction_gate").get("result")
        expected = str(scenario["result"]); status = "pass" if observed == expected else "material-false-positive"
        scenario_rows.append({"scenario_id": scenario["scenario_id"], "isolated_input_summary": _scenario_input_summary(scenario), "expected_result": expected, "observed_result": observed, "status": status, "evidence_ref": f"validator-self-test#scenario:{scenario['scenario_id']}"})
        if status != "pass": raise AssertionError(f"scenario {scenario['scenario_id']} expected {expected}, observed {observed}")

    def observe_invalid(scenario: dict[str, object], document: ET.Element, expected_error: str) -> None:
        try: validate_document(document, verify_current_filesystem=False)
        except ValidationError as error:
            observed = "rejected" if expected_error in str(error) else f"unexpected-rejection:{error}"
        else: observed = "accepted"
        status = "pass" if observed == "rejected" else "material-false-positive"
        scenario_rows.append({"scenario_id": scenario["scenario_id"], "isolated_input_summary": _scenario_input_summary(scenario), "expected_result": "rejected", "observed_result": observed, "status": status, "evidence_ref": f"validator-self-test#scenario:{scenario['scenario_id']}"})
        if status != "pass": raise AssertionError(f"scenario {scenario['scenario_id']} expected rejection, observed {observed}")

    generalized_definitions = (
        ("generalized-architecture", "architecture", "The current workflow forms candidates before validating semantic abstraction.", "Candidate formation must validate semantic abstraction after lineage and before target state.", "A workflow materializes a candidate from reconciled evidence.", "Runtime implementation details remain outside the orchestration boundary."),
        ("generalized-convention", "convention", "Map022 names and coordinates were embedded in a reusable statement.", "Reusable candidate statements retain concrete identities only in source instances.", "A candidate statement mixes a reusable rule with concrete identifiers.", "Canon and explicit local decisions remain local."),
        ("generalized-runtime-contract-map022", "runtime-contract", "Map022 child events move from exact coordinates during a cutscene.", "Cutscene event movement must preserve destination, facing, and terminal state.", "A cutscene moves configured events to observable destinations.", "Map identity, participant identity, and coordinates remain configuration."),
        ("generalized-state-or-data-contract", "state-or-data-contract", "One approved candidate changed its semantic gate after approval.", "Candidate intent identity must include the complete canonical semantic abstraction gate.", "A candidate approval binds an immutable intent digest.", "Mutable candidate digest and validation evidence remain separate bindings."),
        ("generalized-validation-pattern", "validation-pattern", "A validator accepted one structurally incomplete semantic gate.", "Semantic gate validation must reject unknown shape, stale binding, and invalid transitions.", "A candidate v2 contains a semantic abstraction gate.", "Semantic truth and perceptible runtime behavior remain human-validated."),
        ("generalized-prevention", "prevention", "Instance-bound candidates repeatedly lost their reusable invariant.", "Require semantic abstraction before candidate formation to prevent instance-bound promotion.", "Reconciled evidence contains both concrete configuration and a reusable mechanism.", "Cases without sufficient evidence remain local or blocked."),
    )
    for scenario_id, semantic_type, source_instance, statement, applicability, exclusion in generalized_definitions:
        scenario = {"scenario_id": scenario_id, "semantic_type": semantic_type, "result": "generalized", "confidence": "high", "reason_code": "reusable-invariant", "source_locator": f"analysis.md#{scenario_id}-source", "source_instance": source_instance, "statement": statement, "applicability": applicability, "exclusions": [exclusion], "evidence_locator": f"analysis.md#{scenario_id}-evidence", "counterexample_result": "bounded", "counterexample_locator": f"analysis.md#{scenario_id}-counterexample", "rationale": "The reusable statement preserves the observed boundary without widening root, writer, target, action, or authority."}
        case = _clone(terminal); candidate = _terminal_package(case); _apply_abstraction_scenario(candidate, scenario)
        if semantic_type == "prevention":
            unit = candidate.find("durable_knowledge_unit"); assert unit is not None
            candidate.insert(list(candidate).index(unit) + 1, ET.Element("root_cause", {"problem": "instance-bound promotion", "cause": "missing abstraction gate", "prevention": "validate abstraction before candidate formation"}))
        _refresh_candidate_bindings(case, candidate); observe_valid(scenario, case)

    proposed_scenario = {"scenario_id": "generalized-medium-bounded-proposed", "semantic_type": "validation-pattern", "result": "generalized", "confidence": "medium", "reason_code": "reusable-invariant", "source_locator": "analysis.md#candidate-case", "source_instance": "The concrete case validates one package capability at an exact target.", "statement": "Validate reusable package capabilities through their current command contracts.", "applicability": "A package capability has a current command contract and deterministic validator.", "exclusions": ["Target paths and capability identities remain candidate-specific configuration."], "evidence_locator": "analysis.md#candidate-case", "counterexample_result": "bounded", "counterexample_locator": "analysis.md#candidate-boundary", "rationale": "The reusable validation rule preserves target-specific evidence without widening the approved package envelope."}
    observe_valid(proposed_scenario, _clone(proposed))

    variation_definitions = (
        ("generalized-identity-variation", "Map031 participants move from different coordinates while the cutscene contract remains unchanged.", "Cutscene event movement must preserve destination, facing, and terminal state.", "A cutscene moves configured events to observable destinations."),
        ("generalized-condition-variation", "Map022 events move during a scripted sequence.", "Cutscene event movement must preserve destination, facing, and terminal state.", "A scripted sequence moves configured events and retains its terminal contract."),
        ("generalized-mechanism-variation", "A scripted event route moves configured participants without changing their terminal contract.", "Scripted event movement must preserve destination, facing, and terminal state.", "A scripted sequence moves configured events to observable destinations."),
    )
    for scenario_id, source_instance, statement, applicability in variation_definitions:
        scenario = {"scenario_id": scenario_id, "semantic_type": "runtime-contract", "result": "generalized", "confidence": "high", "reason_code": "reusable-invariant", "source_locator": f"analysis.md#{scenario_id}-source", "source_instance": source_instance, "statement": statement, "applicability": applicability, "exclusions": ["Concrete identities and coordinates remain source configuration."], "evidence_locator": f"analysis.md#{scenario_id}-evidence", "counterexample_result": "bounded", "counterexample_locator": f"analysis.md#{scenario_id}-counterexample", "rationale": "The changed dimension preserves the reusable mechanism and its authority boundary."}
        case = _clone(terminal); candidate = _terminal_package(case); _apply_abstraction_scenario(candidate, scenario); _refresh_candidate_bindings(case, candidate); observe_valid(scenario, case)

    local_scenarios = (
        {"scenario_id": "local-content-or-canon", "semantic_type": "content-or-canon", "result": "local-with-rationale", "confidence": "not-applicable", "reason_code": "content-or-canon", "source_instance": "Map022 uses a canonically fixed mural coordinate in this scene.", "statement": "Map022 keeps the canonically fixed mural coordinate for this scene.", "applicability": "The authored scene is Map022 and the coordinate is part of approved canon.", "exclusions": ["Other maps and non-canonical coordinates are outside this local statement."], "counterexample_result": "none-observed", "rationale": "The canonical identity is material evidence and cannot become a cross-map rule."},
        {"scenario_id": "local-explicit-human-decision", "semantic_type": "human-decision", "result": "local-with-rationale", "confidence": "not-applicable", "reason_code": "explicitly-local-human-decision", "source_instance": "The approver explicitly limited the timing rule to the Map022 cutscene.", "statement": "Apply the approved timing rule only to the Map022 cutscene.", "applicability": "The current target implements the explicitly scoped Map022 decision.", "exclusions": ["Other cutscenes require a separate human decision."], "counterexample_result": "none-observed", "rationale": "The explicit human scope is authoritative and cannot be inferred more broadly."},
        {"scenario_id": "local-deliberate-exception", "semantic_type": "convention", "result": "local-with-rationale", "confidence": "not-applicable", "reason_code": "deliberate-exception", "source_instance": "Map022 deliberately reverses the normal facing rule for a reveal shot.", "statement": "Map022 preserves the deliberate reversed-facing reveal shot.", "applicability": "The event is the approved Map022 reveal shot.", "exclusions": ["Normal cutscene movement continues to use the standard facing rule."], "counterexample_result": "bounded", "rationale": "The intentional exception remains local instead of weakening the general convention."},
        {"scenario_id": "local-no-reusable-invariant", "semantic_type": "implemented-capability", "result": "local-with-rationale", "confidence": "not-applicable", "reason_code": "no-reusable-invariant", "source_instance": "One scene contains a unique one-time staging note with no repeated mechanism.", "statement": "Preserve the one-time staging note for this scene.", "applicability": "The exact scene is maintained or reviewed.", "exclusions": [], "none_observed_rationale": "The bounded evidence contains no second case from which to derive a reusable invariant.", "counterexample_result": "none-observed", "rationale": "The material local record remains recoverable without inventing a reusable rule."},
        {"scenario_id": "local-material-counterexample", "semantic_type": "validation-pattern", "result": "local-with-rationale", "confidence": "not-applicable", "reason_code": "material-counterexample", "source_instance": "The candidate rule works for map events but fails for picture-layer participants.", "statement": "Validate destination, facing, and terminal state for map-event cutscene movement.", "applicability": "The moved participant is a map event rather than a picture-layer participant.", "exclusions": ["Picture-layer participants use a different movement and terminal-state contract."], "counterexample_result": "material-observed", "rationale": "The material counterexample determines a safe local boundary and prevents broader generalization."},
    )
    for raw in local_scenarios:
        scenario = {**raw, "source_locator": f"analysis.md#{raw['scenario_id']}-source", "evidence_locator": f"analysis.md#{raw['scenario_id']}-evidence", "counterexample_locator": f"analysis.md#{raw['scenario_id']}-counterexample"}
        case = _clone(terminal); candidate = _terminal_package(case); _apply_abstraction_scenario(candidate, scenario); _refresh_candidate_bindings(case, candidate); observe_valid(scenario, case)

    blocking_scenarios = (
        {"scenario_id": "blocked-insufficient-evidence", "reason_code": "insufficient-evidence", "counterexample_result": "inconclusive", "source_instance": "The record names Map022 but omits the movement mechanism and terminal condition.", "statement": "Determine whether the Map022 movement evidence supports a reusable contract.", "applicability": "A human reviews missing mechanism and terminal-state evidence.", "exclusions": [], "none_observed_rationale": "The evidence boundary is too incomplete to establish exclusions.", "rationale": "The missing mechanism prevents safe abstraction and requires blocking evidence."},
        {"scenario_id": "blocked-conflicting-scope", "reason_code": "conflicting-scope", "counterexample_result": "inconclusive", "source_instance": "Two approved records assign the same movement rule to incompatible participant scopes.", "statement": "Resolve the conflicting participant scope before forming a reusable movement contract.", "applicability": "Authoritative evidence assigns incompatible scopes to the same candidate rule.", "exclusions": ["Neither conflicting scope may be discarded to save generalization."], "rationale": "Conflicting scope remains visible and requires a specific human decision."},
        {"scenario_id": "blocked-material-counterexample", "reason_code": "material-counterexample-needs-human", "counterexample_result": "material-observed", "source_instance": "A picture-layer counterexample conflicts with the proposed cross-participant movement rule.", "statement": "Resolve whether picture-layer movement belongs to the proposed participant contract.", "applicability": "The candidate evidence includes both map-event and picture-layer movement.", "exclusions": ["The picture-layer counterexample cannot be classified without human scope authority."], "rationale": "The material counterexample is preserved and blocks promotion until scope is decided."},
    )
    for raw in blocking_scenarios:
        scenario = {**raw, "semantic_type": "validation-pattern", "result": "blocked-ambiguous", "confidence": "low", "source_locator": f"analysis.md#{raw['scenario_id']}-source", "evidence_locator": f"analysis.md#{raw['scenario_id']}-evidence", "counterexample_locator": f"analysis.md#{raw['scenario_id']}-counterexample"}
        case = _blocked_abstraction_case(terminal, str(scenario["reason_code"]), str(scenario["counterexample_result"])); candidate = _terminal_package(case); _apply_abstraction_scenario(candidate, scenario); _refresh_candidate_bindings(case, candidate); observe_valid(scenario, case)

    local_by_id = {str(item["scenario_id"]): item for item in local_scenarios}
    for scenario_id, local_id, expected_error, preserve_reason in (
        ("reject-generalized-canon", "local-content-or-canon", "requires eligible semantic type", False),
        ("reject-generalized-explicit-local-decision", "local-explicit-human-decision", "requires eligible semantic type", False),
        ("reject-generalized-deliberate-exception", "local-deliberate-exception", "result, confidence or reason code invalid", True),
    ):
        raw = local_by_id[local_id]; scenario = {**raw, "scenario_id": scenario_id, "source_locator": f"analysis.md#{scenario_id}-source", "evidence_locator": f"analysis.md#{scenario_id}-evidence", "counterexample_locator": f"analysis.md#{scenario_id}-counterexample"}
        case = _clone(terminal); candidate = _terminal_package(case); _apply_abstraction_scenario(candidate, scenario); gate = candidate.find("semantic_abstraction_gate"); assert gate is not None
        gate.set("result", "generalized"); gate.set("generalization_confidence", "high")
        if not preserve_reason: gate.set("reason_code", "reusable-invariant")
        scenario["result"] = "generalized"; scenario["confidence"] = "high"; scenario["reason_code"] = gate.get("reason_code")
        _refresh_candidate_bindings(case, candidate); observe_invalid(scenario, case, expected_error)

    cases: list[tuple[ET.Element, str]] = []
    case = _clone(terminal); case.find("run_state").set("status", "proposed"); cases.append((case, "coverage lifecycle"))
    case = _clone(terminal); case.find("./candidates/continuous_improvement_candidate").set("intent_digest", "sha256:" + "0" * 64); cases.append((case, "intent digest"))
    case = _clone(terminal); case.find("./approvals/envelope").set("target", "other.md"); cases.append((case, "approval immutable"))
    case = _clone(terminal); case.find("./plan_knowledge_coverage/source_coverage").set("material_unread", "1"); cases.append((case, "derived from ledger"))
    case = _clone(terminal); case.find("./candidates/continuous_improvement_candidate/source_lineage/evidence_ref").set("locator", "generated.txt"); cases.append((case, "provenance invalid"))
    case = _clone(terminal); ET.SubElement(case.find("knowledge_digest"), "digester_output"); cases.append((case, "unknown elements"))
    case = _clone(terminal); case.find("knowledge_digest").text = "mixed"; cases.append((case, "non-whitespace text"))
    case = _clone(terminal); case.find("./plan_knowledge_coverage/recoverability/question/expected_claim").text = ""; cases.append((case, "explicit text"))
    case = _clone(terminal); del case.find("./file_processing_ledger/file_result[@disposition='digested']").attrib["batch_id"]; cases.append((case, "missing attributes"))
    case = _clone(terminal); del case.find("./file_processing_ledger/file_result[@disposition='digested']").attrib["result_ref"]; cases.append((case, "missing attributes"))
    case = _clone(terminal); del case.find("./file_processing_ledger/file_result[@disposition='generated-noise']").attrib["rule_id"]; cases.append((case, "missing attributes"))
    case = _clone(terminal); del case.find("./file_processing_ledger/file_result[@disposition='generated-noise']").attrib["reason"]; cases.append((case, "missing attributes"))
    case = _clone(terminal); case.find("./candidates/continuous_improvement_candidate").set("material", "yes"); cases.append((case, "expected true or false"))
    case = _clone(terminal)
    analysis_result = case.find("./file_processing_ledger/file_result[@path='analysis.md']"); copy_result = case.find("./file_processing_ledger/file_result[@path='copy.md']")
    analysis_result.attrib = {"path": "analysis.md", "disposition": "duplicate", "duplicate_of": "copy.md"}; copy_result.attrib = {"path": "copy.md", "disposition": "digested", "batch_id": "batch-1", "result_ref": "digest-1"}
    cases.append((case, "lexicographically smallest group leader"))
    case = _clone(terminal); manifest = case.find("source_manifest"); files = manifest.find("files"); ledger = case.find("file_processing_ledger")
    ET.SubElement(files, "file", {"path": "third.md", "sha256": "sha256:" + "b" * 64, "size": "20", "initial_family": "recognized-text", "safety": "eligible"})
    ET.SubElement(ledger, "file_result", {"path": "third.md", "disposition": "duplicate", "duplicate_of": "copy.md"})
    manifest.find("totals").set("discovered_files", "4"); manifest.find("totals").set("discovered_bytes", "62"); manifest.set("source_tree_digest", _manifest_digest(manifest.findall("./files/file")))
    case.find("run_state").set("source_tree_digest", manifest.get("source_tree_digest")); source_coverage = case.find("./plan_knowledge_coverage/source_coverage"); source_coverage.set("manifest_files", "4"); source_coverage.set("ledger_files", "4")
    cases.append((case, "lexicographically smallest group leader"))
    for tag in ("candidates", "approvals", "plan_knowledge_coverage"):
        case = _clone(terminal); case.find(tag).set("schema_version", "2"); cases.append((case, "version invalid"))
    for locator in ("./candidates/continuous_improvement_candidate/intended_change", "./candidates/continuous_improvement_candidate/durable_knowledge_unit/statement", "./candidates/continuous_improvement_candidate/durable_knowledge_unit/use_when", "./plan_knowledge_coverage/recoverability/question/question_text", "./plan_knowledge_coverage/recoverability/question/expected_claim"):
        case = _clone(terminal); case.find(locator).set("unknown", "forbidden"); cases.append((case, "unknown attributes"))
    case = _clone(terminal); recovery = case.find("./plan_knowledge_coverage/recoverability"); recovery.append(copy.deepcopy(recovery.findall("question")[0])); cases.append((case, "question ids"))
    case = _clone(terminal); q = case.find("./plan_knowledge_coverage/recoverability/question"); q.append(copy.deepcopy(q.find("candidate_ref"))); cases.append((case, "question candidate refs"))

    # Current-only gate shape, transition, lineage and immutable-intent negatives.
    case = _clone(terminal); candidate = _terminal_package(case); candidate.remove(candidate.find("semantic_abstraction_gate")); cases.append((case, "requires one semantic abstraction gate"))
    case = _clone(terminal); candidate = _terminal_package(case); gate = candidate.find("semantic_abstraction_gate"); candidate.remove(gate); candidate.insert(0, gate); cases.append((case, "must immediately follow source lineage"))
    case = _clone(terminal); candidate = _terminal_package(case); candidate.insert(list(candidate).index(candidate.find("semantic_abstraction_gate")) + 1, copy.deepcopy(candidate.find("semantic_abstraction_gate"))); cases.append((case, "requires one semantic abstraction gate"))
    for attribute, value in (("result", "unknown"), ("generalization_confidence", "certain"), ("reason_code", "unknown")):
        case = _clone(terminal); candidate = _terminal_package(case); candidate.find("semantic_abstraction_gate").set(attribute, value); _refresh_candidate_bindings(case, candidate); cases.append((case, "result, confidence or reason code invalid"))
    case = _clone(terminal); candidate = _terminal_package(case); candidate.set("type", "implemented-capability"); _refresh_candidate_bindings(case, candidate); cases.append((case, "requires eligible semantic type"))
    case = _clone(terminal); candidate = _terminal_package(case); candidate.find("semantic_abstraction_gate/source_instances/source_instance").set("locator", "copy.md#other"); _refresh_candidate_bindings(case, candidate); cases.append((case, "source instance is outside source lineage"))
    case = _clone(terminal); candidate = _terminal_package(case); candidate.find("semantic_abstraction_gate/generalization_evidence/evidence_ref").set("locator", "copy.md"); _refresh_candidate_bindings(case, candidate); cases.append((case, "generalization evidence is outside source lineage"))
    case = _clone(terminal); candidate = _terminal_package(case); candidate.find("semantic_abstraction_gate/counterexample_check/evidence_ref").set("locator", "copy.md"); _refresh_candidate_bindings(case, candidate); cases.append((case, "counterexample evidence is outside source lineage"))
    case = _clone(terminal); candidate = _terminal_package(case); candidate.find("semantic_abstraction_gate/resulting_statement").text = "A different invariant."; _refresh_candidate_bindings(case, candidate); cases.append((case, "must exactly equal knowledge unit statement"))
    case = _clone(terminal); candidate = _terminal_package(case); statement = "analysis.md is not a valid reusable statement."; candidate.find("semantic_abstraction_gate/resulting_statement").text = statement; candidate.find("durable_knowledge_unit/statement").text = statement; _refresh_candidate_bindings(case, candidate); cases.append((case, "lineage locators are forbidden"))
    case = _clone(terminal); candidate = _terminal_package(case); exclusions = candidate.find("semantic_abstraction_gate/exclusions"); exclusions.clear(); exclusions.set("status", "observed"); _refresh_candidate_bindings(case, candidate); cases.append((case, "observed exclusions require"))
    case = _clone(terminal); candidate = _terminal_package(case); exclusions = candidate.find("semantic_abstraction_gate/exclusions"); exclusions.set("status", "none-observed"); exclusions.clear(); exclusions.set("status", "none-observed"); ET.SubElement(exclusions, "none_observed_rationale").text = "No exclusion appeared in the reviewed boundary."; _refresh_candidate_bindings(case, candidate); cases.append((case, "bounded counterexample requires observed exclusions"))
    case = _clone(terminal); candidate = _terminal_package(case); gate = candidate.find("semantic_abstraction_gate"); gate.set("result", "local-with-rationale"); gate.set("generalization_confidence", "not-applicable"); gate.set("reason_code", "content-or-canon"); gate.find("counterexample_check").set("result", "material-observed"); _refresh_candidate_bindings(case, candidate); cases.append((case, "local material counterexample binding invalid"))
    case = _clone(terminal); candidate = _terminal_package(case); gate = candidate.find("semantic_abstraction_gate"); gate.set("result", "blocked-ambiguous"); gate.set("generalization_confidence", "low"); gate.set("reason_code", "insufficient-evidence"); gate.find("counterexample_check").set("result", "inconclusive"); _refresh_candidate_bindings(case, candidate); cases.append((case, "blocked transition invalid"))
    case = _blocked_abstraction_case(terminal, "material-counterexample-needs-human", "inconclusive"); cases.append((case, "blocked counterexample reason invalid"))
    case = _clone(terminal); candidate = _terminal_package(case); gate = candidate.find("semantic_abstraction_gate"); ET.SubElement(gate, "unknown"); _refresh_candidate_bindings(case, candidate); cases.append((case, "unknown elements"))
    case = _clone(terminal); candidate = _terminal_package(case); candidate.find("semantic_abstraction_gate").set("target", "outside.md"); _refresh_candidate_bindings(case, candidate); cases.append((case, "unknown attributes"))
    case = _clone(terminal); candidate = _terminal_package(case); exclusions = candidate.find("semantic_abstraction_gate/exclusions"); ET.SubElement(exclusions, "none_observed_rationale").text = "This mixed form is forbidden."; _refresh_candidate_bindings(case, candidate); cases.append((case, "unknown elements"))
    case = _clone(terminal); candidate = _terminal_package(case); gate = candidate.find("semantic_abstraction_gate"); counterexample = gate.find("counterexample_check"); rationale = gate.find("rationale"); gate.remove(counterexample); gate.remove(rationale); gate.append(rationale); gate.append(counterexample); _refresh_candidate_bindings(case, candidate); cases.append((case, "child order or cardinality invalid"))
    case = _clone(terminal); candidate = _terminal_package(case); candidate.find("semantic_abstraction_gate/rationale").append(ET.Element("child")); _refresh_candidate_bindings(case, candidate); cases.append((case, "explicit text"))
    case = _blocked_abstraction_case(terminal, "insufficient-evidence", "inconclusive"); candidate = _terminal_package(case); candidate.find("residual_blockers").clear(); _refresh_candidate_bindings(case, candidate); cases.append((case, "requires blocking evidence and a material residual blocker"))
    case = _blocked_abstraction_case(terminal, "insufficient-evidence", "inconclusive"); candidate = _terminal_package(case); candidate.remove(candidate.find("blocked_evidence")); _refresh_candidate_bindings(case, candidate); cases.append((case, "requires blocking evidence and a material residual blocker"))
    case = _clone(terminal); candidate = _terminal_package(case); candidate.find("semantic_abstraction_gate/rationale").text = "Changed after approval without rebinding."; candidate.set("candidate_digest", _candidate_digest(candidate)); _refresh_canonical_digests(case); cases.append((case, "intent digest is stale"))
    for document, expected in cases:
        _refresh_canonical_digests(document)
        _expect_invalid(document, expected)

    false_candidate = _clone(terminal); candidates = false_candidate.find("candidates"); approvals = false_candidate.find("approvals")
    candidate = copy.deepcopy(candidates.find("continuous_improvement_candidate")); candidate.set("candidate_id", "candidate-nonmaterial"); candidate.set("material", "false")
    approval = candidate.find("approval"); approval.set("approval_id", "approval-nonmaterial"); candidate.set("intent_digest", _intent_digest(candidate, false_candidate.get("run_id", ""))); candidate.set("candidate_digest", _candidate_digest(candidate)); candidates.append(candidate)
    envelope = copy.deepcopy(approvals.find("envelope")); envelope.set("approval_id", "approval-nonmaterial"); envelope.set("candidate_id", "candidate-nonmaterial"); envelope.set("intent_digest", candidate.get("intent_digest")); approvals.append(envelope)
    _refresh_canonical_digests(false_candidate); validate_document(false_candidate, verify_current_filesystem=False)

    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary); plan = (base / "plan").resolve(); plan.mkdir(); (plan / "analysis.md").write_text("source\n")
        inventory_path = Path(__file__).resolve().parent / "inventory-plan-directory.py"; spec = importlib.util.spec_from_file_location("inventory_test", inventory_path); assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        live = _clone(terminal); live.set("run_id", "run-live"); run = live.find("run_state"); run.set("run_id", "run-live"); manifest = module.inventory(plan, "run-live")
        old = live.find("source_manifest"); index = list(live).index(old); live.remove(old); live.insert(index, manifest); run.set("source_tree_digest", manifest.get("source_tree_digest"))
        ledger = live.find("file_processing_ledger"); assert ledger is not None
        for result in list(ledger):
            if result.get("path") != "analysis.md": ledger.remove(result)
        source_coverage = live.find("./plan_knowledge_coverage/source_coverage"); assert source_coverage is not None
        source_coverage.set("manifest_files", "1"); source_coverage.set("ledger_files", "1")
        package = base / "package"; consumer = base / "consumer"; package.mkdir(); consumer.mkdir(); roots = {"package": package.resolve(), "consumer-docs": consumer.resolve()}
        for item in live.findall("./approved_roots/approved_root"): item.set("root", roots[item.get("destination_scope")].as_posix())
        for candidate in live.findall("./candidates/continuous_improvement_candidate"):
            candidate.set("root", roots[candidate.get("destination_scope")].as_posix()); candidate.set("intent_digest", _intent_digest(candidate, "run-live")); candidate.set("candidate_digest", _candidate_digest(candidate))
            env = live.find(f"./approvals/envelope[@candidate_id='{candidate.get('candidate_id')}']"); env.set("run_id", "run-live"); env.set("root", candidate.get("root")); env.set("intent_digest", candidate.get("intent_digest"))
            target = roots[candidate.get("destination_scope")] / candidate.get("target"); target.parent.mkdir(parents=True, exist_ok=True)
            state = candidate.find("target_after_state") if candidate.get("lifecycle") == "promoted" else candidate.find("target_before_state"); target.write_bytes(base64.b64decode((state.text or "").strip()))
        canonical = run.find("canonical_files")
        for ref in canonical.findall("file"): ref.set("sha256", _digest(_canonical_bytes(live.find(CANONICAL_FILES[ref.get("path")]))))
        run_dir = plan / "continuous-improvement" / "runs" / "run-live"; run_dir.mkdir(parents=True)
        (plan / "continuous-improvement" / "managed-namespace.xml").write_text('<continuous_improvement_namespace owner="loki-continuous-improvement" schema_version="1"></continuous_improvement_namespace>\n')
        (run_dir / "run-state.xml").write_bytes(_canonical_bytes(run))
        for name, tag in CANONICAL_FILES.items(): (run_dir / name).write_bytes(_canonical_bytes(live.find(tag)))
        validate_path(run_dir, roots, plan.resolve())
        external_run = base / "external" / "run-live"; shutil.copytree(run_dir, external_run)
        try: validate_path(external_run, roots, plan.resolve())
        except ValidationError as error: assert "lexically bound" in str(error)
        else: raise AssertionError("external run directory must fail")
        (run_dir / "coverage.xml").write_bytes((run_dir / "coverage.xml").read_bytes() + b" ")
        try: validate_path(run_dir, roots, plan.resolve())
        except ValidationError as error: assert "not canonical" in str(error)
        else: raise AssertionError("altered canonical bytes must fail")
        (run_dir / "coverage.xml").write_bytes(_canonical_bytes(live.find("plan_knowledge_coverage")))
        real_runs = base / "real-runs"; runs = plan / "continuous-improvement" / "runs"; runs.rename(real_runs); runs.symlink_to(real_runs, target_is_directory=True)
        try: validate_path(runs / "run-live", roots, plan.resolve())
        except ValidationError as error: assert "symlink component" in str(error)
        else: raise AssertionError("symlinked run ancestor must fail")
        runs.unlink(); real_runs.rename(runs); run_dir = runs / "run-live"
        coverage_path = run_dir / "coverage.xml"; coverage_alias = base / "coverage-alias.xml"; coverage_alias.write_bytes(coverage_path.read_bytes()); coverage_path.unlink(); coverage_path.symlink_to(coverage_alias)
        try: validate_path(run_dir, roots, plan.resolve())
        except ValidationError as error: assert "symlink component" in str(error)
        else: raise AssertionError("symlinked canonical file must fail")
        coverage_path.unlink(); coverage_path.write_bytes(coverage_alias.read_bytes())
        alias = package / "alias"; real = package / "real"; real.mkdir(); alias.symlink_to(real, target_is_directory=True)
        candidate = live.find("./candidates/continuous_improvement_candidate[@candidate_id='candidate-package']"); candidate.set("target", "alias/file.md"); candidate.set("intent_digest", _intent_digest(candidate, "run-live")); candidate.set("candidate_digest", _candidate_digest(candidate))
        try: _validate_current_target(candidate, roots["package"], _decode_state(candidate, "before"), _decode_state(candidate, "after"))
        except ValidationError as error: assert "symlink component" in str(error)
        else: raise AssertionError("parent symlink must fail")
    scenario_ids = [str(row["scenario_id"]) for row in scenario_rows]
    if len(scenario_rows) != 21 or len(set(scenario_ids)) != len(scenario_ids): raise AssertionError("semantic scenario matrix identity or cardinality invalid")
    material_false_positives = sum(row["status"] != "pass" for row in scenario_rows)
    matrix = {"semantic_abstraction_scenario_matrix": {"schema_version": 1, "scenario_count": len(scenario_rows), "material_false_positives": material_false_positives, "rows": scenario_rows}}
    print(json.dumps(matrix, sort_keys=True, separators=(",", ":")))
    print("validate-plan-knowledge-result self-test: pass")


def _parse_roots(values: list[str]) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for value in values:
        if "=" not in value: _fail("--approved-root requires SCOPE=PATH")
        scope, raw = value.split("=", 1)
        if scope not in DESTINATION_WRITERS or scope in roots or not raw: _fail("approved root scope unknown, duplicate or empty")
        roots[scope] = Path(raw)
    return roots


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("path", nargs="?", type=Path); parser.add_argument("--plan-directory", type=Path); parser.add_argument("--approved-root", action="append", default=[]); parser.add_argument("--fixture-schema-only", action="store_true"); parser.add_argument("--self-test", action="store_true"); return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test: self_test(); return 0
    if args.path is None: _fail("run directory or fixture XML path is required")
    if args.fixture_schema_only:
        fixture_root = Path(__file__).resolve().parent.parent / "fixtures" / "plan-directory-intake"; resolved = args.path.resolve(strict=True)
        try: resolved.relative_to(fixture_root.resolve(strict=True))
        except ValueError as error: raise ValidationError("fixture mode restricted to canonical package fixtures") from error
        if args.plan_directory is not None or args.approved_root: _fail("fixture mode forbids filesystem authority")
        validate_path(resolved, fixture=True)
    else:
        roots = _parse_roots(args.approved_root)
        if not roots or args.plan_directory is None: _fail("live validation requires --plan-directory and --approved-root")
        validate_path(args.path, roots, args.plan_directory)
    print(f"validate-plan-knowledge-result: pass: {args.path}"); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except (ValidationError, OSError, ET.ParseError) as error:
        print(f"validate-plan-knowledge-result: blocked: {error}", file=sys.stderr); raise SystemExit(2)
