#!/usr/bin/env python3
"""Validate the pure analytic-inference preparation object (stdlib only)."""

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PREP_KEYS = {
    "schema_version", "artifact_type", "preparation_id", "input_fingerprint",
    "preparation_digest", "status", "input", "root", "source_map", "policy",
    "catalog_observation", "technologies", "candidates", "duplicate_analysis",
    "selected_for_investigation", "planned_investigations", "dispatch_admitted",
    "generation_state", "validators", "blockers", "minimum_next_path", "execution_boundary",
}
FAILURE_WRAPPER_KEYS = {"preparation_failure"}
FAILURE_KEYS = {"status", "stage", "blockers", "minimum_next_path", "execution_boundary"}
FAILURE_STAGES = {"input", "source", "request-controls", "policy", "root", "authority"}
CANDIDATE_KEYS = {
    "candidate_id", "origin", "lifecycle_status", "summary", "investigable_statement",
    "technologies", "surfaces", "support_evidence_refs", "confirm_or_reject_evidence",
    "stop_condition", "catalog_locator", "catalog_revision",
    "duplicate_relation", "disposition", "disposition_reason", "suggested_capabilities",
}
REQUEST_CONTROL_KEYS = {
    "candidate_ceiling", "catalog_retrieval_page_size",
    "minimum_candidate_floor",
}
DUPLICATE_ITEM_KEYS = {"candidate_id", "duplicate_of"}
DISPOSITION_REASON_CODES = {
    "selected": {"selected:essential-criteria-satisfied"},
    "rejected": {
        "rejected:irrelevant", "rejected:invalid", "rejected:incompatible",
        "rejected:unverifiable", "rejected:exact-duplicate",
    },
    "deferred": {
        "deferred:essential-evidence", "deferred:compatibility",
        "deferred:context",
    },
}
BOUNDARY = {
    "dispatch_authorized": False,
    "investigation_handoffs_dispatched": 0,
    "agent_runs_created": 0,
    "handoffs_created": 0,
    "web_research_performed": False,
    "downstream_workflows_invoked": [],
    "catalog_mutation_applied": False,
}
FORBIDDEN_ID = re.compile(r"^(?:ar|agent|ho|handoff|ev|evidence)-", re.I)
LOOKUP_ACTION_PREFIXES = (
    "search-docs: ", "inspect-source: ", "inspect-data: ",
    "inspect-runtime: ", "compare-precedent: ", "ask-human: ",
)


class ValidationError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code, self.message = code, message
        super().__init__(f"{code}: {message}")


def canonical_json(value: Any) -> str:
    """Return the contract's UTF-8 JSON text, rejecting non-finite values."""
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValidationError("E001", f"value is not canonical JSON: {exc}") from exc


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def fail(code: str, message: str) -> None:
    raise ValidationError(code, message)


