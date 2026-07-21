#!/usr/bin/env python3
"""Validate Loki installer scope metadata and neutral shared artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path


VALID_SCOPES = {"internal-only", "both", "consumer-only"}
SCOPE_FILE = "install-scopes.json"
INSTALL_SCOPE_ROOT_KEYS = frozenset(
    {"schema_version", "profiles", "artifact_identity_policy", "artifacts"}
)
INSTALL_SCOPE_ARTIFACT_KEYS = frozenset({"skills", "agents", "codex_agents", "docs"})
INSTALL_SCOPE_REQUIRED_ARTIFACT_KEYS = frozenset({"skills", "agents", "codex_agents"})
INSTALL_SCOPE_PROFILE_SCOPES = {
    "consumer": frozenset({"both", "consumer-only"}),
    "package-source": frozenset({"both", "internal-only"}),
    "all": frozenset(VALID_SCOPES),
}
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
TRANSIENT_PLAN_REFERENCE_PATTERNS = (
    (
        re.compile(r"\btask-[0-9]+(?:\.[0-9]+)+\b", re.IGNORECASE),
        "numbered task ID",
    ),
    (
        re.compile(
            r"\bplanos/(?!000-init-loki(?=/|$|[\s`'\"\)\],;:]|\.(?=\s|$)))[0-9]{3}-[a-z0-9._-]+",
            re.IGNORECASE,
        ),
        "numbered transient plan path",
    ),
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
FINAL_LOKI_COMMAND_COUNT = 17
FINAL_BUNDLE_RESOURCES = (
    "references/execution.md",
    "references/response.md",
    "assets/response-template.md",
)
INSTALLABLE_PACKAGE_ROOTS = ("skills", "agents", "codex", "templates")
ANALYTIC_INFERENCE_RELATIVE_ROOT = Path("skills/lf-analytic-inference")
ANALYTIC_INFERENCE_FIXTURES = Path("references/fixtures")
PRODUCTION_STATE_COMPONENTS = {"catalog", "catalogs", "records", "events"}
PRODUCTION_STATE_FILENAMES = {"registry.xml", "index.xml"}
PRODUCTION_RECORD_FILENAME = re.compile(r"^rev-[1-9][0-9]*\.xml$")


def load_scopes(package_root: Path) -> dict:
    path = package_root / SCOPE_FILE
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("INSTALL_SCOPES:ROOT_TYPE: root must be an object")
    unknown_root = sorted(set(data) - INSTALL_SCOPE_ROOT_KEYS)
    missing_root = sorted(INSTALL_SCOPE_ROOT_KEYS - set(data))
    if unknown_root or missing_root:
        details = []
        if missing_root:
            details.append("missing " + ", ".join(missing_root))
        if unknown_root:
            details.append("unknown " + ", ".join(unknown_root))
        raise ValueError("INSTALL_SCOPES:ROOT_KEYS: " + "; ".join(details))
    if data["schema_version"] != 2:
        raise ValueError("INSTALL_SCOPES:SCHEMA_VERSION: schema_version must be 2")
    profiles = data["profiles"]
    if not isinstance(profiles, dict):
        raise ValueError("INSTALL_SCOPES:PROFILES_TYPE: profiles must be an object")
    unknown_profiles = sorted(set(profiles) - set(INSTALL_SCOPE_PROFILE_SCOPES))
    missing_profiles = sorted(set(INSTALL_SCOPE_PROFILE_SCOPES) - set(profiles))
    if unknown_profiles or missing_profiles:
        details = []
        if missing_profiles:
            details.append("missing " + ", ".join(missing_profiles))
        if unknown_profiles:
            details.append("unknown " + ", ".join(unknown_profiles))
        raise ValueError("INSTALL_SCOPES:PROFILE_KEYS: " + "; ".join(details))
    for profile, expected_scopes in INSTALL_SCOPE_PROFILE_SCOPES.items():
        configured = profiles[profile]
        if not isinstance(configured, list) or not all(isinstance(scope, str) for scope in configured):
            raise ValueError(
                f"INSTALL_SCOPES:PROFILE_SCOPES: profile {profile} must be a list of scopes"
            )
        if frozenset(configured) != expected_scopes:
            raise ValueError(
                "INSTALL_SCOPES:PROFILE_SCOPES: "
                f"profile {profile} must map to {sorted(expected_scopes)}"
            )
    identity_policy = data["artifact_identity_policy"]
    if not isinstance(identity_policy, dict):
        raise ValueError("INSTALL_SCOPES:IDENTITY_POLICY_TYPE: artifact_identity_policy must be an object")
    command_projection = identity_policy.get("skills/loki-*/SKILL.md", {})
    expected_command_policy = {
        "operational_role": "command",
        "serialization": "skill-bundle",
        "required_resources": list(FINAL_BUNDLE_RESOURCES),
    }
    if command_projection != expected_command_policy:
        raise ValueError(
            "install-scopes.json has an invalid skills/loki-*/SKILL.md "
            "identity policy for schema 2"
        )
    artifacts = data["artifacts"]
    if not isinstance(artifacts, dict):
        raise ValueError("INSTALL_SCOPES:ARTIFACTS_TYPE: artifacts must be an object")
    unknown_artifacts = sorted(set(artifacts) - INSTALL_SCOPE_ARTIFACT_KEYS)
    missing_artifacts = sorted(INSTALL_SCOPE_REQUIRED_ARTIFACT_KEYS - set(artifacts))
    if unknown_artifacts or missing_artifacts:
        details = []
        if missing_artifacts:
            details.append("missing " + ", ".join(missing_artifacts))
        if unknown_artifacts:
            details.append("unknown " + ", ".join(unknown_artifacts))
        raise ValueError("INSTALL_SCOPES:ARTIFACT_KEYS: " + "; ".join(details))
    invalid_artifacts = sorted(
        key for key, value in artifacts.items() if not isinstance(value, dict)
    )
    if invalid_artifacts:
        raise ValueError(
            "INSTALL_SCOPES:ARTIFACT_VALUES: artifact maps must be objects: "
            + ", ".join(invalid_artifacts)
        )
    framework_skill = identity_policy.get("skills/lf-*/SKILL.md", {})
    has_framework_skills = any(
        name.startswith("lf-")
        for name in artifacts["skills"]
    )
    if has_framework_skills and framework_skill.get("operational_role") != "skill":
        raise ValueError(
            "install-scopes.json must classify skills/lf-*/SKILL.md as skills"
        )
    return data


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-root",
        type=Path,
        help="Validate an isolated package fixture instead of this package root.",
    )
    parser.add_argument(
        "--scope-contract-only",
        action="store_true",
        help=(
            "Validate install-scopes and schema-2 command bundles only. This is "
            "intended for isolated tempfile fixtures, not release validation."
        ),
    )
    return parser.parse_args(argv)


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


def _parse_yaml_string_scalar(raw_value: str, path: Path, field: str) -> str:
    value = raw_value.strip()
    if not value:
        raise ValueError(f"{path}: {field} contains an empty list item")
    if value.startswith('"'):
        if not value.endswith('"'):
            raise ValueError(f"{path}: {field} contains an unterminated double quote")
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{path}: {field} contains an invalid double-quoted item: {exc}"
            ) from exc
        if not isinstance(parsed, str):
            raise ValueError(f"{path}: {field} items must be strings")
        return parsed
    if value.startswith("'"):
        if not value.endswith("'") or len(value) < 2:
            raise ValueError(f"{path}: {field} contains an unterminated single quote")
        inner = value[1:-1]
        index = 0
        decoded: list[str] = []
        while index < len(inner):
            if inner[index] == "'":
                if index + 1 >= len(inner) or inner[index + 1] != "'":
                    raise ValueError(
                        f"{path}: {field} contains an invalid single-quoted item"
                    )
                decoded.append("'")
                index += 2
                continue
            decoded.append(inner[index])
            index += 1
        return "".join(decoded)
    if any(character in value for character in "'\"[]{}#,"):
        raise ValueError(
            f"{path}: {field} contains malformed or unsupported unquoted YAML: {value}"
        )
    if not re.fullmatch(r"[A-Za-z0-9_.+/@-]+", value):
        raise ValueError(f"{path}: {field} contains invalid unquoted item: {value}")
    return value


def _parse_inline_yaml_list(raw_value: str, path: Path, field: str) -> list[str]:
    value = raw_value.strip()
    if not value.startswith("[") or not value.endswith("]"):
        raise ValueError(f"{path}: {field} inline value must be a bracketed list")
    inner = value[1:-1]
    if not inner.strip():
        return []

    tokens: list[str] = []
    current: list[str] = []
    quote = ""
    escaped = False
    index = 0
    while index < len(inner):
        character = inner[index]
        if quote == '"':
            current.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quote = ""
            index += 1
            continue
        if quote == "'":
            current.append(character)
            if character == "'":
                if index + 1 < len(inner) and inner[index + 1] == "'":
                    current.append(inner[index + 1])
                    index += 2
                    continue
                quote = ""
            index += 1
            continue
        if character in {'"', "'"}:
            quote = character
            current.append(character)
        elif character == ",":
            tokens.append("".join(current))
            current = []
        elif character in "[]":
            raise ValueError(f"{path}: {field} does not support nested YAML lists")
        else:
            current.append(character)
        index += 1
    if quote or escaped:
        raise ValueError(f"{path}: {field} contains an unterminated quoted item")
    tokens.append("".join(current))
    return [_parse_yaml_string_scalar(token, path, field) for token in tokens]


def parse_frontmatter_list(path: Path, field: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing frontmatter while parsing {field}")

    frontmatter_end = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if frontmatter_end is None:
        raise ValueError(f"{path}: unterminated frontmatter while parsing {field}")

    declaration_index: int | None = None
    declaration_value = ""
    for index, line in enumerate(lines[1:frontmatter_end], start=1):
        match = re.fullmatch(rf"{re.escape(field)}:\s*(.*)", line)
        if not match:
            continue
        if declaration_index is not None:
            raise ValueError(f"{path}: duplicate frontmatter field {field}")
        declaration_index = index
        declaration_value = match.group(1)

    if declaration_index is None:
        return []
    if declaration_value:
        return _parse_inline_yaml_list(declaration_value, path, field)

    values: list[str] = []
    index = declaration_index + 1
    while index < frontmatter_end:
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if not line.startswith(" "):
            break
        match = re.fullmatch(r"  -\s+(.+)", line)
        if not match:
            raise ValueError(f"{path}: malformed multiline list for {field}: {line}")
        values.append(_parse_yaml_string_scalar(match.group(1), path, field))
        index += 1
    return values


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


def duplicate_frontmatter_keys(path: Path, package_root: Path) -> list[str]:
    """Detect duplicate mapping keys in the frontmatter subset used here."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    parents: dict[int, str] = {}
    seen: set[tuple[str, str]] = set()
    duplicates: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^( *)([A-Za-z0-9_-]+):(?:\s|$)", line)
        if not match:
            continue
        indent = len(match.group(1))
        key = match.group(2)
        for level in list(parents):
            if level >= indent:
                del parents[level]
        parent = ".".join(parents[level] for level in sorted(parents))
        qualified = f"{parent}.{key}" if parent else key
        marker = (parent, key)
        if marker in seen:
            duplicates.append(qualified)
        else:
            seen.add(marker)
        if line.rstrip().endswith(":"):
            parents[indent] = key
    return duplicates


