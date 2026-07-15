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
class PlannedLegacyRemoval:
    destination: Path
    origin: Path | None
    existing_state: str
    status: str
    blocked: bool = False
    reason: str = ""

    def manifest_entry(self) -> dict[str, str]:
        entry = {
            "destination": str(self.destination),
            "status": "removed",
        }
        if self.origin is not None:
            entry["origin"] = str(self.origin)
        return entry


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
    parser.add_argument(
        "--cleanup-legacy-commands",
        action="store_true",
        help=(
            "Remove only exact legacy command symlinks claimed by the previous "
            "Loki installation manifest. Apply also requires --yes."
        ),
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

    schema_version = raw_config.get("schema_version")
    if schema_version not in {1, 2}:
        raise InstallError(f"{path} must declare schema_version 1 or 2")

    profiles = raw_config.get("profiles", {})
    for profile, expected_scopes in PROFILE_SCOPES.items():
        configured = frozenset(profiles.get(profile, []))
        if configured != expected_scopes:
            raise InstallError(
                f"profile {profile} must map to {sorted(expected_scopes)}"
            )

    artifacts = raw_config.get("artifacts", {})
    skills = artifacts.get("skills")
    commands = artifacts.get("commands")
    agents = artifacts.get("agents")
    codex_agents = artifacts.get("codex_agents")
    if (
        not isinstance(skills, dict)
        or not isinstance(agents, dict)
        or not isinstance(codex_agents, dict)
    ):
        raise InstallError(
            f"{path} must define artifacts.skills, artifacts.agents and "
            "artifacts.codex_agents"
        )
    if schema_version == 1 and not isinstance(commands, dict):
        raise InstallError(f"{path} schema 1 must define artifacts.commands")
    if schema_version == 2 and commands is not None:
        raise InstallError(f"{path} schema 2 must not define artifacts.commands")

    unknown_scopes = sorted(
        (
            set(skills.values())
            | (set(commands.values()) if isinstance(commands, dict) else set())
            | set(agents.values())
            | set(codex_agents.values())
        )
        - VALID_SCOPES
    )
    if unknown_scopes:
        raise InstallError("unknown install scope(s): " + ", ".join(unknown_scopes))

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
    missing = sorted(discovered_names - configured_names)
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
        if scope_selected(scope_config.skills[path.name], profile)
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
                f"parent path is a symlink: {parent}; remove or replace the "
                "legacy directory symlink before installing per-file links"
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
        "legacy skill file symlink exists; use --replace to migrate to "
        "a skill directory symlink"
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
    if state == "parent-symlink-conflict":
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
            f"invalid install_profile in installation manifest: {manifest_path}"
        )
    return profile


def lexical_absolute(path: Path, relative_to: Path | None = None) -> Path:
    if not path.is_absolute():
        if relative_to is None:
            raise InstallError(f"expected absolute path, got: {path}")
        path = relative_to / path
    return Path(os.path.abspath(os.path.normpath(str(path))))


def is_lexically_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def legacy_command_root(destination_root: Path) -> Path:
    return lexical_absolute(destination_root / ".agents" / "commands" / "loki")


def legacy_parent_symlink(destination_root: Path) -> Path | None:
    root = legacy_command_root(destination_root)
    for candidate in (destination_root / ".agents", root.parent, root):
        if candidate.is_symlink():
            return candidate
    return None


def _blocked_legacy(
    destination: Path,
    reason: str,
    origin: Path | None = None,
    existing_state: str = "unsafe",
) -> PlannedLegacyRemoval:
    return PlannedLegacyRemoval(
        destination=destination,
        origin=origin,
        existing_state=existing_state,
        status="blocked",
        blocked=True,
        reason=reason,
    )