def mapping(value: Any, label: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail("E002", f"{label} must be an object")
    actual = set(value)
    if actual != keys:
        missing, extra = sorted(keys - actual), sorted(actual - keys)
        fail("E003", f"{label} exact keys violated; missing={missing} extra={extra}")
    return value


def string(value: Any, label: str, nonempty: bool = False) -> str:
    if not isinstance(value, str) or (nonempty and not value):
        fail("E004", f"{label} must be a{' non-empty' if nonempty else ''} string")
    return value


def sha(value: Any, label: str, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        fail("E005", f"{label} must be a lowercase sha256 digest")


def integer(value: Any, label: str, positive: bool = False) -> None:
    if type(value) is not int or (positive and value <= 0):
        fail("E006", f"{label} must be a{' positive' if positive else 'n'} integer")


def string_list(value: Any, label: str, *, sorted_unique: bool = False, nonempty_items: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        fail("E007", f"{label} must be an array of strings")
    if nonempty_items and any(not item for item in value):
        fail("E004", f"{label} items must be non-empty strings")
    if sorted_unique and (value != sorted(value) or len(value) != len(set(value))):
        fail("E008", f"{label} must be lexicographically sorted and unique")
    return value


def reject_runtime_ids(value: Any, path: str = "inference_preparation") -> None:
    if isinstance(value, str) and FORBIDDEN_ID.match(value):
        fail("E009", f"{path} contains forbidden agent/handoff/evidence ID {value!r}")
    if isinstance(value, list):
        for index, item in enumerate(value):
            reject_runtime_ids(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            if FORBIDDEN_ID.match(key):
                fail("E009", f"{path} contains forbidden runtime identity key {key!r}")
            reject_runtime_ids(item, f"{path}.{key}")


def candidate_semantic_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    # The contract contains no flag that proves a reason was derived later; the
    # supplied reason is consequently semantic input and remains covered.
    return {key: value for key, value in candidate.items() if key != "candidate_id"}


def disposition_reason_code(value: str, disposition: str, label: str) -> str:
    allowed = DISPOSITION_REASON_CODES[disposition]
    matches = [code for code in allowed if value == code or value.startswith(code + " | ")]
    if len(matches) != 1:
        fail("E027", f"{label}.disposition_reason has no allowed {disposition} reason code")
    return matches[0]


def validate_candidate(candidate: Any, input_fingerprint: str, index: int) -> str:
    label = f"candidates[{index}]"
    candidate = mapping(candidate, label, CANDIDATE_KEYS)
    origin = candidate["origin"]
    if origin not in {"catalogued", "generated"}:
        fail("E010", f"{label}.origin is invalid")
    if candidate["lifecycle_status"] != "unreviewed":
        fail("E010", f"{label}.lifecycle_status must be unreviewed")
    for key in ("summary", "investigable_statement", "stop_condition", "disposition_reason"):
        string(candidate[key], f"{label}.{key}", nonempty=True)
    for key in ("technologies", "surfaces", "support_evidence_refs", "confirm_or_reject_evidence", "suggested_capabilities"):
        string_list(candidate[key], f"{label}.{key}", nonempty_items=True)
    if candidate["technologies"] != sorted(candidate["technologies"]):
        fail("E008", f"{label}.technologies must be lexicographically sorted")
    if not candidate["investigable_statement"].rstrip().endswith("?"):
        fail("E041", f"{label}.investigable_statement must be one direct question ending in ?")
    for action_index, action in enumerate(candidate["confirm_or_reject_evidence"]):
        if not any(action.startswith(prefix) and len(action) > len(prefix)
                   for prefix in LOOKUP_ACTION_PREFIXES):
            fail("E042", f"{label}.confirm_or_reject_evidence[{action_index}] must use an allowed lookup-action prefix and non-empty target")
    if candidate["duplicate_relation"] not in {"none", "exact-duplicate", "near-duplicate"}:
        fail("E010", f"{label}.duplicate_relation is invalid")
    if candidate["disposition"] not in {"selected", "rejected", "deferred"}:
        fail("E010", f"{label}.disposition is invalid")
    disposition = candidate["disposition"]
    reason_code = disposition_reason_code(candidate["disposition_reason"], disposition, label)
    relation = candidate["duplicate_relation"]
    if relation == "exact-duplicate" and (disposition != "rejected" or reason_code != "rejected:exact-duplicate"):
        fail("E028", f"{label} exact duplicate must be rejected with its exact reason code")
    if reason_code == "rejected:exact-duplicate" and relation != "exact-duplicate":
        fail("E028", f"{label} exact-duplicate reason requires exact-duplicate relation")
    if relation == "near-duplicate" and reason_code == "rejected:exact-duplicate":
        fail("E028", f"{label} near duplicate must remain distinct from exact duplicates")
    if disposition == "selected":
        if not candidate["support_evidence_refs"]:
            fail("E029", f"{label} selected candidate requires observable provenance support")
        if not candidate["confirm_or_reject_evidence"]:
            fail("E029", f"{label} selected candidate requires confirm-or-reject evidence")
        marker = " | decision-impact: "
        if marker not in candidate["disposition_reason"] or not candidate["disposition_reason"].split(marker, 1)[1]:
            fail("E043", f"{label} selected candidate requires non-empty decision-impact detail")
    locator, revision = candidate["catalog_locator"], candidate["catalog_revision"]
    if origin == "catalogued":
        string(locator, f"{label}.catalog_locator", nonempty=True)
        integer(revision, f"{label}.catalog_revision", positive=True)
    elif locator is not None or revision is not None:
        fail("E011", f"{label} generated candidates require null catalog fields")
    identity_domain: dict[str, Any]
    if origin == "catalogued":
        identity_domain = {"catalog_locator": locator, "catalog_revision": revision,
                           "semantic_payload": candidate_semantic_payload(candidate)}
        expected = "cat-" + digest(identity_domain)[7:]
    else:
        identity_domain = {"input_fingerprint": input_fingerprint,
                           "semantic_payload": candidate_semantic_payload(candidate)}
        expected = "gen-" + digest(identity_domain)[7:]
    if candidate["candidate_id"] != expected:
        fail("E012", f"{label}.candidate_id does not reproduce its canonical identity")
    return expected


def validate_duplicate_items(
        value: Any, label: str, relation: str,
        candidates_by_id: dict[str, dict[str, Any]]) -> tuple[set[str], set[str]]:
    if not isinstance(value, list):
        fail("E007", f"{label} must be an array")
    pairs: list[tuple[str, str]] = []
    related_ids: list[str] = []
    target_ids: list[str] = []
    for index, raw_item in enumerate(value):
        item_label = f"{label}[{index}]"
        item = mapping(raw_item, item_label, DUPLICATE_ITEM_KEYS)
        candidate_id = string(
            item["candidate_id"], f"{item_label}.candidate_id", nonempty=True)
        duplicate_of = string(
            item["duplicate_of"], f"{item_label}.duplicate_of", nonempty=True)
        if candidate_id not in candidates_by_id or duplicate_of not in candidates_by_id:
            fail("E036", f"{item_label} must reference existing candidate IDs")
        if candidate_id == duplicate_of:
            fail("E036", f"{item_label} must reference two distinct candidates")
        if candidates_by_id[candidate_id]["duplicate_relation"] != relation:
            fail("E036", f"{item_label}.candidate_id has the wrong duplicate relation")
        if candidates_by_id[duplicate_of]["duplicate_relation"] != "none":
            fail("E036", f"{item_label}.duplicate_of must be a canonical representative")
        pairs.append((candidate_id, duplicate_of))
        related_ids.append(candidate_id)
        target_ids.append(duplicate_of)
    if pairs != sorted(pairs) or len(related_ids) != len(set(related_ids)):
        fail("E037", f"{label} must be sorted and unique by candidate_id")
    return set(related_ids), set(target_ids)


def validate_preparation(obj: Any) -> None:
    obj = mapping(obj, "inference_preparation", PREP_KEYS)
    reject_runtime_ids(obj)
    if type(obj["schema_version"]) is not int or obj["schema_version"] != 3 or obj["artifact_type"] != "analytic-inference-preparation":
        fail("E010", "schema_version or artifact_type is invalid")
    if obj["status"] not in {"pre-investigation-complete", "partial", "blocked"}:
        fail("E010", "status is invalid")
    sha(obj["input_fingerprint"], "input_fingerprint")
    sha(obj["preparation_digest"], "preparation_digest")
    if not isinstance(obj["preparation_id"], str) or not re.fullmatch(r"prep-[0-9a-f]{64}", obj["preparation_id"]):
        fail("E005", "preparation_id is invalid")
    inp = mapping(obj["input"], "input", {"demand_digest", "ordered_source_digests", "request_controls", "request_controls_digest"})
    sha(inp["demand_digest"], "input.demand_digest")
    for index, value in enumerate(string_list(inp["ordered_source_digests"], "input.ordered_source_digests", nonempty_items=True)):
        sha(value, f"input.ordered_source_digests[{index}]")
    sha(inp["request_controls_digest"], "input.request_controls_digest")
    request_controls = mapping(inp["request_controls"], "input.request_controls", REQUEST_CONTROL_KEYS)
    if request_controls["candidate_ceiling"] is not None:
        fail("E031", "input.request_controls.candidate_ceiling must be null")
    integer(request_controls["catalog_retrieval_page_size"], "input.request_controls.catalog_retrieval_page_size", positive=True)
    integer(request_controls["minimum_candidate_floor"], "input.request_controls.minimum_candidate_floor", positive=True)
    if inp["request_controls_digest"] != digest(request_controls):
        fail("E030", "request_controls_digest does not reproduce the exact mapping")
    root = mapping(obj["root"], "root", {"consumer_root", "root_provenance"})
    string(root["consumer_root"], "root.consumer_root", nonempty=True)
    if root["root_provenance"] != "canonical-pwd": fail("E010", "root_provenance must be canonical-pwd")
    sources = mapping(obj["source_map"], "source_map", {"sources"})["sources"]
    if not isinstance(sources, list): fail("E007", "source_map.sources must be an array")
    actual_source_digests = []
    for index, source in enumerate(sources):
        source = mapping(source, f"source_map.sources[{index}]", {"locator", "digest", "facts"})
        string(source["locator"], f"source_map.sources[{index}].locator", nonempty=True)
        sha(source["digest"], f"source_map.sources[{index}].digest")
        if not isinstance(source["facts"], list): fail("E007", f"source_map.sources[{index}].facts must be an array")
        actual_source_digests.append(source["digest"])
    if actual_source_digests != inp["ordered_source_digests"]:
        fail("E013", "ordered_source_digests must equal source_map source order")
    policy = mapping(obj["policy"], "policy", {"policy_id", "policy_digest", "values"})
    string(policy["policy_id"], "policy.policy_id", nonempty=True); sha(policy["policy_digest"], "policy.policy_digest")
    if not isinstance(policy["values"], dict): fail("E002", "policy.values must be an object")
    for key in ("catalog_retrieval_page_size", "minimum_candidate_floor"):
        if key not in policy["values"]:
            fail("E031", f"policy.values.{key} is required for preparation v3")
        integer(policy["values"][key], f"policy.values.{key}", positive=True)
        if request_controls[key] != policy["values"][key]:
            fail("E031", f"request control {key} must equal policy.values.{key}")
    if policy["values"].get("candidate_ceiling", "missing") is not None:
        fail("E031", "policy.values.candidate_ceiling must be null")
    catalog = mapping(obj["catalog_observation"], "catalog_observation", {"state", "catalog_snapshot_digest", "indices_read", "record_locators_loaded", "diagnostics", "retrieval_pages_read", "retrieval_exhausted", "retrieval_resume_cursor"})
    state = catalog["state"]
    if state not in {"loaded", "absent", "empty", "no-match", "blocked"}: fail("E010", "catalog_observation.state is invalid")
    sha(catalog["catalog_snapshot_digest"], "catalog_snapshot_digest", nullable=True)
    if (state == "loaded") != (catalog["catalog_snapshot_digest"] is not None):
        fail("E014", "loaded catalog requires digest; non-loaded catalog requires null digest")
    for key in ("indices_read", "record_locators_loaded"):
        string_list(catalog[key], f"catalog_observation.{key}", sorted_unique=True, nonempty_items=True)
    diagnostics = string_list(
        catalog["diagnostics"], "catalog_observation.diagnostics",
        sorted_unique=True, nonempty_items=True)
    if any(not item for item in diagnostics):
        fail("E004", "catalog_observation.diagnostics items must be non-empty strings")
    integer(catalog["retrieval_pages_read"], "catalog_observation.retrieval_pages_read")
    if catalog["retrieval_pages_read"] < 0:
        fail("E006", "catalog_observation.retrieval_pages_read must be non-negative")
    if type(catalog["retrieval_exhausted"]) is not bool:
        fail("E010", "catalog_observation.retrieval_exhausted must be boolean")
    if catalog["retrieval_exhausted"]:
        if catalog["retrieval_resume_cursor"] is not None:
            fail("E039", "exhausted retrieval requires a null cursor")
    else:
        string(catalog["retrieval_resume_cursor"], "catalog_observation.retrieval_resume_cursor", nonempty=True)
        if obj["status"] == "pre-investigation-complete":
            fail("E039", "an unexhausted retrieval requires partial or blocked status")
    expected_fp = digest({"demand_digest": inp["demand_digest"], "ordered_source_digests": inp["ordered_source_digests"], "catalog_snapshot_digest": catalog["catalog_snapshot_digest"], "policy_digest": policy["policy_digest"], "request_controls_digest": inp["request_controls_digest"]})
    if obj["input_fingerprint"] != expected_fp: fail("E015", "input_fingerprint does not reproduce")
    string_list(obj["technologies"], "technologies", sorted_unique=True, nonempty_items=True)
    candidate_ids = [validate_candidate(item, obj["input_fingerprint"], index) for index, item in enumerate(obj["candidates"])] if isinstance(obj["candidates"], list) else fail("E007", "candidates must be an array")
    if candidate_ids != sorted(candidate_ids) or len(candidate_ids) != len(set(candidate_ids)):
        fail("E016", "candidates must be sorted by unique candidate_id")
    if state == "blocked" and (obj["status"] != "blocked" or any(item["origin"] == "catalogued" for item in obj["candidates"])):
        fail("E017", "blocked catalog cannot be represented as loaded or contain catalogued candidates")
    duplicate = mapping(obj["duplicate_analysis"], "duplicate_analysis", {"exact_duplicates", "near_duplicates"})
    candidates_by_id = {item["candidate_id"]: item for item in obj["candidates"]}
    exact_ids, exact_targets = validate_duplicate_items(
        duplicate["exact_duplicates"], "duplicate_analysis.exact_duplicates",
        "exact-duplicate", candidates_by_id)
    near_ids, near_targets = validate_duplicate_items(
        duplicate["near_duplicates"], "duplicate_analysis.near_duplicates",
        "near-duplicate", candidates_by_id)
    all_duplicate_ids = exact_ids | near_ids
    if len(all_duplicate_ids) != len(exact_ids) + len(near_ids):
        fail("E037", "candidate_id must be globally unique across duplicate_analysis")
    if all_duplicate_ids & (exact_targets | near_targets):
        fail("E036", "duplicate targets cannot form chains or cycles")
    expected_exact_ids = {
        item["candidate_id"] for item in obj["candidates"]
        if item["duplicate_relation"] == "exact-duplicate"}
    expected_near_ids = {
        item["candidate_id"] for item in obj["candidates"]
        if item["duplicate_relation"] == "near-duplicate"}
    if exact_ids != expected_exact_ids or near_ids != expected_near_ids:
        fail("E036", "duplicate_analysis must have bidirectional candidate relation parity")
    selected = string_list(obj["selected_for_investigation"], "selected_for_investigation", sorted_unique=True, nonempty_items=True)
    expected_selected = sorted(item["candidate_id"] for item in obj["candidates"] if item["disposition"] == "selected")
    if selected != expected_selected: fail("E018", "selected_for_investigation must equal selected candidate IDs")
    unresolved_deferred = [item for item in obj["candidates"] if item["disposition"] == "deferred"]
    if unresolved_deferred and obj["status"] == "pre-investigation-complete":
        fail("E033", "unresolved essential deferral requires partial or blocked status")
    if not isinstance(obj["planned_investigations"], list): fail("E007", "planned_investigations must be an array")
    plan_ids = []
    for index, intent in enumerate(obj["planned_investigations"]):
        label = f"planned_investigations[{index}]"
        intent = mapping(intent, label, {"candidate_id"})
        plan_ids.append(string(intent["candidate_id"], f"{label}.candidate_id", nonempty=True))
    if plan_ids != selected:
        fail("E019", "planned_investigations must exactly match selected candidates in sorted order")
    if obj["dispatch_admitted"] is not False: fail("E020", "dispatch_admitted must be false")
    generation = mapping(obj["generation_state"], "generation_state", {"completion_reason", "semantic_saturation", "resume_cursor", "unexplored_surfaces", "explored_surfaces", "final_pass_new_distinct_candidates", "saturation_evidence_refs"})
    if generation["completion_reason"] not in {"semantic-saturation", "context-interruption"}:
        fail("E010", "generation_state.completion_reason is invalid")
    if type(generation["semantic_saturation"]) is not bool:
        fail("E010", "generation_state.semantic_saturation must be boolean")
    string_list(generation["unexplored_surfaces"], "generation_state.unexplored_surfaces", sorted_unique=True, nonempty_items=True)
    explored = string_list(generation["explored_surfaces"], "generation_state.explored_surfaces", sorted_unique=True, nonempty_items=True)
    evidence_refs = string_list(generation["saturation_evidence_refs"], "generation_state.saturation_evidence_refs", sorted_unique=True, nonempty_items=True)
    if generation["completion_reason"] == "semantic-saturation":
        if (not generation["semantic_saturation"] or generation["resume_cursor"] is not None or
                generation["unexplored_surfaces"] or not explored or
                type(generation["final_pass_new_distinct_candidates"]) is not int or
                generation["final_pass_new_distinct_candidates"] != 0 or not evidence_refs):
            fail("E040", "semantic saturation requires explored surfaces and an evidenced zero-new-candidate final pass")
    else:
        if generation["semantic_saturation"]:
            fail("E040", "context interruption cannot claim semantic saturation")
        string(generation["resume_cursor"], "generation_state.resume_cursor", nonempty=True)
        if not generation["unexplored_surfaces"] or obj["status"] != "partial":
            fail("E040", "context interruption requires partial status and unexplored surfaces")
        if generation["final_pass_new_distinct_candidates"] is not None or evidence_refs:
            fail("E040", "context interruption cannot claim saturation evidence")
    material_count = sum(item["disposition"] != "rejected" for item in obj["candidates"])
    if material_count < request_controls["minimum_candidate_floor"] and not generation["semantic_saturation"] and obj["status"] != "partial":
        fail("E041", "below-floor generation without saturation must be partial and resumable")
    validators = string_list(obj["validators"], "validators", sorted_unique=True, nonempty_items=True)
    if not validators or any(not item for item in validators):
        fail("E035", "validators must name one or more checks that passed")
    blockers = string_list(obj["blockers"], "blockers", sorted_unique=True, nonempty_items=True)
    if any(not item for item in blockers):
        fail("E004", "blockers items must be non-empty strings")
    if obj["status"] == "partial" and not blockers and not diagnostics:
        fail("E034", "partial requires an observable non-blocking limitation")
    if obj["status"] == "pre-investigation-complete" and blockers:
        fail("E038", "pre-investigation-complete requires an empty blockers array")
    string(obj["minimum_next_path"], "minimum_next_path", nonempty=True)
    boundary = mapping(obj["execution_boundary"], "execution_boundary", set(BOUNDARY))
    for key in ("dispatch_authorized", "web_research_performed", "catalog_mutation_applied"):
        if type(boundary[key]) is not bool or boundary[key] is not False:
            fail("E021", "execution_boundary must be literal zero/false/empty boundary")
    for key in ("investigation_handoffs_dispatched", "agent_runs_created", "handoffs_created"):
        if type(boundary[key]) is not int or boundary[key] != 0:
            fail("E021", "execution_boundary must be literal zero/false/empty boundary")
    if type(boundary["downstream_workflows_invoked"]) is not list or boundary["downstream_workflows_invoked"]:
        fail("E021", "execution_boundary must be literal zero/false/empty boundary")
    expected_prep = "prep-" + digest({"input_fingerprint": obj["input_fingerprint"], "candidate_ids": sorted(candidate_ids)})[7:]
    if obj["preparation_id"] != expected_prep: fail("E022", "preparation_id does not reproduce")
    digest_domain = dict(obj); del digest_domain["preparation_digest"]
    if obj["preparation_digest"] != digest(digest_domain): fail("E023", "preparation_digest does not reproduce")


def validate_preparation_failure(obj: Any) -> None:
    wrapper = mapping(obj, "preparation_failure_response", FAILURE_WRAPPER_KEYS)
    failure = mapping(wrapper["preparation_failure"], "preparation_failure", FAILURE_KEYS)
    if failure["status"] != "blocked":
        fail("E044", "preparation_failure.status must be blocked")
    if failure["stage"] not in FAILURE_STAGES:
        fail("E044", "preparation_failure.stage is invalid")
    blockers = string_list(failure["blockers"], "preparation_failure.blockers",
                           sorted_unique=True, nonempty_items=True)
    if not blockers:
        fail("E044", "preparation_failure.blockers must be non-empty")
    string(failure["minimum_next_path"], "preparation_failure.minimum_next_path", nonempty=True)
    boundary = mapping(failure["execution_boundary"],
                       "preparation_failure.execution_boundary", set(BOUNDARY))
    for key in ("dispatch_authorized", "web_research_performed", "catalog_mutation_applied"):
        if type(boundary[key]) is not bool or boundary[key] is not False:
            fail("E021", "preparation_failure.execution_boundary must be literal zero/false/empty boundary")
    for key in ("investigation_handoffs_dispatched", "agent_runs_created", "handoffs_created"):
        if type(boundary[key]) is not int or boundary[key] != 0:
            fail("E021", "preparation_failure.execution_boundary must be literal zero/false/empty boundary")
    if type(boundary["downstream_workflows_invoked"]) is not list or boundary["downstream_workflows_invoked"]:
        fail("E021", "preparation_failure.execution_boundary must be literal zero/false/empty boundary")


def fixture() -> dict[str, Any]:
    controls = {"candidate_ceiling": None, "catalog_retrieval_page_size": 20, "minimum_candidate_floor": 8}
    value: dict[str, Any] = {"schema_version": 3, "artifact_type": "analytic-inference-preparation", "preparation_id": "", "input_fingerprint": "", "preparation_digest": "", "status": "pre-investigation-complete", "input": {"demand_digest": "sha256:" + "1" * 64, "ordered_source_digests": ["sha256:" + "2" * 64], "request_controls": controls, "request_controls_digest": digest(controls)}, "root": {"consumer_root": "/fixture", "root_provenance": "canonical-pwd"}, "source_map": {"sources": [{"locator": "source.md", "digest": "sha256:" + "2" * 64, "facts": []}]}, "policy": {"policy_id": "fixture-policy", "policy_digest": "sha256:" + "4" * 64, "values": {"candidate_ceiling": None, "catalog_retrieval_page_size": 20, "minimum_candidate_floor": 8}}, "catalog_observation": {"state": "no-match", "catalog_snapshot_digest": None, "indices_read": [], "record_locators_loaded": [], "diagnostics": [], "retrieval_pages_read": 0, "retrieval_exhausted": True, "retrieval_resume_cursor": None}, "technologies": [], "candidates": [], "duplicate_analysis": {"exact_duplicates": [], "near_duplicates": []}, "selected_for_investigation": [], "planned_investigations": [], "dispatch_admitted": False, "generation_state": {"completion_reason": "semantic-saturation", "semantic_saturation": True, "resume_cursor": None, "unexplored_surfaces": [], "explored_surfaces": ["fixture-surface"], "final_pass_new_distinct_candidates": 0, "saturation_evidence_refs": ["source.md#final-pass"]}, "validators": ["fixture"], "blockers": [], "minimum_next_path": "return-to-caller", "execution_boundary": copy.deepcopy(BOUNDARY)}
    refresh_identities(value)
    return value


def refresh_identities(value: dict[str, Any]) -> None:
    """Recalculate all content-addressed fields for an in-memory fixture."""
    value["input"]["request_controls_digest"] = digest(value["input"]["request_controls"])
    catalog_digest = value["catalog_observation"]["catalog_snapshot_digest"]
    value["input_fingerprint"] = digest({"demand_digest": value["input"]["demand_digest"], "ordered_source_digests": value["input"]["ordered_source_digests"], "catalog_snapshot_digest": catalog_digest, "policy_digest": value["policy"]["policy_digest"], "request_controls_digest": value["input"]["request_controls_digest"]})
    for candidate in value["candidates"]:
        semantic_payload = candidate_semantic_payload(candidate)
        if candidate["origin"] == "catalogued":
            identity_domain = {"catalog_locator": candidate["catalog_locator"],
                               "catalog_revision": candidate["catalog_revision"],
                               "semantic_payload": semantic_payload}
            candidate["candidate_id"] = "cat-" + digest(identity_domain)[7:]
        else:
            identity_domain = {"input_fingerprint": value["input_fingerprint"],
                               "semantic_payload": semantic_payload}
            candidate["candidate_id"] = "gen-" + digest(identity_domain)[7:]
    value["candidates"].sort(key=lambda candidate: candidate["candidate_id"])
    value["selected_for_investigation"] = sorted(
        candidate["candidate_id"] for candidate in value["candidates"]
        if candidate["disposition"] == "selected")
    value["planned_investigations"] = [
        {"candidate_id": candidate_id} for candidate_id in value["selected_for_investigation"]]
    value["preparation_id"] = "prep-" + digest({"input_fingerprint": value["input_fingerprint"], "candidate_ids": [candidate["candidate_id"] for candidate in value["candidates"]]})[7:]
    domain = dict(value); del domain["preparation_digest"]; value["preparation_digest"] = digest(domain)


def fixture_path(name: str) -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "fixtures" / name


def load_fixture(name: str) -> dict[str, Any]:
    try:
        value = json.loads(fixture_path(name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssertionError(f"fixture {name} is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise AssertionError(f"fixture {name} must be an object")
    return value


def generated_candidate(summary: str, disposition: str = "selected") -> dict[str, Any]:
    return {
        "candidate_id": "", "origin": "generated", "lifecycle_status": "unreviewed",
        "summary": summary, "investigable_statement": f"What existing context resolves {summary}?",
        "technologies": ["fixture"], "surfaces": ["fixture-surface"],
        "support_evidence_refs": ["source.md#fixture"],
        "confirm_or_reject_evidence": ["search-docs: fixture-check"],
        "stop_condition": "fixture stop",
        "catalog_locator": None, "catalog_revision": None, "duplicate_relation": "none",
        "disposition": disposition,
        "disposition_reason": {
            "selected": "selected:essential-criteria-satisfied | decision-impact: fixture answer changes a later decision",
            "rejected": "rejected:irrelevant",
            "deferred": "deferred:context",
        }[disposition],
        "suggested_capabilities": [],
    }


def candidate_from_fixture(spec: dict[str, Any]) -> dict[str, Any]:
    label = spec.get("label")
    disposition = spec.get("disposition", "selected")
    if not isinstance(label, str) or not label or disposition not in {"selected", "rejected", "deferred"}:
        raise AssertionError("fixture candidate needs a non-empty label and valid disposition")
    candidate = generated_candidate(label, disposition)
    candidate["duplicate_relation"] = spec.get("duplicate_relation", "none")
    candidate["disposition_reason"] = spec.get("reason", candidate["disposition_reason"])
    for key in ("support_evidence_refs", "confirm_or_reject_evidence"):
        if key in spec:
            candidate[key] = spec[key]
    if spec.get("origin", "generated") == "catalogued":
        candidate.update({"origin": "catalogued", "catalog_locator": f"records/{label}.xml", "catalog_revision": 1})
    elif spec.get("origin", "generated") != "generated":
        raise AssertionError("fixture candidate origin is invalid")
    return candidate


def apply_fixture_duplicate_analysis(
        value: dict[str, Any], specs: list[dict[str, Any]]) -> None:
    ids_by_summary = {
        candidate["summary"]: candidate["candidate_id"]
        for candidate in value["candidates"]}
    analysis = {"exact_duplicates": [], "near_duplicates": []}
    for spec in specs:
        relation = spec.get("duplicate_relation", "none")
        duplicate_of = spec.get("duplicate_of")
        if relation == "none":
            if duplicate_of is not None:
                raise AssertionError("fixture duplicate_of requires a duplicate relation")
            continue
        if not isinstance(duplicate_of, str) or duplicate_of not in ids_by_summary:
            raise AssertionError("fixture duplicate relation requires an existing duplicate_of label")
        key = "exact_duplicates" if relation == "exact-duplicate" else "near_duplicates"
        analysis[key].append({
            "candidate_id": ids_by_summary[spec["label"]],
            "duplicate_of": ids_by_summary[duplicate_of],
        })
    for key in analysis:
        analysis[key].sort(key=lambda item: (item["candidate_id"], item["duplicate_of"]))
    value["duplicate_analysis"] = analysis


def assert_case_matrix() -> None:
    matrix = load_fixture("preparation-cases.json")
    if matrix.get("schema_version") != 3 or matrix.get("fixture_kind") != "analytic-inference-preparation-case-matrix":
        raise AssertionError("preparation case matrix schema is invalid")
    if matrix.get("byte_replay_is_out_of_scope") is not True or matrix.get("execution_boundary") != BOUNDARY:
        raise AssertionError("case matrix must declare byte replay out of scope and literal zero boundary")
    cases = matrix.get("cases")
    if not isinstance(cases, list): raise AssertionError("case matrix cases must be an array")
    required_case_ids = {"loaded-relevant-without-cost", "registry-absent", "catalog-empty", "technology-no-match", "catalog-blocked", "candidate-outcomes-and-duplicates", "more-than-floor-preserved", "below-floor-saturated", "below-floor-context-resume", "page-boundary-resume", "adversarial-order"}
    if {case.get("id") for case in cases if isinstance(case, dict)} != required_case_ids:
        raise AssertionError("case matrix lacks required unique scenarios")
    for case in cases:
        if not isinstance(case, dict): raise AssertionError("case matrix item must be an object")
        scenario = case.get("scenario")
        if not isinstance(scenario, dict) or set(scenario) != {"input", "expected"}:
            raise AssertionError(f"{case.get('id')}: scenario must contain input and expected")
        fixture_input, expected = scenario["input"], scenario["expected"]
        if not isinstance(fixture_input, dict) or not isinstance(expected, dict):
            raise AssertionError(f"{case.get('id')}: scenario input and expected must be objects")
        value = fixture()
        minimum_floor = fixture_input.get("minimum_candidate_floor", 8)
        if not isinstance(minimum_floor, int) or isinstance(minimum_floor, bool) or minimum_floor <= 0:
            raise AssertionError(f"{case['id']}: minimum_candidate_floor must be a positive integer")
        value["input"]["request_controls"]["minimum_candidate_floor"] = minimum_floor
        value["policy"]["values"]["minimum_candidate_floor"] = minimum_floor
        state, expected_status = fixture_input.get("catalog_state"), expected.get("status")
        value["catalog_observation"]["state"] = state
        value["catalog_observation"]["catalog_snapshot_digest"] = ("sha256:" + "5" * 64) if fixture_input.get("catalog_snapshot") else None
        if (value["catalog_observation"]["catalog_snapshot_digest"] is not None) != (state == "loaded"):
            raise AssertionError(f"{case['id']}: catalog snapshot nullability differs from state")
        diagnostics = fixture_input.get("catalog_diagnostics", [])
        if not isinstance(diagnostics, list):
            raise AssertionError(f"{case['id']}: catalog_diagnostics must be an array")
        value["catalog_observation"]["diagnostics"] = diagnostics
        value["status"] = expected_status
        value["catalog_observation"]["retrieval_pages_read"] = fixture_input.get("retrieval_pages_read", 0)
        value["catalog_observation"]["retrieval_exhausted"] = fixture_input.get("retrieval_exhausted", True)
        value["catalog_observation"]["retrieval_resume_cursor"] = fixture_input.get("retrieval_resume_cursor")
        value["generation_state"] = copy.deepcopy(fixture_input.get("generation_state", value["generation_state"]))
        if expected_status == "partial" and not diagnostics:
            value["blockers"] = ["fixture partial limitation"]
        if state == "blocked": value["minimum_next_path"] = "repair-permitted-catalog-input"
        specs = fixture_input.get("candidates")
        if not isinstance(specs, list): raise AssertionError(f"{case['id']}: candidates must be an array")
        value["candidates"] = [candidate_from_fixture(spec) for spec in specs if isinstance(spec, dict)]
        if len(value["candidates"]) != len(specs): raise AssertionError(f"{case['id']}: candidate must be an object")
        refresh_identities(value)
        apply_fixture_duplicate_analysis(value, specs)
        refresh_identities(value); validate_preparation(value)
        actual_dispositions = {candidate["summary"]: candidate["disposition"] for candidate in value["candidates"]}
        if actual_dispositions != expected.get("dispositions"):
            raise AssertionError(f"{case['id']}: candidate dispositions differ from fixture expectation")
        for excluded_key in expected.get("candidate_keys_exclude", []):
            if any(excluded_key in candidate for candidate in value["candidates"]):
                raise AssertionError(f"{case['id']}: legacy candidate key {excluded_key!r} was retained")
        expected_relations = expected.get("duplicate_relations")
        if expected_relations is not None:
            actual_relations = {candidate["summary"]: candidate["duplicate_relation"] for candidate in value["candidates"]}
            if actual_relations != expected_relations:
                raise AssertionError(f"{case['id']}: duplicate relations differ from fixture expectation")
        selected_count = len(value["selected_for_investigation"])
        if selected_count != expected.get("selected_count"):
            raise AssertionError(f"{case['id']}: selected count differs from fixture expectation")
        if expected.get("all_material_candidates_preserved") and len(value["candidates"]) != len(specs):
            raise AssertionError(f"{case['id']}: material candidates were truncated")
    adversarial = next(case["scenario"]["input"] for case in cases if case["id"] == "adversarial-order")
    ordered = fixture(); ordered["catalog_observation"].update({"state": adversarial["catalog_state"], "catalog_snapshot_digest": "sha256:" + "5" * 64})
    ordered["candidates"] = [candidate_from_fixture(spec) for spec in adversarial["candidates"]]
    refresh_identities(ordered); validate_preparation(ordered)
    reversed_input = copy.deepcopy(ordered); reversed_input["candidates"].reverse(); refresh_identities(reversed_input)
    if ordered != reversed_input:
        raise AssertionError("adversarial candidate order did not normalize to one canonical preparation")


def assert_structural_parity() -> None:
    parity = load_fixture("parity-cases.json")
    expected = parity.get("expected", {})
    projections = parity.get("caller_projections")
    if parity.get("schema_version") != 3 or parity.get("byte_replay_is_out_of_scope") is not True or not isinstance(projections, dict) or set(projections) != {"loki-deep-analysis", "loki-generate-inferences"}:
        raise AssertionError("parity fixture is invalid")
    common = parity.get("common_normalized_input")
    if not isinstance(common, dict): raise AssertionError("parity fixture has no common normalized input")
    outputs = []
    for _caller, projection in projections.items():
        if not isinstance(projection, dict) or not {"command", "run_id", "destination"} <= set(projection):
            raise AssertionError("caller projection is incomplete")
        value = fixture()
        value["input"]["demand_digest"] = common["demand_digest"]
        value["input"]["request_controls"] = copy.deepcopy(common["request_controls"])
        value["policy"]["values"] = copy.deepcopy(common["request_controls"])
        value["source_map"]["sources"] = common["sources"]
        value["input"]["ordered_source_digests"] = [source["digest"] for source in common["sources"]]
        value["policy"].update({"policy_id": common["policy_id"], "policy_digest": common["policy_digest"]})
        value["catalog_observation"]["state"] = common["catalog_state"]
        value["catalog_observation"]["catalog_snapshot_digest"] = None
        value["candidates"] = [generated_candidate("shared normalized candidate")]
        refresh_identities(value); validate_preparation(value); outputs.append(value)
    if outputs[0] != outputs[1]: raise AssertionError("caller projections produced unequal preparation cores")
    if expected.get("zero_dispatch_web_downstream") is not True or outputs[0]["execution_boundary"] != BOUNDARY:
        raise AssertionError("parity fixture did not retain zero execution boundary")
    if sorted(outputs[0]["input"]["request_controls"]) != expected.get("request_controls_exact_keys"):
        raise AssertionError("parity fixture request_controls keys differ from v3 contract")
    for excluded_key in expected.get("candidate_keys_exclude", []):
        if any(excluded_key in candidate for candidate in outputs[0]["candidates"]):
            raise AssertionError(f"parity fixture retained legacy candidate key {excluded_key!r}")
    for field in expected.get("equal_fields", []):
        if outputs[0][field] != outputs[1][field]: raise AssertionError(f"parity differs for {field}")


def self_test() -> None:
    good = fixture(); validate_preparation(good)
    failure = {"preparation_failure": {
        "status": "blocked", "stage": "input",
        "blockers": ["normalized demand is missing"],
        "minimum_next_path": "supply-normalized-demand",
        "execution_boundary": copy.deepcopy(BOUNDARY),
    }}
    validate_preparation_failure(failure)
    invalid_failure = copy.deepcopy(failure)
    invalid_failure["preparation_failure"]["blockers"] = []
    try:
        validate_preparation_failure(invalid_failure)
    except ValidationError as exc:
        if exc.code != "E044":
            raise AssertionError(f"preparation-failure-empty-blocker: expected E044, got {exc.code}")
    else:
        raise AssertionError("preparation-failure-empty-blocker: accepted invalid envelope")
    partial = fixture()
    partial["status"] = "partial"
    partial["blockers"] = ["observable non-blocking fixture limitation"]
    refresh_identities(partial); validate_preparation(partial)
    def blocked_as_loaded(value: dict[str, Any]) -> None:
        value["catalog_observation"]["state"] = "blocked"
        refresh_identities(value)

    def legacy_candidate_keys(value: dict[str, Any]) -> None:
        value["candidates"] = [generated_candidate("legacy")]
        refresh_identities(value)
        value["candidates"][0].update({"cost": "unknown", "impact": "unknown"})

    def selected_exact_duplicate(value: dict[str, Any]) -> None:
        candidate = generated_candidate("duplicate")
        candidate["duplicate_relation"] = "exact-duplicate"
        value["candidates"] = [candidate]
        refresh_identities(value)

    def selected_without_support(value: dict[str, Any]) -> None:
        candidate = generated_candidate("unsupported")
        candidate["support_evidence_refs"] = []
        value["candidates"] = [candidate]
        refresh_identities(value)

    def implementation_task_statement(value: dict[str, Any]) -> None:
        candidate = generated_candidate("implementation task")
        candidate["investigable_statement"] = "Implement the requested solution"
        value["candidates"] = [candidate]
        refresh_identities(value)

    def invalid_lookup_action(value: dict[str, Any]) -> None:
        candidate = generated_candidate("invalid lookup")
        candidate["confirm_or_reject_evidence"] = ["look somewhere"]
        value["candidates"] = [candidate]
        refresh_identities(value)

    def selected_without_decision_impact(value: dict[str, Any]) -> None:
        candidate = generated_candidate("missing decision impact")
        candidate["disposition_reason"] = "selected:essential-criteria-satisfied"
        value["candidates"] = [candidate]
        refresh_identities(value)

    def planned_investigation_extra_key(value: dict[str, Any]) -> None:
        value["candidates"] = [generated_candidate("planned-extra")]
        refresh_identities(value)
        value["planned_investigations"][0]["extra"] = True

    def planned_investigation_missing_key(value: dict[str, Any]) -> None:
        value["candidates"] = [generated_candidate("planned-missing")]
        refresh_identities(value)
        value["planned_investigations"][0].pop("candidate_id")

    def planned_investigation_non_string(value: dict[str, Any]) -> None:
        value["candidates"] = [generated_candidate("planned-non-string")]
        refresh_identities(value)
        value["planned_investigations"][0]["candidate_id"] = None

    def loaded_without_snapshot(value: dict[str, Any]) -> None:
        value["catalog_observation"]["state"] = "loaded"
        value["catalog_observation"]["catalog_snapshot_digest"] = None
        refresh_identities(value)

    def blocked_with_snapshot(value: dict[str, Any]) -> None:
        value["status"] = "blocked"
        value["catalog_observation"]["state"] = "blocked"
        value["catalog_observation"]["catalog_snapshot_digest"] = "sha256:" + "5" * 64
        refresh_identities(value)

    def saturation_without_evidence(value: dict[str, Any]) -> None:
        value["generation_state"]["explored_surfaces"] = []
        value["generation_state"]["saturation_evidence_refs"] = []
        refresh_identities(value)

    def empty_candidate_semantic_item(value: dict[str, Any], key: str) -> None:
        candidate = generated_candidate(f"empty-{key}")
        candidate[key] = [""]
        value["candidates"] = [candidate]
        refresh_identities(value)

    def empty_explored_surface(value: dict[str, Any]) -> None:
        value["generation_state"]["explored_surfaces"] = [""]
        refresh_identities(value)

    def empty_unexplored_surface(value: dict[str, Any]) -> None:
        value["status"] = "partial"
        value["blockers"] = ["context interrupted before surface exploration"]
        value["generation_state"].update({
            "completion_reason": "context-interruption",
            "semantic_saturation": False,
            "resume_cursor": "surface:pending",
            "unexplored_surfaces": [""],
            "final_pass_new_distinct_candidates": None,
            "saturation_evidence_refs": [],
        })
        refresh_identities(value)

    def empty_catalog_semantic_item(value: dict[str, Any], key: str) -> None:
        value["catalog_observation"][key] = [""]
        refresh_identities(value)

    def empty_top_level_technology(value: dict[str, Any]) -> None:
        value["technologies"] = [""]
        refresh_identities(value)

    def install_duplicate_specs(
            value: dict[str, Any], specs: list[dict[str, Any]]) -> None:
        value["candidates"] = [candidate_from_fixture(spec) for spec in specs]
        refresh_identities(value)
        apply_fixture_duplicate_analysis(value, specs)
        refresh_identities(value)

    def install_duplicate_fixture(value: dict[str, Any]) -> None:
        install_duplicate_specs(value, [
            {"label": "canonical", "disposition": "selected"},
            {"label": "exact", "disposition": "rejected",
             "duplicate_relation": "exact-duplicate", "duplicate_of": "canonical",
             "reason": "rejected:exact-duplicate | fixture exact pair"},
            {"label": "near-a", "disposition": "selected",
             "duplicate_relation": "near-duplicate", "duplicate_of": "canonical",
             "reason": "selected:essential-criteria-satisfied | decision-impact: fixture near pair a remains decision-relevant"},
            {"label": "near-b", "disposition": "selected",
             "duplicate_relation": "near-duplicate", "duplicate_of": "canonical",
             "reason": "selected:essential-criteria-satisfied | decision-impact: fixture near pair b remains decision-relevant"},
        ])

    def duplicate_extra_key(value: dict[str, Any]) -> None:
        install_duplicate_fixture(value)
        value["duplicate_analysis"]["exact_duplicates"][0]["extra"] = True

    def duplicate_unknown_id(value: dict[str, Any]) -> None:
        install_duplicate_fixture(value)
        value["duplicate_analysis"]["exact_duplicates"][0]["duplicate_of"] = "gen-" + "f" * 64

    def duplicate_self_pair(value: dict[str, Any]) -> None:
        install_duplicate_fixture(value)
        item = value["duplicate_analysis"]["exact_duplicates"][0]
        item["duplicate_of"] = item["candidate_id"]

    def duplicate_wrong_relation(value: dict[str, Any]) -> None:
        install_duplicate_fixture(value)
        value["duplicate_analysis"]["exact_duplicates"][0]["candidate_id"] = \
            value["duplicate_analysis"]["near_duplicates"][0]["candidate_id"]

    def duplicate_missing_parity(value: dict[str, Any]) -> None:
        install_duplicate_fixture(value)
        value["duplicate_analysis"]["exact_duplicates"] = []

    def duplicate_wrong_order(value: dict[str, Any]) -> None:
        install_duplicate_fixture(value)
        value["duplicate_analysis"]["near_duplicates"].reverse()

    def duplicate_repeated_candidate(value: dict[str, Any]) -> None:
        install_duplicate_fixture(value)
        value["duplicate_analysis"]["near_duplicates"].append(
            copy.deepcopy(value["duplicate_analysis"]["near_duplicates"][0]))

    def duplicate_reciprocal_exact(value: dict[str, Any]) -> None:
        install_duplicate_specs(value, [
            {"label": "exact-a", "disposition": "rejected",
             "duplicate_relation": "exact-duplicate", "duplicate_of": "exact-b",
             "reason": "rejected:exact-duplicate | reciprocal fixture a"},
            {"label": "exact-b", "disposition": "rejected",
             "duplicate_relation": "exact-duplicate", "duplicate_of": "exact-a",
             "reason": "rejected:exact-duplicate | reciprocal fixture b"},
        ])

    def duplicate_reciprocal_near(value: dict[str, Any]) -> None:
        install_duplicate_specs(value, [
            {"label": "near-a", "disposition": "selected",
             "duplicate_relation": "near-duplicate", "duplicate_of": "near-b",
             "reason": "selected:essential-criteria-satisfied | decision-impact: reciprocal fixture a remains decision-relevant"},
            {"label": "near-b", "disposition": "selected",
             "duplicate_relation": "near-duplicate", "duplicate_of": "near-a",
             "reason": "selected:essential-criteria-satisfied | decision-impact: reciprocal fixture b remains decision-relevant"},
        ])

    def duplicate_chain(value: dict[str, Any]) -> None:
        install_duplicate_specs(value, [
            {"label": "canonical", "disposition": "selected"},
            {"label": "exact-a", "disposition": "rejected",
             "duplicate_relation": "exact-duplicate", "duplicate_of": "exact-b",
             "reason": "rejected:exact-duplicate | chain fixture a"},
            {"label": "exact-b", "disposition": "rejected",
             "duplicate_relation": "exact-duplicate", "duplicate_of": "canonical",
             "reason": "rejected:exact-duplicate | chain fixture b"},
        ])

    def duplicate_cross_array_chain(value: dict[str, Any]) -> None:
        install_duplicate_specs(value, [
            {"label": "canonical", "disposition": "selected"},
            {"label": "exact", "disposition": "rejected",
             "duplicate_relation": "exact-duplicate", "duplicate_of": "near",
             "reason": "rejected:exact-duplicate | cross-array fixture"},
            {"label": "near", "disposition": "selected",
             "duplicate_relation": "near-duplicate", "duplicate_of": "canonical",
             "reason": "selected:essential-criteria-satisfied | decision-impact: cross-array fixture remains decision-relevant"},
        ])

    duplicate_good = fixture(); install_duplicate_fixture(duplicate_good)
    validate_preparation(duplicate_good)

    cases = [
        ("tampered-digest", lambda x: x.__setitem__("preparation_digest", "sha256:" + "0" * 64), "E023"),
        ("extra-field", lambda x: x.__setitem__("extra", True), "E003"),
        ("legacy-schema-v2", lambda x: x.__setitem__("schema_version", 2), "E010"),
        ("schema-version-bool", lambda x: x.__setitem__("schema_version", True), "E010"),
        ("schema-version-float", lambda x: x.__setitem__("schema_version", 3.0), "E010"),
        ("schema-version-string", lambda x: x.__setitem__("schema_version", "3"), "E010"),
        ("request-page-size-bool", lambda x: x["input"]["request_controls"].__setitem__("catalog_retrieval_page_size", True), "E006"),
        ("request-floor-float", lambda x: x["input"]["request_controls"].__setitem__("minimum_candidate_floor", 8.0), "E006"),
        ("request-floor-string", lambda x: x["input"]["request_controls"].__setitem__("minimum_candidate_floor", "8"), "E006"),
        ("policy-page-size-float", lambda x: x["policy"]["values"].__setitem__("catalog_retrieval_page_size", 20.0), "E006"),
        ("policy-floor-bool", lambda x: x["policy"]["values"].__setitem__("minimum_candidate_floor", True), "E006"),
        ("retrieval-pages-bool", lambda x: x["catalog_observation"].__setitem__("retrieval_pages_read", False), "E006"),
        ("retrieval-pages-float", lambda x: x["catalog_observation"].__setitem__("retrieval_pages_read", 0.0), "E006"),
        ("retrieval-pages-string", lambda x: x["catalog_observation"].__setitem__("retrieval_pages_read", "0"), "E006"),
        ("retrieval-exhausted-integer", lambda x: x["catalog_observation"].__setitem__("retrieval_exhausted", 1), "E010"),
        ("semantic-saturation-integer", lambda x: x["generation_state"].__setitem__("semantic_saturation", 1), "E010"),
        ("final-pass-count-bool", lambda x: x["generation_state"].__setitem__("final_pass_new_distinct_candidates", False), "E040"),
        ("final-pass-count-float", lambda x: x["generation_state"].__setitem__("final_pass_new_distinct_candidates", 0.0), "E040"),
        ("final-pass-count-string", lambda x: x["generation_state"].__setitem__("final_pass_new_distinct_candidates", "0"), "E040"),
        ("boundary-count-bool", lambda x: x["execution_boundary"].__setitem__("agent_runs_created", False), "E021"),
        ("boundary-count-float", lambda x: x["execution_boundary"].__setitem__("handoffs_created", 0.0), "E021"),
        ("boundary-count-string", lambda x: x["execution_boundary"].__setitem__("investigation_handoffs_dispatched", "0"), "E021"),
        ("boundary-boolean-integer", lambda x: x["execution_boundary"].__setitem__("dispatch_authorized", 0), "E021"),
        ("legacy-candidate-cost-impact", legacy_candidate_keys, "E003"),
        ("request-control-extra-key", lambda x: x["input"]["request_controls"].__setitem__("cost_budget", 6), "E003"),
        ("request-control-digest", lambda x: x["input"].__setitem__("request_controls_digest", "sha256:" + "0" * 64), "E030"),
        ("invalid-order", lambda x: x.__setitem__("technologies", ["z", "a"]), "E008"),
        ("dispatch-nonzero", lambda x: x["execution_boundary"].__setitem__("agent_runs_created", 1), "E021"),
        ("blocked-as-loaded", blocked_as_loaded, "E017"),
        ("loaded-without-snapshot", loaded_without_snapshot, "E014"),
        ("blocked-with-snapshot", blocked_with_snapshot, "E014"),
        ("saturation-without-evidence", saturation_without_evidence, "E040"),
        ("saturation-empty-evidence-reference", lambda x: x["generation_state"].__setitem__("saturation_evidence_refs", [""]), "E004"),
        ("empty-explored-surface", empty_explored_surface, "E004"),
        ("empty-unexplored-surface", empty_unexplored_surface, "E004"),
        ("empty-candidate-technology", lambda x: empty_candidate_semantic_item(x, "technologies"), "E004"),
        ("empty-candidate-surface", lambda x: empty_candidate_semantic_item(x, "surfaces"), "E004"),
        ("empty-candidate-support-reference", lambda x: empty_candidate_semantic_item(x, "support_evidence_refs"), "E004"),
        ("empty-candidate-confirm-reference", lambda x: empty_candidate_semantic_item(x, "confirm_or_reject_evidence"), "E004"),
        ("empty-candidate-capability", lambda x: empty_candidate_semantic_item(x, "suggested_capabilities"), "E004"),
        ("empty-catalog-index", lambda x: empty_catalog_semantic_item(x, "indices_read"), "E004"),
        ("empty-record-locator", lambda x: empty_catalog_semantic_item(x, "record_locators_loaded"), "E004"),
        ("empty-top-level-technology", empty_top_level_technology, "E004"),
        ("selected-exact-duplicate", selected_exact_duplicate, "E028"),
        ("selected-without-support", selected_without_support, "E029"),
        ("implementation-task-statement", implementation_task_statement, "E041"),
        ("invalid-lookup-action", invalid_lookup_action, "E042"),
        ("selected-without-decision-impact", selected_without_decision_impact, "E043"),
        ("planned-investigation-extra-key", planned_investigation_extra_key, "E003"),
        ("planned-investigation-missing-key", planned_investigation_missing_key, "E003"),
        ("planned-investigation-non-string", planned_investigation_non_string, "E004"),
        ("partial-without-limitation", lambda x: x.__setitem__("status", "partial"), "E034"),
        ("validators-empty", lambda x: x.__setitem__("validators", []), "E035"),
        ("validators-empty-name", lambda x: x.__setitem__("validators", [""]), "E004"),
        ("validators-not-sorted", lambda x: x.__setitem__("validators", ["z-check", "a-check"]), "E008"),
        ("validators-not-unique", lambda x: x.__setitem__("validators", ["check", "check"]), "E008"),
        ("complete-with-blocker", lambda x: x.__setitem__("blockers", ["unresolved blocker"]), "E038"),
        ("duplicate-extra-key", duplicate_extra_key, "E003"),
        ("duplicate-unknown-id", duplicate_unknown_id, "E036"),
        ("duplicate-self-pair", duplicate_self_pair, "E036"),
        ("duplicate-wrong-relation", duplicate_wrong_relation, "E036"),
        ("duplicate-missing-parity", duplicate_missing_parity, "E036"),
        ("duplicate-wrong-order", duplicate_wrong_order, "E037"),
        ("duplicate-repeated-candidate", duplicate_repeated_candidate, "E037"),
        ("duplicate-reciprocal-exact", duplicate_reciprocal_exact, "E036"),
        ("duplicate-reciprocal-near", duplicate_reciprocal_near, "E036"),
        ("duplicate-chain", duplicate_chain, "E036"),
        ("duplicate-cross-array-chain", duplicate_cross_array_chain, "E036"),
    ]
    for name, mutate, code in cases:
        case = fixture(); mutate(case)
        try: validate_preparation(case)
        except ValidationError as exc:
            if exc.code != code: raise AssertionError(f"{name}: expected {code}, got {exc.code}")
        else: raise AssertionError(f"{name}: accepted invalid fixture")
    assert_case_matrix()
    assert_structural_parity()
    print("self-test: ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="canonical JSON file; stdin when omitted")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            if args.input: fail("E024", "--self-test accepts no input file")
            self_test(); return 0
        raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
        try: value = json.loads(raw)
        except json.JSONDecodeError as exc: fail("E025", f"invalid JSON: {exc.msg}")
        if raw != canonical_json(value): fail("E026", "input must itself be canonical JSON")
        if isinstance(value, dict) and set(value) == FAILURE_WRAPPER_KEYS:
            validate_preparation_failure(value)
        else:
            validate_preparation(value)
        print("valid"); return 0
    except ValidationError as exc:
        print(f"{exc.code}: {exc.message}", file=sys.stderr); return 2
    except (OSError, AssertionError) as exc:
        print(f"E099: {exc}", file=sys.stderr); return 3


if __name__ == "__main__":
    raise SystemExit(main())