def validate_frontmatter_duplicate_keys(package_root: Path) -> None:
    failures: list[str] = []
    candidates = sorted((package_root / "skills").glob("*/SKILL.md"))
    candidates += sorted((package_root / "agents").glob("*.md"))
    candidates += sorted((package_root / "commands").glob("*.md"))
    for path in candidates:
        for key in duplicate_frontmatter_keys(path, package_root):
            relative = str(path.relative_to(package_root))
            failures.append(f"{relative}: duplicate frontmatter key {key}")
    if failures:
        raise ValueError("frontmatter duplicate key failures:\n- " + "\n- ".join(failures))


def validate_transitional_loki_bundles(package_root: Path) -> None:
    failures: list[str] = []
    for skill_path in sorted((package_root / "skills").glob("loki-*/SKILL.md")):
        bundle = skill_path.parent
        execution = bundle / "references" / "execution.md"
        response = bundle / "references" / "response.md"
        template = bundle / "assets" / "response-template.md"
        resources = (execution, response, template)
        skill_text = skill_path.read_text(encoding="utf-8")
        frontmatter = skill_text.split("---", 2)[1]
        if "serialization:" in frontmatter:
            failures.append(f"{skill_path}: schema 1 bundle must not declare serialization")
        if not any(path.exists() or path.is_symlink() for path in resources):
            continue
        for path in resources:
            if not path.exists():
                failures.append(f"{bundle}: incomplete transitional bundle; missing {path.relative_to(bundle)}")
            elif path.is_symlink():
                failures.append(f"{path}: transitional bundle resource must not be a symlink")
        for reference in (
            "references/execution.md",
            "references/response.md",
            "assets/response-template.md",
        ):
            if reference not in skill_text:
                failures.append(f"{skill_path}: does not route {reference}")
        headings = [skill_text.find(f"## {name}") for name in ("Input", "Execution", "Response")]
        if any(index < 0 for index in headings) or headings != sorted(headings):
            failures.append(
                f"{skill_path}: transitional bundle must route ## Input, ## Execution and ## Response in order"
            )
        if execution.exists() and "## Execution" not in execution.read_text(encoding="utf-8"):
            failures.append(f"{execution}: missing ## Execution")
        if response.exists() and "## Response" not in response.read_text(encoding="utf-8"):
            failures.append(f"{response}: missing ## Response")
    if failures:
        raise ValueError("transitional Loki bundle failures:\n- " + "\n- ".join(failures))


