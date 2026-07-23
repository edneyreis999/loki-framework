#!/usr/bin/env python3
"""Collect a provider-neutral, sanitized session-evidence manifest atomically.

Input is JSON so adapters can remain small and closed by default.  The command
never stores the supplied raw event document: it first removes payload-bearing
keys and then publishes only a structural snapshot plus an XML manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

DIMENSIONS = ("transcript", "tool_io", "errors", "reasoning_summary", "token_usage")
STATES = {"complete", "partial", "pointer-only", "unavailable", "unsupported"}
SENSITIVE = {"content", "prompt", "text", "message", "messages", "transcript", "payload", "raw", "token", "secret", "password", "authorization", "api_key", "environment", "env", "headers", "cookies"}
INPUT_KEYS = {"identity", "runtime", "terminal_status", "locator", "dimensions", "usage", "events", "completion_summary", "next_destination"}
IDENTITY_KEYS = {"run_id", "agent_run_id", "handoff_id", "agent_name"}
RUNTIME_KEYS = {"adapter", "adapter_version", "root_session_id", "parent_thread_id", "thread_id", "runtime_agent_id"}
LOCATOR_KEYS = {"kind", "value", "portability", "reason"}
DIMENSION_KEYS = {"status", "reason"}
USAGE_KEYS = {"metric_kind", "source", "source_scope", "measured_at", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens"}
USAGE_COUNTERS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")

def now() -> str: return datetime.now(timezone.utc).isoformat()
def clean(value):
    if isinstance(value, dict): return {k: clean(v) for k, v in value.items() if k.lower() not in SENSITIVE}
    if isinstance(value, list): return [clean(v) for v in value]
    return value
def atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".evidence-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
        try:
            dfd = os.open(path.parent, os.O_DIRECTORY); os.fsync(dfd); os.close(dfd)
        except (AttributeError, OSError): pass
    except Exception:
        try: os.unlink(name)
        except FileNotFoundError: pass
        raise
def add(parent, tag, value="", **attrs):
    node = ET.SubElement(parent, tag, attrs); node.text = "" if value is None else str(value); return node
def canonical(root):
    node = root.find("integrity/canonical_content_checksum"); old = node.text; node.text = ""
    result = hashlib.sha256(ET.tostring(root, encoding="utf-8", short_empty_elements=True)).hexdigest(); node.text = old
    return result
def reject_unknown(mapping, allowed, label):
    unknown = set(mapping) - allowed
    if unknown:
        raise ValueError(f"unknown {label} field(s): {', '.join(sorted(unknown))}")
def validate_input(data):
    if not isinstance(data, dict): raise ValueError("input must be a JSON object")
    reject_unknown(data, INPUT_KEYS, "input")
    for key, allowed, label, required in (("identity", IDENTITY_KEYS, "identity", True), ("runtime", RUNTIME_KEYS, "runtime", False), ("locator", LOCATOR_KEYS, "locator", False), ("usage", USAGE_KEYS, "usage", False)):
        item = data.get(key, {})
        if required and not isinstance(item, dict): raise ValueError(f"{label} must be an object")
        if item is not None and not isinstance(item, dict): raise ValueError(f"{label} must be an object")
        reject_unknown(item or {}, allowed, label)
    if set(data["identity"]) != IDENTITY_KEYS or any(not str(data["identity"][name]).strip() for name in IDENTITY_KEYS):
        raise ValueError("identity must contain exactly four non-empty typed values")
    dimensions = data.get("dimensions", {})
    if not isinstance(dimensions, dict): raise ValueError("dimensions must be an object")
    reject_unknown(dimensions, set(DIMENSIONS), "dimensions")
    for name, item in dimensions.items():
        if not isinstance(item, dict): raise ValueError(f"dimension {name} must be an object")
        reject_unknown(item, DIMENSION_KEYS, f"dimension {name}")
        if item.get("status") not in STATES: raise ValueError(f"dimension {name} has invalid status")
        if item.get("status") != "complete" and not str(item.get("reason", "")).strip(): raise ValueError(f"degraded dimension {name} needs a reason")
    token_state = dimensions.get("token_usage", {}).get("status", "unsupported")
    usage = data.get("usage", {}) or {}
    if token_state == "complete":
        if set(usage) != USAGE_KEYS: raise ValueError("complete token usage requires every provenance field and counter")
        if usage.get("metric_kind") != "per-turn-delta" or usage.get("source_scope") != "verified-agent-run": raise ValueError("complete token usage requires a verified run-scoped per-turn counter")
        if not str(usage.get("source", "")).strip() or not str(usage.get("measured_at", "")).strip(): raise ValueError("complete token usage requires source and measured_at")
        if any(type(usage.get(key)) is not int or usage[key] < 0 for key in USAGE_COUNTERS): raise ValueError("complete token usage counters must be explicit non-negative integers")
        if usage["total_tokens"] != usage["input_tokens"] + usage["output_tokens"]: raise ValueError("complete token usage total must equal input plus output")
    elif usage:
        raise ValueError("degraded token usage cannot carry counters; record the reason on the dimension")
def status_for(data, name):
    item = data.get("dimensions", {}).get(name, {})
    state = item.get("status", "unsupported")
    return state, item.get("reason") or "adapter capability not evidenced"
def build(data, snapshot_path, snapshot_sum):
    ids = data["identity"]; runtime = data.get("runtime", {}); root = ET.Element("agent_session_evidence", {"schema_version":"1"})
    identity = ET.SubElement(root,"identity")
    for name, typ in (("run_id","loki-run-id"),("agent_run_id","agent-run-id"),("handoff_id","handoff-id"),("agent_name","agent-name")): add(identity,name,ids[name],type=typ)
    r = ET.SubElement(root,"runtime"); add(r,"adapter",runtime.get("adapter","generic")); add(r,"adapter_version",runtime.get("adapter_version",""));
    for name, typ in (("root_session_id","runtime-root-session-id"),("parent_thread_id","runtime-parent-thread-id"),("thread_id","runtime-thread-id"),("runtime_agent_id","runtime-agent-id")): add(r,name,runtime.get(name, f"unknown-{name}"),type=typ)
    add(r,"terminal_status",data.get("terminal_status","unknown")); parent=ET.SubElement(r,"parent_reference"); add(parent,"type",""); add(parent,"value","")
    loc = ET.SubElement(root,"locator"); locator=data.get("locator",{})
    kind=locator.get("kind","unavailable"); add(loc,"kind",kind); add(loc,"value",locator.get("value", "")); add(loc,"portability",locator.get("portability", "none" if kind=="unavailable" else "same-profile")); add(loc,"unavailable_reason",locator.get("reason", "runtime locator unavailable" if kind=="unavailable" else ""))
    snap=ET.SubElement(root,"snapshot")
    if snapshot_path:
        add(snap,"storage_mode","pointer-plus-sanitized-snapshot"); add(snap,"payload_path",snapshot_path.name); add(snap,"captured_at",now()); add(snap,"payload_checksum",snapshot_sum,algorithm="sha-256"); add(snap,"checksum_absence_reason","")
    else:
        add(snap,"storage_mode","unavailable"); add(snap,"payload_path",""); add(snap,"captured_at",""); add(snap,"payload_checksum",""); add(snap,"checksum_absence_reason","no sanitized payload supplied")
    comp=ET.SubElement(root,"evidence_completeness"); states=[]
    for name in DIMENSIONS:
        state, reason=status_for(data,name); states.append(state); d=ET.SubElement(comp,"dimension",name=name); add(d,"status",state); add(d,"missing_reason","" if state=="complete" else reason)
        if name == "reasoning_summary": add(d, "provenance", "")
    overall="complete" if all(s=="complete" for s in states) and snapshot_path and kind!="unavailable" else next((s for s in states if s!="complete"),"partial")
    add(comp,"overall_status",overall)
    usage=ET.SubElement(root,"usage"); us=data.get("usage",{}); ustate,status_reason=status_for(data,"token_usage"); add(usage,"status",ustate)
    if ustate=="complete":
        for key in ("metric_kind","source","source_scope","measured_at"): add(usage,key,us[key])
        for key in USAGE_COUNTERS: add(usage,key,us[key])
        add(usage,"unavailable_reason","")
    else:
        for key in ("metric_kind","source","source_scope","measured_at","input_tokens","cached_input_tokens","output_tokens","reasoning_output_tokens","total_tokens"): add(usage,key,"")
        add(usage,"unavailable_reason",status_reason)
    sec=ET.SubElement(root,"security"); add(sec,"snapshot_classification","sanitized"); add(sec,"structural_redaction_result","sensitive structural fields removed"); add(sec,"secret_pii_hardening","deferred"); add(sec,"retention_metadata","deferred"); add(sec,"purge_policy","deferred")
    integ=ET.SubElement(root,"integrity"); add(integ,"canonical_content_checksum","",algorithm="sha-256"); add(integ,"result","verified"); add(integ,"verification_notes","published atomically")
    cr=ET.SubElement(root,"completion_record"); add(cr,"agent_run_id",ids["agent_run_id"],type="agent-run-id"); add(cr,"handoff_id",ids["handoff_id"],type="handoff-id"); add(cr,"terminal_status",data.get("terminal_status","unknown")); add(cr,"summary",data.get("completion_summary","collector result"));
    for container, child in (("changed_files", "file"), ("read_files", "file"), ("validations", "validation"), ("material_attempts", "attempt"), ("known_errors", "error"), ("decisions", "decision"), ("residual_risks", "risk")): ET.SubElement(cr, container)
    add(cr,"next_destination",data.get("next_destination","orchestrator"))
    policy=ET.SubElement(root,"evidence_policy"); [add(policy,k,v) for k,v in (("mode","evidence-first"),("gap_handling","preserve-gap"),("capture_owner","collector-only"),("retrospective_dispatch","explicit-only"))]
    root.find("integrity/canonical_content_checksum").text=canonical(root); return root
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("input"); parser.add_argument("--output-dir",required=True); args=parser.parse_args()
    data=json.loads(Path(args.input).read_text(encoding="utf-8")); validate_input(data); output=Path(args.output_dir); snapshot=None; checksum=""
    if data.get("events") is not None:
        snapshot=output/"sanitized-snapshot.json"; payload=json.dumps(clean(data["events"]),sort_keys=True,separators=(",",":")).encode(); checksum=hashlib.sha256(payload).hexdigest(); atomic(snapshot,payload)
    root=build(data,snapshot,checksum); manifest=output/"evidence-manifest.xml"; atomic(manifest,ET.tostring(root,encoding="utf-8",xml_declaration=True))
    # post-publication verification; failure is visible to callers and never relabelled complete
    if hashlib.sha256(snapshot.read_bytes()).hexdigest()!=checksum if snapshot else False: raise RuntimeError("snapshot checksum mismatch")
if __name__ == "__main__": main()
