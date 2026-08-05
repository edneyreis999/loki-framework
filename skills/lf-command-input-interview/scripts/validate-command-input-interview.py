#!/usr/bin/env python3
"""Deterministically validate structured command-input fixtures and package adoption."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


CONTRACT_VERSION = "command-input-interview-v1"
FIXTURE_VERSION = "command-input-interview-fixtures-v1"
EXPECTED_COMMANDS = (
    "loki-abrir-pr", "loki-catalogar-docs", "loki-commit",
    "loki-continuous-improvement", "loki-criar-branch", "loki-deep-research",
    "loki-demand-text-improver", "loki-enrich-tasks", "loki-feedback",
    "loki-human-decision-preflight", "loki-implement-feature", "loki-init",
    "loki-knowledge-extraction-analysis", "loki-manual-qa",
    "loki-retrospectiva-tecnica", "loki-self-healing", "loki-tech-analysis",
)
EXPECTED_CASE_IDS = (
    "INTAKE-01-READY-FOR-EXECUTION",
    "INTAKE-02-RESUMED-APPROVE",
    "INTAKE-03-RESUMED-ALTER",
    "INTAKE-04-RESUMED-CANCEL",
    "INTAKE-05-RESUMED-ABSENT-ACTION",
    "INTAKE-06-STRUCTURED-ADAPTER-LIMIT",
    "INTAKE-07-FREE-FORM-FALLBACK",
    "INTAKE-08-PROVIDED-DISCOVERED-CONFLICT",
    "INTAKE-09-SERIAL-DEPENDENCY",
    "INTAKE-10-SENSITIVE-GATE-PRESERVED",
    "INTAKE-11-MATERIAL-GATE-PRESERVED",
    "INTAKE-12-CANCELLED-DASHBOARD-COHERENCE",
    "INTAKE-13-NONINTERACTIVE-FIRST-REVIEW",
    "INTAKE-14-CONSUMED-ACTION-REPLAY-REJECTED",
    "INTAKE-15-NO-GROUNDED-RECOMMENDATION-FALLBACK",
)
CASE_KEYS = {"id", "input", "expected_output"}
INPUT_KEYS = {
    "command_name", "parameter_schema_digest", "command_contract_locator",
    "prior_envelope_digest",
    "invocation_mode", "is_resume", "envelope_state", "required_valid",
    "ambiguities_resolved", "optional_review_complete", "resume_action",
    "interaction_mode", "question_count", "questions_independent",
    "serial_dependency_satisfied", "question", "command_gates",
    "resume_request_id", "consumed_actions",
}
OUTPUT_KEYS = {
    "state", "transition", "review_reshown", "available_actions",
    "action_consumed", "question_delivery", "grouped_question_count",
    "ambiguity_required", "resumption_condition", "command_gate_disposition",
    "workspace_write",
}
QUESTION_KEYS = {
    "question_id", "prompt", "choices", "allow_client_free_form",
    "free_form_validation", "adapter_constraints",
}
CHOICE_KEYS = {
    "value", "label", "description", "recommended", "recommendation_reason",
}
CONSTRAINT_KEYS = {
    "capability_locator", "max_questions_per_request",
    "max_choices_per_question", "grouping",
    "recommendation_required_by_client",
}
ACTION_KEYS = {"action_id", "action_fingerprint", "name", "alterations"}
ALTERATION_KEYS = {"key", "value", "provenance"}
CONSUMED_ACTION_KEYS = {"resume_request_id", "action_id", "action_fingerprint"}
GATE_KEYS = {
    "gate_id", "gate_kind", "state", "authority_locator",
    "validation_locator", "resumption_condition",
}
GATE_KINDS = {
    "approval", "human-validation", "sensitive-write", "material",
    "command-specific",
}
QUESTION_ID_RE = re.compile(
    r"^intake\.[a-z0-9][a-z0-9-]*\.[A-Za-z_][A-Za-z0-9_]*\."
    r"(?:required|ambiguity|alter|review-action)$"
)
PLAN_AS_INTAKE_RE = re.compile(
    r"(?:enter|entre no)\s+(?:the\s+)?(?:modo\s+)?plan(?:\s+mode)?\s+(?:and|e)\s+"
    r"(?:request|pe[cç]a|solicite)", re.IGNORECASE,
)


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load JSON {path}: {exc}") from exc


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_exact_keys(value: Any, keys: set[str], locator: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{locator}: keys must be exactly {sorted(keys)}")
    return value


def validate_action(value: Any) -> str | None:
    if value is None:
        return None
    action = require_exact_keys(value, ACTION_KEYS, "resume_action")
    name = action["name"]
    if name is None:
        if action["action_id"] is not None or action["action_fingerprint"] is not None or action["alterations"] != []:
            raise ValueError("null action requires null identity and empty alterations")
        return None
    if name not in {"approve", "alter", "cancel"}:
        raise ValueError("resume_action.name must be approve, alter, cancel, or absent")
    if not nonempty(action["action_id"]):
        raise ValueError("non-null action requires action_id")
    if not isinstance(action["action_fingerprint"], str) or not re.fullmatch(
        r"sha256:[0-9a-f]{64}", action["action_fingerprint"]
    ):
        raise ValueError("non-null action requires current action_fingerprint")
    alterations = action["alterations"]
    if not isinstance(alterations, list):
        raise ValueError("resume_action.alterations must be a list")
    keys: list[str] = []
    for index, item in enumerate(alterations):
        record = require_exact_keys(item, ALTERATION_KEYS, f"alterations[{index}]")
        if not nonempty(record["key"]) or not nonempty(record["provenance"]):
            raise ValueError(f"alterations[{index}] requires key and provenance")
        keys.append(record["key"])
    if len(keys) != len(set(keys)):
        raise ValueError("alteration keys must be unique")
    if name == "alter" and not alterations:
        raise ValueError("alter requires at least one alteration")
    if name != "alter" and alterations:
        raise ValueError("approve and cancel require empty alterations")
    return name


def derive_action_fingerprint(item: dict[str, Any], action: dict[str, Any]) -> str:
    """Derive the semantic action identity from current request authority fields."""
    canonical_alterations = sorted(action["alterations"], key=lambda record: record["key"])
    payload = {
        "command_name": item["command_name"],
        "parameter_schema_digest": item["parameter_schema_digest"],
        "command_contract_locator": item["command_contract_locator"],
        "prior_envelope_digest": item["prior_envelope_digest"],
        "name": action["name"],
        "alterations": canonical_alterations,
    }
    try:
        canonical_json = json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"review action cannot be canonicalized: {exc}") from exc
    return "sha256:" + hashlib.sha256(canonical_json).hexdigest()


def validate_question(value: Any, mode: str, count: int) -> tuple[str, int]:
    if count == 0:
        if value is not None or mode != "none":
            raise ValueError("zero questions require interaction_mode none and question null")
        return "none", 0
    if mode not in {"structured", "free-form"}:
        raise ValueError("positive question_count requires structured or free-form mode")
    question = require_exact_keys(value, QUESTION_KEYS, "question")
    if not QUESTION_ID_RE.fullmatch(str(question["question_id"])):
        raise ValueError("question.question_id is not stable")
    if not nonempty(question["prompt"]) or not nonempty(question["free_form_validation"]):
        raise ValueError("question prompt and free-form validation must be non-empty")
    if question["allow_client_free_form"] is not True:
        raise ValueError("client free-form answers must remain enabled")
    constraints = require_exact_keys(
        question["adapter_constraints"], CONSTRAINT_KEYS, "adapter_constraints"
    )
    if not nonempty(constraints["capability_locator"]):
        raise ValueError("adapter capability locator must be non-empty")
    for key in ("max_questions_per_request", "max_choices_per_question"):
        if not isinstance(constraints[key], int) or isinstance(constraints[key], bool) or constraints[key] < 1:
            raise ValueError(f"adapter_constraints.{key} must be a positive integer")
    if constraints["grouping"] != "independent-only":
        raise ValueError("structured grouping must be independent-only")
    if not isinstance(constraints["recommendation_required_by_client"], bool):
        raise ValueError("recommendation_required_by_client must be boolean")
    choices = question["choices"]
    if not isinstance(choices, list) or len(choices) < 2:
        raise ValueError("question requires at least two mutually exclusive choices")
    if len(choices) > constraints["max_choices_per_question"]:
        raise ValueError("choices exceed the observed adapter limit")
    values: list[str] = []
    labels: list[str] = []
    recommended = 0
    for index, item in enumerate(choices):
        choice = require_exact_keys(item, CHOICE_KEYS, f"choices[{index}]")
        if not all(nonempty(choice[key]) for key in ("value", "label", "description")):
            raise ValueError(f"choices[{index}] requires value, label, and description")
        values.append(choice["value"])
        labels.append(choice["label"])
        if not isinstance(choice["recommended"], bool):
            raise ValueError(f"choices[{index}].recommended must be boolean")
        if choice["recommended"]:
            recommended += 1
            if not nonempty(choice["recommendation_reason"]):
                raise ValueError("recommended choice requires a justified reason")
        elif choice["recommendation_reason"] is not None:
            raise ValueError("non-recommended choice requires null recommendation_reason")
    if len(values) != len(set(values)) or len(labels) != len(set(labels)):
        raise ValueError("choice values and labels must be mutually exclusive and unique")
    if recommended > 1:
        raise ValueError("at most one choice may carry a justified recommendation")
    if recommended == 0 and constraints["recommendation_required_by_client"] and mode == "structured":
        raise ValueError("client-required recommendation without grounding requires textual fallback")
    limit = constraints["max_questions_per_request"]
    return mode, 1 if mode == "free-form" else min(count, limit)


def validate_gates(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("command_gates must be a list")
    gates: list[dict[str, Any]] = []
    ids: list[str] = []
    for index, item in enumerate(value):
        gate = require_exact_keys(item, GATE_KEYS, f"command_gates[{index}]")
        if gate["gate_kind"] not in GATE_KINDS or gate["state"] not in {"pending", "satisfied"}:
            raise ValueError(f"command_gates[{index}] has invalid kind or state")
        if not all(nonempty(gate[key]) for key in (
            "gate_id", "authority_locator", "validation_locator", "resumption_condition"
        )):
            raise ValueError(f"command_gates[{index}] requires exact authority, validation, and resumption data")
        ids.append(gate["gate_id"])
        gates.append(gate)
    if len(ids) != len(set(ids)):
        raise ValueError("command gate IDs must be unique")
    return gates


def validate_consumed_actions(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError("consumed_actions must be a list")
    records: list[dict[str, str]] = []
    for index, item in enumerate(value):
        record = require_exact_keys(item, CONSUMED_ACTION_KEYS, f"consumed_actions[{index}]")
        if not all(nonempty(record[key]) for key in CONSUMED_ACTION_KEYS):
            raise ValueError(f"consumed_actions[{index}] requires request, action, and fingerprint identity")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", record["action_fingerprint"]):
            raise ValueError(f"consumed_actions[{index}] fingerprint is invalid")
        records.append(record)
    for key in CONSUMED_ACTION_KEYS:
        values = [record[key] for record in records]
        if len(values) != len(set(values)):
            raise ValueError(f"consumed action {key} values must be unique")
    return records


def evaluate_fixture_input(value: Any) -> dict[str, Any]:
    item = require_exact_keys(value, INPUT_KEYS, "input")
    if not isinstance(item["command_name"], str) or not re.fullmatch(
        r"loki-[a-z0-9][a-z0-9-]*", item["command_name"]
    ):
        raise ValueError("command_name must be a canonical Loki command name")
    for key in ("parameter_schema_digest", "prior_envelope_digest"):
        if not isinstance(item[key], str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", item[key]):
            raise ValueError(f"{key} must be a current SHA-256 digest")
    expected_locator = f"skills/{item['command_name']}/SKILL.md#heading:Input"
    if item["command_contract_locator"] != expected_locator:
        raise ValueError("command_contract_locator must resolve to the named command Input")
    if item["invocation_mode"] not in {"interactive", "non-interactive"}:
        raise ValueError("invalid invocation_mode")
    for key in (
        "is_resume", "required_valid", "ambiguities_resolved",
        "optional_review_complete", "questions_independent",
        "serial_dependency_satisfied",
    ):
        if not isinstance(item[key], bool):
            raise ValueError(f"{key} must be boolean")
    if not isinstance(item["question_count"], int) or isinstance(item["question_count"], bool) or item["question_count"] < 0:
        raise ValueError("question_count must be a non-negative integer")
    if item["is_resume"]:
        if item["envelope_state"] not in {"needs-input", "cancelled"}:
            raise ValueError("resume requires a needs-input or cancelled envelope")
    elif item["envelope_state"] is not None:
        raise ValueError("first invocation cannot carry envelope_state")
    action = validate_action(item["resume_action"])
    if action is not None:
        derived_fingerprint = derive_action_fingerprint(item, item["resume_action"])
        if item["resume_action"]["action_fingerprint"] != derived_fingerprint:
            raise ValueError("supplied action_fingerprint does not match the canonical action fingerprint")
    if item["is_resume"]:
        if not nonempty(item["resume_request_id"]):
            raise ValueError("resume requires resume_request_id")
    elif item["resume_request_id"] is not None:
        raise ValueError("first invocation requires null resume_request_id")
    consumed_actions = validate_consumed_actions(item["consumed_actions"])
    gates = validate_gates(item["command_gates"])
    delivery, grouped = validate_question(
        item["question"], item["interaction_mode"], item["question_count"]
    )
    if item["question_count"] and (
        not item["questions_independent"] or not item["serial_dependency_satisfied"]
    ):
        grouped = 1
    base = {
        "transition": None, "review_reshown": False, "available_actions": [],
        "action_consumed": None, "question_delivery": delivery,
        "grouped_question_count": grouped, "ambiguity_required": False,
        "command_gate_disposition": "preserved", "workspace_write": False,
    }
    if action is not None:
        action_record = item["resume_action"]
        replay = any(
            item["resume_request_id"] == record["resume_request_id"]
            or action_record["action_id"] == record["action_id"]
            or action_record["action_fingerprint"] == record["action_fingerprint"]
            for record in consumed_actions
        )
        if replay:
            return base | {
                "state": "rejected-replay",
                "resumption_condition": "reject-consumed-action",
            }
    if item["is_resume"] and item["envelope_state"] == "cancelled":
        if action is not None or item["question_count"] != 0:
            raise ValueError("cancelled envelope cannot accept actions or questions")
        return base | {
            "state": "cancelled", "resumption_condition": "cancelled-no-resume",
            "command_gate_disposition": "preserved-cancelled",
        }
    if item["invocation_mode"] == "non-interactive" and not item["is_resume"] and action is not None:
        raise ValueError("first non-interactive invocation cannot consume an action")
    if not item["required_valid"] or not item["serial_dependency_satisfied"]:
        if action is not None:
            raise ValueError("action cannot precede required inputs and dependencies")
        return base | {"state": "needs-input", "resumption_condition": "resolve-required"}
    if not item["ambiguities_resolved"]:
        if action is not None:
            raise ValueError("action cannot precede ambiguity resolution")
        return base | {
            "state": "needs-input", "ambiguity_required": True,
            "resumption_condition": "resolve-ambiguity",
        }
    if not item["optional_review_complete"]:
        if action is not None:
            raise ValueError("action requires a complete optional review")
        return base | {"state": "needs-input", "resumption_condition": "review-optional"}
    if item["invocation_mode"] == "non-interactive" and not item["is_resume"]:
        return base | {
            "state": "needs-input", "review_reshown": True,
            "available_actions": ["approve", "alter", "cancel"],
            "resumption_condition": "apply-resume-action",
        }
    if action is None:
        return base | {
            "state": "needs-input", "review_reshown": True,
            "available_actions": ["approve", "alter", "cancel"],
            "resumption_condition": "apply-resume-action",
        }
    if action == "approve":
        pending = any(gate["state"] == "pending" for gate in gates)
        return base | {
            "state": "ready-for-execution", "transition": "ready-for-execution",
            "action_consumed": "approve", "resumption_condition": "enforce-command-gates",
            "command_gate_disposition": "carried-pending" if pending else "clear",
        }
    if action == "alter":
        return base | {
            "state": "needs-input", "review_reshown": True,
            "available_actions": ["approve", "alter", "cancel"],
            "action_consumed": "alter", "resumption_condition": "apply-resume-action",
        }
    return base | {
        "state": "cancelled", "question_delivery": "none",
        "grouped_question_count": 0, "action_consumed": "cancel",
        "resumption_condition": "cancelled-no-resume",
        "command_gate_disposition": "preserved-cancelled",
    }


def validate_fixture_document(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict) or set(data) != {"schema_version", "contract_version", "cases"}:
        return ["fixture root keys are not closed"]
    if data["schema_version"] != FIXTURE_VERSION:
        errors.append("fixture schema_version is not current")
    if data["contract_version"] != CONTRACT_VERSION:
        errors.append("fixture contract_version is not current")
    cases = data["cases"]
    if not isinstance(cases, list):
        return errors + ["cases must be a list"]
    seen: list[str] = []
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict) or set(case) != CASE_KEYS:
            errors.append(f"{prefix} keys are not closed")
            continue
        seen.append(case.get("id"))
        expected = case["expected_output"]
        if not isinstance(expected, dict) or set(expected) != OUTPUT_KEYS:
            errors.append(f"{prefix}.expected_output keys are not closed")
            continue
        try:
            actual = evaluate_fixture_input(case["input"])
        except ValueError as exc:
            errors.append(f"{prefix}.input: {exc}")
            continue
        if actual != expected:
            errors.append(
                f"{prefix}: expected output diverges from deterministic result "
                f"expected={json.dumps(expected, sort_keys=True)} actual={json.dumps(actual, sort_keys=True)}"
            )
    if tuple(seen) != EXPECTED_CASE_IDS:
        errors.append("fixture IDs must match the canonical ordered set exactly")
    return errors


def validate_fixtures(path: Path) -> list[str]:
    return validate_fixture_document(load_json(path))


def extract_required_skills(text: str) -> str:
    match = re.search(r"^required_skills:(.*?)^required_commands:", text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def validate_package(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    skill_root = root / "skills" / "lf-command-input-interview"
    required_paths = (
        skill_root / "SKILL.md",
        skill_root / "references" / "intake-contract.md",
        skill_root / "references" / "fixtures" / "intake-cases.json",
        skill_root / "scripts" / "validate-command-input-interview.py",
        root / "manifest.yaml", root / "install-scopes.json",
    )
    for path in required_paths:
        if not path.is_file():
            errors.append(f"missing required path: {path.relative_to(root)}")
    if errors:
        return errors
    errors.extend(validate_fixtures(required_paths[2]))
    skill_text = required_paths[0].read_text(encoding="utf-8")
    frontmatter = skill_text.split("---", 2)[1]
    for argument_name in (
        "command_name", "command_parameter_schema", "command_contract_locator",
        "invocation_mode", "adapter_capability", "command_gate_snapshot",
        "provided_values", "discovery_results", "intake_resume_request",
    ):
        if f"- {argument_name}" not in frontmatter:
            errors.append(f"skill frontmatter missing operative argument {argument_name}")
    if "- resume_envelope" in frontmatter:
        errors.append("skill frontmatter retains superseded resume_envelope vocabulary")
    contract_text = required_paths[1].read_text(encoding="utf-8")
    for token in (
        "## Closed Schema: Structured Question",
        "## Closed Schema: Normalized Input",
        "## Closed Schema: Command Gate Snapshot",
        "## Closed Schema: Review Action And Resume Request",
        "## Closed Schema: Intake Resume Envelope",
        "## Closed Schema: Intake Resume Dashboard",
        "allow_client_free_form", "independent-only", "approve, alter, cancel",
        "pending_review_action", "command_gate_snapshot", "resumption_condition",
        "enforce-command-gates", "cancelled-no-resume",
        "action_fingerprint", "consumption_authority", "state_owner",
        "Action Consumption Receipt", "recommendation_required_by_client",
        "forged fresh fingerprint", "canonical ordered alterations",
    ):
        if token not in contract_text:
            errors.append(f"intake contract missing invariant token: {token}")
    if not QUESTION_ID_RE.fullmatch("intake.loki-example.optional_review.review-action"):
        errors.append("stable question ID positive self-check failed")
    if QUESTION_ID_RE.fullmatch("question.target"):
        errors.append("stable question ID negative self-check failed")
    digest = "sha256:" + hashlib.sha256(b"parameters").hexdigest()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        errors.append("schema digest self-check failed")
    command_paths = tuple(sorted((root / "skills").glob("loki-*/SKILL.md")))
    install_scopes = load_json(required_paths[5])
    skill_scopes = install_scopes["artifacts"]["skills"]
    shared_command_names = tuple(
        path.parent.name
        for path in command_paths
        if skill_scopes.get(path.parent.name) == "both"
    )
    if shared_command_names != EXPECTED_COMMANDS:
        errors.append("current shared Loki command set differs from the expected 17-command set")
    for path in command_paths:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        if "lf-command-input-interview" not in extract_required_skills(text):
            errors.append(f"{relative}: missing required skill adoption")
        if "../lf-command-input-interview/SKILL.md" not in text:
            errors.append(f"{relative}: missing canonical skill link in Input")
        if "../lf-command-input-interview/references/intake-contract.md" not in text:
            errors.append(f"{relative}: missing canonical contract link in Input")
        if "## Input" not in text or "parameters:" not in text:
            errors.append(f"{relative}: missing command Input parameter schema")
        if PLAN_AS_INTAKE_RE.search(text):
            errors.append(f"{relative}: superseded Plan-mode-as-intake wording remains")
    creator = (root / "skills" / "lf-command-creator" / "SKILL.md").read_text(encoding="utf-8")
    template = (root / "skills" / "lf-command-creator" / "references" / "command-contract-template.md").read_text(encoding="utf-8")
    for label, text in (("lf-command-creator", creator), ("command template", template)):
        if "lf-command-input-interview" not in text:
            errors.append(f"{label}: missing canonical intake authority")
        if PLAN_AS_INTAKE_RE.search(text):
            errors.append(f"{label}: superseded Plan-mode-as-intake wording remains")
    manifest = required_paths[4].read_text(encoding="utf-8")
    if 'name: "lf-command-input-interview"' not in manifest or 'file: "skills/lf-command-input-interview/SKILL.md"' not in manifest:
        errors.append("manifest.yaml: missing skill registration")
    scopes = load_json(required_paths[5])
    try:
        scope = scopes["artifacts"]["skills"]["lf-command-input-interview"]  # type: ignore[index]
    except (KeyError, TypeError):
        scope = None
    if scope != "both":
        errors.append("install-scopes.json: lf-command-input-interview must be both")
    return errors


def print_result(mode: str, errors: list[str]) -> int:
    result = {
        "validator": "validate-command-input-interview",
        "contract_version": CONTRACT_VERSION,
        "mode": mode,
        "status": "pass" if not errors else "fail",
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--package-root", type=Path)
    args = parser.parse_args()
    script_root = Path(__file__).resolve().parents[1]
    fixtures = script_root / "references" / "fixtures" / "intake-cases.json"
    if args.self_test:
        data = load_json(fixtures)
        errors = validate_fixture_document(data)
        divergent = copy.deepcopy(data)
        divergent["cases"][0]["expected_output"]["state"] = "needs-input"
        if not validate_fixture_document(divergent):
            errors.append("divergent expected output was not rejected")
        invalid_action = copy.deepcopy(data["cases"][2]["input"])
        invalid_action["resume_action"] = {
            "action_id": "invalid-alter",
            "action_fingerprint": "sha256:" + "4" * 64,
            "name": "alter",
            "alterations": [],
        }
        try:
            evaluate_fixture_input(invalid_action)
        except ValueError:
            pass
        else:
            errors.append("invalid alter action was not rejected")
        cancelled_action = copy.deepcopy(data["cases"][11]["input"])
        cancelled_action["resume_action"] = {
            "action_id": "invalid-cancelled-approve",
            "action_fingerprint": "sha256:" + "5" * 64,
            "name": "approve",
            "alterations": [],
        }
        try:
            evaluate_fixture_input(cancelled_action)
        except ValueError:
            pass
        else:
            errors.append("cancelled envelope action was not rejected")
        replay_accepted = copy.deepcopy(data)
        replay_accepted["cases"][13]["input"]["consumed_actions"] = []
        if not validate_fixture_document(replay_accepted):
            errors.append("consumed-action replay acceptance was not caught")
        forged_fingerprint = copy.deepcopy(data["cases"][13]["input"])
        forged_fingerprint["resume_action"]["action_id"] = "action-replay-forged"
        forged_fingerprint["resume_action"]["action_fingerprint"] = "sha256:" + "6" * 64
        try:
            evaluate_fixture_input(forged_fingerprint)
        except ValueError as exc:
            if "fingerprint" not in str(exc) or "match" not in str(exc):
                errors.append("forged fresh fingerprint failed for a non-mismatch reason")
        else:
            errors.append("same-semantic action with forged fresh fingerprint was accepted")
        unjustified_structured = copy.deepcopy(data["cases"][14]["input"])
        unjustified_structured["interaction_mode"] = "structured"
        try:
            evaluate_fixture_input(unjustified_structured)
        except ValueError:
            pass
        else:
            errors.append("client-required unjustified recommendation did not force textual fallback")
        if PLAN_AS_INTAKE_RE.search("Enter Plan mode and request the workflow parameters.") is None:
            errors.append("Plan-mode negative wording self-check failed")
        if PLAN_AS_INTAKE_RE.search("Use Plan Mode only as adapter scenario data.") is not None:
            errors.append("Plan-mode legitimate-data self-check failed")
        return print_result("self-test", errors)
    return print_result("package-scan", validate_package(args.package_root))


if __name__ == "__main__":
    sys.exit(main())