def iter_artifact_files(package_root: Path, kind: str, name: str) -> list[Path]:
    if kind == "skills":
        root = package_root / "skills" / name
        # Compiled Python caches are runtime by-products, never package
        # artifacts.  Do not decode them during neutrality scanning.
        return sorted(
            path for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        )
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
                if kind == "skills" and name.startswith("loki-"):
                    for pattern, label in TRANSIENT_PLAN_REFERENCE_PATTERNS:
                        match = pattern.search(text)
                        if match is not None:
                            failures.append(
                                f"{path}: both Loki bundle contains normative transient "
                                f"{label} '{match.group(0)}'"
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


def parse_manifest_file_catalog(package_root: Path, section_name: str) -> set[str]:
    """Read a simple manifest catalog without treating presentation as authority."""
    files: set[str] = set()
    in_section = False
    for line in (package_root / "manifest.yaml").read_text(encoding="utf-8").splitlines():
        if line == f"{section_name}:":
            in_section = True
            continue
        if in_section and line and not line.startswith(" "):
            break
        if in_section and line.startswith("    file:"):
            files.add(parse_manifest_scalar(line.split(":", 1)[1]))
    return files


def validate_claude_coverage(package_root: Path, data: dict) -> None:
    """Prove manual Claude categories from the manifest and scope inventory."""
    policy = data["artifact_identity_policy"].get("claude_code")
    if not isinstance(policy, dict) or policy.get("projection") != "manual-copy":
        raise ValueError("Claude coverage must declare the manual-copy projection")
    categories = policy.get("categories")
    if not isinstance(categories, dict):
        raise ValueError("Claude coverage must declare categories")
    expected_categories = {
        "skills": {"source": "skills/*/", "scope_source": "artifacts.skills", "target": ".claude/skills/"},
        "agents": {"source": "agents/*.md", "scope_source": "artifacts.agents", "target": ".claude/agents/"},
        "templates": {"source": "templates/*", "scope": "all-profiles", "target": ".claude/templates/loki/"},
    }
    if categories != expected_categories:
        raise ValueError("Claude coverage categories drift from the schema-2 contract")

    skill_sources = {path.parent.name for path in (package_root / "skills").glob("*/SKILL.md")}
    agent_sources = {path.name for path in (package_root / "agents").glob("*.md")}
    template_sources = {
        str(path.relative_to(package_root))
        for path in (package_root / "templates").glob("*")
        if path.is_file()
    }
    manifest_skills = set(parse_manifest_skill_catalog(package_root))
    manifest_agents = {
        entry.get("file", "") for entry in parse_manifest_agent_catalog(package_root)["agents"]
    }
    manifest_templates = parse_manifest_file_catalog(package_root, "templates")
    failures: list[str] = []
    for label, actual, expected in (
        ("Claude skills", skill_sources, set(artifact_scopes(data, "skills"))),
        ("Claude agents", agent_sources, set(artifact_scopes(data, "agents"))),
        ("manifest skills", manifest_skills, skill_sources),
        ("manifest agents", manifest_agents, {f"agents/{name}" for name in agent_sources}),
        ("manifest templates", manifest_templates, template_sources),
    ):
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing or extra:
            detail = []
            if missing:
                detail.append("missing " + ", ".join(missing))
            if extra:
                detail.append("extra " + ", ".join(extra))
            failures.append(f"{label} coverage: " + "; ".join(detail))
    if failures:
        raise ValueError("Claude coverage failures:\n- " + "\n- ".join(failures))


def validate_no_goose_projection(package_root: Path) -> None:
    """Reject the retired Goose adapter before any profile can be accepted."""
    failures: list[str] = []
    goose_root = package_root / "goose"
    if goose_root.exists() and any(path.is_file() for path in goose_root.rglob("*")):
        failures.append("goose/: retired projection files are present")
    scanned_roots = (
        package_root / "README.md",
        package_root / "manifest.yaml",
        package_root / "install-scopes.json",
        package_root / "docs",
        package_root / "skills",
        package_root / "agents",
        package_root / "codex",
        package_root / "templates",
        package_root / "scripts",
    )
    validator_path = package_root / "scripts" / "validate-install-scopes.py"
    for root in scanned_roots:
        candidates = [root] if root.is_file() else sorted(root.rglob("*")) if root.is_dir() else []
        for path in candidates:
            if not path.is_file() or path == validator_path or path.suffix == ".pyc":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if re.search(
                r"(?i)(?:\bgoose/|\bgoose[-_ ](?:recipe|agent|skill|projection)\b)",
                text,
            ):
                failures.append(
                    f"{path.relative_to(package_root)}: residual Goose projection reference"
                )
    if failures:
        raise ValueError("Goose projection failures:\n- " + "\n- ".join(failures))


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


def validate_no_production_consumer_state(package_root: Path) -> None:
    """Reject live consumer state from package surfaces installed by Loki.

    Analytic-inference fixtures are immutable test inputs declared by their
    `references/fixtures` placement. Contracts, schemas, scripts, and the
    default policy remain package capability; a live catalog or `.loki` tree
    does not.
    """
    failures: list[str] = []

    for root_name in INSTALLABLE_PACKAGE_ROOTS:
        root = package_root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            relative = path.relative_to(package_root)
            if ".loki" in relative.parts:
                failures.append(f"{relative}: packaged .loki consumer state is forbidden")

    inference_root = package_root / ANALYTIC_INFERENCE_RELATIVE_ROOT
    if inference_root.exists():
        fixtures_root = inference_root / ANALYTIC_INFERENCE_FIXTURES
        for path in inference_root.rglob("*"):
            is_declared_fixture = path == fixtures_root or fixtures_root in path.parents
            if not path.is_file() and not path.is_symlink():
                continue
            relative_to_inference = path.relative_to(inference_root)
            relative_to_package = path.relative_to(package_root)
            if path.suffix == ".json" and path.is_file():
                payload = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(payload, dict) and payload.get("production_seed") is True:
                    failures.append(
                        f"{relative_to_package}: production_seed=true is forbidden in the package"
                    )
            if is_declared_fixture:
                continue
            if path.name == "index.json" or path.name in PRODUCTION_STATE_FILENAMES or (
                path.suffix == ".xml" and PRODUCTION_RECORD_FILENAME.fullmatch(path.name)
            ) or any(
                component in PRODUCTION_STATE_COMPONENTS
                for component in relative_to_inference.parts
            ):
                failures.append(
                    f"{relative_to_package}: packaged analytic-inference catalog state is forbidden"
                )
            if path.name.lower().startswith(("seed.", "seed-", "seed_")):
                failures.append(
                    f"{relative_to_package}: packaged analytic-inference live seed is forbidden"
                )

    if failures:
        raise ValueError(
            "production consumer state failures:\n- " + "\n- ".join(sorted(set(failures)))
        )


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


def frontmatter_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"{path}: missing parseable YAML frontmatter delimiters")
    return parts[1]