def plan_legacy_cleanup(
    destination_root: Path,
    cleanup_requested: bool,
    dry_run: bool,
) -> list[PlannedLegacyRemoval]:
    """Plan lexical-only deletion of v1 command links without following them."""

    root = legacy_command_root(destination_root)
    parent_symlink = legacy_parent_symlink(destination_root)
    if parent_symlink is not None:
        return [
            _blocked_legacy(
                root,
                f"legacy command parent is a symlink: {parent_symlink}",
                existing_state="parent-symlink",
            )
        ]

    manifest = read_previous_manifest(destination_root)
    entries: list[dict] = []
    if manifest is not None:
        raw_links = manifest.get("links", [])
        if not isinstance(raw_links, list):
            return [
                _blocked_legacy(
                    root,
                    "previous installation manifest links must be a list",
                    existing_state="invalid-manifest",
                )
            ]
        entries = [
            entry
            for entry in raw_links
            if isinstance(entry, dict) and entry.get("type") == "command"
        ]

    discovered: set[Path] = set()
    if root.exists():
        if not root.is_dir():
            return [
                _blocked_legacy(
                    root,
                    "legacy command root is a real file",
                    existing_state="real-file",
                )
            ]
        try:
            discovered = {lexical_absolute(path) for path in root.iterdir()}
        except OSError as exc:
            return [
                _blocked_legacy(
                    root,
                    f"cannot inspect legacy command root: {exc}",
                    existing_state="unreadable",
                )
            ]

    planned: list[PlannedLegacyRemoval] = []
    claimed: set[Path] = set()
    previous_package_root_raw = manifest.get("package_root") if manifest else None
    previous_package_root = None
    if entries:
        if not isinstance(previous_package_root_raw, str) or not previous_package_root_raw:
            planned.append(
                _blocked_legacy(
                    root,
                    "previous manifest with command links is missing package_root",
                    existing_state="invalid-manifest",
                )
            )
        else:
            previous_package_root = lexical_absolute(Path(previous_package_root_raw))

    for entry in entries:
        raw_destination = entry.get("destination")
        raw_origin = entry.get("origin")
        if not isinstance(raw_destination, str) or not isinstance(raw_origin, str):
            planned.append(
                _blocked_legacy(
                    root,
                    "legacy command manifest entry must contain string destination and origin",
                    existing_state="invalid-entry",
                )
            )
            continue

        destination_raw_path = Path(raw_destination)
        destination = lexical_absolute(destination_raw_path)
        origin = lexical_absolute(Path(raw_origin))
        if not destination_raw_path.is_absolute() or str(destination_raw_path) != str(destination):
            planned.append(
                _blocked_legacy(
                    destination,
                    "legacy destination is not an absolute normalized path",
                    origin,
                    "path-traversal",
                )
            )
            continue
        if destination.parent != root:
            planned.append(
                _blocked_legacy(
                    destination,
                    f"legacy destination is outside exact command root {root}",
                    origin,
                    "unknown-path",
                )
            )
            continue
        if destination in claimed:
            planned.append(
                _blocked_legacy(
                    destination,
                    "duplicate legacy destination in previous manifest",
                    origin,
                    "duplicate-entry",
                )
            )
            continue
        claimed.add(destination)

        if previous_package_root is None or not is_lexically_within(
            origin, previous_package_root / "commands"
        ):
            planned.append(
                _blocked_legacy(
                    destination,
                    "legacy origin is outside the previous package commands directory",
                    origin,
                    "origin-outside-package",
                )
            )
            continue
        if not destination.is_symlink():
            if destination.exists():
                state = "real-directory" if destination.is_dir() else "real-file"
                planned.append(
                    _blocked_legacy(
                        destination,
                        f"legacy destination is a {state}; automatic cleanup only removes symlinks",
                        origin,
                        state,
                    )
                )
            continue

        raw_target = Path(os.readlink(destination))
        actual_target = lexical_absolute(raw_target, destination.parent)
        if actual_target != origin:
            planned.append(
                _blocked_legacy(
                    destination,
                    f"legacy symlink target {actual_target} differs from recorded origin {origin}",
                    origin,
                    "divergent-symlink",
                )
            )
            continue

        status = "would-remove" if cleanup_requested and dry_run else "remove"
        if not cleanup_requested:
            status = "requires-cleanup-flag"
        planned.append(
            PlannedLegacyRemoval(
                destination=destination,
                origin=origin,
                existing_state="exact-symlink",
                status=status,
                reason=(
                    "pass --cleanup-legacy-commands to authorize exact legacy cleanup"
                    if not cleanup_requested
                    else "lexical target matches the previous manifest"
                ),
            )
        )

    for unknown in sorted(discovered - claimed):
        kind = "symlink" if unknown.is_symlink() else (
            "directory" if unknown.is_dir() else "file"
        )
        planned.append(
            _blocked_legacy(
                unknown,
                f"unclaimed legacy {kind}; no exact command entry exists in previous manifest",
                existing_state=f"unclaimed-{kind}",
            )
        )

    return planned


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


def print_plan(
    planned_links: list[PlannedLink],
    package_root: Path,
    destination_root: Path,
    dry_run: bool,
    replace: bool,
    profile: str,
    cleanup_requested: bool,
    legacy_cleanup: list[PlannedLegacyRemoval],
) -> None:
    mode = "dry-run" if dry_run else "apply"
    print(f"mode: {mode}")
    print(f"profile: {profile}")
    print("install_scope: " + ",".join(sorted(PROFILE_SCOPES[profile])))
    print(f"replace: {str(replace).lower()}")
    print(f"cleanup_legacy_commands: {str(cleanup_requested).lower()}")
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
    print("legacy_command_cleanup:")
    if not legacy_cleanup:
        print("  none")
    for removal in legacy_cleanup:
        origin = str(removal.origin) if removal.origin is not None else "unknown"
        print(
            f"- status={removal.status} type=legacy-command "
            f"origin={origin} destination={removal.destination}"
        )
        if removal.reason:
            print(f"  reason={removal.reason}")


