#!/usr/bin/env python3
"""Validate Loki installer scope metadata and neutral shared artifacts."""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path


VALID_SCOPES = {"internal-only", "both", "consumer-only"}
SCOPE_FILE = "install-scopes.json"
SUSPICIOUS_BOTH_TERMS = (
    "package source",
    "inside the package",
    "when running inside",
    "installed in a consumer",
    "fonte do pacote",
    "workspace do loki",
    "projeto consumidor sem",
    "package authoring",
    "self-healing",
    "branch guardada",
    "prefer these sources",
    "if this skill",
)


def load_scopes(package_root: Path) -> dict:
    path = package_root / SCOPE_FILE
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("schema_version") != 1:
        raise ValueError("install-scopes.json must use schema_version 1")
    return data


def artifact_scopes(data: dict, kind: str) -> dict[str, str]:
    try:
        scopes = data["artifacts"][kind]
    except KeyError as exc:
        raise ValueError(f"missing artifacts.{kind}") from exc
    unknown = sorted(set(scopes.values()) - VALID_SCOPES)
    if unknown:
        raise ValueError(f"unknown scope(s) in {kind}: {', '.join(unknown)}")
    return scopes


def assert_exact_keys(label: str, actual: set[str], expected: set[str]) -> None:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        message = [f"{label} scope keys do not match filesystem"]
        if missing:
            message.append("missing: " + ", ".join(missing))
        if extra:
            message.append("extra: " + ", ".join(extra))
        raise ValueError("; ".join(message))