def validate_final_loki_bundles(
    package_root: Path,
    data: dict,
    require_full_inventory: bool = True,
) -> None:
    skill_scopes = artifact_scopes(data, "skills")
    loki_names = sorted(name for name in skill_scopes if name.startswith("loki-"))
    public_loki_names = sorted(
        name for name in loki_names if skill_scopes[name] != "internal-only"
    )
    if require_full_inventory and len(public_loki_names) != FINAL_LOKI_COMMAND_COUNT:
        raise ValueError(
            f"schema 2 must declare {FINAL_LOKI_COMMAND_COUNT} public Loki command bundles; "
            f"found {len(public_loki_names)}"
        )

    failures: list[str] = []
    for name in loki_names:
        bundle = package_root / "skills" / name
        skill_path = bundle / "SKILL.md"
        if not skill_path.is_file() or skill_path.is_symlink():
            failures.append(f"{skill_path}: command entrypoint must be a real file")
            continue
        try:
            frontmatter = frontmatter_text(skill_path)
        except ValueError as exc:
            failures.append(str(exc))
            continue

        checks = {
            "name": name,
            "type": "command",
            "serialization": "skill-bundle",
            "hooks": "{}",
            "shell": "bash",
        }
        for field, expected in checks.items():
            actual = frontmatter_scalar(skill_path, field)
            if actual != expected:
                failures.append(
                    f"{skill_path}: {field}={actual or 'missing'}; expected {expected}"
                )
        for forbidden in ("projection", "command_name", "command_contract"):
            if re.search(rf"(?m)^\s*{re.escape(forbidden)}:", frontmatter):
                failures.append(f"{skill_path}: forbidden schema-1 key {forbidden}")
        for field in ("required_skills", "required_commands"):
            if not frontmatter_declares_field(skill_path, field):
                failures.append(f"{skill_path}: missing {field}")

        bundle_resolved = bundle.resolve(strict=True)
        for relative in FINAL_BUNDLE_RESOURCES:
            resource = bundle / relative
            if resource.is_symlink() or not resource.is_file():
                failures.append(f"{resource}: required bundle resource must be a real file")
                continue
            try:
                resource.resolve(strict=True).relative_to(bundle_resolved)
            except ValueError:
                failures.append(f"{resource}: resource resolves outside its bundle")

        skill_text = skill_path.read_text(encoding="utf-8")
        for reference in ("references/execution.md", "references/response.md"):
            if reference not in skill_text:
                failures.append(f"{skill_path}: does not route {reference}")
        headings = [
            skill_text.find(f"## {heading}")
            for heading in ("Input", "Execution", "Response")
        ]
        if any(index < 0 for index in headings) or headings != sorted(headings):
            failures.append(
                f"{skill_path}: must route ## Input, ## Execution and ## Response in order"
            )
        response_path = bundle / "references" / "response.md"
        if response_path.is_file() and "assets/response-template.md" not in response_path.read_text(
            encoding="utf-8"
        ):
            failures.append(
                f"{response_path}: must reference assets/response-template.md"
            )

    if failures:
        raise ValueError("final Loki bundle failures:\n- " + "\n- ".join(failures))


