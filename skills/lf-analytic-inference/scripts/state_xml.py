#!/usr/bin/env python3
"""Encode and strictly decode canonical analytic-inference XML state v2."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


NS = "urn:loki:analytic-inference:state:v2"
DECLARATION = b'<?xml version="1.0" encoding="UTF-8"?>\n'
KINDS = {"registry", "catalog", "record", "event"}
PREDEFINED_ENTITIES = {"amp", "lt", "gt", "apos", "quot"}
NAMED_ENTITY = re.compile(r"&([A-Za-z_:][A-Za-z0-9_.:-]*);")
SEGMENT = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
CATALOG_LOCATOR = re.compile(r"^catalogs/[a-z0-9][a-z0-9._-]*/index\.xml$")
RECORD_LOCATOR = re.compile(r"^catalogs/[a-z0-9][a-z0-9._-]*/records/[a-z0-9][a-z0-9._-]*/rev-[1-9][0-9]*\.xml$")
STATUSES = {"active", "protected", "redirect", "tombstone"}
FRESHNESS = {"current", "stale", "unknown", "unsupported"}
INVESTIGATION_COSTS = {"low", "medium", "high", "unknown", "unsupported"}
EVENT_STAGES = {"selected", "investigated", "validated", "rejected", "material-finding", "task-helped", "false-positive", "repeated-evidence", "stale"}
ET.register_namespace("", NS)


class StateXmlError(ValueError):
    """Fail-closed XML state codec error with a stable diagnostic."""

    def __init__(self, diagnostic: str):
        super().__init__(diagnostic)
        self.diagnostic = diagnostic


def _tag(name: str) -> str:
    return f"{{{NS}}}{name}"


def _element(name: str) -> ET.Element:
    return ET.Element(_tag(name))


def _sub(parent: ET.Element, name: str, text: str | None = None) -> ET.Element:
    child = ET.SubElement(parent, _tag(name))
    child.text = text
    return child


def _exact_mapping(value: Any, keys: set[str], where: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise StateXmlError(f"{where}:KEYS")
    return value


def _integer(value: Any, where: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise StateXmlError(f"{where}:INTEGER")
    if minimum is not None and value < minimum:
        raise StateXmlError(f"{where}:MINIMUM")
    return value


def _string(value: Any, where: str, *, nonempty: bool = False) -> str:
    if not isinstance(value, str) or (nonempty and not value):
        raise StateXmlError(f"{where}:STRING")
    try:
        value.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise StateXmlError(f"{where}:UNPAIRED_SURROGATE") from exc
    return value


def _segment(value: Any, where: str) -> str:
    logical = _string(value, where, nonempty=True)
    if SEGMENT.fullmatch(logical) is None:
        raise StateXmlError(f"{where}:PATH_SEGMENT")
    return logical


def _enum(value: Any, allowed: set[str], where: str) -> str:
    logical = _string(value, where, nonempty=True)
    if logical not in allowed:
        raise StateXmlError(f"{where}:ENUM")
    return logical


def _xml_char_allowed(codepoint: int) -> bool:
    return (
        codepoint in {0x9, 0xA, 0xD}
        or 0x20 <= codepoint <= 0xD7FF
        or 0xE000 <= codepoint <= 0xFFFD
        or 0x10000 <= codepoint <= 0x10FFFF
    )


def _write_string_value(parent: ET.Element, value: Any, where: str, *, nonempty: bool = False) -> None:
    logical = _string(value, where, nonempty=nonempty)
    if all(_xml_char_allowed(ord(character)) for character in logical):
        _sub(parent, "text", logical)
    else:
        encoded = base64.b64encode(logical.encode("utf-8")).decode("ascii")
        _sub(parent, "base64Utf8", encoded)


def _canonical_decimal(value: Any, where: str, *, nonnegative: bool = False) -> str:
    if isinstance(value, bool) or isinstance(value, int) or not isinstance(value, (float, Decimal)):
        raise StateXmlError(f"{where}:NUMBER")
    if isinstance(value, float) and not math.isfinite(value):
        raise StateXmlError(f"{where}:NONFINITE")
    try:
        decimal = Decimal(str(value))
    except InvalidOperation as exc:
        raise StateXmlError(f"{where}:NUMBER") from exc
    if not decimal.is_finite():
        raise StateXmlError(f"{where}:NONFINITE")
    if nonnegative and decimal < 0:
        raise StateXmlError(f"{where}:NEGATIVE")
    if decimal == 0:
        return "0"
    rendered = format(decimal, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    if rendered.startswith("+"):
        rendered = rendered[1:]
    return rendered


def _write_id_list(parent: ET.Element, values: Any, where: str) -> None:
    if not isinstance(values, list):
        raise StateXmlError(f"{where}:ARRAY")
    for position, value in enumerate(values):
        _sub(parent, "item", _segment(value, f"{where}[{position}]"))


def _write_string_list(parent: ET.Element, values: Any, where: str) -> None:
    if not isinstance(values, list):
        raise StateXmlError(f"{where}:ARRAY")
    for position, value in enumerate(values):
        item = _sub(parent, "item")
        _write_string_value(item, value, f"{where}[{position}]", nonempty=True)


def _write_nullable_id(parent: ET.Element, value: Any, where: str) -> None:
    if value is None:
        _sub(parent, "none")
    else:
        _sub(parent, "value", _segment(value, where))


def _write_json_object(parent: ET.Element, value: Any, where: str) -> None:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise StateXmlError(f"{where}:OBJECT")
    for key in sorted(value):
        entry = _sub(parent, "entry")
        key_node = _sub(entry, "key")
        _write_string_value(key_node, key, f"{where}.key")
        value_node = _sub(entry, "value")
        _write_json_value(value_node, value[key], f"{where}.{key}")


def _write_json_value(parent: ET.Element, value: Any, where: str) -> None:
    if value is None:
        _sub(parent, "null")
    elif isinstance(value, bool):
        _sub(parent, "boolean", "true" if value else "false")
    elif isinstance(value, int):
        _sub(parent, "integer", str(value))
    elif isinstance(value, (float, Decimal)):
        _sub(parent, "number", _canonical_decimal(value, where))
    elif isinstance(value, str):
        node = _sub(parent, "string")
        _write_string_value(node, value, where)
    elif isinstance(value, dict):
        node = _sub(parent, "object")
        _write_json_object(node, value, where)
    elif isinstance(value, list):
        node = _sub(parent, "array")
        for position, item in enumerate(value):
            item_node = _sub(node, "value")
            _write_json_value(item_node, item, f"{where}[{position}]")
    else:
        raise StateXmlError(f"{where}:JSON_TYPE")


def _write_registry(value: Any) -> ET.Element:
    value = _exact_mapping(value, {"schema_version", "state_layout", "entries"}, "REGISTRY")
    if value["schema_version"] != 2 or value["state_layout"] != "analytic-inference-consumer-v2":
        raise StateXmlError("REGISTRY:IDENTITY")
    root = _element("registry")
    _sub(root, "schemaVersion", "2")
    _sub(root, "stateLayout", value["state_layout"])
    entries_node = _sub(root, "entries")
    if not isinstance(value["entries"], list):
        raise StateXmlError("REGISTRY:ENTRIES")
    for position, raw in enumerate(value["entries"]):
        entry = _exact_mapping(raw, {"technology", "aliases", "catalog_id", "locator"}, f"REGISTRY[{position}]")
        node = _sub(entries_node, "entry")
        _sub(node, "technology", _segment(entry["technology"], "REGISTRY:TECHNOLOGY"))
        aliases = _sub(node, "aliases")
        _write_id_list(aliases, entry["aliases"], "REGISTRY:ALIASES")
        _sub(node, "catalogId", _segment(entry["catalog_id"], "REGISTRY:CATALOG_ID"))
        locator = _string(entry["locator"], "REGISTRY:LOCATOR", nonempty=True)
        if CATALOG_LOCATOR.fullmatch(locator) is None: raise StateXmlError("REGISTRY:LOCATOR:PATTERN")
        _sub(node, "locator", locator)
    return root


def _write_catalog(value: Any) -> ET.Element:
    keys = {"schema_version", "catalog_id", "technology", "aliases", "active_limit", "entries"}
    value = _exact_mapping(value, keys, "CATALOG")
    if value["schema_version"] != 1:
        raise StateXmlError("CATALOG:SCHEMA_VERSION")
    root = _element("catalog")
    _sub(root, "schemaVersion", "1")
    _sub(root, "catalogId", _segment(value["catalog_id"], "CATALOG:ID"))
    _sub(root, "technology", _segment(value["technology"], "CATALOG:TECHNOLOGY"))
    aliases = _sub(root, "aliases")
    _write_id_list(aliases, value["aliases"], "CATALOG:ALIASES")
    _sub(root, "activeLimit", str(_integer(value["active_limit"], "CATALOG:ACTIVE_LIMIT", minimum=0)))
    entries_node = _sub(root, "entries")
    if not isinstance(value["entries"], list):
        raise StateXmlError("CATALOG:ENTRIES")
    entry_keys = {"inference_id", "revision", "status", "summary", "technologies", "surfaces", "objectives", "signals", "locator"}
    for position, raw in enumerate(value["entries"]):
        entry = _exact_mapping(raw, entry_keys, f"CATALOG[{position}]")
        node = _sub(entries_node, "entry")
        _sub(node, "inferenceId", _segment(entry["inference_id"], "CATALOG:INFERENCE_ID"))
        _sub(node, "revision", str(_integer(entry["revision"], "CATALOG:REVISION", minimum=1)))
        _sub(node, "status", _enum(entry["status"], STATUSES, "CATALOG:STATUS"))
        summary = _sub(node, "summary")
        _write_string_value(summary, entry["summary"], "CATALOG:SUMMARY")
        for logical, xml_name, id_list in (
            ("technologies", "technologies", True), ("surfaces", "surfaces", False),
            ("objectives", "objectives", False), ("signals", "signals", False),
        ):
            list_node = _sub(node, xml_name)
            (_write_id_list if id_list else _write_string_list)(list_node, entry[logical], f"CATALOG:{logical}")
        locator = _string(entry["locator"], "CATALOG:LOCATOR", nonempty=True)
        if RECORD_LOCATOR.fullmatch(locator) is None: raise StateXmlError("CATALOG:LOCATOR:PATTERN")
        _sub(node, "locator", locator)
    return root


def _write_record(value: Any) -> ET.Element:
    keys = {"schema_version", "inference_id", "revision", "status", "statement", "applicability", "investigation", "provenance", "lineage", "snapshot"}
    value = _exact_mapping(value, keys, "RECORD")
    if value["schema_version"] != 1:
        raise StateXmlError("RECORD:SCHEMA_VERSION")
    root = _element("record")
    _sub(root, "schemaVersion", "1")
    _sub(root, "inferenceId", _segment(value["inference_id"], "RECORD:ID"))
    _sub(root, "revision", str(_integer(value["revision"], "RECORD:REVISION", minimum=1)))
    _sub(root, "status", _enum(value["status"], STATUSES, "RECORD:STATUS"))
    statement = _sub(root, "statement")
    _write_string_value(statement, value["statement"], "RECORD:STATEMENT", nonempty=True)

    applicability = _exact_mapping(value["applicability"], {"technologies", "versions", "surfaces", "objectives", "signals", "exclusions"}, "RECORD:APPLICABILITY")
    app_node = _sub(root, "applicability")
    for key in ("technologies", "versions", "surfaces", "objectives", "signals", "exclusions"):
        node = _sub(app_node, key)
        (_write_id_list if key == "technologies" else _write_string_list)(node, applicability[key], f"RECORD:{key}")

    investigation = _exact_mapping(value["investigation"], {"demand_relation", "confirm_or_reject_evidence", "potential_impact", "cost", "stop_condition", "suggested_capabilities"}, "RECORD:INVESTIGATION")
    inv_node = _sub(root, "investigation")
    for key, xml_name in (("demand_relation", "demandRelation"), ("confirm_or_reject_evidence", "confirmOrRejectEvidence"), ("potential_impact", "potentialImpact"), ("cost", "cost"), ("stop_condition", "stopCondition"), ("suggested_capabilities", "suggestedCapabilities")):
        node = _sub(inv_node, xml_name)
        if key in {"confirm_or_reject_evidence", "suggested_capabilities"}:
            _write_string_list(node, investigation[key], f"RECORD:{key}")
        elif key == "cost":
            node.text = _enum(investigation[key], INVESTIGATION_COSTS, "RECORD:COST")
        else:
            _write_string_value(node, investigation[key], f"RECORD:{key}")

    provenance = _exact_mapping(value["provenance"], {"source_refs", "accepted_evidence_refs", "freshness"}, "RECORD:PROVENANCE")
    prov_node = _sub(root, "provenance")
    for key, xml_name in (("source_refs", "sourceRefs"), ("accepted_evidence_refs", "acceptedEvidenceRefs")):
        node = _sub(prov_node, xml_name)
        _write_string_list(node, provenance[key], f"RECORD:{key}")
    _sub(prov_node, "freshness", _enum(provenance["freshness"], FRESHNESS, "RECORD:FRESHNESS"))

    lineage = _exact_mapping(value["lineage"], {"supersedes", "merged_from", "redirect_to", "tombstone"}, "RECORD:LINEAGE")
    lineage_node = _sub(root, "lineage")
    supersedes = _sub(lineage_node, "supersedes"); _write_id_list(supersedes, lineage["supersedes"], "RECORD:SUPERSEDES")
    merged = _sub(lineage_node, "mergedFrom"); _write_id_list(merged, lineage["merged_from"], "RECORD:MERGED_FROM")
    redirect = _sub(lineage_node, "redirectTo"); _write_nullable_id(redirect, lineage["redirect_to"], "RECORD:REDIRECT")
    tombstone = _sub(lineage_node, "tombstone")
    if lineage["tombstone"] is None:
        _sub(tombstone, "none")
    elif isinstance(lineage["tombstone"], dict):
        tomb_value = _sub(tombstone, "value")
        _write_json_object(tomb_value, lineage["tombstone"], "RECORD:TOMBSTONE")
    else:
        raise StateXmlError("RECORD:TOMBSTONE")

    snapshot = _exact_mapping(value["snapshot"], {"algorithm_version", "components", "score", "as_of_event", "freshness", "denominators"}, "RECORD:SNAPSHOT")
    snapshot_node = _sub(root, "snapshot")
    algorithm = _sub(snapshot_node, "algorithmVersion"); _write_string_value(algorithm, snapshot["algorithm_version"], "RECORD:ALGORITHM", nonempty=True)
    component_keys = ["selected_count", "investigated_count", "validated_count", "rejected_count", "material_findings_count", "tasks_helped_count", "false_positive_count", "repeated_evidence_count", "stale_count"]
    components = _exact_mapping(snapshot["components"], set(component_keys), "RECORD:COMPONENTS")
    components_node = _sub(snapshot_node, "components")
    for key in component_keys:
        xml_name = "".join([key.split("_")[0], *[part.title() for part in key.split("_")[1:]]])
        _sub(components_node, xml_name, str(_integer(components[key], f"RECORD:{key}", minimum=0)))
    _sub(snapshot_node, "score", str(_integer(snapshot["score"], "RECORD:SCORE")))
    as_of = _sub(snapshot_node, "asOfEvent"); _write_nullable_id(as_of, snapshot["as_of_event"], "RECORD:AS_OF")
    _sub(snapshot_node, "freshness", _enum(snapshot["freshness"], FRESHNESS, "RECORD:SNAPSHOT_FRESHNESS"))
    denominators = _sub(snapshot_node, "denominators"); _write_json_object(denominators, snapshot["denominators"], "RECORD:DENOMINATORS")
    return root


def _write_observed_cost(parent: ET.Element, value: Any, where: str) -> None:
    if isinstance(value, str) and value in {"unknown", "unsupported"}:
        _sub(parent, value)
    elif isinstance(value, int) and not isinstance(value, bool):
        if value < 0:
            raise StateXmlError(f"{where}:NEGATIVE")
        _sub(parent, "value", str(value))
    elif isinstance(value, (float, Decimal)):
        _sub(parent, "value", _canonical_decimal(value, where, nonnegative=True))
    else:
        raise StateXmlError(f"{where}:COST")


def _write_event(value: Any) -> ET.Element:
    required = {"schema_version", "event_id", "source", "inference_id", "inference_revision", "stage", "outcome", "reason", "agent_capability", "cost"}
    if not isinstance(value, dict) or not required.issubset(value) or not set(value).issubset(required | {"sequence"}):
        raise StateXmlError("EVENT:KEYS")
    if value["schema_version"] != 1:
        raise StateXmlError("EVENT:SCHEMA_VERSION")
    root = _element("event")
    _sub(root, "schemaVersion", "1")
    _sub(root, "eventId", _segment(value["event_id"], "EVENT:ID"))
    if "sequence" in value:
        _sub(root, "sequence", str(_integer(value["sequence"], "EVENT:SEQUENCE", minimum=0)))
    source = _exact_mapping(value["source"], {"analysis_ref", "run_id", "handoff_id", "evidence_refs"}, "EVENT:SOURCE")
    source_node = _sub(root, "source")
    for key, xml_name in (("analysis_ref", "analysisRef"), ("run_id", "runId"), ("handoff_id", "handoffId")):
        node = _sub(source_node, xml_name); _write_string_value(node, source[key], f"EVENT:{key}", nonempty=True)
    evidence = _sub(source_node, "evidenceRefs"); _write_string_list(evidence, source["evidence_refs"], "EVENT:EVIDENCE")
    _sub(root, "inferenceId", _segment(value["inference_id"], "EVENT:INFERENCE_ID"))
    _sub(root, "inferenceRevision", str(_integer(value["inference_revision"], "EVENT:REVISION", minimum=1)))
    _sub(root, "stage", _enum(value["stage"], EVENT_STAGES, "EVENT:STAGE"))
    outcome = _sub(root, "outcome"); _write_json_value(outcome, value["outcome"], "EVENT:OUTCOME")
    reason = _sub(root, "reason"); _write_string_value(reason, value["reason"], "EVENT:REASON", nonempty=True)
    capability = _sub(root, "agentCapability"); _write_string_value(capability, value["agent_capability"], "EVENT:CAPABILITY", nonempty=True)
    cost = _exact_mapping(value["cost"], {"context", "tools"}, "EVENT:COST")
    cost_node = _sub(root, "cost")
    for key in ("context", "tools"):
        node = _sub(cost_node, key); _write_observed_cost(node, cost[key], f"EVENT:COST:{key}")
    return root


WRITERS = {"registry": _write_registry, "catalog": _write_catalog, "record": _write_record, "event": _write_event}


def _canonical_root(root: ET.Element) -> bytes:
    serialized = ET.tostring(root, encoding="unicode", short_empty_elements=True)
    canonical = ET.canonicalize(serialized, with_comments=False, strip_text=False, rewrite_prefixes=False)
    return DECLARATION + canonical.encode("utf-8") + b"\n"


def _logical_equivalent(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, int) or isinstance(right, int):
        return isinstance(left, int) and isinstance(right, int) and left == right
    if isinstance(left, (float, Decimal)) or isinstance(right, (float, Decimal)):
        if not isinstance(left, (float, Decimal)) or not isinstance(right, (float, Decimal)):
            return False
        return _canonical_decimal(left, "ROUND_TRIP") == _canonical_decimal(right, "ROUND_TRIP")
    if isinstance(left, dict) or isinstance(right, dict):
        return isinstance(left, dict) and isinstance(right, dict) and set(left) == set(right) and all(_logical_equivalent(left[key], right[key]) for key in left)
    if isinstance(left, list) or isinstance(right, list):
        return isinstance(left, list) and isinstance(right, list) and len(left) == len(right) and all(_logical_equivalent(a, b) for a, b in zip(left, right))
    return type(left) is type(right) and left == right


def canonical_state(value: Any, kind: str) -> bytes:
    """Return the sole canonical XML byte representation for one logical state object."""
    if kind not in KINDS:
        raise StateXmlError("DOCUMENT_KIND")
    payload = _canonical_root(WRITERS[kind](value))
    parsed = _parse_document(payload, expected_kind=kind, require_canonical=False)
    if not _logical_equivalent(parsed, value):
        raise StateXmlError("ROUND_TRIP_MISMATCH")
    if _canonical_root(WRITERS[kind](parsed)) != payload:
        raise StateXmlError("CANONICAL_REPLAY_MISMATCH")
    return payload


def _children(element: ET.Element, expected: list[str], where: str) -> list[ET.Element]:
    children = list(element)
    if [child.tag for child in children] != [_tag(name) for name in expected]:
        raise StateXmlError(f"{where}:STRUCTURE")
    return children


def _leaf_text(element: ET.Element, where: str, *, nonempty: bool = False) -> str:
    if element.attrib or list(element):
        raise StateXmlError(f"{where}:LEAF")
    value = element.text or ""
    if nonempty and not value:
        raise StateXmlError(f"{where}:EMPTY")
    return value


def _read_string_value(element: ET.Element, where: str, *, nonempty: bool = False) -> str:
    children = list(element)
    if len(children) != 1 or children[0].tag not in {_tag("text"), _tag("base64Utf8")}:
        raise StateXmlError(f"{where}:STRING_VALUE")
    child = children[0]
    raw = _leaf_text(child, where)
    if child.tag == _tag("text"):
        value = raw
        if not all(_xml_char_allowed(ord(character)) for character in value):
            raise StateXmlError(f"{where}:XML_CHAR")
    else:
        try:
            encoded = raw.encode("ascii")
            decoded = base64.b64decode(encoded, validate=True)
            value = decoded.decode("utf-8", "strict")
        except (UnicodeError, ValueError) as exc:
            raise StateXmlError(f"{where}:BASE64") from exc
        if base64.b64encode(decoded) != encoded:
            raise StateXmlError(f"{where}:BASE64_NONCANONICAL")
        if all(_xml_char_allowed(ord(character)) for character in value):
            raise StateXmlError(f"{where}:BASE64_NOT_REQUIRED")
    if nonempty and not value:
        raise StateXmlError(f"{where}:EMPTY")
    return value


def _read_id_list(element: ET.Element, where: str) -> list[str]:
    values = []
    for child in list(element):
        if child.tag != _tag("item"):
            raise StateXmlError(f"{where}:ITEM")
        values.append(_leaf_text(child, where, nonempty=True))
    return values


def _read_string_list(element: ET.Element, where: str) -> list[str]:
    values = []
    for child in list(element):
        if child.tag != _tag("item"):
            raise StateXmlError(f"{where}:ITEM")
        values.append(_read_string_value(child, where, nonempty=True))
    return values


def _read_nullable_id(element: ET.Element, where: str) -> str | None:
    children = list(element)
    if len(children) != 1:
        raise StateXmlError(f"{where}:NULLABLE")
    if children[0].tag == _tag("none"):
        _leaf_text(children[0], where)
        return None
    if children[0].tag == _tag("value"):
        return _leaf_text(children[0], where, nonempty=True)
    raise StateXmlError(f"{where}:NULLABLE")


def _read_decimal(element: ET.Element, where: str, *, nonnegative: bool = False) -> Decimal:
    raw = _leaf_text(element, where, nonempty=True)
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise StateXmlError(f"{where}:DECIMAL") from exc
    if not value.is_finite() or _canonical_decimal(value, where, nonnegative=nonnegative) != raw:
        raise StateXmlError(f"{where}:DECIMAL_NONCANONICAL")
    return value


def _read_json_object(element: ET.Element, where: str) -> dict[str, Any]:
    output: dict[str, Any] = {}
    previous: str | None = None
    for entry in list(element):
        if entry.tag != _tag("entry"):
            raise StateXmlError(f"{where}:ENTRY")
        key_node, value_node = _children(entry, ["key", "value"], where)
        key = _read_string_value(key_node, f"{where}:KEY")
        if key in output or (previous is not None and key <= previous):
            raise StateXmlError(f"{where}:KEY_ORDER_OR_DUPLICATE")
        previous = key
        output[key] = _read_json_value(value_node, f"{where}.{key}")
    return output


def _read_json_value(element: ET.Element, where: str) -> Any:
    children = list(element)
    if len(children) != 1:
        raise StateXmlError(f"{where}:JSON_VALUE")
    child = children[0]
    name = child.tag.removeprefix(f"{{{NS}}}")
    if name == "null":
        _leaf_text(child, where); return None
    if name == "boolean":
        raw = _leaf_text(child, where)
        if raw not in {"true", "false"}: raise StateXmlError(f"{where}:BOOLEAN")
        return raw == "true"
    if name == "integer":
        raw = _leaf_text(child, where, nonempty=True)
        if not re.fullmatch(r"0|-?[1-9][0-9]*", raw): raise StateXmlError(f"{where}:INTEGER")
        return int(raw)
    if name == "number": return _read_decimal(child, where)
    if name == "string": return _read_string_value(child, where)
    if name == "object": return _read_json_object(child, where)
    if name == "array":
        result = []
        for item in list(child):
            if item.tag != _tag("value"): raise StateXmlError(f"{where}:ARRAY")
            result.append(_read_json_value(item, where))
        return result
    raise StateXmlError(f"{where}:JSON_TYPE")


def _read_registry(root: ET.Element) -> dict[str, Any]:
    version, layout, entries_node = _children(root, ["schemaVersion", "stateLayout", "entries"], "REGISTRY")
    if _leaf_text(version, "REGISTRY:VERSION") != "2" or _leaf_text(layout, "REGISTRY:LAYOUT") != "analytic-inference-consumer-v2":
        raise StateXmlError("REGISTRY:IDENTITY")
    entries = []
    for node in list(entries_node):
        if node.tag != _tag("entry"): raise StateXmlError("REGISTRY:ENTRY")
        technology, aliases, catalog_id, locator = _children(node, ["technology", "aliases", "catalogId", "locator"], "REGISTRY:ENTRY")
        entries.append({"technology": _leaf_text(technology, "REGISTRY:TECHNOLOGY", nonempty=True), "aliases": _read_id_list(aliases, "REGISTRY:ALIASES"), "catalog_id": _leaf_text(catalog_id, "REGISTRY:CATALOG_ID", nonempty=True), "locator": _leaf_text(locator, "REGISTRY:LOCATOR", nonempty=True)})
    return {"schema_version": 2, "state_layout": "analytic-inference-consumer-v2", "entries": entries}


def _read_catalog(root: ET.Element) -> dict[str, Any]:
    version, catalog_id, technology, aliases, active_limit, entries_node = _children(root, ["schemaVersion", "catalogId", "technology", "aliases", "activeLimit", "entries"], "CATALOG")
    if _leaf_text(version, "CATALOG:VERSION") != "1": raise StateXmlError("CATALOG:VERSION")
    entries = []
    for node in list(entries_node):
        fields = _children(node, ["inferenceId", "revision", "status", "summary", "technologies", "surfaces", "objectives", "signals", "locator"], "CATALOG:ENTRY")
        entries.append({"inference_id": _leaf_text(fields[0], "CATALOG:ID", nonempty=True), "revision": int(_leaf_text(fields[1], "CATALOG:REVISION", nonempty=True)), "status": _leaf_text(fields[2], "CATALOG:STATUS", nonempty=True), "summary": _read_string_value(fields[3], "CATALOG:SUMMARY"), "technologies": _read_id_list(fields[4], "CATALOG:TECHNOLOGIES"), "surfaces": _read_string_list(fields[5], "CATALOG:SURFACES"), "objectives": _read_string_list(fields[6], "CATALOG:OBJECTIVES"), "signals": _read_string_list(fields[7], "CATALOG:SIGNALS"), "locator": _leaf_text(fields[8], "CATALOG:LOCATOR", nonempty=True)})
    return {"schema_version": 1, "catalog_id": _leaf_text(catalog_id, "CATALOG:ID", nonempty=True), "technology": _leaf_text(technology, "CATALOG:TECHNOLOGY", nonempty=True), "aliases": _read_id_list(aliases, "CATALOG:ALIASES"), "active_limit": int(_leaf_text(active_limit, "CATALOG:LIMIT", nonempty=True)), "entries": entries}


def _read_record(root: ET.Element) -> dict[str, Any]:
    fields = _children(root, ["schemaVersion", "inferenceId", "revision", "status", "statement", "applicability", "investigation", "provenance", "lineage", "snapshot"], "RECORD")
    if _leaf_text(fields[0], "RECORD:VERSION") != "1": raise StateXmlError("RECORD:VERSION")
    app = _children(fields[5], ["technologies", "versions", "surfaces", "objectives", "signals", "exclusions"], "RECORD:APP")
    inv = _children(fields[6], ["demandRelation", "confirmOrRejectEvidence", "potentialImpact", "cost", "stopCondition", "suggestedCapabilities"], "RECORD:INV")
    prov = _children(fields[7], ["sourceRefs", "acceptedEvidenceRefs", "freshness"], "RECORD:PROV")
    lineage = _children(fields[8], ["supersedes", "mergedFrom", "redirectTo", "tombstone"], "RECORD:LINEAGE")
    tomb_children = list(lineage[3])
    if len(tomb_children) != 1: raise StateXmlError("RECORD:TOMBSTONE")
    if tomb_children[0].tag == _tag("none"):
        _leaf_text(tomb_children[0], "RECORD:TOMBSTONE"); tombstone = None
    elif tomb_children[0].tag == _tag("value"):
        tombstone = _read_json_object(tomb_children[0], "RECORD:TOMBSTONE")
    else: raise StateXmlError("RECORD:TOMBSTONE")
    snap = _children(fields[9], ["algorithmVersion", "components", "score", "asOfEvent", "freshness", "denominators"], "RECORD:SNAPSHOT")
    component_keys = ["selected_count", "investigated_count", "validated_count", "rejected_count", "material_findings_count", "tasks_helped_count", "false_positive_count", "repeated_evidence_count", "stale_count"]
    component_xml = ["".join([key.split("_")[0], *[part.title() for part in key.split("_")[1:]]]) for key in component_keys]
    component_nodes = _children(snap[1], component_xml, "RECORD:COMPONENTS")
    return {
        "schema_version": 1, "inference_id": _leaf_text(fields[1], "RECORD:ID", nonempty=True), "revision": int(_leaf_text(fields[2], "RECORD:REVISION", nonempty=True)), "status": _leaf_text(fields[3], "RECORD:STATUS", nonempty=True), "statement": _read_string_value(fields[4], "RECORD:STATEMENT", nonempty=True),
        "applicability": {"technologies": _read_id_list(app[0], "RECORD:TECHNOLOGIES"), "versions": _read_string_list(app[1], "RECORD:VERSIONS"), "surfaces": _read_string_list(app[2], "RECORD:SURFACES"), "objectives": _read_string_list(app[3], "RECORD:OBJECTIVES"), "signals": _read_string_list(app[4], "RECORD:SIGNALS"), "exclusions": _read_string_list(app[5], "RECORD:EXCLUSIONS")},
        "investigation": {"demand_relation": _read_string_value(inv[0], "RECORD:DEMAND"), "confirm_or_reject_evidence": _read_string_list(inv[1], "RECORD:EVIDENCE"), "potential_impact": _read_string_value(inv[2], "RECORD:IMPACT"), "cost": _leaf_text(inv[3], "RECORD:COST", nonempty=True), "stop_condition": _read_string_value(inv[4], "RECORD:STOP"), "suggested_capabilities": _read_string_list(inv[5], "RECORD:CAPABILITIES")},
        "provenance": {"source_refs": _read_string_list(prov[0], "RECORD:SOURCES"), "accepted_evidence_refs": _read_string_list(prov[1], "RECORD:ACCEPTED"), "freshness": _leaf_text(prov[2], "RECORD:FRESHNESS", nonempty=True)},
        "lineage": {"supersedes": _read_id_list(lineage[0], "RECORD:SUPERSEDES"), "merged_from": _read_id_list(lineage[1], "RECORD:MERGED"), "redirect_to": _read_nullable_id(lineage[2], "RECORD:REDIRECT"), "tombstone": tombstone},
        "snapshot": {"algorithm_version": _read_string_value(snap[0], "RECORD:ALGORITHM", nonempty=True), "components": {key: int(_leaf_text(node, f"RECORD:{key}", nonempty=True)) for key, node in zip(component_keys, component_nodes)}, "score": int(_leaf_text(snap[2], "RECORD:SCORE", nonempty=True)), "as_of_event": _read_nullable_id(snap[3], "RECORD:AS_OF"), "freshness": _leaf_text(snap[4], "RECORD:SNAPSHOT_FRESHNESS", nonempty=True), "denominators": _read_json_object(snap[5], "RECORD:DENOMINATORS")},
    }


def _read_observed_cost(element: ET.Element, where: str) -> int | Decimal | str:
    children = list(element)
    if len(children) != 1: raise StateXmlError(f"{where}:COST")
    child = children[0]
    if child.tag in {_tag("unknown"), _tag("unsupported")}:
        _leaf_text(child, where); return child.tag.removeprefix(f"{{{NS}}}")
    if child.tag != _tag("value"): raise StateXmlError(f"{where}:COST")
    raw = _leaf_text(child, where, nonempty=True)
    if re.fullmatch(r"0|[1-9][0-9]*", raw): return int(raw)
    return _read_decimal(child, where, nonnegative=True)


def _read_event(root: ET.Element) -> dict[str, Any]:
    names = [child.tag.removeprefix(f"{{{NS}}}") for child in list(root)]
    expected_without = ["schemaVersion", "eventId", "source", "inferenceId", "inferenceRevision", "stage", "outcome", "reason", "agentCapability", "cost"]
    expected_with = ["schemaVersion", "eventId", "sequence", *expected_without[2:]]
    if names != expected_without and names != expected_with:
        raise StateXmlError("EVENT:STRUCTURE")
    fields = list(root); offset = 1 if names == expected_with else 0
    if _leaf_text(fields[0], "EVENT:VERSION") != "1": raise StateXmlError("EVENT:VERSION")
    result: dict[str, Any] = {"schema_version": 1, "event_id": _leaf_text(fields[1], "EVENT:ID", nonempty=True)}
    if offset: result["sequence"] = int(_leaf_text(fields[2], "EVENT:SEQUENCE", nonempty=True))
    source = fields[2 + offset]
    source_fields = _children(source, ["analysisRef", "runId", "handoffId", "evidenceRefs"], "EVENT:SOURCE")
    result.update({"source": {"analysis_ref": _read_string_value(source_fields[0], "EVENT:ANALYSIS", nonempty=True), "run_id": _read_string_value(source_fields[1], "EVENT:RUN", nonempty=True), "handoff_id": _read_string_value(source_fields[2], "EVENT:HANDOFF", nonempty=True), "evidence_refs": _read_string_list(source_fields[3], "EVENT:EVIDENCE")}, "inference_id": _leaf_text(fields[3 + offset], "EVENT:INFERENCE", nonempty=True), "inference_revision": int(_leaf_text(fields[4 + offset], "EVENT:REVISION", nonempty=True)), "stage": _leaf_text(fields[5 + offset], "EVENT:STAGE", nonempty=True), "outcome": _read_json_value(fields[6 + offset], "EVENT:OUTCOME"), "reason": _read_string_value(fields[7 + offset], "EVENT:REASON", nonempty=True), "agent_capability": _read_string_value(fields[8 + offset], "EVENT:CAPABILITY", nonempty=True)})
    cost_fields = _children(fields[9 + offset], ["context", "tools"], "EVENT:COST")
    result["cost"] = {"context": _read_observed_cost(cost_fields[0], "EVENT:CONTEXT"), "tools": _read_observed_cost(cost_fields[1], "EVENT:TOOLS")}
    return result


READERS = {"registry": _read_registry, "catalog": _read_catalog, "record": _read_record, "event": _read_event}


def _preparse(data: bytes) -> str:
    if data.startswith(b"\xef\xbb\xbf"): raise StateXmlError("XML_BOM")
    try: text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc: raise StateXmlError("XML_UTF8") from exc
    if not data.startswith(DECLARATION): raise StateXmlError("XML_DECLARATION")
    body = text[len(DECLARATION.decode("ascii")):]
    upper = body.upper()
    if "<!DOCTYPE" in upper: raise StateXmlError("XML_DOCTYPE")
    if "<!ENTITY" in upper: raise StateXmlError("XML_ENTITY_DECLARATION")
    if "<!--" in body: raise StateXmlError("XML_COMMENT")
    if "<?" in body: raise StateXmlError("XML_PROCESSING_INSTRUCTION")
    for name in NAMED_ENTITY.findall(body):
        if name not in PREDEFINED_ENTITIES: raise StateXmlError("XML_NAMED_ENTITY")
    return text


def _validate_tree(root: ET.Element) -> None:
    for element in root.iter():
        if not isinstance(element.tag, str) or not element.tag.startswith(f"{{{NS}}}"):
            raise StateXmlError("XML_NAMESPACE")
        if element.attrib: raise StateXmlError("XML_ATTRIBUTE")
        if element.tail not in {None, ""}: raise StateXmlError("XML_MIXED_CONTENT")
        if list(element) and element.text not in {None, ""}: raise StateXmlError("XML_MIXED_CONTENT")


def _parse_document(data: bytes, expected_kind: str | None, *, require_canonical: bool) -> dict[str, Any]:
    text = _preparse(data)
    try: root = ET.fromstring(text)
    except ET.ParseError as exc: raise StateXmlError(f"XML_PARSE:{exc}") from exc
    _validate_tree(root)
    kind = root.tag.removeprefix(f"{{{NS}}}") if root.tag.startswith(f"{{{NS}}}") else ""
    if kind not in KINDS or (expected_kind is not None and kind != expected_kind): raise StateXmlError("DOCUMENT_KIND")
    value = READERS[kind](root)
    canonical = _canonical_root(WRITERS[kind](value))
    if require_canonical and canonical != data: raise StateXmlError("XML_NONCANONICAL")
    return value


def parse_state_bytes(data: bytes, expected_kind: str | None = None) -> dict[str, Any]:
    """Strictly parse one canonical state document and return its logical object."""
    return _parse_document(data, expected_kind, require_canonical=True)


def load_state(path: Path, expected_kind: str | None = None) -> dict[str, Any]:
    return parse_state_bytes(path.read_bytes(), expected_kind)


def _self_test(fixture_path: Path) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"), parse_float=Decimal)
    passed = 0
    digests: dict[str, str] = {}
    canonical_documents: dict[str, bytes] = {}
    for case in fixture["documents"]:
        payload = canonical_state(case["value"], case["kind"])
        if not _logical_equivalent(parse_state_bytes(payload, case["kind"]), case["value"]):
            raise StateXmlError(f"SELF_TEST_ROUND_TRIP:{case['id']}")
        if canonical_state(case["value"], case["kind"]) != payload:
            raise StateXmlError(f"SELF_TEST_DETERMINISM:{case['id']}")
        canonical_documents[case["kind"]] = payload
        digests[case["id"]] = hashlib.sha256(payload).hexdigest()
        passed += 1
    base = canonical_documents["registry"]
    event = canonical_documents["event"]
    record = canonical_documents["record"]
    schema = b"<schemaVersion>2</schemaVersion>"
    layout = b"<stateLayout>analytic-inference-consumer-v2</stateLayout>"
    decimal_entry = b"<entry><key><text>decimal</text></key><value><number>1.25</number></value></entry>"
    integer_entry = b"<entry><key><text>integer</text></key><value><integer>1</integer></value></entry>"
    attacks = {
        "missing_declaration": base[len(DECLARATION):],
        "wrong_declaration": base.replace(b'encoding="UTF-8"', b'encoding="utf-8"', 1),
        "bom": b"\xef\xbb\xbf" + base,
        "invalid_utf8": base[:-2] + b"\xff\n",
        "doctype": base.replace(b"<registry", b"<!DOCTYPE registry><registry", 1),
        "entity": base.replace(b"<registry", b"<!ENTITY x 'y'><registry", 1),
        "named_entity": base.replace(b"analytic-inference-consumer-v2", b"analytic&custom;-inference-consumer-v2", 1),
        "comment": base.replace(b"<registry", b"<!--x--><registry", 1),
        "processing_instruction": base.replace(b"<registry", b"<?unsafe value?><registry", 1),
        "attribute": base.replace(b"<registry", b"<registry bad=\"1\"", 1),
        "noncanonical": base.replace(b"><", b">\n<", 1),
        "numeric_entity": base.replace(b"analytic-inference", b"&#97;nalytic-inference", 1),
        "wrong_namespace": base.replace(NS.encode(), b"urn:loki:wrong", 1),
        "unknown_element": base.replace(layout, layout + b"<unknown></unknown>", 1),
        "reordered_element": base.replace(schema + layout, layout + schema, 1),
        "missing_element": base.replace(layout, b"", 1),
        "duplicate_element": base.replace(schema, schema + schema, 1),
        "malformed_xml": base.replace(b"</registry>", b"", 1),
        "malformed_base64": record.replace(b"Y29udHJvbDoBIG11c3QgdXNlIGJhc2U2NA==", b"!!!", 1),
        "base64_not_required": record.replace(b"Y29udHJvbDoBIG11c3QgdXNlIGJhc2U2NA==", b"ZWxpZ2libGU=", 1),
        "duplicate_object_key": event.replace(decimal_entry, decimal_entry + decimal_entry, 1),
        "unsorted_object_key": event.replace(decimal_entry + integer_entry, integer_entry + decimal_entry, 1),
        "nan_number": event.replace(b"<number>1.25</number>", b"<number>NaN</number>", 1),
        "infinite_number": event.replace(b"<number>1.25</number>", b"<number>INF</number>", 1),
        "negative_cost": event.replace(b"<context><value>1.5</value></context>", b"<context><value>-1.5</value></context>", 1),
    }
    for hostile in fixture["hostile_cases"]:
        if hostile == "wrong_kind":
            try: parse_state_bytes(event, "record")
            except StateXmlError: passed += 1
            else: raise StateXmlError("SELF_TEST_HOSTILE_ACCEPTED:wrong_kind")
            continue
        if hostile == "unpaired_surrogate":
            candidate = dict(fixture["documents"][1]["value"])
            candidate["entries"] = [dict(candidate["entries"][0], summary="\ud800")]
            try: canonical_state(candidate, "catalog")
            except StateXmlError: passed += 1
            else: raise StateXmlError("SELF_TEST_HOSTILE_ACCEPTED:unpaired_surrogate")
            continue
        if hostile == "bool_int_distinct":
            outcome = parse_state_bytes(event, "event")["outcome"]
            if type(outcome["ok"]) is bool and type(outcome["integer"]) is int:
                passed += 1
                continue
            raise StateXmlError("SELF_TEST_TYPE_COLLAPSE:bool_int")
        if hostile == "precise_decimal":
            candidate = dict(fixture["documents"][3]["value"])
            candidate["outcome"] = {"precise": Decimal("0.12345678901234567890123456789")}
            payload = canonical_state(candidate, "event")
            observed = parse_state_bytes(payload, "event")["outcome"]["precise"]
            if observed == Decimal("0.12345678901234567890123456789") and type(observed) is Decimal:
                passed += 1
                continue
            raise StateXmlError("SELF_TEST_DECIMAL_PRECISION")
        payload = attacks[hostile]
        try: parse_state_bytes(payload)
        except StateXmlError: passed += 1
        else: raise StateXmlError(f"SELF_TEST_HOSTILE_ACCEPTED:{hostile}")
    return {"digests": digests, "passed": passed, "status": "valid", "total": len(fixture["documents"]) + len(fixture["hostile_cases"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    self_test = subparsers.add_parser("self-test")
    self_test.add_argument("--fixture", type=Path, required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("path", type=Path)
    validate.add_argument("--kind", choices=sorted(KINDS))
    args = parser.parse_args()
    try:
        if args.command == "self-test":
            output = _self_test(args.fixture)
        else:
            value = load_state(args.path, args.kind)
            output = {"kind": args.kind, "path": str(args.path), "root_keys": sorted(value), "sha256": hashlib.sha256(args.path.read_bytes()).hexdigest(), "status": "valid"}
        print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except (OSError, json.JSONDecodeError, StateXmlError) as exc:
        diagnostic = exc.diagnostic if isinstance(exc, StateXmlError) else f"INPUT:{exc}"
        print(json.dumps({"diagnostics": [diagnostic], "status": "blocked"}, sort_keys=True, separators=(",", ":")))
        return 2


if __name__ == "__main__":
    sys.exit(main())