def parse_required_skills(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    required: list[str] = []
    in_required = False
    for line in lines:
        if line == "required_skills:":
            in_required = True
            continue
        if in_required:
            if line.startswith("  - "):
                required.append(line[4:].strip())
                continue
            if line and not line.startswith(" "):
                break
    return required


def iter_artifact_files(package_root: Path, kind: str, name: str) -> list[Path]:
    if kind == "skills":
        root = package_root / "skills" / name
        return sorted(path for path in root.rglob("*") if path.is_file())
    if kind == "commands":
        return [package_root / "commands" / name]
    if kind == "agents":
        return [package_root / "agents" / name]
    if kind == "codex_agents":
        return [package_root / "codex" / "agents" / name]
    raise ValueError(f"unsupported kind: {kind}")


def validate_neutrality(package_root: Path, data: dict) -> None:
    skill_scopes = artifact_scopes(data, "skills")
    command_scopes = artifact_scopes(data, "commands")
    agent_scopes = artifact_scopes(data, "agents")
    codex_agent_scopes = artifact_scopes(data, "codex_agents")
    internal_skill_names = {
        name for name, scope in skill_scopes.items() if scope == "internal-only"
    }

    failures: list[str] = []
    for command_name, scope in command_scopes.items():
        if scope != "both":
            continue
        command_path = package_root / "commands" / command_name
        for skill_name in parse_required_skills(command_path):
            if skill_name in internal_skill_names:
                failures.append(
                    f"{command_path}: both command requires internal-only {skill_name}"
                )

    for kind, scopes in (
        ("skills", skill_scopes),
        ("commands", command_scopes),
        ("agents", agent_scopes),
        ("codex_agents", codex_agent_scopes),
    ):
        for name, scope in scopes.items():
            if scope != "both":
                continue
            for path in iter_artifact_files(package_root, kind, name):
                text = path.read_text(encoding="utf-8").lower()
                for term in SUSPICIOUS_BOTH_TERMS:
                    if term in text:
                        failures.append(f"{path}: both artifact contains '{term}'")
                for internal_name in internal_skill_names:
                    if internal_name in text:
                        failures.append(
                            f"{path}: both artifact references internal-only {internal_name}"
                        )

    if failures:
        raise ValueError("neutrality failures:\n- " + "\n- ".join(failures))


def validate_toml(package_root: Path) -> None:
    for path in sorted((package_root / "codex" / "agents").glob("*.toml")):
        with path.open("rb") as handle:
            tomllib.load(handle)


def validate_manifest_entries(package_root: Path) -> None:
    manifest = package_root / "manifest.yaml"
    missing: list[str] = []
    for relative in (SCOPE_FILE, "scripts/validate-install-scopes.py"):
        if not (package_root / relative).exists():
            missing.append(relative)
    if SCOPE_FILE not in manifest.read_text(encoding="utf-8"):
        missing.append(f"manifest entry for {SCOPE_FILE}")
    if missing:
        raise ValueError("missing manifest/source entries: " + ", ".join(missing))


def parse_manifest_scalar(value: str) -> str:
    text = value.strip()
    if (
        len(text) >= 2
        and text[0] == text[-1]
        and text.startswith(("'", '"'))
    ):
        return text[1:-1]
    return text


def parse_manifest_list_value(value: str) -> list[str]:
    text = value.strip()
    if not text or text == "[]":
        return []
    if not (text.startswith("[") and text.endswith("]")):
        return [parse_manifest_scalar(text)]
    inner = text[1:-1].strip()
    if not inner:
        return []
    return [
        parse_manifest_scalar(part)
        for part in inner.split(",")
        if part.strip()
    ]


def parse_manifest_agent_catalog(package_root: Path) -> dict:
    lines = (package_root / "manifest.yaml").read_text(encoding="utf-8").splitlines()
    supported_project_types: list[str] = []
    agent_project_tag_policy: dict[str, str] = {}
    agents: list[dict] = []
    codex_agents: list[dict] = []

    section = ""
    current_agent: dict | None = None
    current_codex_agent: dict | None = None
    project_tags_owner: dict | None = None

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            current_agent = None
            current_codex_agent = None
            project_tags_owner = None
            continue

        if section == "supported_project_types":
            if indent == 2 and stripped.startswith("- "):
                supported_project_types.append(parse_manifest_scalar(stripped[2:]))
            continue

        if section == "agent_project_tag_policy":
            if indent == 2 and ":" in stripped:
                key, value = stripped.split(":", 1)
                agent_project_tag_policy[key.strip()] = parse_manifest_scalar(value)
            continue

        if section == "agents":
            if indent == 2 and stripped.startswith("- "):
                current_agent = {}
                agents.append(current_agent)
                current_codex_agent = None
                project_tags_owner = None
                item = stripped[2:]
                if ":" in item:
                    key, value = item.split(":", 1)
                    current_agent[key.strip()] = parse_manifest_scalar(value)
                continue
            if current_agent is None:
                continue
            if indent == 4 and ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip()
                if key == "project_tags":
                    current_agent[key] = parse_manifest_list_value(value)
                    project_tags_owner = current_agent
                else:
                    current_agent[key] = parse_manifest_scalar(value)
                    project_tags_owner = None
                continue
            if indent == 6 and project_tags_owner is current_agent:
                if stripped.startswith("- "):
                    current_agent.setdefault("project_tags", []).append(
                        parse_manifest_scalar(stripped[2:])
                    )
                continue

        if section == "codex_agents":
            if indent == 2 and stripped.startswith("- "):
                current_codex_agent = {}
                codex_agents.append(current_codex_agent)
                current_agent = None
                project_tags_owner = None
                item = stripped[2:]
                if ":" in item:
                    key, value = item.split(":", 1)
                    current_codex_agent[key.strip()] = parse_manifest_scalar(value)
                continue
            if current_codex_agent is None:
                continue
            if indent == 4 and ":" in stripped:
                key, value = stripped.split(":", 1)
                current_codex_agent[key.strip()] = parse_manifest_scalar(value)

    return {
        "supported_project_types": supported_project_types,
        "agent_project_tag_policy": agent_project_tag_policy,
        "agents": agents,
        "codex_agents": codex_agents,
    }


def validate_agent_project_tags(package_root: Path) -> None:
    catalog = parse_manifest_agent_catalog(package_root)
    supported_project_types = catalog["supported_project_types"]
    agent_project_tag_policy = catalog["agent_project_tag_policy"]
    agents = catalog["agents"]
    codex_agents = catalog["codex_agents"]

    failures: list[str] = []
    required_project_types = {"game-dev", "software-development"}
    missing_project_types = sorted(
        required_project_types - set(supported_project_types)
    )
    if missing_project_types:
        failures.append(
            "supported_project_types missing: "
            + ", ".join(missing_project_types)
        )

    base_tag = agent_project_tag_policy.get("base_tag")
    if base_tag != "core":
        failures.append("agent_project_tag_policy.base_tag must be core")
    if "core" in supported_project_types:
        failures.append("core must not appear in supported_project_types")

    allowed_tags = set(supported_project_types)
    if base_tag:
        allowed_tags.add(base_tag)

    agent_files: set[str] = set()
    agent_names: set[str] = set()
    for agent in agents:
        name = agent.get("name", "")
        file = agent.get("file", "")
        tags = agent.get("project_tags", [])
        if not name:
            failures.append("agent entry missing name")
        elif name in agent_names:
            failures.append(f"duplicate agent in manifest: {name}")
        else:
            agent_names.add(name)
        if not file:
            failures.append(f"agent {name or '<unnamed>'} missing file")
        else:
            agent_files.add(file)
            if not (package_root / file).exists():
                failures.append(f"agent file does not exist: {file}")
        if not tags:
            failures.append(f"agent {name or file or '<unnamed>'} missing project_tags")
            continue
        unknown_tags = sorted(set(tags) - allowed_tags)
        if unknown_tags:
            failures.append(
                f"agent {name or file} has unknown project_tags: "
                + ", ".join(unknown_tags)
            )

    for codex_agent in codex_agents:
        source_agent = codex_agent.get("source_agent", "")
        name = codex_agent.get("name", "")
        file = codex_agent.get("file", "")
        if not file:
            failures.append(f"codex agent {name or '<unnamed>'} missing file")
        elif not (package_root / file).exists():
            failures.append(f"codex agent file does not exist: {file}")
        if not source_agent:
            failures.append(f"codex agent {name or '<unnamed>'} missing source_agent")
            continue
        if source_agent not in agent_files:
            failures.append(
                f"codex agent {name or source_agent} source_agent not in agents: "
                f"{source_agent}"
            )

    if failures:
        raise ValueError("agent project tag failures:\n- " + "\n- ".join(failures))


def main() -> int:
    package_root = Path(__file__).resolve().parent.parent
    try:
        data = load_scopes(package_root)
        skill_scopes = artifact_scopes(data, "skills")
        command_scopes = artifact_scopes(data, "commands")
        agent_scopes = artifact_scopes(data, "agents")
        codex_agent_scopes = artifact_scopes(data, "codex_agents")

        skill_names = {
            path.parent.name
            for path in (package_root / "skills").glob("*/SKILL.md")
        }
        command_names = {path.name for path in (package_root / "commands").glob("*.md")}
        agent_names = {path.name for path in (package_root / "agents").glob("*.md")}
        codex_agent_names = {
            path.name for path in (package_root / "codex" / "agents").glob("*.toml")
        }
        assert_exact_keys("skill", set(skill_scopes), skill_names)
        assert_exact_keys("command", set(command_scopes), command_names)
        assert_exact_keys("agent", set(agent_scopes), agent_names)
        assert_exact_keys("Codex agent", set(codex_agent_scopes), codex_agent_names)

        mismatched_agent_scopes = []
        for agent_name, scope in sorted(agent_scopes.items()):
            codex_name = f"{Path(agent_name).stem}.toml"
            if codex_agent_scopes.get(codex_name) != scope:
                mismatched_agent_scopes.append(
                    f"{agent_name}={scope} vs {codex_name}="
                    f"{codex_agent_scopes.get(codex_name, 'missing')}"
                )
        if mismatched_agent_scopes:
            raise ValueError(
                "agent and Codex agent scopes differ: "
                + "; ".join(mismatched_agent_scopes)
            )

        validate_neutrality(package_root, data)
        validate_toml(package_root)
        validate_manifest_entries(package_root)
        validate_agent_project_tags(package_root)
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("install scope validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
