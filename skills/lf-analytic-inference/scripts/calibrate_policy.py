#!/usr/bin/env python3
"""Compare non-normative policy candidates against deterministic cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


VALUE_KEYS = {
    "candidate_ceiling", "catalog_retrieval_page_size",
    "concurrent_handoff_limit", "handoff_timeout_ticks",
    "max_delegated_investigations_per_round", "max_investigation_rounds",
    "minimum_candidate_floor", "persistent_catalog_limit", "promotion_min",
    "purge_review_max", "removals_per_cycle", "reorganization_max",
    "score_weights",
}
WEIGHT_KEYS = {"false_positive", "investigated", "material_finding", "repeated_evidence", "selected", "stale", "task_helped", "validated"}
PROFILES = {
    "false_positive": {"investigated": 1, "false_positive": 1},
    "material_utility": {"investigated": 1, "validated": 1, "material_finding": 1, "task_helped": 1},
    "repeated_evidence": {"validated": 1, "repeated_evidence": 1},
    "selection_only": {"selected": 3},
    "stale_validated": {"validated": 1, "stale": 1},
    "validated_only": {"validated": 1},
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def candidate_values(value: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(value, dict):
        raise ValueError("candidate must be an object")
    if "approved_candidate" in value:
        candidate = value["approved_candidate"]
        if hashlib.sha256(canonical(candidate)).hexdigest() != value.get("approved_candidate_digest_sha256"):
            raise ValueError("approved candidate digest mismatch")
        return value.get("policy_id", "unknown-policy"), candidate.get("values")
    if "values" in value:
        return value.get("candidate_id", "unknown-candidate"), value["values"]
    return value.get("policy_id", "inline-candidate"), value


def validate_values(values: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(values, dict):
        return ["POLICY_VALUES_OBJECT"]
    errors.extend(f"POLICY_REQUIRED:{key}" for key in sorted(VALUE_KEYS - values.keys()))
    errors.extend(f"POLICY_UNKNOWN:{key}" for key in sorted(values.keys() - VALUE_KEYS))
    for key in (
        "catalog_retrieval_page_size", "concurrent_handoff_limit",
        "handoff_timeout_ticks", "max_delegated_investigations_per_round",
        "max_investigation_rounds", "minimum_candidate_floor",
        "persistent_catalog_limit", "removals_per_cycle",
    ):
        if key in values and (not is_int(values[key]) or values[key] <= 0):
            errors.append(f"POLICY_POSITIVE_INTEGER:{key}")
    if "candidate_ceiling" in values and values["candidate_ceiling"] is not None:
        errors.append("POLICY_CANDIDATE_CEILING_MUST_BE_NULL")
    if (is_int(values.get("concurrent_handoff_limit")) and
            is_int(values.get("max_delegated_investigations_per_round")) and
            values["concurrent_handoff_limit"] > values["max_delegated_investigations_per_round"]):
        errors.append("POLICY_CONCURRENCY_EXCEEDS_ROUND_CAPACITY")
    for key in ("promotion_min", "purge_review_max", "reorganization_max"):
        if key in values and not is_int(values[key]):
            errors.append(f"POLICY_INTEGER:{key}")
    weights = values.get("score_weights")
    if not isinstance(weights, dict):
        errors.append("POLICY_WEIGHTS_OBJECT")
    else:
        errors.extend(f"POLICY_WEIGHT_REQUIRED:{key}" for key in sorted(WEIGHT_KEYS - weights.keys()))
        errors.extend(f"POLICY_WEIGHT_UNKNOWN:{key}" for key in sorted(weights.keys() - WEIGHT_KEYS))
        for key in sorted(WEIGHT_KEYS & weights.keys()):
            if not is_int(weights[key]):
                errors.append(f"POLICY_WEIGHT_INTEGER:{key}")
        if weights.get("selected") != 0:
            errors.append("POLICY_SELECTION_GAMING")
    return errors


def parse_markdown(text: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    match = re.search(r"## Concrete policy candidates.*?```json\n(.*?)\n```", text, re.S)
    policies = json.loads(match.group(1)) if match else {}
    cases: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line.startswith("| `F-P"):
            continue
        cells = line[2:-2].split(" | ")
        if len(cells) != 7:
            raise ValueError(f"invalid fixture row: {line[:80]}")
        values = [cell.strip("`") for cell in cells]
        cases.append({
            "id": values[0],
            "state": values[1],
            "policy": None if values[2] == "null" else values[2],
            "input": json.loads(values[3]),
            "status": values[4],
            "output": json.loads(values[5]),
            "patch": json.loads(values[6]),
        })
    return policies, cases


def parse_cases(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".md", ".markdown"}:
        return parse_markdown(text)
    document = json.loads(text)
    if isinstance(document, list):
        return {}, document
    if not isinstance(document, dict) or not isinstance(document.get("cases"), list):
        raise ValueError("JSON cases must be an array or an object with a cases array")
    return document.get("policies", {}), document["cases"]


def score(values: dict[str, Any], components: dict[str, Any]) -> int:
    return sum(components.get(key, 0) * weight for key, weight in values["score_weights"].items())


def classify(values: dict[str, Any], score_value: int, protected: bool = False) -> dict[str, bool]:
    return {
        "promotion_eligible": score_value >= values["promotion_min"],
        "purge_review_eligible": (not protected) and score_value <= values["purge_review_max"],
        "reorganization_eligible": score_value <= values["reorganization_max"],
    }


def verify_case(case: dict[str, Any], policies: dict[str, dict[str, Any]]) -> tuple[bool, str]:
    operation = case.get("input", {}).get("op")
    policy_id = case.get("policy")
    if operation not in {"classify_score", "score"} or policy_id not in policies:
        return True, "structural"
    values = policies[policy_id]
    if operation == "classify_score":
        expected = classify(values, case["input"]["score"], case["input"].get("protected", False))
        observed = {key: case["output"].get(key) for key in expected}
        return expected == observed and case.get("patch") == [], "evaluated"
    score_value = score(values, case["input"]["components"])
    if case["status"] == "blocked" and case["output"].get("candidate_policy_result") == "rejected":
        return score_value == case["output"].get("score"), "evaluated-adverse"
    return score_value == case["output"].get("score") and case.get("patch") == [], "evaluated"


def investigation_controls(values: dict[str, Any]) -> dict[str, Any]:
    return {
        "concurrent_handoff_limit": values["concurrent_handoff_limit"],
        "cost_admission_gate": False,
        "cost_mode": "telemetry-only",
        "max_delegated_investigations_per_round": values["max_delegated_investigations_per_round"],
        "max_investigation_rounds": values["max_investigation_rounds"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Exit 0 returns valid or partial; exit 2 returns blocked. Partial lists every unevaluated case.",
    )
    parser.add_argument("cases", type=Path, help="fixture Markdown or JSON cases")
    parser.add_argument("--policy", type=Path, action="append", default=[], help="additional policy JSON; repeatable")
    args = parser.parse_args()
    try:
        policies, cases = parse_cases(args.cases)
        for path in args.policy:
            identifier, values = candidate_values(load_json(path))
            policies[identifier] = values
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"diagnostics": [f"INPUT:{exc}"], "mutation_applied": False, "normative_policy_selected": False, "status": "blocked"}, sort_keys=True, separators=(",", ":")))
        return 1
    policy_errors: dict[str, list[str]] = {}
    summaries: dict[str, Any] = {}
    for identifier in sorted(policies):
        raw = policies[identifier]
        try:
            _, values = candidate_values(raw)
        except ValueError as exc:
            policy_errors[identifier] = [str(exc)]
            continue
        errors = validate_values(values)
        if errors:
            policy_errors[identifier] = errors
            continue
        profiles = {}
        for name, components in sorted(PROFILES.items()):
            score_value = score(values, components)
            profiles[name] = {"eligibility": classify(values, score_value), "score": score_value}
        summaries[identifier] = {
            "generation": {"candidate_ceiling": None, "completion": "semantic-saturation", "minimum_candidate_floor": values["minimum_candidate_floor"]},
            "investigation": investigation_controls(values),
            "catalog": {"active_count": 2, "headroom": max(values["persistent_catalog_limit"] - 2, 0), "persistent_limit": values["persistent_catalog_limit"], "retrieval_page_size": values["catalog_retrieval_page_size"], "retrieval_total_limit": None, "removals_per_cycle": values["removals_per_cycle"]},
            "digest_sha256": hashlib.sha256(canonical(values)).hexdigest(),
            "profiles": profiles,
            "values": values,
        }
    verified = 0
    structural = 0
    unevaluated: list[dict[str, str]] = []
    failures: list[str] = []
    usable = {key: summary["values"] for key, summary in summaries.items()}
    for case in cases:
        ok, kind = verify_case(case, usable)
        if kind.startswith("evaluated"):
            verified += 1
        else:
            structural += 1
            unevaluated.append({
                "fixture_id": case.get("id", "UNKNOWN_CASE"),
                "reason": "STRUCTURAL_ONLY_OPERATION_NOT_IMPLEMENTED",
            })
        if not ok:
            failures.append(case.get("id", "UNKNOWN_CASE"))
    matrix_digest = hashlib.sha256(canonical(cases)).hexdigest()
    status = "blocked" if failures or not summaries else ("partial" if unevaluated else "valid")
    output = {
        "candidate_comparison": summaries,
        "case_count": len(cases),
        "diagnostics": {"case_failures": sorted(failures), "rejected_candidates": policy_errors},
        "evaluated_case_count": verified,
        "matrix_digest_sha256": matrix_digest,
        "mutation_applied": False,
        "normative_policy_selected": False,
        "status": status,
        "structural_case_count": structural,
        "unevaluated_cases": unevaluated,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 2 if status == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