def remove_exact_conflict(path: Path, existing_state: str) -> None:
    if path.is_symlink():
        path.unlink()
        return

    if existing_state == "skill-file-symlink-conflict":
        skill_file = path / "SKILL.md"
        if not skill_file.is_symlink():
            raise InstallError(
                f"cannot migrate legacy skill install without SKILL.md symlink: {path}"
            )
        skill_file.unlink()
        try:
            path.rmdir()
        except OSError as exc:
            raise InstallError(
                f"cannot migrate legacy skill install with extra entries: {path}"
            ) from exc
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


def apply_legacy_cleanup(
    destination_root: Path,
    planned_removals: list[PlannedLegacyRemoval],
) -> list[PlannedLegacyRemoval]:
    removed: list[PlannedLegacyRemoval] = []
    for removal in planned_removals:
        if removal.blocked:
            raise InstallError(
                f"blocked legacy destination {removal.destination}: {removal.reason}"
            )
        if removal.status not in {"remove", "would-remove"}:
            continue
        if not removal.destination.is_symlink():
            raise InstallError(
                f"legacy destination changed before apply: {removal.destination}"
            )
        actual_target = lexical_absolute(
            Path(os.readlink(removal.destination)), removal.destination.parent
        )
        if removal.origin is None or actual_target != removal.origin:
            raise InstallError(
                f"legacy symlink target changed before apply: {removal.destination}"
            )
        removal.destination.unlink()
        removed.append(removal)

    root = legacy_command_root(destination_root)
    for directory in (root, root.parent):
        if directory.is_symlink() or not directory.exists():
            continue
        try:
            directory.rmdir()
        except OSError:
            pass
    return removed


def write_manifest(
    destination_root: Path,
    package_root: Path,
    replace: bool,
    profile: str,
    planned_links: list[PlannedLink],
    removed_legacy_links: list[PlannedLegacyRemoval],
) -> Path:
    manifest_path = destination_root / MANIFEST_RELATIVE_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    previous_manifest = read_previous_manifest(destination_root)
    previous_removed = (
        previous_manifest.get("removed_legacy_links", [])
        if previous_manifest is not None
        else []
    )
    if not isinstance(previous_removed, list):
        raise InstallError(
            f"invalid removed_legacy_links in previous manifest: {manifest_path}"
        )
    removal_history: list[dict[str, str]] = []
    seen_removals: set[tuple[str, str]] = set()
    for entry in [
        *(item for item in previous_removed if isinstance(item, dict)),
        *(removal.manifest_entry() for removal in removed_legacy_links),
    ]:
        destination = entry.get("destination")
        origin = entry.get("origin", "")
        if not isinstance(destination, str) or not isinstance(origin, str):
            continue
        marker = (destination, origin)
        if marker in seen_removals:
            continue
        seen_removals.add(marker)
        removal_history.append(dict(entry))
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
        "removed_legacy_links": removal_history,
    }
    payload = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
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
        os.replace(temporary_path, manifest_path)
        temporary_path = None
    except OSError as exc:
        raise InstallError(f"cannot atomically write manifest {manifest_path}: {exc}") from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
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
        legacy_cleanup = plan_legacy_cleanup(
            destination_root,
            cleanup_requested=args.cleanup_legacy_commands,
            dry_run=args.dry_run,
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
        cleanup_requested=args.cleanup_legacy_commands,
        legacy_cleanup=legacy_cleanup,
    )
    sys.stdout.flush()

    blocked_links = [link for link in planned_links if link.blocked]
    blocked_legacy = [removal for removal in legacy_cleanup if removal.blocked]
    if blocked_links or (args.cleanup_legacy_commands and blocked_legacy):
        print(
            f"error: {len(blocked_links) + len(blocked_legacy)} blocked destination(s); resolve the "
            "reported blocker(s). Use --replace only for exact path conflicts "
            "after approval",
            file=sys.stderr,
        )
        return CONFLICT_EXIT_CODE

    if args.dry_run:
        return 0

    legacy_present = bool(legacy_cleanup)
    if legacy_present and not args.cleanup_legacy_commands:
        print(
            "error: legacy command paths detected; apply requires --yes "
            "--cleanup-legacy-commands; --replace does not authorize cleanup",
            file=sys.stderr,
        )
        return CONFLICT_EXIT_CODE

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
        revalidated_legacy = plan_legacy_cleanup(
            destination_root,
            cleanup_requested=args.cleanup_legacy_commands,
            dry_run=False,
        )
        if any(link.blocked for link in revalidated_links):
            raise InstallError("a destination changed or remained blocked before apply")
        if any(removal.blocked for removal in revalidated_legacy):
            raise InstallError("a legacy destination changed or remained blocked before apply")
        if revalidated_legacy and not args.cleanup_legacy_commands:
            raise InstallError(
                "legacy command paths require --cleanup-legacy-commands"
            )

        removed_legacy = apply_legacy_cleanup(
            destination_root, revalidated_legacy
        )
        applied_links = apply_plan(revalidated_links)
        manifest_path = write_manifest(
            destination_root,
            package_root=package_root,
            replace=args.replace,
            profile=args.profile,
            planned_links=applied_links,
            removed_legacy_links=removed_legacy,
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
