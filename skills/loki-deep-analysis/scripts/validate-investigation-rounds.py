#!/usr/bin/env python3
"""Validate the post-preparation adaptive investigation-round ledger."""

import argparse
import copy
import importlib.util
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

POLICY_KEYS = {"max_rounds", "max_delegated_per_round", "concurrent_handoff_limit", "cost_mode"}
PREPARATION_BINDING_KEYS = {"preparation_id", "preparation_digest", "candidate_ids"}
INITIAL_CLASSIFICATION_KEYS = {"selected_candidate_ids", "useful_candidate_ids", "decisions"}
LEDGER_KEYS = {"schema_version", "preparation_binding", "candidate_universe", "initial_classification", "initial_useful_investigations", "policy", "rounds", "analysis_terminal_reason", "downstream_handoff"}
ROUND_KEYS = {"round", "status", "delegated_investigations", "local_resolutions", "terminal_barrier", "reclassification"}
INVESTIGATION_KEYS = {"candidate_id", "owner", "material_question", "reinvestigation_rationale", "subwave", "handoff_id", "agent_run_id", "evidence_id", "cost", "terminal_state"}
RECLASSIFICATION_KEYS = {"all_candidate_ids", "useful_next_round", "decisions"}
DOWNSTREAM_KEYS = {"analysis_phase_complete", "auto_invoked", "allowed_destinations", "minimum_next_path"}
PREPARATION_ID = re.compile(r"^prep-[0-9a-f]{64}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
HANDOFF_ID = re.compile(r"^handoff-[a-z0-9][a-z0-9-]*$")
AGENT_RUN_ID = re.compile(r"^agent-run-[a-z0-9][a-z0-9-]*$")
EVIDENCE_ID = re.compile(r"^evidence-[a-z0-9][a-z0-9-]*$")


class ValidationError(Exception):
    pass


def exact(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValidationError(f"{label}: exact keys required; expected={sorted(keys)}")
    return value


def nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label}: non-empty string required")
    return value


def string_list(value: Any, label: str, *, sorted_unique: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValidationError(f"{label}: non-empty string array required")
    if sorted_unique and (value != sorted(value) or len(value) != len(set(value))):
        raise ValidationError(f"{label}: sorted unique array required")
    return value


def preparation_validator() -> Any:
    path = Path(__file__).resolve().parents[2] / "lf-analytic-inference-preparation" / "scripts" / "validate-preparation.py"
    spec = importlib.util.spec_from_file_location("loki_validate_preparation", path)
    if spec is None or spec.loader is None:
        raise ValidationError("preparation: canonical validator is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(value: Any, preparation: Any) -> None:
    if isinstance(preparation, dict) and set(preparation) == {"inference_preparation"}:
        preparation = preparation["inference_preparation"]
    module = preparation_validator()
    try:
        module.validate_preparation(preparation)
    except (module.ValidationError, TypeError, KeyError) as exc:
        raise ValidationError(f"preparation: invalid canonical schema-v3 artifact: {exc}") from exc
    if preparation.get("status") not in {"pre-investigation-complete", "partial"}:
        raise ValidationError("preparation: blocked core cannot authorize investigation rounds")
    canonical_candidate_ids = [candidate["candidate_id"] for candidate in preparation["candidates"]]
    canonical_selected_ids = preparation["selected_for_investigation"]
    actionable_candidate_ids = set(canonical_selected_ids)
    ledger = exact(value, LEDGER_KEYS, "ledger")
    if type(ledger["schema_version"]) is not int or ledger["schema_version"] != 1:
        raise ValidationError("ledger.schema_version: exact integer 1 required")
    universe = string_list(ledger["candidate_universe"], "candidate_universe", sorted_unique=True)
    binding = exact(ledger["preparation_binding"], PREPARATION_BINDING_KEYS, "preparation_binding")
    if not isinstance(binding["preparation_id"], str) or not PREPARATION_ID.fullmatch(binding["preparation_id"]):
        raise ValidationError("preparation_binding.preparation_id: canonical preparation ID required")
    if not isinstance(binding["preparation_digest"], str) or not SHA256.fullmatch(binding["preparation_digest"]):
        raise ValidationError("preparation_binding.preparation_digest: canonical digest required")
    if string_list(binding["candidate_ids"], "preparation_binding.candidate_ids", sorted_unique=True) != universe:
        raise ValidationError("preparation_binding: candidate IDs must exactly equal candidate_universe")
    if binding["preparation_id"] != preparation["preparation_id"]:
        raise ValidationError("preparation_binding.preparation_id: does not equal validated preparation artifact")
    if binding["preparation_digest"] != preparation["preparation_digest"]:
        raise ValidationError("preparation_binding.preparation_digest: does not equal validated preparation artifact")
    if universe != canonical_candidate_ids:
        raise ValidationError("candidate_universe: must exactly equal validated preparation candidate IDs")
    initial_useful = string_list(ledger["initial_useful_investigations"], "initial_useful_investigations", sorted_unique=True)
    initial_classification = exact(ledger["initial_classification"], INITIAL_CLASSIFICATION_KEYS, "initial_classification")
    if string_list(initial_classification["selected_candidate_ids"], "initial_classification.selected_candidate_ids", sorted_unique=True) != canonical_selected_ids:
        raise ValidationError("initial_classification.selected_candidate_ids: must exactly equal preparation selected_for_investigation")
    if string_list(initial_classification["useful_candidate_ids"], "initial_classification.useful_candidate_ids", sorted_unique=True) != initial_useful:
        raise ValidationError("initial_classification.useful_candidate_ids: must equal initial_useful_investigations")
    if any(candidate_id not in canonical_selected_ids for candidate_id in initial_useful):
        raise ValidationError("initial_useful_investigations: only preparation-selected candidates are admissible")
    initial_decisions = initial_classification["decisions"]
    if not isinstance(initial_decisions, dict) or set(initial_decisions) != set(canonical_selected_ids) or any(not isinstance(reason, str) or not reason for reason in initial_decisions.values()):
        raise ValidationError("initial_classification.decisions: one observable matching decision per preparation-selected candidate required")
    policy = exact(ledger["policy"], POLICY_KEYS, "policy")
    expected_integer_controls = {"max_rounds": 3, "max_delegated_per_round": 6, "concurrent_handoff_limit": 2}
    if any(type(policy[key]) is not int or policy[key] != expected for key, expected in expected_integer_controls.items()) or policy["cost_mode"] != "telemetry-only":
        raise ValidationError("policy: required values are 3 rounds, 6 delegated, concurrency 2, telemetry-only cost")
    rounds = ledger["rounds"]
    if not isinstance(rounds, list) or len(rounds) > 3:
        raise ValidationError("rounds: require zero to three rounds")
    seen_handoffs: set[str] = set()
    seen_runs: set[str] = set()
    seen_evidence: set[str] = set()
    candidate_rounds: dict[str, list[int]] = {}
    candidate_action_rounds: dict[str, list[int]] = {}
    locally_resolved_candidates: set[str] = set()
    prior_useful: set[str] | None = set(initial_useful)
    for index, raw_round in enumerate(rounds, 1):
        round_item = exact(raw_round, ROUND_KEYS, f"rounds[{index - 1}]")
        if type(round_item["round"]) is not int or round_item["round"] != index or round_item["status"] != "terminal":
            raise ValidationError(f"rounds[{index - 1}]: rounds must be sequential and terminal before reclassification")
        delegated = round_item["delegated_investigations"]
        if not isinstance(delegated, list) or len(delegated) > 6:
            raise ValidationError(f"rounds[{index - 1}]: delegated capacity exceeds 6")
        terminal_ids: list[str] = []
        round_candidate_ids: set[str] = set()
        subwaves: dict[int, int] = {}
        for item_index, raw_investigation in enumerate(delegated):
            label = f"rounds[{index - 1}].delegated_investigations[{item_index}]"
            investigation = exact(raw_investigation, INVESTIGATION_KEYS, label)
            candidate_id = nonempty(investigation["candidate_id"], f"{label}.candidate_id")
            if candidate_id not in universe:
                raise ValidationError(f"{label}: candidate is outside candidate_universe")
            if candidate_id in round_candidate_ids:
                raise ValidationError(f"{label}: candidate may appear at most once per round")
            round_candidate_ids.add(candidate_id)
            if prior_useful is not None and candidate_id not in prior_useful:
                raise ValidationError(f"{label}: candidate was not useful_next_round in the preceding reclassification")
            nonempty(investigation["owner"], f"{label}.owner")
            nonempty(investigation["material_question"], f"{label}.material_question")
            subwave = investigation["subwave"]
            if type(subwave) is not int or subwave < 1:
                raise ValidationError(f"{label}.subwave: positive integer required")
            subwaves[subwave] = subwaves.get(subwave, 0) + 1
            if subwaves[subwave] > 2:
                raise ValidationError(f"rounds[{index - 1}]: subwave concurrency exceeds 2")
            prior = candidate_action_rounds.get(candidate_id, [])
            rationale = investigation["reinvestigation_rationale"]
            if prior:
                nonempty(rationale, f"{label}.reinvestigation_rationale")
                if investigation["material_question"] in {
                    previous[1] for previous in _candidate_questions(rounds[:index - 1], candidate_id)
                }:
                    raise ValidationError(f"{label}: reinvestigation requires a materially new question")
            elif rationale is not None:
                raise ValidationError(f"{label}: first investigation requires null reinvestigation_rationale")
            for key, seen, pattern in (("handoff_id", seen_handoffs, HANDOFF_ID), ("agent_run_id", seen_runs, AGENT_RUN_ID), ("evidence_id", seen_evidence, EVIDENCE_ID)):
                identity = nonempty(investigation[key], f"{label}.{key}")
                if not pattern.fullmatch(identity) or identity in seen:
                    raise ValidationError(f"{label}.{key}: correctly prefixed globally unique ID required")
                seen.add(identity)
            cost = investigation["cost"]
            valid_cost = (
                isinstance(cost, str) and cost in {"unknown", "unsupported"}
            ) or (
                isinstance(cost, int) and not isinstance(cost, bool) and cost >= 0
            ) or (
                isinstance(cost, float) and math.isfinite(cost) and cost >= 0
            )
            if not valid_cost:
                raise ValidationError(f"{label}.cost: telemetry must be a finite real number >= 0, unknown, or unsupported")
            if investigation["terminal_state"] not in {"completed", "partial", "blocked", "failed", "unavailable", "unsupported"}:
                raise ValidationError(f"{label}.terminal_state: terminal value required")
            terminal_ids.append(investigation["handoff_id"])
            candidate_rounds.setdefault(candidate_id, []).append(index)
            candidate_action_rounds.setdefault(candidate_id, []).append(index)
        local = string_list(round_item["local_resolutions"], f"rounds[{index - 1}].local_resolutions", sorted_unique=True)
        if not delegated and not local:
            raise ValidationError(f"rounds[{index - 1}]: do not materialize an empty round; stop early instead")
        if any(candidate_id not in universe for candidate_id in local):
            raise ValidationError(f"rounds[{index - 1}].local_resolutions: candidate outside universe")
        if set(local) & round_candidate_ids:
            raise ValidationError(f"rounds[{index - 1}]: delegated investigations and local resolutions must be disjoint")
        if any(candidate_id not in prior_useful for candidate_id in local):
            raise ValidationError(f"rounds[{index - 1}].local_resolutions: candidate was not useful_next_round in the preceding reclassification")
        if any(candidate_id in locally_resolved_candidates for candidate_id in local):
            raise ValidationError(f"rounds[{index - 1}].local_resolutions: a candidate may be resolved locally only once")
        locally_resolved_candidates.update(local)
        for candidate_id in local:
            candidate_action_rounds.setdefault(candidate_id, []).append(index)
        barrier = string_list(round_item["terminal_barrier"], f"rounds[{index - 1}].terminal_barrier", sorted_unique=True)
        if barrier != sorted(terminal_ids):
            raise ValidationError(f"rounds[{index - 1}].terminal_barrier: must contain every delegated handoff exactly once")
        classification = exact(round_item["reclassification"], RECLASSIFICATION_KEYS, f"rounds[{index - 1}].reclassification")
        if string_list(classification["all_candidate_ids"], "reclassification.all_candidate_ids", sorted_unique=True) != universe:
            raise ValidationError(f"rounds[{index - 1}].reclassification: all candidates must be reclassified")
        useful = string_list(classification["useful_next_round"], "reclassification.useful_next_round", sorted_unique=True)
        if any(candidate_id not in actionable_candidate_ids for candidate_id in useful):
            raise ValidationError(f"rounds[{index - 1}].reclassification: useful_next_round must remain within preparation-selected actionable candidates")
        decisions = classification["decisions"]
        if not isinstance(decisions, dict) or set(decisions) != set(universe) or any(not isinstance(reason, str) or not reason for reason in decisions.values()):
            raise ValidationError(f"rounds[{index - 1}].reclassification: one observable decision per candidate required")
        if index < len(rounds) and not useful:
            raise ValidationError(f"rounds[{index - 1}]: no useful next-round candidate requires early stop")
        prior_useful = set(useful)
    terminal_reason = ledger["analysis_terminal_reason"]
    if terminal_reason not in {"round-limit-reached", "no-useful-investigation", "analysis-sufficient"}:
        raise ValidationError("analysis_terminal_reason: invalid")
    if not rounds:
        if initial_useful or terminal_reason != "no-useful-investigation":
            raise ValidationError("analysis_terminal_reason: zero rounds require no-useful-investigation")
    last_useful = rounds[-1]["reclassification"]["useful_next_round"] if rounds else []
    if len(rounds) == 3 and terminal_reason != "round-limit-reached":
        raise ValidationError("analysis_terminal_reason: round 3 is an absolute analysis boundary")
    if len(rounds) < 3:
        if last_useful:
            raise ValidationError("analysis_terminal_reason: fewer than three rounds may terminate only with no useful next-round candidates")
        if terminal_reason not in {"no-useful-investigation", "analysis-sufficient"}:
            raise ValidationError("analysis_terminal_reason: early stop must be explicit")
    downstream = exact(ledger["downstream_handoff"], DOWNSTREAM_KEYS, "downstream_handoff")
    if downstream["analysis_phase_complete"] is not True or downstream["auto_invoked"] is not False:
        raise ValidationError("downstream_handoff: analysis completes without automatic invocation")
    allowed_destinations = string_list(downstream["allowed_destinations"], "downstream_handoff.allowed_destinations", sorted_unique=True)
    if not allowed_destinations:
        raise ValidationError("downstream_handoff.allowed_destinations: at least one permitted destination required")
    nonempty(downstream["minimum_next_path"], "downstream_handoff.minimum_next_path")


def _candidate_questions(rounds: list[dict[str, Any]], candidate_id: str) -> list[tuple[int, str]]:
    return [(round_item["round"], item["material_question"]) for round_item in rounds for item in round_item["delegated_investigations"] if item["candidate_id"] == candidate_id]


def load_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent / "references" / "fixtures" / "investigation-round-cases.json"
    container = json.loads(path.read_text(encoding="utf-8"))
    return container["investigation_round_ledger"], container["inference_preparation"]


def self_test() -> None:
    fixture, preparation = load_fixture()
    validate(fixture, preparation)
    zero_round = copy.deepcopy(fixture)
    zero_round["rounds"] = []
    zero_round["initial_useful_investigations"] = []
    zero_round["initial_classification"]["useful_candidate_ids"] = []
    zero_round["analysis_terminal_reason"] = "no-useful-investigation"
    validate(zero_round, preparation)
    full_three = copy.deepcopy(fixture)
    reinvestigated_id = full_three["rounds"][1]["delegated_investigations"][0]["candidate_id"]
    full_three["rounds"][1]["reclassification"]["useful_next_round"] = [reinvestigated_id]
    round_three = copy.deepcopy(full_three["rounds"][1])
    round_three["round"] = 3
    investigation = round_three["delegated_investigations"][0]
    investigation.update({
        "material_question": "question-a-r3-materially-new",
        "reinvestigation_rationale": "round-two evidence exposed a final distinct mechanism",
        "handoff_id": "handoff-r3-a",
        "agent_run_id": "agent-run-r3-a",
        "evidence_id": "evidence-r3-a",
    })
    round_three["terminal_barrier"] = ["handoff-r3-a"]
    round_three["reclassification"]["useful_next_round"] = [reinvestigated_id]
    round_three["reclassification"]["decisions"][reinvestigated_id] = "still useful but round limit ends analysis"
    full_three["rounds"].append(round_three)
    full_three["analysis_terminal_reason"] = "round-limit-reached"
    validate(full_three, preparation)
    fourth_round = copy.deepcopy(full_three)
    extra_round = copy.deepcopy(round_three)
    extra_round["round"] = 4
    fourth_round["rounds"].append(extra_round)
    try:
        validate(fourth_round, preparation)
    except ValidationError:
        pass
    else:
        raise AssertionError("a fourth investigation round was accepted")
    mutations = []
    for invalid_schema_version in (True, 1.0, "1"):
        mutations.append(lambda value, schema_version=invalid_schema_version: value.__setitem__("schema_version", schema_version))
    for invalid_round in (True, 1.0, "1"):
        mutations.append(lambda value, round_number=invalid_round: value["rounds"][0].__setitem__("round", round_number))
    mutations.append(lambda value: value["rounds"][1].__setitem__("round", 2.0))
    for control, expected in (("max_rounds", 3), ("max_delegated_per_round", 6), ("concurrent_handoff_limit", 2)):
        for invalid_control in (True, float(expected), str(expected)):
            mutations.append(lambda value, key=control, control_value=invalid_control: value["policy"].__setitem__(key, control_value))
    for invalid_subwave in (True, 1.0, "1"):
        mutations.append(lambda value, subwave=invalid_subwave: value["rounds"][0]["delegated_investigations"][0].__setitem__("subwave", subwave))
    mutations.append(lambda value: value["policy"].__setitem__("max_rounds", 4))
    def duplicate_candidate_same_round(value: dict[str, Any]) -> None:
        duplicate = copy.deepcopy(value["rounds"][1]["delegated_investigations"][0])
        duplicate.update({"material_question": "another-question-same-round", "handoff_id": "handoff-r2-a-duplicate", "agent_run_id": "agent-run-r2-a-duplicate", "evidence_id": "evidence-r2-a-duplicate"})
        value["rounds"][1]["delegated_investigations"].append(duplicate)
        value["rounds"][1]["terminal_barrier"].append("handoff-r2-a-duplicate")
        value["rounds"][1]["terminal_barrier"].sort()
    mutations.append(duplicate_candidate_same_round)
    mutations.append(lambda value: value["rounds"][0]["delegated_investigations"][2].__setitem__("subwave", 1))
    mutations.append(lambda value: value["rounds"][1]["delegated_investigations"][0].__setitem__("handoff_id", value["rounds"][0]["delegated_investigations"][0]["handoff_id"]))
    mutations.append(lambda value: value["rounds"][1]["delegated_investigations"][0].__setitem__("reinvestigation_rationale", None))
    mutations.append(lambda value: value["rounds"][0].__setitem__("terminal_barrier", []))
    def overlap_local_and_delegated(value: dict[str, Any]) -> None:
        candidate_id = value["rounds"][0]["delegated_investigations"][0]["candidate_id"]
        value["rounds"][0]["local_resolutions"].append(candidate_id)
        value["rounds"][0]["local_resolutions"].sort()
    mutations.append(overlap_local_and_delegated)
    def later_local_outside_prior_useful(value: dict[str, Any]) -> None:
        prior_useful = set(value["rounds"][0]["reclassification"]["useful_next_round"])
        candidate_id = next(item for item in value["candidate_universe"] if item not in prior_useful)
        value["rounds"][1]["local_resolutions"] = [candidate_id]
    mutations.append(later_local_outside_prior_useful)
    mutations.append(lambda value: value["rounds"][0]["reclassification"].__setitem__("all_candidate_ids", value["candidate_universe"][:-1]))
    mutations.append(lambda value: value["preparation_binding"].__setitem__("preparation_id", "prep-" + "f" * 64))
    mutations.append(lambda value: value["preparation_binding"].__setitem__("preparation_digest", "sha256:" + "f" * 64))
    def coherently_reduce_declared_universe(value: dict[str, Any]) -> None:
        removed = value["candidate_universe"][-1]
        reduced = value["candidate_universe"][:-1]
        value["candidate_universe"] = reduced
        value["preparation_binding"]["candidate_ids"] = reduced
        value["initial_useful_investigations"] = [item for item in value["initial_useful_investigations"] if item != removed]
        for round_item in value["rounds"]:
            round_item["delegated_investigations"] = [item for item in round_item["delegated_investigations"] if item["candidate_id"] != removed]
            round_item["local_resolutions"] = [item for item in round_item["local_resolutions"] if item != removed]
            round_item["terminal_barrier"] = sorted(item["handoff_id"] for item in round_item["delegated_investigations"])
            round_item["reclassification"]["all_candidate_ids"] = reduced
            round_item["reclassification"]["useful_next_round"] = [item for item in round_item["reclassification"]["useful_next_round"] if item != removed]
            round_item["reclassification"]["decisions"].pop(removed)
    mutations.append(coherently_reduce_declared_universe)
    non_prior_candidate = next(candidate_id for candidate_id in fixture["candidate_universe"] if candidate_id != reinvestigated_id)
    mutations.append(lambda value: value["rounds"][1]["delegated_investigations"][0].__setitem__("candidate_id", non_prior_candidate))
    mutations.append(lambda value: value["rounds"][1]["reclassification"].__setitem__("useful_next_round", [reinvestigated_id]))
    for invalid_cost in (float("nan"), float("inf"), float("-inf"), json.loads("NaN"), json.loads("Infinity"), json.loads("-Infinity")):
        mutations.append(lambda value, cost=invalid_cost: value["rounds"][0]["delegated_investigations"][0].__setitem__("cost", cost))
    def empty_materialized_round(value: dict[str, Any]) -> None:
        value["rounds"][0]["delegated_investigations"] = []
        value["rounds"][0]["local_resolutions"] = []
        value["rounds"][0]["terminal_barrier"] = []
    mutations.append(empty_materialized_round)
    mutations.append(lambda value: value["rounds"][0]["delegated_investigations"][0].__setitem__("handoff_id", "run-wrong-prefix"))
    mutations.append(lambda value: value["policy"].__setitem__("cost_mode", "admission-gate"))
    mutations.append(lambda value: value["downstream_handoff"].__setitem__("auto_invoked", True))
    mutations.append(lambda value: value["downstream_handoff"].__setitem__("analysis_phase_complete", 1))
    mutations.append(lambda value: value["downstream_handoff"].__setitem__("auto_invoked", 0))
    mutations.append(lambda value: value["downstream_handoff"].__setitem__("allowed_destinations", []))
    def repeat_local_resolution(value: dict[str, Any]) -> None:
        candidate_id = value["rounds"][0]["local_resolutions"][0]
        value["rounds"][0]["reclassification"]["useful_next_round"] = sorted({*value["rounds"][0]["reclassification"]["useful_next_round"], candidate_id})
        value["rounds"][1]["local_resolutions"] = [candidate_id]
    mutations.append(repeat_local_resolution)
    for mutate in mutations:
        invalid = copy.deepcopy(fixture)
        mutate(invalid)
        try:
            validate(invalid, preparation)
        except ValidationError:
            continue
        raise AssertionError("invalid adaptive-round fixture was accepted")
    rejected_preparation = copy.deepcopy(preparation)
    rejected_summary = rejected_preparation["candidates"][0]["summary"]
    old_rejected_id = rejected_preparation["candidates"][0]["candidate_id"]
    rejected_preparation["candidates"][0]["disposition"] = "rejected"
    rejected_preparation["candidates"][0]["disposition_reason"] = "rejected:irrelevant | canonical negative fixture"
    module = preparation_validator()
    module.refresh_identities(rejected_preparation)
    module.validate_preparation(rejected_preparation)
    new_rejected_id = next(candidate["candidate_id"] for candidate in rejected_preparation["candidates"] if candidate["summary"] == rejected_summary)
    rejected_ledger = _replace_identity(copy.deepcopy(fixture), old_rejected_id, new_rejected_id)
    rejected_ledger["preparation_binding"].update({"preparation_id": rejected_preparation["preparation_id"], "preparation_digest": rejected_preparation["preparation_digest"], "candidate_ids": [candidate["candidate_id"] for candidate in rejected_preparation["candidates"]]})
    rejected_ledger["candidate_universe"] = [candidate["candidate_id"] for candidate in rejected_preparation["candidates"]]
    rejected_ledger["initial_classification"]["selected_candidate_ids"] = rejected_preparation["selected_for_investigation"]
    rejected_ledger["initial_classification"]["decisions"].pop(new_rejected_id, None)
    rejected_ledger["initial_useful_investigations"].sort()
    rejected_ledger["initial_classification"]["useful_candidate_ids"] = list(rejected_ledger["initial_useful_investigations"])
    for round_item in rejected_ledger["rounds"]:
        round_item["reclassification"]["all_candidate_ids"] = list(rejected_ledger["candidate_universe"])
        round_item["reclassification"]["useful_next_round"].sort()
    try:
        validate(rejected_ledger, rejected_preparation)
    except ValidationError:
        pass
    else:
        raise AssertionError("rejected preparation candidate entered initial useful/delegated work")
    later_rejected_preparation = copy.deepcopy(preparation)
    later_rejected_summary = later_rejected_preparation["candidates"][1]["summary"]
    old_later_rejected_id = later_rejected_preparation["candidates"][1]["candidate_id"]
    later_rejected_preparation["candidates"][1]["disposition"] = "rejected"
    later_rejected_preparation["candidates"][1]["disposition_reason"] = "rejected:irrelevant | canonical later-round negative fixture"
    module.refresh_identities(later_rejected_preparation)
    module.validate_preparation(later_rejected_preparation)
    new_later_rejected_id = next(candidate["candidate_id"] for candidate in later_rejected_preparation["candidates"] if candidate["summary"] == later_rejected_summary)
    later_rejected_ledger = _replace_identity(copy.deepcopy(fixture), old_later_rejected_id, new_later_rejected_id)
    later_rejected_ledger["preparation_binding"].update({"preparation_id": later_rejected_preparation["preparation_id"], "preparation_digest": later_rejected_preparation["preparation_digest"], "candidate_ids": [candidate["candidate_id"] for candidate in later_rejected_preparation["candidates"]]})
    later_rejected_ledger["candidate_universe"] = [candidate["candidate_id"] for candidate in later_rejected_preparation["candidates"]]
    later_rejected_ledger["initial_classification"]["selected_candidate_ids"] = later_rejected_preparation["selected_for_investigation"]
    later_rejected_ledger["initial_classification"]["decisions"].pop(new_later_rejected_id, None)
    later_rejected_ledger["initial_useful_investigations"] = [candidate_id for candidate_id in later_rejected_ledger["initial_useful_investigations"] if candidate_id != new_later_rejected_id]
    later_rejected_ledger["initial_classification"]["useful_candidate_ids"] = list(later_rejected_ledger["initial_useful_investigations"])
    first_round = later_rejected_ledger["rounds"][0]
    first_round["delegated_investigations"] = [item for item in first_round["delegated_investigations"] if item["candidate_id"] != new_later_rejected_id]
    first_round["terminal_barrier"] = sorted(item["handoff_id"] for item in first_round["delegated_investigations"])
    first_round["reclassification"]["useful_next_round"] = [new_later_rejected_id]
    second_investigation = later_rejected_ledger["rounds"][1]["delegated_investigations"][0]
    second_investigation.update({"candidate_id": new_later_rejected_id, "material_question": "can rejected candidate-b become operational without a new preparation version", "reinvestigation_rationale": None})
    for round_item in later_rejected_ledger["rounds"]:
        round_item["reclassification"]["all_candidate_ids"] = list(later_rejected_ledger["candidate_universe"])
    try:
        validate(later_rejected_ledger, later_rejected_preparation)
    except ValidationError:
        pass
    else:
        raise AssertionError("rejected candidate-b was promoted through useful_next_round into round two")
    print("self-test: ok")


def _replace_identity(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return new if value == old else value
    if isinstance(value, list):
        return [_replace_identity(item, old, new) for item in value]
    if isinstance(value, dict):
        return {_replace_identity(key, old, new): _replace_identity(item, old, new) for key, item in value.items()}
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?")
    parser.add_argument("--preparation", required=False, help="validated preparation schema-v3 artifact path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            if not args.preparation:
                raise ValidationError("--preparation is required outside --self-test")
            ledger_document = json.loads(Path(args.input).read_text(encoding="utf-8")) if args.input else json.load(sys.stdin)
            preparation_document = json.loads(Path(args.preparation).read_text(encoding="utf-8"))
            value = ledger_document.get("investigation_round_ledger", ledger_document) if isinstance(ledger_document, dict) else ledger_document
            preparation = preparation_document.get("inference_preparation", preparation_document) if isinstance(preparation_document, dict) else preparation_document
            validate(value, preparation)
            print("valid")
        return 0
    except (OSError, json.JSONDecodeError, ValidationError, AssertionError) as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