def validate_final_command_dependencies(package_root: Path, data: dict) -> None:
    scopes = artifact_scopes(data, "skills")
    command_names = {name for name in scopes if name.startswith("loki-")}
    failures: list[str] = []

    for command_name in sorted(command_names):
        path = package_root / "skills" / command_name / "SKILL.md"
        source_profiles = {
            profile
            for profile in PROFILE_SCOPES_FOR_VALIDATION
            if scopes[command_name] in PROFILE_SCOPES_FOR_VALIDATION[profile]
        }
        for skill_name in parse_required_skills(path):
            if skill_name.startswith("loki-"):
                failures.append(
                    f"{path}: required_skills contains command bundle {skill_name}"
                )
                continue
            if skill_name not in scopes:
                failures.append(f"{path}: required skill {skill_name} is not installed")
                continue
            dependency_profiles = {
                profile
                for profile in PROFILE_SCOPES_FOR_VALIDATION
                if scopes[skill_name] in PROFILE_SCOPES_FOR_VALIDATION[profile]
            }
            missing_profiles = sorted(source_profiles - dependency_profiles)
            if missing_profiles:
                failures.append(
                    f"{path}: required skill {skill_name} is absent from profile(s) "
                    + ", ".join(missing_profiles)
                )

        for required_command in parse_required_commands(path):
            if not required_command.startswith("loki-"):
                failures.append(
                    f"{path}: required_commands contains non-command {required_command}"
                )
                continue
            if required_command == command_name:
                failures.append(f"{path}: command must not require itself")
            if required_command not in command_names:
                failures.append(
                    f"{path}: required command {required_command} is not installed"
                )
                continue
            dependency_profiles = {
                profile
                for profile in PROFILE_SCOPES_FOR_VALIDATION
                if scopes[required_command] in PROFILE_SCOPES_FOR_VALIDATION[profile]
            }
            missing_profiles = sorted(source_profiles - dependency_profiles)
            if missing_profiles:
                failures.append(
                    f"{path}: required command {required_command} is absent from profile(s) "
                    + ", ".join(missing_profiles)
                )

    if failures:
        raise ValueError(
            "final command dependency failures:\n- " + "\n- ".join(failures)
        )


