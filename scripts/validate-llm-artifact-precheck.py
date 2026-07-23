#!/usr/bin/env python3
"""Validate the mechanical pre-audit packet for package LLM artifacts."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_VERSION = 1
CONTRACT_VERSION = "llm-artifact-quality-v1"
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
POSITIVE_REASONS = {
    "agent-facing",
    "instruction-bearing",
    "routing",
    "prompt-assembly",
    "context-hydration",
    "validation-contract",
}
LLM_TASKS = {"routing", "retrieval", "generation", "validation", "context-hydration"}
FIXTURE_IDS = (
    "LLM-Q-01-COLD-START-EXTRACTION",
    "LLM-Q-02-MISSING-MATERIAL-INPUT",
    "LLM-Q-03-INSTRUCTION-DATA-CONFLICT",
    "LLM-Q-04-SOURCE-PROJECTION-PARITY",
    "LLM-Q-05-PARAPHRASE-INVARIANCE",
    "LLM-Q-06-CRITICAL-SALIENCE",
    "LLM-Q-07-VERBOSITY-CONTROL",
    "LLM-Q-08-EXAMPLE-NORM-SEPARATION",
    "LLM-Q-09-NORMATIVE-UNCERTAINTY",
    "LLM-Q-10-NOMINAL-AND-BLOCKING-ROUTES",
)
PACKET_KEYS = {
    "schema_version",
    "writer_identity",
    "destination_scope",
    "approved_target_files",
    "observed_changed_files",
    "materiality",
    "artifact_profiles",
    "paired_projection_pairs",
    "intended_auditor",
}
PROFILE_KEYS = {
    "contract_version",
    "applicable",
    "reason",
    "not_applicable_reason",
    "artifact_class",
    "intended_llm_task",
    "authoritative_sections",
    "untrusted_data_sections",
    "source_priority",
    "paired_projections",
    "selected_fixture_ids",
    "skipped_fixture_ids",
}
FORBIDDEN_WRITER_KEYS = {
    "llm_consumption_quality",
    "approval",
    "approved",
    "audit_result",
    "auditor_result",
}
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def exact_keys(value: Any, expected: set[str], locator: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{locator}: expected object")
        return False
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{locator}: missing keys {missing}")
    if extra:
        errors.append(f"{locator}: unexpected keys {extra}")
    return not missing and not extra


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalized_path(value: Any) -> str | None:
    if not nonempty_string(value):
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) in {"", "."}:
        return None
    normalized = path.as_posix()
    return normalized if normalized == value else None


def actual_digest(path: str) -> str | None:
    resolved = (PACKAGE_ROOT / path).resolve()
    try:
        resolved.relative_to(PACKAGE_ROOT)
    except ValueError:
        return None
    if not resolved.is_file():
        return None
    return "sha256:" + hashlib.sha256(resolved.read_bytes()).hexdigest()


def package_file(path: str) -> Path | None:
    resolved = (PACKAGE_ROOT / path).resolve()
    try:
        resolved.relative_to(PACKAGE_ROOT)
    except ValueError:
        return None
    return resolved if resolved.is_file() else None


def nested_key_exists(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(nested_key_exists(child, key) for child in value.values())
    if isinstance(value, list):
        return any(nested_key_exists(child, key) for child in value)
    return False


def locator_resolves(value: str) -> tuple[bool, str]:
    if "#" not in value:
        return False, "locator must contain a supported fragment"
    path_value, fragment = value.rsplit("#", 1)
    path = normalized_path(path_value)
    target = package_file(path) if path else None
    if target is None:
        return False, "locator path does not resolve to a package file"
    try:
        text_value = target.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False, "locator target is not readable UTF-8"
    suffix = target.suffix.lower()
    if suffix in {".md", ".markdown"} and fragment.startswith("heading:"):
        heading = fragment.removeprefix("heading:")
        found = any(re.fullmatch(r"#{1,6}\s+" + re.escape(heading) + r"\s*", line) for line in text_value.splitlines())
        return found, "Markdown heading is absent"
    if suffix == ".py" and fragment.startswith("symbol:"):
        symbol = fragment.removeprefix("symbol:")
        try:
            tree = ast.parse(text_value)
        except SyntaxError:
            return False, "Python target does not parse"
        names = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        names.update(
            target.id
            for node in tree.body
            if isinstance(node, (ast.Assign, ast.AnnAssign))
            for target in ([node.target] if isinstance(node, ast.AnnAssign) else node.targets)
            if isinstance(target, ast.Name)
        )
        return symbol in names, "top-level Python symbol is absent"
    if suffix in {".json", ".yaml", ".yml", ".toml", ".xml"} and fragment.startswith("field:"):
        field = fragment.removeprefix("field:")
        try:
            if suffix == ".json":
                found = nested_key_exists(json.loads(text_value), field)
            elif suffix == ".toml":
                found = nested_key_exists(tomllib.loads(text_value), field)
            elif suffix == ".xml":
                root = ET.fromstring(text_value)
                found = root.tag == field or any(node.tag == field for node in root.iter())
            else:
                found = any(re.match(r"^\s*(?:-\s+)?" + re.escape(field) + r"\s*:", line) for line in text_value.splitlines())
        except (json.JSONDecodeError, tomllib.TOMLDecodeError, ET.ParseError):
            return False, "structured locator target does not parse"
        return found, "structured key/tag is absent"
    return False, "fragment kind is unsupported for the target type"


def validate_locators(value: Any, locator: str, errors: list[str], *, nonempty: bool) -> None:
    locators = validate_string_list(value, locator, errors, nonempty=nonempty)
    for index, item in enumerate(locators):
        resolved, reason = locator_resolves(item)
        if not resolved:
            errors.append(f"{locator}[{index}]: unresolved locator ({reason})")


def find_forbidden_keys(value: Any, locator: str = "packet") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_locator = f"{locator}.{key}"
            if key in FORBIDDEN_WRITER_KEYS:
                errors.append(f"{child_locator}: Writer-owned packet may not contain this key")
            errors.extend(find_forbidden_keys(child, child_locator))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(find_forbidden_keys(child, f"{locator}[{index}]"))
    return errors


def validate_string_list(value: Any, locator: str, errors: list[str], *, nonempty: bool) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        errors.append(f"{locator}: expected {'non-empty ' if nonempty else ''}list")
        return []
    result: list[str] = []
    for index, item in enumerate(value):
        if not nonempty_string(item):
            errors.append(f"{locator}[{index}]: expected non-empty string")
        else:
            result.append(item)
    if len(result) != len(set(result)):
        errors.append(f"{locator}: duplicate values")
    return result


def validate_pair(value: Any, locator: str, errors: list[str]) -> tuple[str, str] | None:
    if not exact_keys(value, {"source", "projection"}, locator, errors):
        return None
    source = normalized_path(value["source"])
    projection = normalized_path(value["projection"])
    if source is None:
        errors.append(f"{locator}.source: expected normalized package-relative path")
    if projection is None:
        errors.append(f"{locator}.projection: expected normalized package-relative path")
    if source == projection and source is not None:
        errors.append(f"{locator}: source and projection must differ")
    for field, path in (("source", source), ("projection", projection)):
        if path is not None and package_file(path) is None:
            errors.append(f"{locator}.{field}: path does not resolve to a package file")
    return (source, projection) if source and projection else None


def validate_profile(
    profile: Any,
    locator: str,
    declared_classification: Any,
    required_pairs: set[tuple[str, str]],
    errors: list[str],
) -> None:
    if not exact_keys(profile, PROFILE_KEYS, locator, errors):
        return
    if profile["contract_version"] != CONTRACT_VERSION:
        errors.append(f"{locator}.contract_version: expected {CONTRACT_VERSION}")
    applicable = profile["applicable"]
    if not isinstance(applicable, bool):
        errors.append(f"{locator}.applicable: expected boolean")
        return
    if declared_classification not in {"llm-facing", "human-only"}:
        errors.append(f"{locator}: classification must be llm-facing or human-only")
    elif applicable != (declared_classification == "llm-facing"):
        errors.append(f"{locator}: classification and applicable disagree")

    classes = validate_string_list(profile["artifact_class"], f"{locator}.artifact_class", errors, nonempty=applicable)
    unknown_classes = sorted(set(classes) - POSITIVE_REASONS)
    if unknown_classes:
        errors.append(f"{locator}.artifact_class: invalid values {unknown_classes}")

    reason = profile["reason"]
    if applicable:
        if reason not in POSITIVE_REASONS:
            errors.append(f"{locator}.reason: expected one positive canonical reason")
        elif reason not in classes:
            errors.append(f"{locator}.reason: primary reason absent from artifact_class")
        if profile["not_applicable_reason"] is not None:
            errors.append(f"{locator}.not_applicable_reason: expected null when applicable")
        if profile["intended_llm_task"] not in LLM_TASKS:
            errors.append(f"{locator}.intended_llm_task: invalid applicable task")
    else:
        if reason != "not-applicable":
            errors.append(f"{locator}.reason: expected not-applicable")
        if not nonempty_string(profile["not_applicable_reason"]):
            errors.append(f"{locator}.not_applicable_reason: concrete justification required")
        if classes:
            errors.append(f"{locator}.artifact_class: expected empty for human-only")
        if profile["intended_llm_task"] is not None:
            errors.append(f"{locator}.intended_llm_task: expected null for human-only")

    validate_locators(
        profile["authoritative_sections"],
        f"{locator}.authoritative_sections",
        errors,
        nonempty=applicable,
    )
    validate_locators(
        profile["untrusted_data_sections"],
        f"{locator}.untrusted_data_sections",
        errors,
        nonempty=False,
    )
    validate_string_list(
        profile["source_priority"],
        f"{locator}.source_priority",
        errors,
        nonempty=applicable,
    )

    profile_pairs: set[tuple[str, str]] = set()
    if not isinstance(profile["paired_projections"], list):
        errors.append(f"{locator}.paired_projections: expected list")
    else:
        for index, value in enumerate(profile["paired_projections"]):
            pair = validate_pair(value, f"{locator}.paired_projections[{index}]", errors)
            if pair:
                profile_pairs.add(pair)
        if len(profile_pairs) != len(profile["paired_projections"]):
            errors.append(f"{locator}.paired_projections: duplicate or invalid pair")
    missing_pairs = sorted(required_pairs - profile_pairs)
    if missing_pairs:
        errors.append(f"{locator}.paired_projections: missing declared pairs {missing_pairs}")

    selected = validate_string_list(
        profile["selected_fixture_ids"],
        f"{locator}.selected_fixture_ids",
        errors,
        nonempty=False,
    )
    skipped: list[str] = []
    if not isinstance(profile["skipped_fixture_ids"], list):
        errors.append(f"{locator}.skipped_fixture_ids: expected list")
    else:
        for index, item in enumerate(profile["skipped_fixture_ids"]):
            item_locator = f"{locator}.skipped_fixture_ids[{index}]"
            if not exact_keys(item, {"id", "reason"}, item_locator, errors):
                continue
            if not nonempty_string(item["id"]):
                errors.append(f"{item_locator}.id: expected non-empty string")
            else:
                skipped.append(item["id"])
            if not nonempty_string(item["reason"]):
                errors.append(f"{item_locator}.reason: specific reason required")
    combined = selected + skipped
    if len(combined) != len(set(combined)):
        errors.append(f"{locator}: fixture IDs are duplicated across selected/skipped")
    if set(combined) != set(FIXTURE_IDS) or len(combined) != len(FIXTURE_IDS):
        missing = sorted(set(FIXTURE_IDS) - set(combined))
        unknown = sorted(set(combined) - set(FIXTURE_IDS))
        errors.append(f"{locator}: fixture partition must contain exactly ten canonical IDs; missing={missing}, unknown={unknown}")
    if not applicable and selected:
        errors.append(f"{locator}.selected_fixture_ids: human-only profile must select none")


def validate_packet(document: Any) -> dict[str, Any]:
    errors: list[str] = find_forbidden_keys(document)
    if not exact_keys(document, {"llm_artifact_precheck_packet"}, "document", errors):
        return blocked(errors)
    packet = document.get("llm_artifact_precheck_packet")
    if not exact_keys(packet, PACKET_KEYS, "packet", errors):
        return blocked(errors)
    if packet["schema_version"] != SCHEMA_VERSION:
        errors.append("packet.schema_version: expected 1")
    writer = packet["writer_identity"]
    if not nonempty_string(writer):
        errors.append("packet.writer_identity: expected non-empty string")
    if packet["destination_scope"] != "package":
        errors.append("packet.destination_scope: expected package")

    approved_raw = packet["approved_target_files"]
    approved = validate_string_list(approved_raw, "packet.approved_target_files", errors, nonempty=True)
    for index, path in enumerate(approved):
        if normalized_path(path) is None:
            errors.append(f"packet.approved_target_files[{index}]: expected normalized package-relative path")
    approved_set = set(approved)

    observed = packet["observed_changed_files"]
    observed_records: list[dict[str, Any]] = []
    observed_paths: list[str] = []
    expected_observed_keys = {"path", "sha256", "added_lines", "removed_lines"}
    if not isinstance(observed, list):
        errors.append("packet.observed_changed_files: expected list")
    else:
        for index, item in enumerate(observed):
            locator = f"packet.observed_changed_files[{index}]"
            if not exact_keys(item, expected_observed_keys, locator, errors):
                continue
            path = normalized_path(item["path"])
            if path is None:
                errors.append(f"{locator}.path: expected normalized package-relative path")
                continue
            observed_paths.append(path)
            if path not in approved_set:
                errors.append(f"{locator}.path: outside approved_target_files")
            digest = item["sha256"]
            if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                errors.append(f"{locator}.sha256: expected sha256:<64 lowercase hex>")
            else:
                current = actual_digest(path)
                if current is None:
                    errors.append(f"{locator}.sha256: target does not resolve to a package file")
                elif current != digest:
                    errors.append(f"{locator}.sha256: does not match current package file")
            for count_key in ("added_lines", "removed_lines"):
                count = item[count_key]
                if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                    errors.append(f"{locator}.{count_key}: expected non-negative integer")
            if (
                isinstance(item["added_lines"], int)
                and isinstance(item["removed_lines"], int)
                and item["added_lines"] + item["removed_lines"] == 0
            ):
                errors.append(f"{locator}: observed changed file must contain a non-zero diff")
            observed_records.append(item)
    if len(observed_paths) != len(set(observed_paths)):
        errors.append("packet.observed_changed_files: duplicate paths")

    mechanically_material = bool(observed_records)
    materiality = packet["materiality"]
    if exact_keys(materiality, {"decision", "evidence"}, "packet.materiality", errors):
        expected_decision = "material" if mechanically_material else "no-material-write"
        if materiality["decision"] != expected_decision:
            errors.append(f"packet.materiality.decision: observed diffs require {expected_decision}")
        evidence = materiality["evidence"]
        if not isinstance(evidence, list):
            errors.append("packet.materiality.evidence: expected list")
        elif evidence != observed_records:
            errors.append("packet.materiality.evidence: must exactly reproduce observed diff records")

    top_pairs: set[tuple[str, str]] = set()
    pairs = packet["paired_projection_pairs"]
    if not isinstance(pairs, list):
        errors.append("packet.paired_projection_pairs: expected list")
    else:
        for index, item in enumerate(pairs):
            pair = validate_pair(item, f"packet.paired_projection_pairs[{index}]", errors)
            if pair:
                top_pairs.add(pair)
        if len(top_pairs) != len(pairs):
            errors.append("packet.paired_projection_pairs: duplicate or invalid pair")

    profiles = packet["artifact_profiles"]
    profiled_paths: list[str] = []
    if not isinstance(profiles, list):
        errors.append("packet.artifact_profiles: expected list")
    else:
        for index, item in enumerate(profiles):
            locator = f"packet.artifact_profiles[{index}]"
            if not exact_keys(item, {"artifact_path", "classification", "llm_artifact_profile"}, locator, errors):
                continue
            path = normalized_path(item["artifact_path"])
            if path is None:
                errors.append(f"{locator}.artifact_path: expected normalized package-relative path")
                continue
            profiled_paths.append(path)
            if path not in observed_paths:
                errors.append(f"{locator}.artifact_path: profile has no observed material diff")
            required_pairs = {pair for pair in top_pairs if path in pair}
            validate_profile(
                item["llm_artifact_profile"],
                f"{locator}.llm_artifact_profile",
                item["classification"],
                required_pairs,
                errors,
            )
    if len(profiled_paths) != len(set(profiled_paths)):
        errors.append("packet.artifact_profiles: duplicate artifact paths")
    if mechanically_material and set(profiled_paths) != set(observed_paths):
        missing = sorted(set(observed_paths) - set(profiled_paths))
        extra = sorted(set(profiled_paths) - set(observed_paths))
        errors.append(f"packet.artifact_profiles: must cover every material changed file; missing={missing}, extra={extra}")
    if not mechanically_material and profiles:
        errors.append("packet.artifact_profiles: no-material-write packet must not contain profiles")

    auditor = packet["intended_auditor"]
    if exact_keys(auditor, {"identity", "destination"}, "packet.intended_auditor", errors):
        if auditor["identity"] != "framework-artifact-quality-auditor":
            errors.append("packet.intended_auditor.identity: expected framework-artifact-quality-auditor")
        if auditor["destination"] != "framework-artifact-quality-auditor":
            errors.append("packet.intended_auditor.destination: expected framework-artifact-quality-auditor")
        if auditor["identity"] == writer:
            errors.append("packet.intended_auditor.identity: Auditor must be distinct from Writer")

    if errors:
        return blocked(errors)
    if not mechanically_material:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "skipped-no-material-write",
            "dispatch_allowed": False,
            "errors": [],
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready-for-auditor",
        "dispatch_allowed": True,
        "errors": [],
    }


def blocked(errors: list[str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "blocked-to-writer",
        "dispatch_allowed": False,
        "errors": sorted(set(errors)),
    }


def fixture_partition() -> tuple[list[str], list[dict[str, str]]]:
    return [FIXTURE_IDS[0]], [
        {"id": fixture_id, "reason": "Fixture condition does not apply to this self-test artifact."}
        for fixture_id in FIXTURE_IDS[1:]
    ]


def self_test() -> dict[str, Any]:
    selected, skipped = fixture_partition()
    with tempfile.NamedTemporaryFile(dir=PACKAGE_ROOT, prefix="llm-precheck-", suffix=".md") as handle:
        path = Path(handle.name).relative_to(PACKAGE_ROOT).as_posix()
        handle.write(b"# Self Test\n\nmaterial self-test\n")
        handle.flush()
        digest = actual_digest(path)
        observed = {"path": path, "sha256": digest, "added_lines": 3, "removed_lines": 0}
        profile = {
            "contract_version": CONTRACT_VERSION,
            "applicable": True,
            "reason": "validation-contract",
            "not_applicable_reason": None,
            "artifact_class": ["validation-contract"],
            "intended_llm_task": "validation",
            "authoritative_sections": [f"{path}#heading:Self Test"],
            "untrusted_data_sections": [],
            "source_priority": ["self-test packet"],
            "paired_projections": [],
            "selected_fixture_ids": selected,
            "skipped_fixture_ids": skipped,
        }
        base = {
            "llm_artifact_precheck_packet": {
                "schema_version": 1,
                "writer_identity": "framework-artifact-writer",
                "destination_scope": "package",
                "approved_target_files": [path],
                "observed_changed_files": [observed],
                "materiality": {"decision": "material", "evidence": [observed]},
                "artifact_profiles": [
                    {"artifact_path": path, "classification": "llm-facing", "llm_artifact_profile": profile}
                ],
                "paired_projection_pairs": [],
                "intended_auditor": {
                    "identity": "framework-artifact-quality-auditor",
                    "destination": "framework-artifact-quality-auditor",
                },
            }
        }
        cases: list[tuple[str, dict[str, Any], str]] = [("valid-material-profile", base, "ready-for-auditor")]
        cases.append(("missing-profile", json.loads(json.dumps(base)), "blocked-to-writer"))
        cases[-1][1]["llm_artifact_precheck_packet"]["artifact_profiles"] = []
        cases.append(("outside-approval", json.loads(json.dumps(base)), "blocked-to-writer"))
        cases[-1][1]["llm_artifact_precheck_packet"]["approved_target_files"] = ["unrelated.md"]
        no_material = json.loads(json.dumps(base))
        no_material["llm_artifact_precheck_packet"]["observed_changed_files"] = []
        no_material["llm_artifact_precheck_packet"]["materiality"] = {"decision": "no-material-write", "evidence": []}
        no_material["llm_artifact_precheck_packet"]["artifact_profiles"] = []
        cases.append(("no-material-write", no_material, "skipped-no-material-write"))
        self_audit = json.loads(json.dumps(base))
        self_audit["llm_artifact_precheck_packet"]["intended_auditor"]["identity"] = "framework-artifact-writer"
        self_audit["llm_artifact_precheck_packet"]["intended_auditor"]["destination"] = "framework-artifact-writer"
        self_audit["llm_artifact_precheck_packet"]["artifact_profiles"][0]["llm_artifact_profile"][
            "llm_consumption_quality"
        ] = {}
        cases.append(("writer-self-audit", self_audit, "blocked-to-writer"))
        bad_locator = json.loads(json.dumps(base))
        bad_locator["llm_artifact_precheck_packet"]["artifact_profiles"][0]["llm_artifact_profile"][
            "authoritative_sections"
        ] = [f"{path}#synthetic-fragment"]
        cases.append(("unresolved-profile-locator", bad_locator, "blocked-to-writer"))

        results = []
        for name, packet, expected in cases:
            actual = validate_packet(packet)["status"]
            if actual != expected:
                raise AssertionError(f"{name}: expected {expected}, received {actual}")
            results.append({"case": name, "status": actual})
    return {"self_test": "passed", "schema_version": SCHEMA_VERSION, "cases": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--packet", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return 0
    try:
        document = json.loads(args.packet.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = blocked([f"packet input: {exc}"])
    else:
        result = validate_packet(document)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] != "blocked-to-writer" else 1


if __name__ == "__main__":
    sys.exit(main())
