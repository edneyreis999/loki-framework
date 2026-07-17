#!/usr/bin/env python3
"""Validate the Loki init/catalogador handoff contracts.

The default run validates the versioned package templates and executes a
self-contained contract suite in a temporary directory.  ``--enforce-current-tree``
also enables the post-migration agent ownership and Markdown/TOML projection
checks; it is intentionally opt-in while the package is between migration
phases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import sys
import tempfile
import tomllib
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


CALLER_MODES = {
    "loki-init": {
        "init-bootstrap-cataloger",
        "init-publication-batch",
        "init-final-reconciliation",
    },
    "loki-continuous-improvement": {"task_scoped_writer"},
    "loki-catalogar-docs": {"task_scoped_writer", "proposal-only"},
    "loki-run-plan": {"task_scoped_writer"},
}
INIT_MODES = CALLER_MODES["loki-init"]
BATCH_TRANSITIONS = {
    "planned": {"dispatched", "blocked"},
    "dispatched": {"write-applied", "blocked"},
    "write-applied": {"validated", "blocked"},
    "validated": {"committed", "blocked"},
    "committed": set(),
    "blocked": set(),
}
PACKET_TEMPLATE = "templates/loki-init-research-packet-template.xml"
BATCH_TEMPLATE = "templates/loki-init-publication-batch-template.xml"
REPORT_TEMPLATE = "templates/agent-run-report-template.xml"
PARITY_FIELDS = {
    "name",
    "status",
    "mode",
    "required_skills",
    "scoped_write_modes",
    "task_write_mode",
    "scoped_write_domains",
    "init_role",
    "domain_context_preflight",
}
CONSUMER_DOC_CAPABILITIES = {"consumer-docs", "docs-index"}


class ContractError(ValueError):
    """An actionable contract validation failure."""


@dataclass(frozen=True)
class PacketIdentity:
    packet_id: str
    revision: int
    packet_hash: str
    supersedes_id: str = ""
    supersedes_revision: int = 0
    supersedes_hash: str = ""


@dataclass(frozen=True)
class BatchIdentity:
    batch_id: str
    idempotency_key: str
    batch_hash: str
    packets: tuple[tuple[int, str, int, str], ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def node_text(root: ET.Element, path: str) -> str:
    node = root.find(path)
    return "" if node is None or node.text is None else node.text.strip()


def parse_xml(path: Path) -> ET.Element:
    try:
        return ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise ContractError(f"{path}: XML parse failed: {exc}") from exc


def require_template_node(
    root: ET.Element,
    path: str,
    *,
    attributes: dict[str, str] | None = None,
) -> ET.Element:
    node = root.find(path)
    require(node is not None, f"template <{root.tag}> missing required node {path}")
    for key, expected in (attributes or {}).items():
        require(
            node.get(key) == expected,
            f"template <{root.tag}> node {path} must declare {key}={expected!r}",
        )
    return node


def validate_package_templates(package_root: Path) -> int:
    packet = parse_xml(package_root / PACKET_TEMPLATE)
    require(packet.tag == "loki_init_research_packet", "research packet template has wrong root")
    require(packet.get("schema_version") == "1", "research packet template must use schema_version=1")
    packet_nodes = {
        "identity/run_id": {"required": "true"},
        "identity/investigator_invocation_id": {"required": "true"},
        "identity/packet_id": {"required": "true"},
        "identity/packet_revision": {"required": "true"},
        "identity/sequence": {"required": "true"},
        "identity/packet_hash": {"required": "true", "algorithm": "sha-256"},
        "status": {"required": "true"},
        "sources/read": {},
        "findings/facts/fact/source_refs": {"required": "true", "min_items": "1"},
        "coverage_delta": {},
        "continuation/logical_status": {"required": "true"},
        "validation/acceptance_status": {"required": "true"},
    }
    for path, attributes in packet_nodes.items():
        require_template_node(packet, path, attributes=attributes)
    packet_invariants = {node.get("id") for node in packet.findall("invariants/invariant")}
    require(
        {
            "accepted-packet-immutable",
            "identical-retry-no-op",
            "divergent-retry-requires-lineage",
            "fact-source-required",
        } <= packet_invariants,
        "research packet template is missing an identity/source invariant",
    )

    batch = parse_xml(package_root / BATCH_TEMPLATE)
    require(batch.tag == "loki_init_publication_batch", "publication batch template has wrong root")
    require(batch.get("schema_version") == "1", "publication batch template must use schema_version=1")
    batch_nodes = {
        "invocation/calling_workflow": {"required": "true", "enum": "loki-init"},
        "invocation/write_mode": {"required": "true", "enum": "init-publication-batch"},
        "invocation/exclusive_write_owner": {"required": "true"},
        "identity/run_id": {"required": "true"},
        "identity/batch_id": {"required": "true"},
        "identity/idempotency_key": {"required": "true"},
        "identity/batch_hash": {"required": "true", "algorithm": "sha-256"},
        "packet_set": {"required": "true", "immutable": "true", "ordered": "true"},
        "checkpoint/previous_checkpoint_ref": {"required": "true"},
        "checkpoint/before_state_hash": {"required": "true"},
        "validators": {"required": "true", "min_items": "1"},
        "lifecycle/status": {"required": "true"},
        "destinations/success": {"required": "true"},
        "destinations/failure": {"required": "true"},
    }
    for path, attributes in batch_nodes.items():
        require_template_node(batch, path, attributes=attributes)
    require(node_text(batch, "invocation/calling_workflow") == "loki-init", "batch caller must be fixed to loki-init")
    require(node_text(batch, "invocation/write_mode") == "init-publication-batch", "batch mode must be fixed")
    require(node_text(batch, "invocation/exclusive_write_owner") == "catalogador", "batch owner must be catalogador")

    report = parse_xml(package_root / REPORT_TEMPLATE)
    require(report.tag == "agent_run_report", "agent run report template has wrong root")
    for path in (
        "identity/agent_run_id",
        "write_contract/write_mode",
        "operational_refs/research_packets",
        "operational_refs/publication_batches",
        "completion/status",
    ):
        require_template_node(report, path)
    return len(packet_nodes) + len(batch_nodes) + 5


def validate_packet(root: ET.Element) -> PacketIdentity:
    require(root.tag == "loki_init_research_packet", "packet: wrong XML root")
    require(root.get("schema_version") == "1", "packet: unsupported schema_version")
    required = (
        "identity/run_id",
        "identity/investigator",
        "identity/investigator_invocation_id",
        "identity/packet_id",
        "identity/packet_revision",
        "identity/sequence",
        "identity/topic_id",
        "identity/packet_hash",
        "status",
        "scope/objective",
        "continuation/logical_status",
        "validation/schema_status",
        "validation/acceptance_status",
    )
    for path in required:
        require(bool(node_text(root, path)), f"packet: missing required field {path}")
    try:
        revision = int(node_text(root, "identity/packet_revision"))
        sequence = int(node_text(root, "identity/sequence"))
    except ValueError as exc:
        raise ContractError("packet: revision and sequence must be integers") from exc
    require(revision > 0 and sequence > 0, "packet: revision and sequence must be positive")
    packet_hash = node_text(root, "identity/packet_hash")
    require(len(packet_hash) == 64 and all(c in "0123456789abcdef" for c in packet_hash), "packet: packet_hash must be lowercase sha-256")

    read_ids = {
        source.get("source_id", "")
        for source in root.findall("sources/read/source")
        if source.get("source_id") and node_text(source, "locator")
    }
    require(bool(read_ids), "packet: sources/read must contain a source with locator")
    for fact in root.findall("findings/facts/fact"):
        finding_id = fact.get("finding_id") or "<missing-id>"
        require(bool(node_text(fact, "statement")), f"packet: fact {finding_id} missing statement")
        refs = [ref.get("source_id", "") for ref in fact.findall("source_refs/source_ref")]
        require(bool(refs), f"packet: fact {finding_id} requires at least one source_ref")
        unknown = sorted(set(refs) - read_ids)
        require(not unknown, f"packet: fact {finding_id} references unread source(s): {', '.join(unknown)}")

    supersedes = root.find("identity/supersedes/packet_ref")
    return PacketIdentity(
        packet_id=node_text(root, "identity/packet_id"),
        revision=revision,
        packet_hash=packet_hash,
        supersedes_id="" if supersedes is None else supersedes.get("id", ""),
        supersedes_revision=0 if supersedes is None else int(supersedes.get("revision", "0") or 0),
        supersedes_hash="" if supersedes is None else supersedes.get("hash", ""),
    )


def accept_packet(existing: PacketIdentity | None, candidate: PacketIdentity) -> str:
    if existing is None:
        return "accepted"
    if candidate.packet_id == existing.packet_id and candidate.packet_hash == existing.packet_hash:
        require(candidate.revision == existing.revision, "packet retry: identical hash changed revision")
        return "no-op"
    require(candidate.packet_id == existing.packet_id, "packet revision: identity must retain packet_id")
    require(candidate.revision > existing.revision, "packet retry: divergent same ID requires a higher revision")
    require(candidate.supersedes_id == existing.packet_id, "packet retry: divergent same ID requires supersedes packet_id")
    require(candidate.supersedes_revision == existing.revision, "packet retry: supersedes revision does not match accepted packet")
    require(candidate.supersedes_hash == existing.packet_hash, "packet retry: supersedes hash does not match accepted packet")
    return "superseded"


def validate_caller_mode(caller: str, mode: str) -> None:
    require(bool(caller), "caller/mode preflight: missing calling_workflow; rejected before write")
    require(caller in CALLER_MODES, f"caller/mode preflight: unknown calling_workflow {caller!r}; rejected before write")
    known_modes = set().union(*CALLER_MODES.values())
    require(mode in known_modes, f"caller/mode preflight: unknown write_mode {mode!r}; rejected before write")
    require(mode in CALLER_MODES[caller], f"caller/mode preflight: crossed pair {caller!r} + {mode!r}; rejected before write")


def validate_batch(root: ET.Element) -> BatchIdentity:
    require(root.tag == "loki_init_publication_batch", "batch: wrong XML root")
    require(root.get("schema_version") == "1", "batch: unsupported schema_version")
    caller = node_text(root, "invocation/calling_workflow")
    mode = node_text(root, "invocation/write_mode")
    validate_caller_mode(caller, mode)
    require(caller == "loki-init" and mode == "init-publication-batch", "batch: fixed caller/mode contract violated")
    require(node_text(root, "invocation/exclusive_write_owner") == "catalogador", "batch: consumer docs owner must be catalogador")
    required = (
        "identity/run_id",
        "identity/batch_id",
        "identity/idempotency_key",
        "identity/batch_hash",
        "checkpoint/previous_checkpoint_ref",
        "checkpoint/before_state_hash",
        "destinations/success",
        "destinations/failure",
        "lifecycle/status",
    )
    for path in required:
        require(bool(node_text(root, path)), f"batch: missing required field {path}")
    refs = root.findall("packet_set/packet_ref")
    require(bool(refs), "batch: immutable ordered packet_set must not be empty")
    packets: list[tuple[int, str, int, str]] = []
    for ref in refs:
        try:
            packet = (int(ref.get("position", "0")), ref.get("packet_id", ""), int(ref.get("revision", "0")), ref.get("hash", ""))
        except ValueError as exc:
            raise ContractError("batch: packet positions and revisions must be integers") from exc
        require(packet[1] and packet[2] > 0 and len(packet[3]) == 64, "batch: packet_ref requires ID, positive revision and sha-256 hash")
        packets.append(packet)
    require([item[0] for item in packets] == list(range(1, len(packets) + 1)), "batch: packet_set positions must be ordered and contiguous")
    require(len({item[1] for item in packets}) == len(packets), "batch: packet_set contains duplicate packet_id")
    require(bool(root.findall("validators/validator/command")), "batch: at least one validator command is required")
    batch_hash = node_text(root, "identity/batch_hash")
    require(len(batch_hash) == 64, "batch: batch_hash must be sha-256")
    return BatchIdentity(node_text(root, "identity/batch_id"), node_text(root, "identity/idempotency_key"), batch_hash, tuple(packets))


def accept_batch(existing: BatchIdentity | None, candidate: BatchIdentity) -> str:
    if existing is None:
        return "accepted"
    same_identity = existing.batch_id == candidate.batch_id or existing.idempotency_key == candidate.idempotency_key
    if not same_identity:
        return "accepted"
    require(existing == candidate, "batch retry: divergent content reused batch_id or idempotency_key")
    return "no-op"


def validate_transition(before: str, after: str) -> None:
    require(before in BATCH_TRANSITIONS and after in BATCH_TRANSITIONS, f"batch lifecycle: unknown state {before!r} or {after!r}")
    require(after in BATCH_TRANSITIONS[before], f"batch lifecycle: invalid transition {before} -> {after}")


def validate_single_init_writer(writers: list[dict[str, str]]) -> None:
    active = [writer for writer in writers if writer.get("workflow") == "loki-init" and writer.get("mode") in INIT_MODES and writer.get("status") in {"dispatched", "writing", "running", "write-applied"}]
    require(len(active) <= 1, "init writer ownership: two concurrent catalogador init writers detected")
    for writer in active:
        require(writer.get("owner") == "catalogador", "init writer ownership: active consumer docs writer is not catalogador")


def lexical_absolute(root: Path, target: str) -> str:
    root_text = posixpath.normpath(root.as_posix())
    require(root_text.startswith("/"), f"ownership roots must be explicit absolute paths: {root}")
    target_text = target.replace("\\", "/")
    if not target_text.startswith("/"):
        target_text = posixpath.join(root_text, target_text)
    return posixpath.normpath(target_text)


def path_is_within(path: str, root: str) -> bool:
    root = root.rstrip("/")
    return path == root or path.startswith(root + "/")


def validate_write_ownership(
    owner: str,
    write_class: str,
    target: str,
    mode: str,
    *,
    consumer_project_root: Path,
    package_root: Path,
) -> None:
    require(consumer_project_root != package_root, "ownership roots must distinguish consumer project from package source")
    base = package_root if write_class == "package-documentation" else consumer_project_root
    normalized_target = lexical_absolute(base, target)
    consumer_docs_root = lexical_absolute(consumer_project_root, "docs")
    package_docs_root = lexical_absolute(package_root, "docs")
    package_documentation = write_class == "package-documentation" and path_is_within(normalized_target, package_docs_root)
    consumer_docs = (
        write_class in CONSUMER_DOC_CAPABILITIES
        or (path_is_within(normalized_target, consumer_docs_root) and not package_documentation)
    )
    if consumer_docs:
        require(owner == "catalogador", f"consumer docs ownership: {owner!r} cannot write normalized target {normalized_target!r}")
    else:
        require(mode == "task_scoped_writer", "non-document write: legitimate writes still require task_scoped_writer")


def validate_governed_caller_policy(
    caller: str,
    declared_modes: set[str],
    *,
    rejects_before_write: bool,
    consumer_docs_fallback: bool,
) -> None:
    require(caller in CALLER_MODES, f"governed caller contract: unknown caller {caller!r}")
    missing = CALLER_MODES[caller] - declared_modes
    require(not missing, f"governed caller contract {caller}: missing allowed mode(s): {', '.join(sorted(missing))}")
    require(rejects_before_write, f"governed caller contract {caller}: caller/mode rejection must occur before write")
    require(not consumer_docs_fallback, f"governed caller contract {caller}: direct-write fallback over consumer docs is prohibited")


def folded(text: str) -> str:
    return "".join(character for character in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(character))


def caller_text_prohibits_consumer_docs_fallback(text: str) -> bool:
    compact = re.sub(r"\s+", " ", folded(text))
    explicit_marker = re.search(r"consumer-docs-fallback\s*[:=]\s*(?:prohibited|blocked|forbidden)", compact)
    prose = re.search(
        r"(?:consumer docs|documentacao do consumidor|docs/\*\*).{0,240}"
        r"(?:nenhum fallback|sem fallback|no fallback|fallback.{0,80}(?:proibid|bloquead|forbidden))"
        r"|(?:nenhum fallback|sem fallback|no fallback|fallback.{0,80}(?:proibid|bloquead|forbidden)).{0,240}"
        r"(?:consumer docs|documentacao do consumidor|docs/\*\*)",
        compact,
    )
    return bool(explicit_marker or prose)


def validate_governed_caller_text(caller: str, text: str, label: str) -> None:
    normalized = folded(text)
    require("calling_workflow" in normalized, f"{label}: missing calling_workflow contract")
    require("write_mode" in normalized, f"{label}: missing write_mode contract")
    require(caller in normalized, f"{label}: missing fixed caller identity {caller}")
    declared_modes = {mode for mode in set().union(*CALLER_MODES.values()) if mode in normalized}
    prewrite = any(phrase in normalized for phrase in ("before write", "before the first write", "antes da escrita", "antes de escrever", "antes da primeira escrita"))
    validate_governed_caller_policy(
        caller,
        declared_modes,
        rejects_before_write=prewrite,
        consumer_docs_fallback=not caller_text_prohibits_consumer_docs_fallback(text),
    )


def parse_frontmatter(text: str, label: str) -> dict[str, object]:
    lines = text.splitlines()
    require(lines and lines[0].strip() == "---", f"{label}: missing YAML frontmatter")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ContractError(f"{label}: unterminated YAML frontmatter") from exc
    result: dict[str, object] = {}
    current_list = ""
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  - ") and current_list:
            value = stripped[2:].strip().strip("\"'")
            cast = result.setdefault(current_list, [])
            require(isinstance(cast, list), f"{label}: malformed list {current_list}")
            cast.append(value)
            continue
        current_list = ""
        if ":" not in line or line[0].isspace():
            continue
        key, raw = line.split(":", 1)
        raw = raw.strip()
        if not raw:
            result[key] = []
            current_list = key
        elif raw.startswith("[") and raw.endswith("]"):
            result[key] = [part.strip().strip("\"'") for part in raw[1:-1].split(",") if part.strip()]
        else:
            result[key] = raw.strip("\"'")
    return result


def validate_projection_pair(source: Path, projection: Path) -> None:
    source_text = source.read_text(encoding="utf-8")
    source_fields = parse_frontmatter(source_text, str(source))
    try:
        projection_data = tomllib.loads(projection.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ContractError(f"{projection}: TOML parse failed: {exc}") from exc
    embedded = projection_data.get("developer_instructions", "")
    require(isinstance(embedded, str) and embedded, f"{projection}: missing developer_instructions projection")
    if embedded.startswith("---\n"):
        embedded_source = embedded
    else:
        marker = embedded.find("\n---\n")
        require(marker >= 0, f"{projection}: embedded source frontmatter not found")
        embedded_source = embedded[marker + 1 :]
    projected_fields = parse_frontmatter(embedded_source, str(projection))
    require(source_fields.get("name") == projection_data.get("name"), f"{projection}: top-level name differs from source")
    for field in sorted(PARITY_FIELDS & (set(source_fields) | set(projected_fields))):
        require(source_fields.get(field) == projected_fields.get(field), f"{projection}: projection drift in {field}")


def enforce_current_tree(package_root: Path) -> int:
    checks = 0
    for source in sorted((package_root / "agents").glob("*.md")):
        fields = parse_frontmatter(source.read_text(encoding="utf-8"), str(source))
        name = str(fields.get("name", source.stem))
        domains = set(fields.get("scoped_write_domains", []))
        writes = set(fields.get("task_allowed_writes", []))
        if name != "catalogador":
            require(not (domains & CONSUMER_DOC_CAPABILITIES), f"{source}: non-catalogador declares consumer docs capability")
            require(not any(write == "docs/**" or write.startswith("docs/") for write in writes), f"{source}: non-catalogador declares consumer docs write")
        projection = package_root / "codex" / "agents" / f"{source.stem}.toml"
        require(projection.is_file(), f"{source}: missing Codex projection {projection}")
        try:
            projection_data = tomllib.loads(projection.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ContractError(f"{projection}: TOML parse failed: {exc}") from exc
        require(projection_data.get("name") == name, f"{projection}: top-level name differs from source")
        embedded = projection_data.get("developer_instructions", "")
        if isinstance(embedded, str) and (embedded.startswith("---\n") or "\n---\n" in embedded):
            validate_projection_pair(source, projection)
        checks += 1
    for caller in CALLER_MODES:
        bundle = package_root / "skills" / caller
        paths = sorted(bundle.rglob("*.md"))
        require(paths, f"governed caller surface is missing: {bundle}")
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        validate_governed_caller_text(caller, combined, str(bundle))
        checks += 1
    return checks


def write_packet(path: Path, *, source_ref: str = "src-1", packet_hash: str | None = None, revision: int = 1, supersedes: tuple[str, int, str] | None = None) -> None:
    digest = packet_hash or hashlib.sha256(b"packet-one").hexdigest()
    lineage = "" if supersedes is None else f'<packet_ref id="{supersedes[0]}" revision="{supersedes[1]}" hash="{supersedes[2]}" />'
    path.write_text(
        f'''<?xml version="1.0"?>
<loki_init_research_packet schema_version="1"><identity><run_id>run-1</run_id><investigator>api</investigator><investigator_invocation_id>inv-1</investigator_invocation_id><packet_id>packet-1</packet_id><packet_revision>{revision}</packet_revision><sequence>1</sequence><topic_id>api-map</topic_id><packet_hash>{digest}</packet_hash><supersedes>{lineage}</supersedes></identity><status>emitted</status><scope><objective>Map API</objective></scope><sources><read><source source_id="src-1"><locator>src/api.py</locator></source></read></sources><findings><facts><fact finding_id="fact-1"><statement>API exists</statement><source_refs><source_ref source_id="{source_ref}" /></source_refs></fact></facts></findings><coverage_delta><requirement requirement_id="api"><state>covered</state></requirement></coverage_delta><continuation><logical_status>complete</logical_status></continuation><validation><schema_status>passed</schema_status><acceptance_status>accepted</acceptance_status></validation></loki_init_research_packet>''',
        encoding="utf-8",
    )


def write_batch(path: Path, *, caller: str = "loki-init", mode: str = "init-publication-batch", owner: str = "catalogador", positions: tuple[int, ...] = (1,), batch_hash: str | None = None) -> None:
    digest = batch_hash or hashlib.sha256(b"batch-one").hexdigest()
    packet_digest = hashlib.sha256(b"packet-one").hexdigest()
    refs = "".join(f'<packet_ref position="{position}" packet_id="packet-{index}" revision="1" hash="{packet_digest}" />' for index, position in enumerate(positions, 1))
    path.write_text(
        f'''<?xml version="1.0"?>
<loki_init_publication_batch schema_version="1"><invocation><calling_workflow>{caller}</calling_workflow><write_mode>{mode}</write_mode><exclusive_write_owner>{owner}</exclusive_write_owner></invocation><identity><run_id>run-1</run_id><batch_id>batch-1</batch_id><idempotency_key>key-1</idempotency_key><batch_hash>{digest}</batch_hash></identity><packet_set>{refs}</packet_set><checkpoint><previous_checkpoint_ref>initial</previous_checkpoint_ref><before_state_hash>{hashlib.sha256(b'before').hexdigest()}</before_state_hash></checkpoint><validators><validator><command>validate</command></validator></validators><lifecycle><status>planned</status></lifecycle><destinations><success>orchestrator</success><failure>orchestrator</failure></destinations></loki_init_publication_batch>''',
        encoding="utf-8",
    )


def expect_failure(label: str, expected: str, operation: Callable[[], object]) -> None:
    try:
        operation()
    except ContractError as exc:
        require(expected in str(exc), f"negative fixture {label!r} failed for unexpected reason: {exc}")
        return
    raise ContractError(f"negative fixture {label!r} unexpectedly passed")


def run_fixture_suite() -> tuple[int, int]:
    positive = 0
    negative = 0
    temp_path: Path
    with tempfile.TemporaryDirectory(prefix="loki-init-contracts-") as temp_name:
        temp_path = Path(temp_name)
        packet_path = temp_path / "packet.xml"
        write_packet(packet_path)
        accepted = validate_packet(parse_xml(packet_path))
        require(accept_packet(None, accepted) == "accepted", "positive packet was not accepted")
        require(accept_packet(accepted, accepted) == "no-op", "identical packet retry was not a no-op")
        positive += 2

        missing_source = temp_path / "packet-missing-source.xml"
        write_packet(missing_source, source_ref="missing")
        expect_failure("fact without resolved source", "unread source", lambda: validate_packet(parse_xml(missing_source)))
        negative += 1

        divergent = PacketIdentity(accepted.packet_id, accepted.revision, hashlib.sha256(b"changed").hexdigest())
        expect_failure("divergent packet same ID", "higher revision", lambda: accept_packet(accepted, divergent))
        negative += 1
        revised = PacketIdentity(accepted.packet_id, 2, divergent.packet_hash, accepted.packet_id, accepted.revision, accepted.packet_hash)
        require(accept_packet(accepted, revised) == "superseded", "valid packet revision was not accepted")
        positive += 1

        batch_path = temp_path / "batch.xml"
        write_batch(batch_path)
        batch = validate_batch(parse_xml(batch_path))
        require(accept_batch(None, batch) == "accepted", "positive batch was not accepted")
        require(accept_batch(batch, batch) == "no-op", "identical batch retry was not a no-op")
        positive += 2
        divergent_batch = BatchIdentity(batch.batch_id, batch.idempotency_key, hashlib.sha256(b"different").hexdigest(), batch.packets)
        expect_failure("divergent batch retry", "divergent content", lambda: accept_batch(batch, divergent_batch))
        negative += 1

        unordered = temp_path / "batch-unordered.xml"
        write_batch(unordered, positions=(2, 1))
        expect_failure("unordered packet set", "ordered and contiguous", lambda: validate_batch(parse_xml(unordered)))
        negative += 1

        for caller, modes in CALLER_MODES.items():
            for mode in modes:
                validate_caller_mode(caller, mode)
                positive += 1
        for label, caller, mode, reason in (
            ("missing caller", "", "task_scoped_writer", "missing calling_workflow"),
            ("unknown caller", "other", "task_scoped_writer", "unknown calling_workflow"),
            ("unknown mode", "loki-init", "direct-write", "unknown write_mode"),
            ("crossed init mode", "loki-run-plan", "init-publication-batch", "crossed pair"),
        ):
            expect_failure(label, reason, lambda caller=caller, mode=mode: validate_caller_mode(caller, mode))
            negative += 1

        for before, after in (("planned", "dispatched"), ("dispatched", "write-applied"), ("write-applied", "validated"), ("validated", "committed")):
            validate_transition(before, after)
            positive += 1
        expect_failure("terminal transition", "invalid transition", lambda: validate_transition("committed", "dispatched"))
        negative += 1
        expect_failure(
            "concurrent init writers",
            "two concurrent",
            lambda: validate_single_init_writer([
                {"workflow": "loki-init", "mode": "init-bootstrap-cataloger", "status": "running", "owner": "catalogador"},
                {"workflow": "loki-init", "mode": "init-publication-batch", "status": "dispatched", "owner": "catalogador"},
            ]),
        )
        negative += 1

        consumer_root = temp_path / "consumer-project"
        package_root = temp_path / "loki-package"
        consumer_root.mkdir()
        package_root.mkdir()
        ownership = {"consumer_project_root": consumer_root, "package_root": package_root}
        validate_write_ownership("catalogador", "consumer-docs", "./docs/api.md", "task_scoped_writer", **ownership)
        validate_write_ownership("catalogador", "source-code", "src/../docs/api.md", "task_scoped_writer", **ownership)
        validate_write_ownership("catalogador", "source-code", str(consumer_root / "docs" / "api.md"), "task_scoped_writer", **ownership)
        validate_write_ownership("framework-artifact-writer", "package-documentation", "docs/policy.md", "task_scoped_writer", **ownership)
        validate_write_ownership("backend", "source-code", "src/api.py", "task_scoped_writer", **ownership)
        positive += 5
        for label, target in (
            ("relative consumer docs", "./docs/api.md"),
            ("normalized traversal to consumer docs", "src/../docs/api.md"),
            ("absolute consumer docs", str(consumer_root / "docs" / "api.md")),
        ):
            expect_failure(
                label,
                "cannot write normalized target",
                lambda target=target: validate_write_ownership("backend", "source-code", target, "task_scoped_writer", **ownership),
            )
            negative += 1

        for caller, modes in CALLER_MODES.items():
            validate_governed_caller_policy(
                caller,
                set(modes),
                rejects_before_write=True,
                consumer_docs_fallback=False,
            )
            positive += 1
        expect_failure(
            "prohibited consumer docs fallback",
            "direct-write fallback over consumer docs is prohibited",
            lambda: validate_governed_caller_policy(
                "loki-run-plan",
                {"task_scoped_writer"},
                rejects_before_write=True,
                consumer_docs_fallback=True,
            ),
        )
        negative += 1

        source = temp_path / "agent.md"
        projection = temp_path / "agent.toml"
        source.write_text("---\nname: example\nstatus: draft\nscoped_write_modes:\n  - task_scoped_writer\n---\n", encoding="utf-8")
        embedded = source.read_text(encoding="utf-8")
        projection.write_text('name = "example"\ndeveloper_instructions = \'\'\'\n' + embedded + "\n'''\n", encoding="utf-8")
        validate_projection_pair(source, projection)
        positive += 1
        projection.write_text('name = "example"\ndeveloper_instructions = \'\'\'\n---\nname: example\nstatus: stable\nscoped_write_modes:\n  - task_scoped_writer\n---\n\n\'\'\'\n', encoding="utf-8")
        expect_failure("source/projection drift", "projection drift in status", lambda: validate_projection_pair(source, projection))
        negative += 1

        manifest = temp_path / "fixture-results.json"
        manifest.write_text(json.dumps({"positive": positive, "negative": negative}, sort_keys=True), encoding="utf-8")
        require(json.loads(manifest.read_text(encoding="utf-8"))["negative"] == negative, "fixture manifest did not round-trip")
        positive += 1
    require(not temp_path.exists(), f"temporary fixture residue remains at {temp_path}")
    return positive, negative


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, help="Package root; defaults to the script parent root.")
    parser.add_argument(
        "--enforce-current-tree",
        action="store_true",
        help="Enable post-migration ownership and agent projection parity scans.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    package_root = (args.package_root or Path(__file__).resolve().parent.parent).resolve()
    try:
        template_checks = validate_package_templates(package_root)
        positive, negative = run_fixture_suite()
        tree_checks = enforce_current_tree(package_root) if args.enforce_current_tree else 0
    except ContractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    mode = "post-migration tree enforcement" if args.enforce_current_tree else "preparatory phase-2"
    print(
        "Loki init/catalogador contracts passed: "
        f"{template_checks} template checks, {positive} positive fixtures, "
        f"{negative} expected negative fixtures, {tree_checks} current-tree pairs "
        f"({mode})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
