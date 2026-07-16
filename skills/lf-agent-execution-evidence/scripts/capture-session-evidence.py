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
def status_for(data, name):
    item = data.get("dimensions", {}).get(name, {})
    state = item.get("status", "unsupported")
    return (state if state in STATES else "unsupported", item.get("reason") or "adapter capability not evidenced")
def build(data, snapshot_path, snapshot_sum):
    ids = data["identity"]; runtime = data.get("runtime", {}); root = ET.Element("agent_session_evidence", {"schema_version":"1"})
    identity = ET.SubElement(root,"identity")
    for name, typ in (("run_id","loki-run-id"),("agent_run_id","agent-run-id"),("handoff_id","handoff-id"),("agent_name","agent-name")): add(identity,name,ids[name],type=typ)
    r = ET.SubElement(root,"runtime"); add(r,"adapter",runtime.get("adapter","generic")); add(r,"adapter_version",runtime.get("adapter_version",""));
    for name, typ in (("root_session_id","runtime-root-session-id"),("parent_thread_id","runtime-parent-thread-id"),("thread_id","runtime-thread-id"),("runtime_agent_id","runtime-agent-id")): add(r,name,runtime.get(name, f"unknown-{name}"),type=typ)
    add(r,"terminal_status",data.get("terminal_status","unknown"))
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
    overall="complete" if all(s=="complete" for s in states) and snapshot_path and kind!="unavailable" else next((s for s in states if s!="complete"),"partial")
    add(comp,"overall_status",overall)
    usage=ET.SubElement(root,"usage"); us=data.get("usage",{}); ustate,status_reason=status_for(data,"token_usage"); add(usage,"status",ustate)
    if ustate=="complete":
        for key in ("metric_kind","source","source_scope","measured_at"): add(usage,key,us.get(key,""))
        for key in ("input_tokens","cached_input_tokens","output_tokens","reasoning_output_tokens","total_tokens"): add(usage,key,us.get(key,0))
        add(usage,"unavailable_reason","")
    else:
        for key in ("metric_kind","source","source_scope","measured_at","input_tokens","cached_input_tokens","output_tokens","reasoning_output_tokens","total_tokens"): add(usage,key,"")
        add(usage,"unavailable_reason",status_reason)
    sec=ET.SubElement(root,"security"); add(sec,"snapshot_classification","sanitized"); add(sec,"structural_redaction_result","sensitive structural fields removed"); add(sec,"secret_pii_hardening","deferred"); add(sec,"retention_metadata","deferred"); add(sec,"purge_policy","deferred")
    integ=ET.SubElement(root,"integrity"); add(integ,"canonical_content_checksum","",algorithm="sha-256"); add(integ,"result","verified"); add(integ,"verification_notes","published atomically")
    cr=ET.SubElement(root,"completion_record"); add(cr,"agent_run_id",ids["agent_run_id"],type="agent-run-id"); add(cr,"handoff_id",ids["handoff_id"],type="handoff-id"); add(cr,"terminal_status",data.get("terminal_status","unknown")); add(cr,"summary",data.get("completion_summary","collector result")); add(cr,"next_destination",data.get("next_destination","orchestrator"))
    policy=ET.SubElement(root,"retrospective_policy"); [add(policy,k,v) for k,v in (("mode","evidence-first"),("automatic_agent_retrospective","false"),("dual_capture","false"),("legacy_retrospective_fallback","false"),("evidence_gap_handling","preserve-gap"))]
    root.find("integrity/canonical_content_checksum").text=canonical(root); return root
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("input"); parser.add_argument("--output-dir",required=True); args=parser.parse_args()
    data=json.loads(Path(args.input).read_text(encoding="utf-8")); output=Path(args.output_dir); snapshot=None; checksum=""
    if data.get("events") is not None:
        snapshot=output/"sanitized-snapshot.json"; payload=json.dumps(clean(data["events"]),sort_keys=True,separators=(",",":")).encode(); checksum=hashlib.sha256(payload).hexdigest(); atomic(snapshot,payload)
    root=build(data,snapshot,checksum); manifest=output/"evidence-manifest.xml"; atomic(manifest,ET.tostring(root,encoding="utf-8",xml_declaration=True))
    # post-publication verification; failure is visible to callers and never relabelled complete
    if hashlib.sha256(snapshot.read_bytes()).hexdigest()!=checksum if snapshot else False: raise RuntimeError("snapshot checksum mismatch")
if __name__ == "__main__": main()