PROFILE_SCOPES_FOR_VALIDATION = {
    "consumer": {"both", "consumer-only"},
    "package-source": {"both", "internal-only"},
    "all": set(VALID_SCOPES),
}


def validate_final_neutrality(package_root: Path, data: dict) -> None:
    scopes = artifact_scopes(data, "skills")
    internal_names = {
        name for name, scope in scopes.items() if scope == "internal-only"
    }
    failures: list[str] = []
    for name, scope in sorted(scopes.items()):
        if scope != "both":
            continue
        for path in iter_artifact_files(package_root, "skills", name):
            text = path.read_text(encoding="utf-8").lower()
            for term in SUSPICIOUS_BOTH_TERMS:
                if term in text:
                    failures.append(f"{path}: both artifact contains '{term}'")
            for internal_name in internal_names:
                if internal_name in text:
                    failures.append(
                        f"{path}: both artifact references internal-only {internal_name}"
                    )
            if name.startswith("loki-"):
                for pattern, label in TRANSIENT_PLAN_REFERENCE_PATTERNS:
                    match = pattern.search(text)
                    if match is not None:
                        failures.append(
                            f"{path}: both Loki bundle contains normative transient "
                            f"{label} '{match.group(0)}'"
                        )
    if failures:
        raise ValueError("neutrality failures:\n- " + "\n- ".join(failures))


