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
    "validators", "blockers", "minimum_next_path", "execution_boundary",
}
CANDIDATE_KEYS = {
    "candidate_id", "origin", "lifecycle_status", "summary", "investigable_statement",
    "technologies", "surfaces", "support_evidence_refs", "confirm_or_reject_evidence",
    "impact", "cost", "stop_condition", "catalog_locator", "catalog_revision",
    "duplicate_relation", "disposition", "disposition_reason", "suggested_capabilities",
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
    if isinstance(value, bool) or not isinstance(value, int) or (positive and value <= 0):
        fail("E006", f"{label} must be a{' positive' if positive else 'n'} integer")


def string_list(value: Any, label: str, *, sorted_unique: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        fail("E007", f"{label} must be an array of strings")
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


def validate_candidate(candidate: Any, input_fingerprint: str, index: int) -> str:
    label = f"candidates[{index}]"
    candidate = mapping(candidate, label, CANDIDATE_KEYS)
    origin = candidate["origin"]
    if origin not in {"catalogued", "generated"}:
        fail("E010", f"{label}.origin is invalid")
    if candidate["lifecycle_status"] != "unreviewed":
        fail("E010", f"{label}.lifecycle_status must be unreviewed")
    for key in ("summary", "investigable_statement", "impact", "cost", "stop_condition", "disposition_reason"):
        string(candidate[key], f"{label}.{key}", nonempty=True)
    for key in ("technologies", "surfaces", "support_evidence_refs", "confirm_or_reject_evidence", "suggested_capabilities"):
        string_list(candidate[key], f"{label}.{key}")
    if candidate["technologies"] != sorted(candidate["technologies"]):
        fail("E008", f"{label}.technologies must be lexicographically sorted")
    if candidate["duplicate_relation"] not in {"none", "exact-duplicate", "near-duplicate"}:
        fail("E010", f"{label}.duplicate_relation is invalid")
    if candidate["disposition"] not in {"selected", "rejected", "deferred"}:
        fail("E010", f"{label}.disposition is invalid")
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


def validate_preparation(obj: Any) -> None:
    obj = mapping(obj, "inference_preparation", PREP_KEYS)
    reject_runtime_ids(obj)
    if obj["schema_version"] != 1 or obj["artifact_type"] != "analytic-inference-preparation":
        fail("E010", "schema_version or artifact_type is invalid")
    if obj["status"] not in {"pre-investigation-complete", "partial", "blocked"}:
        fail("E010", "status is invalid")
    sha(obj["input_fingerprint"], "input_fingerprint")
    sha(obj["preparation_digest"], "preparation_digest")
    if not isinstance(obj["preparation_id"], str) or not re.fullmatch(r"prep-[0-9a-f]{64}", obj["preparation_id"]):
        fail("E005", "preparation_id is invalid")
    inp = mapping(obj["input"], "input", {"demand_digest", "ordered_source_digests", "request_controls_digest"})
    sha(inp["demand_digest"], "input.demand_digest")
    for index, value in enumerate(string_list(inp["ordered_source_digests"], "input.ordered_source_digests")):
        sha(value, f"input.ordered_source_digests[{index}]")
    sha(inp["request_controls_digest"], "input.request_controls_digest")
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
    catalog = mapping(obj["catalog_observation"], "catalog_observation", {"state", "catalog_snapshot_digest", "indices_read", "record_locators_loaded", "diagnostics"})
    state = catalog["state"]
    if state not in {"loaded", "absent", "empty", "no-match", "blocked"}: fail("E010", "catalog_observation.state is invalid")
    sha(catalog["catalog_snapshot_digest"], "catalog_snapshot_digest", nullable=True)
    if (state == "loaded") != (catalog["catalog_snapshot_digest"] is not None):
        fail("E014", "loaded catalog requires digest; non-loaded catalog requires null digest")
    for key in ("indices_read", "record_locators_loaded"):
        string_list(catalog[key], f"catalog_observation.{key}", sorted_unique=True)
    if not isinstance(catalog["diagnostics"], list): fail("E007", "catalog_observation.diagnostics must be an array")
    expected_fp = digest({"demand_digest": inp["demand_digest"], "ordered_source_digests": inp["ordered_source_digests"], "catalog_snapshot_digest": catalog["catalog_snapshot_digest"], "policy_digest": policy["policy_digest"], "request_controls_digest": inp["request_controls_digest"]})
    if obj["input_fingerprint"] != expected_fp: fail("E015", "input_fingerprint does not reproduce")
    string_list(obj["technologies"], "technologies", sorted_unique=True)
    candidate_ids = [validate_candidate(item, obj["input_fingerprint"], index) for index, item in enumerate(obj["candidates"])] if isinstance(obj["candidates"], list) else fail("E007", "candidates must be an array")
    if candidate_ids != sorted(candidate_ids) or len(candidate_ids) != len(set(candidate_ids)):
        fail("E016", "candidates must be sorted by unique candidate_id")
    if state == "blocked" and (obj["status"] != "blocked" or any(item["origin"] == "catalogued" for item in obj["candidates"])):
        fail("E017", "blocked catalog cannot be represented as loaded or contain catalogued candidates")
    duplicate = mapping(obj["duplicate_analysis"], "duplicate_analysis", {"exact_duplicates", "near_duplicates"})
    for key in duplicate:
        if not isinstance(duplicate[key], list): fail("E007", f"duplicate_analysis.{key} must be an array")
    selected = string_list(obj["selected_for_investigation"], "selected_for_investigation", sorted_unique=True)
    expected_selected = sorted(item["candidate_id"] for item in obj["candidates"] if item["disposition"] == "selected")
    if selected != expected_selected: fail("E018", "selected_for_investigation must equal selected candidate IDs")
    if not isinstance(obj["planned_investigations"], list): fail("E007", "planned_investigations must be an array")
    plan_ids = []
    for index, intent in enumerate(obj["planned_investigations"]):
        if not isinstance(intent, dict) or "candidate_id" not in intent or not isinstance(intent["candidate_id"], str):
            fail("E019", f"planned_investigations[{index}] needs candidate_id")
        plan_ids.append(intent["candidate_id"])
    if plan_ids != sorted(plan_ids) or len(plan_ids) != len(set(plan_ids)) or any(item not in candidate_ids for item in plan_ids):
        fail("E019", "planned_investigations must be sorted, unique, and refer to candidates")
    if obj["dispatch_admitted"] is not False: fail("E020", "dispatch_admitted must be false")
    for key in ("validators", "blockers"):
        if not isinstance(obj[key], list): fail("E007", f"{key} must be an array")
    string(obj["minimum_next_path"], "minimum_next_path", nonempty=True)
    if obj["execution_boundary"] != BOUNDARY: fail("E021", "execution_boundary must be literal zero/false/empty boundary")
    expected_prep = "prep-" + digest({"input_fingerprint": obj["input_fingerprint"], "candidate_ids": sorted(candidate_ids)})[7:]
    if obj["preparation_id"] != expected_prep: fail("E022", "preparation_id does not reproduce")
    digest_domain = dict(obj); del digest_domain["preparation_digest"]
    if obj["preparation_digest"] != digest(digest_domain): fail("E023", "preparation_digest does not reproduce")


def fixture() -> dict[str, Any]:
    value: dict[str, Any] = {"schema_version": 1, "artifact_type": "analytic-inference-preparation", "preparation_id": "", "input_fingerprint": "", "preparation_digest": "", "status": "pre-investigation-complete", "input": {"demand_digest": "sha256:" + "1" * 64, "ordered_source_digests": ["sha256:" + "2" * 64], "request_controls_digest": "sha256:" + "3" * 64}, "root": {"consumer_root": "/fixture", "root_provenance": "canonical-pwd"}, "source_map": {"sources": [{"locator": "source.md", "digest": "sha256:" + "2" * 64, "facts": []}]}, "policy": {"policy_id": "fixture-policy", "policy_digest": "sha256:" + "4" * 64, "values": {}}, "catalog_observation": {"state": "no-match", "catalog_snapshot_digest": None, "indices_read": [], "record_locators_loaded": [], "diagnostics": []}, "technologies": [], "candidates": [], "duplicate_analysis": {"exact_duplicates": [], "near_duplicates": []}, "selected_for_investigation": [], "planned_investigations": [], "dispatch_admitted": False, "validators": ["fixture"], "blockers": [], "minimum_next_path": "return-to-caller", "execution_boundary": copy.deepcopy(BOUNDARY)}
    refresh_identities(value)
    return value


def refresh_identities(value: dict[str, Any]) -> None:
    """Recalculate all content-addressed fields for an in-memory fixture."""
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
        "summary": summary, "investigable_statement": f"Investigate {summary}",
        "technologies": ["fixture"], "surfaces": ["fixture-surface"],
        "support_evidence_refs": [], "confirm_or_reject_evidence": [],
        "impact": "unknown", "cost": "unknown", "stop_condition": "fixture stop",
        "catalog_locator": None, "catalog_revision": None, "duplicate_relation": "none",
        "disposition": disposition, "disposition_reason": "fixture observable reason",
        "suggested_capabilities": [],
    }


def candidate_from_fixture(spec: dict[str, Any]) -> dict[str, Any]:
    label = spec.get("label")
    disposition = spec.get("disposition", "selected")
    if not isinstance(label, str) or not label or disposition not in {"selected", "rejected", "deferred"}:
        raise AssertionError("fixture candidate needs a non-empty label and valid disposition")
    candidate = generated_candidate(label, disposition)
    candidate["cost"] = spec.get("cost", candidate["cost"])
    candidate["duplicate_relation"] = spec.get("duplicate_relation", "none")
    candidate["disposition_reason"] = spec.get("reason", candidate["disposition_reason"])
    if spec.get("origin", "generated") == "catalogued":
        candidate.update({"origin": "catalogued", "catalog_locator": f"records/{label}.xml", "catalog_revision": 1})
    elif spec.get("origin", "generated") != "generated":
        raise AssertionError("fixture candidate origin is invalid")
    return candidate


def assert_case_matrix() -> None:
    matrix = load_fixture("preparation-cases.json")
    if matrix.get("schema_version") != 1 or matrix.get("fixture_kind") != "analytic-inference-preparation-case-matrix":
        raise AssertionError("preparation case matrix schema is invalid")
    if matrix.get("byte_replay_is_out_of_scope") is not True or matrix.get("execution_boundary") != BOUNDARY:
        raise AssertionError("case matrix must declare byte replay out of scope and literal zero boundary")
    cases = matrix.get("cases")
    if not isinstance(cases, list): raise AssertionError("case matrix cases must be an array")
    required_case_ids = {"loaded-relevant-below-floor", "registry-absent", "catalog-empty", "technology-no-match", "catalog-blocked", "candidate-outcomes-and-duplicates", "adversarial-order"}
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
        state, expected_status = fixture_input.get("catalog_state"), expected.get("status")
        value["catalog_observation"]["state"] = state
        value["catalog_observation"]["catalog_snapshot_digest"] = ("sha256:" + "5" * 64) if fixture_input.get("catalog_snapshot") else None
        value["status"] = expected_status
        if state == "blocked": value["minimum_next_path"] = "repair-permitted-catalog-input"
        specs = fixture_input.get("candidates")
        if not isinstance(specs, list): raise AssertionError(f"{case['id']}: candidates must be an array")
        value["candidates"] = [candidate_from_fixture(spec) for spec in specs if isinstance(spec, dict)]
        if len(value["candidates"]) != len(specs): raise AssertionError(f"{case['id']}: candidate must be an object")
        refresh_identities(value); validate_preparation(value)
        actual_dispositions = {candidate["summary"]: candidate["disposition"] for candidate in value["candidates"]}
        if actual_dispositions != expected.get("dispositions"):
            raise AssertionError(f"{case['id']}: candidate dispositions differ from fixture expectation")
        expected_relations = expected.get("duplicate_relations")
        if expected_relations is not None:
            actual_relations = {candidate["summary"]: candidate["duplicate_relation"] for candidate in value["candidates"]}
            if actual_relations != expected_relations:
                raise AssertionError(f"{case['id']}: duplicate relations differ from fixture expectation")
        selected_count, floor = len(value["selected_for_investigation"]), expected.get("relevant_result_floor")
        if selected_count != expected.get("selected_count") or not isinstance(floor, int):
            raise AssertionError(f"{case['id']}: selected count or floor is invalid")
        if expected.get("zero_padding") is True and selected_count >= floor:
            raise AssertionError(f"{case['id']}: selected candidates were padded to the relevant-result floor")
        for unknown_cost in expected.get("unknown_cost_values", []):
            if not isinstance(unknown_cost, str) or unknown_cost == "0" or unknown_cost == "":
                raise AssertionError(f"{case['id']}: unknown cost was coerced to zero or lost its type")
            if unknown_cost not in [candidate["cost"] for candidate in value["candidates"]]:
                raise AssertionError(f"{case['id']}: typed unknown cost not preserved")
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
    if parity.get("schema_version") != 1 or parity.get("byte_replay_is_out_of_scope") is not True or not isinstance(projections, dict) or set(projections) != {"loki-deep-analysis", "loki-generate-inferences"}:
        raise AssertionError("parity fixture is invalid")
    common = parity.get("common_normalized_input")
    if not isinstance(common, dict): raise AssertionError("parity fixture has no common normalized input")
    outputs = []
    for _caller, projection in projections.items():
        if not isinstance(projection, dict) or not {"command", "run_id", "destination"} <= set(projection):
            raise AssertionError("caller projection is incomplete")
        value = fixture()
        value["input"]["demand_digest"] = common["demand_digest"]
        value["input"]["request_controls_digest"] = common["request_controls_digest"]
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
    for field in expected.get("equal_fields", []):
        if outputs[0][field] != outputs[1][field]: raise AssertionError(f"parity differs for {field}")


def self_test() -> None:
    good = fixture(); validate_preparation(good)
    def blocked_as_loaded(value: dict[str, Any]) -> None:
        value["catalog_observation"]["state"] = "blocked"
        refresh_identities(value)

    cases = [("tampered-digest", lambda x: x.__setitem__("preparation_digest", "sha256:" + "0" * 64), "E023"), ("extra-field", lambda x: x.__setitem__("extra", True), "E003"), ("invalid-order", lambda x: x.__setitem__("technologies", ["z", "a"]), "E008"), ("dispatch-nonzero", lambda x: x["execution_boundary"].__setitem__("agent_runs_created", 1), "E021"), ("blocked-as-loaded", blocked_as_loaded, "E017")]
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
        validate_preparation(value); print("valid"); return 0
    except ValidationError as exc:
        print(f"{exc.code}: {exc.message}", file=sys.stderr); return 2
    except (OSError, AssertionError) as exc:
        print(f"E099: {exc}", file=sys.stderr); return 3


if __name__ == "__main__":
    raise SystemExit(main())
