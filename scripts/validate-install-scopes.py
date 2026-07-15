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
LOKI_COMMAND_PROJECTION_EXCEPTIONS: set[str] = set()
REQUIRED_AGENTIC_METADATA_FIELDS = {
    "capability_tags",
    "phase_roles",
    "agentic_modes",
    "write_classes",
    "risk_tags",
    "parallel_safe",
    "technology_skill_routes",
}


def load_scopes(package_root: Path) -> dict:
    path = package_root / SCOPE_FILE
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("schema_version") != 1:
        raise ValueError("install-scopes.json must use schema_version 1")
    identity_policy = data.get("artifact_identity_policy", {})
    command_projection = identity_policy.get("skills/loki-*/SKILL.md", {})
    if command_projection != {
        "operational_role": "command",
        "projection": "installable-skill",
        "paired_contract": "commands/loki-*.md",
    }:
        raise ValueError(
            "install-scopes.json must classify skills/loki-*/SKILL.md as "
            "installable command projections"
        )
    framework_skill = identity_policy.get("skills/lf-*/SKILL.md", {})
    if framework_skill.get("operational_role") != "skill":
        raise ValueError(
            "install-scopes.json must classify skills/lf-*/SKILL.md as skills"
        )
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


def parse_frontmatter_list(path: Path, field: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    required: list[str] = []
    in_required = False
    for line in lines:
        if line == f"{field}: []":
            return []
        if line == f"{field}:":
            in_required = True
            continue
        if in_required:
            if line.startswith("  - "):
                required.append(line[4:].strip())
                continue
            if line and not line.startswith(" "):
                break
    return required


def parse_required_skills(path: Path) -> list[str]:
    return parse_frontmatter_list(path, "required_skills")


def parse_required_commands(path: Path) -> list[str]:
    return parse_frontmatter_list(path, "required_commands")


def frontmatter_declares_field(path: Path, field: str) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith(f"{field}:"):
            return True
    return False


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
    internal_command_names = {
        Path(name).stem
        for name, scope in command_scopes.items()
        if scope == "internal-only"
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
        for command_name in parse_required_commands(command_path):
            if command_name in internal_command_names:
                failures.append(
                    f"{command_path}: both command requires internal-only "
                    f"{command_name}"
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


def validate_command_dependency_identity(package_root: Path, data: dict) -> None:
    command_scopes = artifact_scopes(data, "commands")
    failures: list[str] = []

    for command_file in sorted(command_scopes):
        path = package_root / "commands" / command_file
        command_stem = Path(command_file).stem

        for required_field in ("required_skills", "required_commands"):
            if not frontmatter_declares_field(path, required_field):
                failures.append(f"{path}: missing {required_field}")

        for skill_name in parse_required_skills(path):
            if skill_name.startswith("loki-"):
                failures.append(
                    f"{path}: required_skills contains command projection "
                    f"{skill_name}; move it to required_commands"
                )

        for required_command in parse_required_commands(path):
            if not required_command.startswith("loki-"):
                failures.append(
                    f"{path}: required_commands contains non-command "
                    f"{required_command}"
                )
                continue
            if required_command == command_stem:
                failures.append(f"{path}: command must not require itself")
            required_file = f"{required_command}.md"
            if required_file not in command_scopes:
                failures.append(
                    f"{path}: required command {required_file} is not installed"
                )

    if failures:
        raise ValueError(
            "command dependency identity failures:\n- " + "\n- ".join(failures)
        )


def validate_toml(package_root: Path) -> None:
    for path in sorted((package_root / "codex" / "agents").glob("*.toml")):
        with path.open("rb") as handle:
            tomllib.load(handle)


def validate_loki_command_projection_namespace(
    skill_names: set[str], command_names: set[str]
) -> None:
    command_wrapper_names = {
        Path(name).stem
        for name in command_names
        if name.startswith("loki-") and name.endswith(".md")
    }
    unexpected = sorted(
        name
        for name in skill_names
        if name.startswith("loki-")
        and name not in command_wrapper_names
        and name not in LOKI_COMMAND_PROJECTION_EXCEPTIONS
    )
    if unexpected:
        raise ValueError(
            "loki command projection namespace failures:\n- skills/loki-* without matching "
            "commands/loki-*.md: " + ", ".join(unexpected)
        )


def frontmatter_scalar(path: Path, key: str, nested_under: str | None = None) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return ""

    active_parent = ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line and not line.startswith(" ") and line.endswith(":"):
            active_parent = line[:-1]
            continue
        if nested_under is None and line.startswith(f"{key}:"):
            return parse_manifest_scalar(line.split(":", 1)[1])
        if (
            nested_under is not None
            and active_parent == nested_under
            and line.startswith(f"  {key}:")
        ):
            return parse_manifest_scalar(line.split(":", 1)[1])
    return ""


def validate_loki_command_projection_identity(package_root: Path, data: dict) -> None:
    skill_scopes = artifact_scopes(data, "skills")
    command_scopes = artifact_scopes(data, "commands")
    failures: list[str] = []

    for skill_name, skill_scope in sorted(skill_scopes.items()):
        if not skill_name.startswith("loki-"):
            continue

        command_file = f"{skill_name}.md"
        command_name = "loki:" + skill_name.removeprefix("loki-")
        projection_path = package_root / "skills" / skill_name / "SKILL.md"
        command_path = package_root / "commands" / command_file
        expected_projection = f"skills/{skill_name}/SKILL.md"
        expected_contract = f"commands/{command_file}"

        checks = {
            "type": (frontmatter_scalar(projection_path, "type"), "command"),
            "projection": (
                frontmatter_scalar(projection_path, "projection"),
                "installable-skill",
            ),
            "command_name": (
                frontmatter_scalar(projection_path, "command_name"),
                command_name,
            ),
            "paths.package_projection": (
                frontmatter_scalar(
                    projection_path, "package_projection", nested_under="paths"
                ),
                expected_projection,
            ),
            "paths.command_contract": (
                frontmatter_scalar(
                    projection_path, "command_contract", nested_under="paths"
                ),
                expected_contract,
            ),
        }
        for field, (actual, expected) in checks.items():
            if actual != expected:
                failures.append(
                    f"{projection_path}: {field}={actual or 'missing'}; "
                    f"expected {expected}"
                )

        actual_command_name = frontmatter_scalar(command_path, "name")
        if actual_command_name != command_name:
            failures.append(
                f"{command_path}: name={actual_command_name or 'missing'}; "
                f"expected {command_name}"
            )

        command_scope = command_scopes.get(command_file)
        if command_scope != skill_scope:
            failures.append(
                f"{projection_path}: install scope {skill_scope} differs from "
                f"{expected_contract}={command_scope or 'missing'}"
            )

    if failures:
        raise ValueError(
            "loki command projection identity failures:\n- "
            + "\n- ".join(failures)
        )


def validate_framework_skill_identity(package_root: Path, data: dict) -> None:
    failures: list[str] = []
    for skill_name in sorted(artifact_scopes(data, "skills")):
        if not skill_name.startswith("lf-"):
            continue
        path = package_root / "skills" / skill_name / "SKILL.md"
        artifact_type = frontmatter_scalar(path, "type")
        if artifact_type != "skill":
            failures.append(
                f"{path}: type={artifact_type or 'missing'}; expected skill"
            )
    if failures:
        raise ValueError(
            "framework skill identity failures:\n- " + "\n- ".join(failures)
        )


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


def parse_manifest_skill_catalog(package_root: Path) -> dict[str, dict[str, str]]:
    lines = (package_root / "manifest.yaml").read_text(encoding="utf-8").splitlines()
    catalog: dict[str, dict[str, str]] = {}
    in_skills = False
    current = ""

    for line in lines:
        if line == "skills:":
            in_skills = True
            continue
        if in_skills and line and not line.startswith(" "):
            break
        if not in_skills:
            continue
        if line.startswith("  - name:"):
            current = parse_manifest_scalar(line.split(":", 1)[1])
            catalog[current] = {}
            continue
        if current and line.startswith("    ") and ":" in line:
            key, value = line.strip().split(":", 1)
            catalog[current][key] = parse_manifest_scalar(value)
    return catalog


def validate_manifest_command_projection_identity(package_root: Path) -> None:
    catalog = parse_manifest_skill_catalog(package_root)
    failures: list[str] = []
    for name, metadata in sorted(catalog.items()):
        if not name.startswith("loki-"):
            continue
        if metadata.get("operational_role") != "command":
            failures.append(
                f"manifest skills.{name}.operational_role must be command"
            )
        if metadata.get("projection") != "installable-skill":
            failures.append(
                f"manifest skills.{name}.projection must be installable-skill"
            )
    if failures:
        raise ValueError(
            "manifest command projection identity failures:\n- "
            + "\n- ".join(failures)
        )


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


def parse_agentic_agent_metadata(package_root: Path) -> dict[str, dict[str, str]]:
    lines = (package_root / "manifest.yaml").read_text(encoding="utf-8").splitlines()
    section = ""
    current_agent = ""
    metadata: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            current_agent = ""
            continue

        if section != "agentic_agent_metadata":
            continue

        if indent == 2 and stripped.endswith(":"):
            current_agent = stripped[:-1]
            metadata[current_agent] = {}
            continue

        if current_agent and indent == 4 and ":" in stripped:
            key, value = stripped.split(":", 1)
            metadata[current_agent][key.strip()] = value.strip()

    return metadata


def validate_agentic_agent_metadata(package_root: Path) -> None:
    catalog = parse_manifest_agent_catalog(package_root)
    agent_names = {agent.get("name", "") for agent in catalog["agents"]}
    metadata = parse_agentic_agent_metadata(package_root)
    manifest_text = (package_root / "manifest.yaml").read_text(encoding="utf-8")

    failures: list[str] = []
    if "selection_reason_required: true" not in manifest_text:
        failures.append("agentic_selection_policy.selection_reason_required must be true")
    if "parallel_safe_required: true" not in manifest_text:
        failures.append("agentic_selection_policy.parallel_safe_required must be true")

    missing_agents = sorted(agent_names - set(metadata))
    extra_agents = sorted(set(metadata) - agent_names)
    if missing_agents:
        failures.append("agentic metadata missing agents: " + ", ".join(missing_agents))
    if extra_agents:
        failures.append("agentic metadata extra agents: " + ", ".join(extra_agents))

    for agent_name, fields in sorted(metadata.items()):
        missing_fields = sorted(REQUIRED_AGENTIC_METADATA_FIELDS - set(fields))
        if missing_fields:
            failures.append(
                f"agentic metadata for {agent_name} missing: "
                + ", ".join(missing_fields)
            )
        parallel_safe = fields.get("parallel_safe", "").lower()
        if parallel_safe not in {"true", "false"}:
            failures.append(
                f"agentic metadata for {agent_name} parallel_safe must be true or false"
            )

    if failures:
        raise ValueError("agentic agent metadata failures:\n- " + "\n- ".join(failures))


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
        validate_loki_command_projection_namespace(skill_names, command_names)
        validate_loki_command_projection_identity(package_root, data)
        validate_framework_skill_identity(package_root, data)
        validate_command_dependency_identity(package_root, data)

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
        validate_manifest_command_projection_identity(package_root)
        validate_agent_project_tags(package_root)
        validate_agentic_agent_metadata(package_root)
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("install scope validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
