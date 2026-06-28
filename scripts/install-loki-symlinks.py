#!/usr/bin/env python3
"""Install Loki Framework artifacts into a target project by symlink."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


MANIFEST_RELATIVE_PATH = Path(".agents") / "loki-installation-manifest.json"
CONFLICT_EXIT_CODE = 2
REQUIRED_SKILL_NAMES = frozenset(
    {
        "loki-action-plan-authoring",
        "loki-agent-creator",
        "loki-command-creator",
        "loki-command-workflows",
        "loki-continuous-improvement",
        "loki-documentation-writing",
        "loki-enrich-tasks",
        "loki-external-knowledge-extraction",
        "loki-feedback",
        "loki-framework-impact-audit",
        "loki-generate-action-plan",
        "loki-index-navigator",
        "loki-knowledge-extraction-analysis",
        "loki-retrospectiva-tecnica",
        "loki-run-plan",
        "loki-run-plan-execution",
        "loki-skill-creator",
        "loki-tech-analysis",
        "loki-tech-analysis-authoring",
        "loki-template-library",
    }
)


class InstallError(Exception):
    """Raised when the install plan cannot be built or applied safely."""


@dataclass(frozen=True)
class LinkSpec:
    source: Path
    destination: Path
    link_type: str
    source_kind: str


@dataclass(frozen=True)
class PlannedLink:
    source: Path
    destination: Path
    link_type: str
    source_kind: str
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
            "status": self.status,
        }
        if self.reason:
            entry["reason"] = self.reason
        return entry


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install Loki Framework skills, commands, agents and templates "
            "into a destination project using symlinks."
        )
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="Destination project directory that should receive the Loki links.",
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


def discover_skills(package_root: Path) -> list[Path]:
    skills_root = require_directory(package_root / "skills", package_root)
    skill_dirs = sorted(
        path
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not skill_dirs:
        raise InstallError(f"missing required skill directories in {skills_root}")
    discovered_names = {path.name for path in skill_dirs}
    missing = sorted(REQUIRED_SKILL_NAMES - discovered_names)
    if missing:
        raise InstallError(
            "missing required Loki skill wrapper(s): " + ", ".join(missing)
        )
    return [resolve_required_source(path, package_root) for path in skill_dirs]


def discover_codex_agents(package_root: Path) -> list[Path]:
    codex_agents_root = require_directory(
        package_root / "codex" / "agents",
        package_root,
    )
    return [
        require_file(path, package_root)
        for path in require_non_empty_files(
            codex_agents_root,
            "*.toml",
            "Codex agent TOML files",
        )
    ]


def assert_destination_inside_root(destination: Path, destination_root: Path) -> None:
    try:
        destination.relative_to(destination_root)
    except ValueError as exc:
        raise InstallError(
            f"planned destination is outside destination root: {destination}"
        ) from exc


def build_link_specs(package_root: Path, destination_root: Path) -> list[LinkSpec]:
    commands_root = require_directory(package_root / "commands", package_root)
    agents_root = require_directory(package_root / "agents", package_root)
    templates_root = require_directory(package_root / "templates", package_root)

    require_non_empty_files(commands_root, "*.md", "command contracts")
    agent_contracts = require_non_empty_files(agents_root, "*.md", "agent contracts")
    require_non_empty_files(templates_root, "*", "templates")
    codex_agent_files = discover_codex_agents(package_root)
    agent_names = {path.stem for path in agent_contracts}
    codex_agent_names = {path.stem for path in codex_agent_files}
    missing_codex_agents = sorted(agent_names - codex_agent_names)
    if missing_codex_agents:
        raise InstallError(
            "missing required Codex agent TOML(s): "
            + ", ".join(missing_codex_agents)
        )

    specs: list[LinkSpec] = []

    for skill_dir in discover_skills(package_root):
        destination = destination_root / ".agents" / "skills" / skill_dir.name
        specs.append(
            LinkSpec(
                source=skill_dir,
                destination=destination,
                link_type="skill",
                source_kind="directory",
            )
        )

    specs.extend(
        [
            LinkSpec(
                source=commands_root,
                destination=destination_root / ".agents" / "commands" / "loki",
                link_type="commands",
                source_kind="directory",
            ),
            LinkSpec(
                source=agents_root,
                destination=destination_root / ".agents" / "agents",
                link_type="agents",
                source_kind="directory",
            ),
            LinkSpec(
                source=templates_root,
                destination=destination_root / ".agents" / "templates",
                link_type="templates",
                source_kind="directory",
            ),
        ]
    )

    for agent_file in codex_agent_files:
        destination = destination_root / ".codex" / "agents" / agent_file.name
        specs.append(
            LinkSpec(
                source=agent_file,
                destination=destination,
                link_type="codex-agent",
                source_kind="file",
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


def classify_destination(destination: Path, source: Path) -> tuple[str, str]:
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
    if state == "missing":
        return ("would-create" if dry_run else "created", False)
    if state == "symlink-correct":
        return ("kept", False)
    if replace:
        return ("would-replace" if dry_run else "replaced", False)
    return ("blocked", True)


def plan_links(
    specs: list[LinkSpec],
    replace: bool,
    dry_run: bool,
) -> list[PlannedLink]:
    planned: list[PlannedLink] = []
    for spec in specs:
        state, reason = classify_destination(spec.destination, spec.source)
        status, blocked = status_for_state(state, replace=replace, dry_run=dry_run)
        planned.append(
            PlannedLink(
                source=spec.source,
                destination=spec.destination,
                link_type=spec.link_type,
                source_kind=spec.source_kind,
                existing_state=state,
                status=status,
                blocked=blocked,
                reason=reason if blocked or state != "missing" else "",
            )
        )
    return planned


def print_plan(
    planned_links: list[PlannedLink],
    package_root: Path,
    destination_root: Path,
    dry_run: bool,
    replace: bool,
) -> None:
    mode = "dry-run" if dry_run else "apply"
    print(f"mode: {mode}")
    print(f"replace: {str(replace).lower()}")
    print(f"package_root: {package_root}")
    print(f"dest_root: {destination_root}")
    print("links:")
    for link in planned_links:
        print(
            f"- status={link.status} type={link.link_type} "
            f"source={link.source} destination={link.destination}"
        )
        if link.reason:
            print(f"  reason={link.reason}")


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


def write_manifest(
    destination_root: Path,
    package_root: Path,
    replace: bool,
    planned_links: list[PlannedLink],
) -> Path:
    manifest_path = destination_root / MANIFEST_RELATIVE_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "package_root": str(package_root),
        "dest_root": str(destination_root),
        "created_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "mode": "apply",
        "replace": replace,
        "links": [link.manifest_entry() for link in planned_links],
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
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
        specs = build_link_specs(package_root, destination_root)
        planned_links = plan_links(
            specs,
            replace=args.replace,
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
    )
    sys.stdout.flush()

    blocked_links = [link for link in planned_links if link.blocked]
    if blocked_links:
        print(
            f"error: {len(blocked_links)} blocked destination(s); rerun with "
            "--replace only after approval",
            file=sys.stderr,
        )
        return CONFLICT_EXIT_CODE

    if args.dry_run:
        return 0

    try:
        applied_links = apply_plan(planned_links)
        manifest_path = write_manifest(
            destination_root,
            package_root=package_root,
            replace=args.replace,
            planned_links=applied_links,
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