def validate_final_manifest(package_root: Path, data: dict) -> None:
    manifest_path = package_root / "manifest.yaml"
    text = manifest_path.read_text(encoding="utf-8")
    failures: list[str] = []
    if re.search(r"(?m)^commands:\s*$", text):
        failures.append("manifest must not contain a top-level commands catalog")
    if re.search(r"(?m)^\s+(commands|command_contract|projection):", text):
        failures.append("manifest contains a legacy commands/projection field")
    catalog = parse_manifest_skill_catalog(package_root)
    loki_entries = {name: metadata for name, metadata in catalog.items() if name.startswith("loki-")}
    skill_scopes = artifact_scopes(data, "skills")
    public_loki_entries = {
        name: metadata
        for name, metadata in loki_entries.items()
        if skill_scopes.get(name) != "internal-only"
    }
    if len(public_loki_entries) != FINAL_LOKI_COMMAND_COUNT:
        failures.append(
            f"manifest must contain {FINAL_LOKI_COMMAND_COUNT} public Loki skill entries"
        )
    for name, metadata in sorted(loki_entries.items()):
        if metadata.get("operational_role") != "command":
            failures.append(f"manifest skills.{name}.operational_role must be command")
        if metadata.get("serialization") != "skill-bundle":
            failures.append(f"manifest skills.{name}.serialization must be skill-bundle")
        if metadata.get("projection"):
            failures.append(f"manifest skills.{name} must not declare projection")
    if failures:
        raise ValueError("final manifest failures:\n- " + "\n- ".join(failures))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    package_root = (
        args.package_root.expanduser().resolve(strict=True)
        if args.package_root
        else Path(__file__).resolve().parent.parent
    )
    try:
        data = load_scopes(package_root)
        skill_scopes = artifact_scopes(data, "skills")
        skill_names = {
            path.parent.name
            for path in (package_root / "skills").glob("*/SKILL.md")
        }
        assert_exact_keys("skill", set(skill_scopes), skill_names)
        validate_frontmatter_duplicate_keys(package_root)
        validate_no_production_consumer_state(package_root)

        if (package_root / "commands").exists():
            raise ValueError("schema 2 final state must not contain commands/")
        validate_final_loki_bundles(
            package_root,
            data,
            require_full_inventory=not args.scope_contract_only,
        )
        validate_final_command_dependencies(package_root, data)

        if args.scope_contract_only:
            print("install scope validation: ok (schema 2 fixture contract)")
            return 0

        agent_scopes = artifact_scopes(data, "agents")
        codex_agent_scopes = artifact_scopes(data, "codex_agents")
        agent_names = {path.name for path in (package_root / "agents").glob("*.md")}
        codex_agent_names = {
            path.name for path in (package_root / "codex" / "agents").glob("*.toml")
        }
        assert_exact_keys("agent", set(agent_scopes), agent_names)
        assert_exact_keys("Codex agent", set(codex_agent_scopes), codex_agent_names)
        validate_framework_skill_identity(package_root, data)

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

        validate_final_neutrality(package_root, data)
        validate_toml(package_root)
        validate_claude_coverage(package_root, data)
        validate_no_goose_projection(package_root)
        validate_manifest_entries(package_root)
        validate_final_manifest(package_root, data)
        validate_agent_project_tags(package_root)
        validate_agentic_agent_metadata(package_root)
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("install scope validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
