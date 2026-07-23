#!/usr/bin/env python3
"""Install Loki Framework artifacts into a target project by symlink."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


MANIFEST_RELATIVE_PATH = Path(".agents") / "loki-installation-manifest.json"
INSTALL_SCOPES_RELATIVE_PATH = Path("install-scopes.json")
CONFLICT_EXIT_CODE = 2
VALID_SCOPES = frozenset({"internal-only", "both", "consumer-only"})
PROFILE_SCOPES = {
    "consumer": frozenset({"both", "consumer-only"}),
    "package-source": frozenset({"both", "internal-only"}),
    "all": frozenset(VALID_SCOPES),
}
INSTALL_SCOPE_ROOT_KEYS = frozenset(
    {"schema_version", "profiles", "artifact_identity_policy", "artifacts"}
)
INSTALL_SCOPE_ARTIFACT_KEYS = frozenset({"skills", "agents", "codex_agents", "docs"})
INSTALL_SCOPE_REQUIRED_ARTIFACT_KEYS = frozenset({"skills", "agents", "codex_agents"})
INSTALL_SCOPE_PROFILE_KEYS = frozenset(PROFILE_SCOPES)
RETIRED_SOURCE_ONLY_SKILLS = frozenset(
    {f"loki-{stem}" for stem in ("generate-action-plan", "run-plan")}
    | {"lf-" + "run-plan-execution"}
)


def scope_error(code: str, message: str) -> "InstallError":
    """Create a stable install-scopes contract error."""
    return InstallError(f"INSTALL_SCOPES:{code}: {message}")


class InstallError(Exception):
    """Raised when the install plan cannot be built or applied safely."""


@dataclass(frozen=True)
class InstallScopeConfig:
    skills: dict[str, str]
    agents: dict[str, str]
    codex_agents: dict[str, str]
    schema_version: int


@dataclass(frozen=True)
class LinkSpec:
    source: Path
    destination: Path
    link_type: str
    source_kind: str
    install_scope: str


@dataclass(frozen=True)
class PlannedLink:
    source: Path
    destination: Path
    link_type: str
    source_kind: str
    install_scope: str
    existing_state: str
    status: str
    blocked: bool = False
    reason: str = ""

    def manifest_entry(self) -> dict[str, str]:
        entry = {
            "origin": str(self.source),
            "destination": str(self.destination),
            "type": self.link_type,
            "source_kind": self.source_kind,
            "install_scope": self.install_scope,
            "status": self.status,
        }
        if self.reason:
            entry["reason"] = self.reason
        return entry


@dataclass(frozen=True)
class ManagedRemoval:
    source: Path
    destination: Path
    source_kind: str


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install Loki Framework skills, agents and templates "
            "into a destination project using symlinks."
        )
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="Destination project directory that should receive the Loki links.",
    )
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILE_SCOPES),
        default="consumer",
        help=(
            "Installation profile. consumer installs both + consumer-only; "
            "package-source installs both + internal-only; all installs every scope."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned links without writing to the destination.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Allow real writes. Required unless --dry-run is used.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace conflicting exact destination paths. Use only after approval.",
    )
    return parser.parse_args(argv)


def resolve_package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_destination_root(raw_destination: str) -> Path:
    return Path(raw_destination).expanduser().resolve(strict=False)


def resolve_required_source(path: Path, package_root: Path) -> Path:
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise InstallError(f"missing required source: {path}") from exc

    try:
        resolved.relative_to(package_root)
    except ValueError as exc:
        raise InstallError(
            f"required source is outside package root: {resolved}"
        ) from exc

    return resolved


def require_directory(path: Path, package_root: Path) -> Path:
    resolved = resolve_required_source(path, package_root)
    if not resolved.is_dir():
        raise InstallError(f"required source is not a directory: {resolved}")
    return resolved


def require_file(path: Path, package_root: Path) -> Path:
    resolved = resolve_required_source(path, package_root)
    if not resolved.is_file():
        raise InstallError(f"required source is not a file: {resolved}")
    return resolved


def require_non_empty_files(
    directory: Path,
    pattern: str,
    description: str,
) -> list[Path]:
    files = sorted(path for path in directory.glob(pattern) if path.is_file())
    if not files:
        raise InstallError(f"missing required {description} in {directory}")
    return files


def read_install_scopes(package_root: Path) -> InstallScopeConfig:
    path = require_file(package_root / INSTALL_SCOPES_RELATIVE_PATH, package_root)
    try:
        raw_config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InstallError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw_config, dict):
        raise scope_error("ROOT_TYPE", "root must be an object")
    unknown_root_keys = sorted(set(raw_config) - INSTALL_SCOPE_ROOT_KEYS)
    missing_root_keys = sorted(INSTALL_SCOPE_ROOT_KEYS - set(raw_config))
    if unknown_root_keys or missing_root_keys:
        details = []
        if missing_root_keys:
            details.append("missing " + ", ".join(missing_root_keys))
        if unknown_root_keys:
            details.append("unknown " + ", ".join(unknown_root_keys))
        raise scope_error("ROOT_KEYS", "; ".join(details))

    schema_version = raw_config["schema_version"]
    if schema_version != 2:
        raise scope_error("SCHEMA_VERSION", "schema_version must be 2")

    profiles = raw_config["profiles"]
    if not isinstance(profiles, dict):
        raise scope_error("PROFILES_TYPE", "profiles must be an object")
    unknown_profile_keys = sorted(set(profiles) - INSTALL_SCOPE_PROFILE_KEYS)
    missing_profile_keys = sorted(INSTALL_SCOPE_PROFILE_KEYS - set(profiles))
    if unknown_profile_keys or missing_profile_keys:
        details = []
        if missing_profile_keys:
            details.append("missing " + ", ".join(missing_profile_keys))
        if unknown_profile_keys:
            details.append("unknown " + ", ".join(unknown_profile_keys))
        raise scope_error("PROFILE_KEYS", "; ".join(details))
    for profile, expected_scopes in PROFILE_SCOPES.items():
        configured_scopes = profiles[profile]
        if not isinstance(configured_scopes, list) or not all(
            isinstance(scope, str) for scope in configured_scopes
        ):
            raise scope_error("PROFILE_SCOPES", f"profile {profile} must be a list of scopes")
        configured = frozenset(configured_scopes)
        if configured != expected_scopes:
            raise scope_error(
                "PROFILE_SCOPES",
                f"profile {profile} must map to {sorted(expected_scopes)}",
            )

    artifacts = raw_config["artifacts"]
    if not isinstance(artifacts, dict):
        raise scope_error("ARTIFACTS_TYPE", "artifacts must be an object")
    unknown_artifact_keys = sorted(set(artifacts) - INSTALL_SCOPE_ARTIFACT_KEYS)
    missing_artifact_keys = sorted(INSTALL_SCOPE_REQUIRED_ARTIFACT_KEYS - set(artifacts))
    if unknown_artifact_keys or missing_artifact_keys:
        details = []
        if missing_artifact_keys:
            details.append("missing " + ", ".join(missing_artifact_keys))
        if unknown_artifact_keys:
            details.append("unknown " + ", ".join(unknown_artifact_keys))
        raise scope_error("ARTIFACT_KEYS", "; ".join(details))
    invalid_artifacts = sorted(
        key for key, value in artifacts.items() if not isinstance(value, dict)
    )
    if invalid_artifacts:
        raise scope_error("ARTIFACT_VALUES", "artifact maps must be objects: " + ", ".join(invalid_artifacts))
    skills = artifacts["skills"]
    agents = artifacts["agents"]
    codex_agents = artifacts["codex_agents"]

    unknown_scopes = sorted(
        (
            set(skills.values())
            | set(agents.values())
            | set(codex_agents.values())
        )
        - VALID_SCOPES
    )
    if unknown_scopes:
        raise scope_error("UNKNOWN_SCOPE", ", ".join(unknown_scopes))

    return InstallScopeConfig(
        skills=dict(skills),
        agents=dict(agents),
        codex_agents=dict(codex_agents),
        schema_version=schema_version,
    )


def scope_selected(scope: str, profile: str) -> bool:
    return scope in PROFILE_SCOPES[profile]


def discover_skills(
    package_root: Path,
    scope_config: InstallScopeConfig,
    profile: str,
) -> list[tuple[Path, str]]:
    skills_root = require_directory(package_root / "skills", package_root)
    skill_dirs = sorted(
        path
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not skill_dirs:
        raise InstallError(f"missing required skill directories in {skills_root}")

    discovered_names = {path.name for path in skill_dirs}
    configured_names = set(scope_config.skills)
    missing = sorted(discovered_names - configured_names - RETIRED_SOURCE_ONLY_SKILLS)
    extra = sorted(configured_names - discovered_names)
    if missing or extra:
        details = []
        if missing:
            details.append("missing scope for skill(s): " + ", ".join(missing))
        if extra:
            details.append("scope references missing skill(s): " + ", ".join(extra))
        raise InstallError("; ".join(details))

    return [
        (resolve_required_source(path, package_root), scope_config.skills[path.name])
        for path in skill_dirs
        if path.name in scope_config.skills
        and scope_selected(scope_config.skills[path.name], profile)
    ]


def discover_agents(
    package_root: Path,
    scope_config: InstallScopeConfig,
    profile: str,
) -> list[tuple[Path, str]]:
    agents_root = require_directory(package_root / "agents", package_root)
    agent_files = require_non_empty_files(agents_root, "*.md", "agent contracts")
    discovered_names = {path.name for path in agent_files}
    configured_names = set(scope_config.agents)
    missing = sorted(discovered_names - configured_names)
    extra = sorted(configured_names - discovered_names)
    if missing or extra:
        details = []
        if missing:
            details.append("missing scope for agent(s): " + ", ".join(missing))
        if extra:
            details.append("scope references missing agent(s): " + ", ".join(extra))
        raise InstallError("; ".join(details))

    return [
        (require_file(path, package_root), scope_config.agents[path.name])
        for path in agent_files
        if scope_selected(scope_config.agents[path.name], profile)
    ]


def discover_codex_agents(
    package_root: Path,
    scope_config: InstallScopeConfig,
    profile: str,
) -> list[tuple[Path, str]]:
    codex_agents_root = require_directory(
        package_root / "codex" / "agents",
        package_root,
    )
    codex_agent_files = require_non_empty_files(
        codex_agents_root,
        "*.toml",
        "Codex agent TOML files",
    )
    discovered_names = {path.name for path in codex_agent_files}
    configured_names = set(scope_config.codex_agents)
    missing = sorted(discovered_names - configured_names)
    extra = sorted(configured_names - discovered_names)
    if missing or extra:
        details = []
        if missing:
            details.append("missing scope for Codex agent(s): " + ", ".join(missing))
        if extra:
            details.append(
                "scope references missing Codex agent(s): " + ", ".join(extra)
            )
        raise InstallError("; ".join(details))

    return [
        (require_file(path, package_root), scope_config.codex_agents[path.name])
        for path in codex_agent_files
        if scope_selected(scope_config.codex_agents[path.name], profile)
    ]


def assert_destination_inside_root(destination: Path, destination_root: Path) -> None:
    try:
        destination.relative_to(destination_root)
    except ValueError as exc:
        raise InstallError(
            f"planned destination is outside destination root: {destination}"
        ) from exc


def build_link_specs(
    package_root: Path,
    destination_root: Path,
    scope_config: InstallScopeConfig,
    profile: str,
) -> list[LinkSpec]:
    templates_root = require_directory(package_root / "templates", package_root)

    require_non_empty_files(templates_root, "*", "templates")
    agent_contracts = discover_agents(package_root, scope_config, "all")
    codex_agent_files = discover_codex_agents(package_root, scope_config, "all")
    agent_names = {path.stem for path, _scope in agent_contracts}
    codex_agent_names = {path.stem for path, _scope in codex_agent_files}
    missing_codex_agents = sorted(agent_names - codex_agent_names)
    if missing_codex_agents:
        raise InstallError(
            "missing required Codex agent TOML(s): "
            + ", ".join(missing_codex_agents)
        )

    specs: list[LinkSpec] = []

    for skill_dir, scope in discover_skills(package_root, scope_config, profile):
        destination = destination_root / ".agents" / "skills" / skill_dir.name
        specs.append(
            LinkSpec(
                source=skill_dir,
                destination=destination,
                link_type="skill",
                source_kind="directory",
                install_scope=scope,
            )
        )

    for agent_file, scope in discover_agents(package_root, scope_config, profile):
        destination = destination_root / ".agents" / "agents" / agent_file.name
        specs.append(
            LinkSpec(
                source=agent_file,
                destination=destination,
                link_type="agent",
                source_kind="file",
                install_scope=scope,
            )
        )

    specs.append(
        LinkSpec(
            source=templates_root,
            destination=destination_root / ".agents" / "templates",
            link_type="templates",
            source_kind="directory",
            install_scope="both",
        )
    )

    for agent_file, scope in discover_codex_agents(package_root, scope_config, profile):
        destination = destination_root / ".codex" / "agents" / agent_file.name
        specs.append(
            LinkSpec(
                source=agent_file,
                destination=destination,
                link_type="codex-agent",
                source_kind="file",
                install_scope=scope,
            )
        )

    for spec in specs:
        assert_destination_inside_root(spec.destination, destination_root)

    return specs


def resolve_symlink_target(path: Path) -> Path:
    raw_target = Path(os.readlink(path))
    if not raw_target.is_absolute():
        raw_target = path.parent / raw_target
    return raw_target.resolve(strict=False)


def parent_symlink_conflict_reason(destination: Path, destination_root: Path) -> str:
    for parent in destination.parents:
        if parent == destination_root:
            return ""
        if parent.is_symlink():
            return (
                f"parent path is a symlink: {parent}; remove it manually before "
                "installing per-file links"
            )
    return ""


def legacy_skill_file_symlink_reason(destination: Path, source: Path) -> str:
    expected_skill_file = source / "SKILL.md"
    if not source.is_dir() or not expected_skill_file.is_file():
        return ""

    try:
        entries = list(destination.iterdir())
    except OSError:
        return ""

    if len(entries) != 1 or entries[0].name != "SKILL.md":
        return ""

    installed_skill_file = destination / "SKILL.md"
    if not installed_skill_file.is_symlink():
        return ""

    target = resolve_symlink_target(installed_skill_file)
    if target != expected_skill_file.resolve(strict=True):
        return ""

    return (
        "legacy skill-file symlink exists; remove it manually before installing "
        "the skill directory symlink"
    )


def classify_destination(
    destination: Path,
    source: Path,
    destination_root: Path,
) -> tuple[str, str]:
    parent_conflict = parent_symlink_conflict_reason(destination, destination_root)
    if parent_conflict:
        return "parent-symlink-conflict", parent_conflict

    if destination.is_symlink():
        target = resolve_symlink_target(destination)
        if target == source:
            return "symlink-correct", f"already points to {source}"
        return "symlink-conflict", f"points to {target}, expected {source}"

    if destination.exists():
        if destination.is_dir():
            legacy_reason = legacy_skill_file_symlink_reason(destination, source)
            if legacy_reason:
                return "skill-file-symlink-conflict", legacy_reason
            return "directory-conflict", "real directory exists"
        return "file-conflict", "real file exists"

    return "missing", "destination is absent"


def status_for_state(state: str, replace: bool, dry_run: bool) -> tuple[str, bool]:
    if state in {"parent-symlink-conflict", "skill-file-symlink-conflict"}:
        return ("blocked", True)
    if state == "missing":
        return ("would-create" if dry_run else "created", False)
    if state == "symlink-correct":
        return ("kept", False)
    if replace:
        return ("would-replace" if dry_run else "replaced", False)
    return ("blocked", True)


def plan_links(
    specs: list[LinkSpec],
    destination_root: Path,
    replace: bool,
    dry_run: bool,
) -> list[PlannedLink]:
    planned: list[PlannedLink] = []
    for spec in specs:
        state, reason = classify_destination(
            spec.destination,
            spec.source,
            destination_root,
        )
        status, blocked = status_for_state(state, replace=replace, dry_run=dry_run)
        planned.append(
            PlannedLink(
                source=spec.source,
                destination=spec.destination,
                link_type=spec.link_type,
                source_kind=spec.source_kind,
                install_scope=spec.install_scope,
                existing_state=state,
                status=status,
                blocked=blocked,
                reason=reason if blocked or state != "missing" else "",
            )
        )
    return planned


def profile_selected_specs(specs: list[LinkSpec], profile: str) -> list[LinkSpec]:
    return [
        spec for spec in specs if scope_selected(spec.install_scope, profile)
    ]


def profile_excluded_specs(specs: list[LinkSpec], profile: str) -> list[LinkSpec]:
    return [
        spec for spec in specs if not scope_selected(spec.install_scope, profile)
    ]


def plan_profile_exclusion_blocks(
    specs: list[LinkSpec],
    destination_root: Path,
    profile: str,
) -> list[PlannedLink]:
    blockers: list[PlannedLink] = []
    for spec in profile_excluded_specs(specs, profile):
        state, reason = classify_destination(
            spec.destination,
            spec.source,
            destination_root,
        )
        if state == "missing":
            continue

        blockers.append(
            PlannedLink(
                source=spec.source,
                destination=spec.destination,
                link_type=spec.link_type,
                source_kind=spec.source_kind,
                install_scope=spec.install_scope,
                existing_state=state,
                status="blocked",
                blocked=True,
                reason=(
                    f"destination contains artifact outside profile {profile}: "
                    f"scope={spec.install_scope}; remove stale Loki install "
                    "targets using the previous installation manifest before "
                    f"applying profile {profile}"
                    + (f"; existing state: {reason}" if reason else "")
                ),
            )
        )
    return blockers


def read_previous_manifest(destination_root: Path) -> dict | None:
    manifest_path = destination_root / MANIFEST_RELATIVE_PATH
    if not manifest_path.exists() and not manifest_path.is_symlink():
        return None
    if not manifest_path.is_file():
        raise InstallError(f"installation manifest is not a file: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InstallError(f"invalid installation manifest: {manifest_path}: {exc}") from exc

    if not isinstance(manifest, dict):
        raise InstallError(f"installation manifest must be a JSON object: {manifest_path}")
    return manifest


def existing_manifest_profile(destination_root: Path) -> str:
    manifest = read_previous_manifest(destination_root)
    if manifest is None:
        return ""

    profile = manifest.get("install_profile")
    if profile is None:
        return ""
    if not isinstance(profile, str):
        raise InstallError(
            "invalid install_profile in installation manifest: "
            f"{destination_root / MANIFEST_RELATIVE_PATH}"
        )
    return profile


def assert_no_legacy_install_layout(destination_root: Path) -> None:
    """Reject v1 layouts before planning any mutation.

    The schema-v2 installer never infers ownership of a legacy layout and never
    removes it. Consumers must remove or migrate those paths explicitly.
    """

    command_tree = destination_root / ".agents" / "commands"
    if command_tree.exists() or command_tree.is_symlink():
        raise InstallError(
            "legacy command tree detected at "
            f"{command_tree}; refusing to migrate or remove consumer paths"
        )

    manifest = read_previous_manifest(destination_root)
    if manifest is None:
        return
    links = manifest.get("links", [])
    if not isinstance(links, list):
        raise InstallError("installation manifest links must be a list")
    if any(isinstance(entry, dict) and entry.get("type") == "command" for entry in links):
        raise InstallError(
            "legacy installation manifest contains command links; refusing to "
            "migrate or remove consumer paths"
        )
    if "removed_legacy_links" in manifest:
        raise InstallError(
            "legacy installation manifest contains cleanup history; refusing to "
            "migrate or remove consumer paths"
        )


def assert_profile_matches_existing_manifest(
    destination_root: Path,
    profile: str,
) -> None:
    existing_profile = existing_manifest_profile(destination_root)
    if not existing_profile or existing_profile == profile:
        return

    raise InstallError(
        "destination already has a Loki installation manifest for profile "
        f"{existing_profile}; refusing to apply profile {profile}. Roll back the "
        "existing Loki links from .agents/loki-installation-manifest.json, then "
        "run a new dry-run for the desired profile."
    )


def lexical_absolute(path: Path) -> Path:
    """Normalize an absolute path without following its final symlink."""
    return Path(os.path.abspath(os.fspath(path)))


def plan_managed_upgrade(
    destination_root: Path,
    package_root: Path,
    specs: list[LinkSpec],
) -> tuple[bytes | None, list[ManagedRemoval], set[Path]]:
    """Validate prior manifest authority and select exact retired managed links."""
    manifest_path = destination_root / MANIFEST_RELATIVE_PATH
    manifest = read_previous_manifest(destination_root)
    if manifest is None:
        return None, [], set()

    previous_bytes = manifest_path.read_bytes()
    links = manifest.get("links")
    if not isinstance(links, list):
        raise InstallError("installation manifest links must be a list")

    expected = {lexical_absolute(spec.destination): spec for spec in specs}
    recorded_destinations: set[Path] = set()
    removals: list[ManagedRemoval] = []
    for index, entry in enumerate(links):
        if not isinstance(entry, dict):
            raise InstallError(f"installation manifest link {index} must be an object")
        required = {"origin", "destination", "type", "source_kind", "install_scope"}
        if not required.issubset(entry) or not all(
            isinstance(entry.get(key), str) and entry.get(key) for key in required
        ):
            raise InstallError(f"installation manifest link {index} is incomplete")
        destination = lexical_absolute(Path(entry["destination"]))
        source = Path(entry["origin"]).resolve(strict=False)
        try:
            destination.relative_to(destination_root)
            source.relative_to(package_root)
        except ValueError as exc:
            raise InstallError(
                f"installation manifest link escapes approved roots: {destination} -> {source}"
            ) from exc
        if destination in recorded_destinations:
            raise InstallError(f"duplicate managed destination in prior manifest: {destination}")
        recorded_destinations.add(destination)
        if not destination.is_symlink():
            raise InstallError(
                f"managed destination is missing or unmanaged/divergent: {destination}"
            )
        actual = resolve_symlink_target(destination)
        if actual != source:
            raise InstallError(
                f"managed destination is divergent: {destination} points to {actual}, "
                f"prior manifest requires {source}"
            )

        current = expected.get(destination)
        if current is not None:
            if current.source != source or current.link_type != entry["type"]:
                raise InstallError(
                    f"managed destination identity changed unexpectedly: {destination}"
                )
            continue

        relative = destination.relative_to(destination_root)
        retired_name = relative.name
        retired_source = (package_root / "skills" / retired_name).resolve(strict=False)
        if (
            relative != Path(".agents") / "skills" / retired_name
            or retired_name not in RETIRED_SOURCE_ONLY_SKILLS
            or source != retired_source
            or entry["type"] != "skill"
            or entry["source_kind"] != "directory"
        ):
            raise InstallError(
                f"prior manifest contains unmanaged stale identity; refusing removal: {destination}"
            )
        removals.append(
            ManagedRemoval(source=source, destination=destination, source_kind="directory")
        )

    return previous_bytes, sorted(removals, key=lambda item: str(item.destination)), recorded_destinations


def print_plan(
    planned_links: list[PlannedLink],
    package_root: Path,
    destination_root: Path,
    dry_run: bool,
    replace: bool,
    profile: str,
    removals: list[ManagedRemoval],
) -> None:
    mode = "dry-run" if dry_run else "apply"
    print(f"mode: {mode}")
    print(f"profile: {profile}")
    print("install_scope: " + ",".join(sorted(PROFILE_SCOPES[profile])))
    print(f"replace: {str(replace).lower()}")
    print(f"package_root: {package_root}")
    print(f"dest_root: {destination_root}")
    print("links:")
    for link in planned_links:
        print(
            f"- status={link.status} type={link.link_type} "
            f"scope={link.install_scope} source={link.source} "
            f"destination={link.destination}"
        )
        if link.reason:
            print(f"  reason={link.reason}")
    for item in removals:
        print(
            f"- status={'would-remove' if dry_run else 'remove'} type=skill "
            f"scope=retired-managed source={item.source} destination={item.destination}"
        )


def remove_exact_conflict(path: Path, existing_state: str) -> None:
    if path.is_symlink():
        path.unlink()
        return

    if path.is_dir():
        try:
            path.rmdir()
        except OSError as exc:
            raise InstallError(
                f"cannot replace non-empty directory without recursive delete: {path}"
            ) from exc
        return

    if path.exists():
        path.unlink()
        return

    raise InstallError(f"cannot replace missing path: {path}")


def create_symlink(source: Path, destination: Path, source_kind: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(
        str(source),
        str(destination),
        target_is_directory=source_kind == "directory",
    )


def apply_plan(planned_links: list[PlannedLink]) -> list[PlannedLink]:
    applied: list[PlannedLink] = []
    for link in planned_links:
        if link.blocked:
            raise InstallError(
                f"blocked destination {link.destination}: {link.reason}"
            )

        if link.status == "kept":
            applied.append(link)
            continue

        if link.status == "replaced":
            remove_exact_conflict(link.destination, link.existing_state)

        create_symlink(link.source, link.destination, link.source_kind)
        applied.append(link)

    return applied


def manifest_payload(
    destination_root: Path,
    package_root: Path,
    replace: bool,
    profile: str,
    planned_links: list[PlannedLink],
) -> str:
    manifest = {
        "package_root": str(package_root),
        "dest_root": str(destination_root),
        "created_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "mode": "apply",
        "replace": replace,
        "install_profile": profile,
        "install_scope": sorted(PROFILE_SCOPES[profile]),
        "links": [link.manifest_entry() for link in planned_links],
    }
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def stage_manifest(manifest_path: Path, payload: str) -> Path:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=manifest_path.parent,
            prefix=f".{manifest_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        staged = json.loads(temporary_path.read_text(encoding="utf-8"))
        if not isinstance(staged, dict) or not isinstance(staged.get("links"), list):
            raise InstallError(f"staged installation manifest is invalid: {temporary_path}")
        return temporary_path
    except (OSError, json.JSONDecodeError) as exc:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise InstallError(f"cannot stage installation manifest {manifest_path}: {exc}") from exc


def publish_staged_manifest(staged_path: Path, manifest_path: Path) -> None:
    try:
        os.replace(staged_path, manifest_path)
    except OSError as exc:
        raise InstallError(
            f"cannot atomically publish manifest {manifest_path}: {exc}"
        ) from exc


def rollback_managed_mutations(
    created: list[PlannedLink],
    removed: list[ManagedRemoval],
) -> list[str]:
    failures: list[str] = []
    for link in reversed(created):
        try:
            if not link.destination.is_symlink():
                failures.append(f"created target no longer symlink: {link.destination}")
            elif resolve_symlink_target(link.destination) != link.source:
                failures.append(f"created target diverged before rollback: {link.destination}")
            else:
                link.destination.unlink()
        except OSError as exc:
            failures.append(f"cannot remove created target {link.destination}: {exc}")
    for item in removed:
        try:
            if item.destination.exists() or item.destination.is_symlink():
                failures.append(f"retired target occupied during rollback: {item.destination}")
            else:
                create_symlink(item.source, item.destination, item.source_kind)
        except OSError as exc:
            failures.append(f"cannot restore managed target {item.destination}: {exc}")
    return failures


def apply_transaction(
    destination_root: Path,
    package_root: Path,
    replace: bool,
    profile: str,
    planned_links: list[PlannedLink],
    removals: list[ManagedRemoval],
    previous_manifest_bytes: bytes | None,
) -> Path:
    manifest_path = destination_root / MANIFEST_RELATIVE_PATH
    payload = manifest_payload(
        destination_root, package_root, replace, profile, planned_links
    )
    staged_path = stage_manifest(manifest_path, payload)
    created: list[PlannedLink] = []
    removed: list[ManagedRemoval] = []
    try:
        if previous_manifest_bytes is not None:
            if not manifest_path.is_file() or manifest_path.read_bytes() != previous_manifest_bytes:
                raise InstallError("prior installation manifest changed before mutation")
        elif manifest_path.exists() or manifest_path.is_symlink():
            raise InstallError("installation manifest appeared before mutation")

        for item in removals:
            if not item.destination.is_symlink() or resolve_symlink_target(item.destination) != item.source:
                raise InstallError(
                    f"managed retired destination changed before removal: {item.destination}"
                )
            item.destination.unlink()
            removed.append(item)

        for link in planned_links:
            if link.blocked:
                raise InstallError(f"blocked destination {link.destination}: {link.reason}")
            if link.status == "kept":
                continue
            if link.status == "replaced":
                remove_exact_conflict(link.destination, link.existing_state)
            create_symlink(link.source, link.destination, link.source_kind)
            created.append(link)

        for link in planned_links:
            if not link.destination.is_symlink() or resolve_symlink_target(link.destination) != link.source:
                raise InstallError(f"post-mutation link validation failed: {link.destination}")
        for item in removals:
            if item.destination.exists() or item.destination.is_symlink():
                raise InstallError(f"retired managed link remains after mutation: {item.destination}")

        publish_staged_manifest(staged_path, manifest_path)
        staged_path = Path()
        return manifest_path
    except (InstallError, OSError) as exc:
        rollback_failures = rollback_managed_mutations(created, removed)
        if rollback_failures:
            locators = "; ".join(rollback_failures)
            raise InstallError(
                f"installation transaction failed ({exc}); rollback incomplete: {locators}; "
                f"prior manifest remains authoritative at {manifest_path}"
            ) from exc
        raise InstallError(
            f"installation transaction failed and prior topology was restored: {exc}"
        ) from exc
    finally:
        if staged_path != Path():
            staged_path.unlink(missing_ok=True)


def write_manifest(
    destination_root: Path,
    package_root: Path,
    replace: bool,
    profile: str,
    planned_links: list[PlannedLink],
) -> Path:
    manifest_path = destination_root / MANIFEST_RELATIVE_PATH
    payload = manifest_payload(
        destination_root, package_root, replace, profile, planned_links
    )
    temporary_path = stage_manifest(manifest_path, payload)
    try:
        publish_staged_manifest(temporary_path, manifest_path)
        temporary_path = Path()
    finally:
        if temporary_path != Path():
            temporary_path.unlink(missing_ok=True)
    return manifest_path


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.dry_run and not args.yes:
        print(
            "error: refusing to write without --yes; use --dry-run to preview",
            file=sys.stderr,
        )
        return 1

    try:
        package_root = resolve_package_root()
        destination_root = resolve_destination_root(args.dest)
        scope_config = read_install_scopes(package_root)
        assert_no_legacy_install_layout(destination_root)
        assert_profile_matches_existing_manifest(destination_root, args.profile)
        all_specs = build_link_specs(
            package_root,
            destination_root,
            scope_config=scope_config,
            profile="all",
        )
        specs = profile_selected_specs(all_specs, args.profile)
        planned_links = plan_links(
            specs,
            destination_root=destination_root,
            replace=args.replace,
            dry_run=args.dry_run,
        )
        planned_links.extend(
            plan_profile_exclusion_blocks(
                all_specs,
                destination_root=destination_root,
                profile=args.profile,
            )
        )
        previous_manifest_bytes, managed_removals, recorded_destinations = (
            plan_managed_upgrade(
                destination_root,
                package_root,
                specs,
            )
        )
        if previous_manifest_bytes is not None:
            for link in planned_links:
                destination = lexical_absolute(link.destination)
                if link.status in {"would-replace", "replaced"}:
                    raise InstallError(
                        f"upgrade refuses divergent or unmanaged target: {destination}"
                    )
                if (
                    link.existing_state != "missing"
                    and destination not in recorded_destinations
                ):
                    raise InstallError(
                        f"upgrade refuses target absent from prior manifest authority: {destination}"
                    )
    except InstallError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print_plan(
        planned_links,
        package_root=package_root,
        destination_root=destination_root,
        dry_run=args.dry_run,
        replace=args.replace,
        profile=args.profile,
        removals=managed_removals,
    )
    sys.stdout.flush()

    blocked_links = [link for link in planned_links if link.blocked]
    if blocked_links:
        print(
            f"error: {len(blocked_links)} blocked destination(s); resolve the "
            "reported blocker(s). Use --replace only for exact path conflicts "
            "after approval",
            file=sys.stderr,
        )
        return CONFLICT_EXIT_CODE

    if args.dry_run:
        return 0

    try:
        # Rebuild both plans immediately before mutation so a changed symlink or
        # destination cannot reuse stale preflight evidence.
        revalidated_links = plan_links(
            specs,
            destination_root=destination_root,
            replace=args.replace,
            dry_run=False,
        )
        revalidated_links.extend(
            plan_profile_exclusion_blocks(
                all_specs,
                destination_root=destination_root,
                profile=args.profile,
            )
        )
        if any(link.blocked for link in revalidated_links):
            raise InstallError("a destination changed or remained blocked before apply")
        assert_no_legacy_install_layout(destination_root)
        revalidated_previous_bytes, revalidated_removals, revalidated_recorded = (
            plan_managed_upgrade(destination_root, package_root, specs)
        )
        if revalidated_previous_bytes != previous_manifest_bytes:
            raise InstallError("prior installation manifest changed before apply")
        if revalidated_removals != managed_removals:
            raise InstallError("managed removal topology changed before apply")
        if revalidated_recorded != recorded_destinations:
            raise InstallError("managed destination set changed before apply")
        if previous_manifest_bytes is not None:
            for link in revalidated_links:
                destination = lexical_absolute(link.destination)
                if link.status == "replaced" or (
                    link.existing_state != "missing"
                    and destination not in revalidated_recorded
                ):
                    raise InstallError(
                        f"upgrade refuses divergent or unmanaged target: {destination}"
                    )
        manifest_path = apply_transaction(
            destination_root,
            package_root=package_root,
            replace=args.replace,
            profile=args.profile,
            planned_links=revalidated_links,
            removals=revalidated_removals,
            previous_manifest_bytes=revalidated_previous_bytes,
        )
    except InstallError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"manifest: {manifest_path}")
    return 0


def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
