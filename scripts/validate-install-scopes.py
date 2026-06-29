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
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("install scope validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
