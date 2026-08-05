#!/usr/bin/env python3
"""Exercise schema-v2 install, managed upgrade, rollback, and refusal behavior."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from unittest import mock


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = PACKAGE_ROOT / "scripts" / "install-loki-symlinks.py"
SCOPE_VALIDATOR = PACKAGE_ROOT / "scripts" / "validate-install-scopes.py"
MANIFEST_RELATIVE_PATH = Path(".agents") / "loki-installation-manifest.json"
LEGACY_COMMAND_RELATIVE_DIR = Path(".agents") / "commands" / "loki"
PLAN_LINE = re.compile(r"^- status=\S+ type=(\S+) ")

FINAL_COUNTS = {
    "consumer": {"skill": 56, "agent": 26, "codex-agent": 26, "templates": 1},
    "package-source": {"skill": 43, "agent": 13, "codex-agent": 13, "templates": 1},
    "all": {"skill": 57, "agent": 26, "codex-agent": 26, "templates": 1},
}
FINAL_TOTALS = {"consumer": 109, "package-source": 70, "all": 110}
RETIRED_SKILLS = (
    "loki-" + "generate-action-plan",
    "loki-" + "run-plan",
    "lf-" + "run-plan-execution",
)
CURRENT_REPLACEMENTS = ("loki-implement-feature", "lf-implement-feature-execution")


@dataclass(frozen=True)
class LegacyFixture:
    case: str
    destination_root: Path
    previous_package_root: Path
    manifest_path: Path
    legacy_destination: Path
    recorded_origin: Path


def run_installer(
    destination: Path, profile: str = "consumer", *extra_args: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(INSTALLER),
            "--dest",
            str(destination),
            "--profile",
            profile,
            *extra_args,
        ],
        cwd=PACKAGE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def planned_type_counts(stdout: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    in_links = False
    for line in stdout.splitlines():
        if line == "links:":
            in_links = True
            continue
        if in_links and (match := PLAN_LINE.match(line)):
            counts[match.group(1)] += 1
    return counts


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_schema_v2_fixture(fixture_root: Path) -> Path:
    package_root = (fixture_root / "schema-v2-package").resolve()
    bundle = package_root / "skills" / "loki-example"
    write_text(
        bundle / "SKILL.md",
        """---
name: loki-example
description: Exercise a synthesized schema-v2 fixture.
type: command
serialization: skill-bundle
hooks: {}
shell: bash
required_skills: []
required_commands: []
---

# loki-example

## Input

Fixture input.

## Execution

Read `references/execution.md` fully.

## Response

Read `references/response.md` and use `assets/response-template.md`.
""",
    )
    write_text(bundle / "references" / "execution.md", "# Contract\n\n## Execution\n")
    write_text(
        bundle / "references" / "response.md",
        "# Contract\n\n## Response\n\nUse `../assets/response-template.md`.\n",
    )
    write_text(bundle / "assets" / "response-template.md", "# Result\n")
    scopes = {
        "schema_version": 2,
        "profiles": {
            "all": ["both", "consumer-only", "internal-only"],
            "consumer": ["both", "consumer-only"],
            "package-source": ["both", "internal-only"],
        },
        "artifact_identity_policy": {
            "skills/loki-*/SKILL.md": {
                "operational_role": "command",
                "serialization": "skill-bundle",
                "required_resources": [
                    "references/execution.md",
                    "references/response.md",
                    "assets/response-template.md",
                ],
            }
        },
        "artifacts": {
            "skills": {"loki-example": "both"},
            "agents": {},
            "codex_agents": {},
        },
    }
    write_text(package_root / "install-scopes.json", json.dumps(scopes, indent=2) + "\n")
    return package_root


def manifest_entry(origin: Path, destination: Path) -> dict[str, str]:
    return {
        "origin": str(origin),
        "destination": str(destination),
        "type": "command",
        "source_kind": "file",
        "install_scope": "both",
        "status": "created",
    }


def build_legacy_fixture(fixture_root: Path, case: str) -> LegacyFixture:
    case_root = (fixture_root / case).resolve()
    destination_root = (case_root / "consumer").resolve()
    previous_package_root = (case_root / "old-package").resolve()
    command_name = "loki-example.md"
    recorded_origin = previous_package_root / "commands" / command_name
    legacy_destination = destination_root / LEGACY_COMMAND_RELATIVE_DIR / command_name
    manifest_path = destination_root / MANIFEST_RELATIVE_PATH

    if case not in {"broken", "origin-outside"}:
        write_text(recorded_origin, "legacy command\n")
    if case == "origin-outside":
        recorded_origin = case_root / "external" / command_name
        write_text(recorded_origin, "external command\n")

    legacy_destination.parent.mkdir(parents=True, exist_ok=True)
    links = [manifest_entry(recorded_origin, legacy_destination)]

    if case in {"absolute", "broken", "flags", "idempotent", "atomic"}:
        os.symlink(recorded_origin, legacy_destination)
    elif case == "relative":
        os.symlink(
            os.path.relpath(recorded_origin, legacy_destination.parent),
            legacy_destination,
        )
    elif case == "divergent":
        other = case_root / "other-package" / "commands" / command_name
        write_text(other, "different\n")
        os.symlink(other, legacy_destination)
    elif case == "orphan":
        links = []
        os.symlink(recorded_origin, legacy_destination)
    elif case == "real-file":
        write_text(legacy_destination, "consumer owned\n")
    elif case == "empty-directory":
        legacy_destination.mkdir()
    elif case == "non-empty-directory":
        write_text(legacy_destination / "keep.txt", "consumer owned\n")
    elif case == "parent-symlink":
        legacy_destination.parent.rmdir()
        legacy_destination.parent.parent.rmdir()
        outside = case_root / "outside-commands"
        (outside / "loki").mkdir(parents=True)
        os.symlink(outside, legacy_destination.parent.parent)
        os.symlink(recorded_origin, legacy_destination)
    elif case == "traversal":
        traversal = destination_root / ".agents" / "commands" / "loki" / ".." / command_name
        links = [manifest_entry(recorded_origin, traversal)]
    elif case == "origin-outside":
        os.symlink(recorded_origin, legacy_destination)
    elif case == "no-manifest":
        os.symlink(recorded_origin, legacy_destination)
    else:
        raise ValueError(f"unknown case: {case}")

    if case != "no-manifest":
        manifest = {
            "package_root": str(previous_package_root),
            "dest_root": str(destination_root),
            "created_at": "2026-07-15T00:00:00Z",
            "mode": "apply",
            "replace": False,
            "install_profile": "consumer",
            "install_scope": ["both", "consumer-only"],
            "links": links,
        }
        write_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    return LegacyFixture(
        case=case,
        destination_root=destination_root,
        previous_package_root=previous_package_root,
        manifest_path=manifest_path,
        legacy_destination=legacy_destination,
        recorded_origin=recorded_origin,
    )


def load_installer_module():
    spec = importlib.util.spec_from_file_location("loki_installer_under_test", INSTALLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load installer module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_scope_validator_module():
    spec = importlib.util.spec_from_file_location(
        "loki_scope_validator_under_test", SCOPE_VALIDATOR
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scope validator module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_managed_previous_inventory(destination: Path) -> Path:
    destination = destination.resolve(strict=False)
    preview = run_installer(destination, "consumer", "--dry-run")
    if preview.returncode != 0:
        raise AssertionError(preview.stderr or preview.stdout)
    applied = run_installer(destination, "consumer", "--yes")
    if applied.returncode != 0:
        raise AssertionError(applied.stderr or applied.stdout)
    manifest_path = destination / MANIFEST_RELATIVE_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    retained = []
    for entry in manifest["links"]:
        name = Path(entry["destination"]).name
        if name in CURRENT_REPLACEMENTS:
            Path(entry["destination"]).unlink()
        else:
            retained.append(entry)
    for name in RETIRED_SKILLS:
        # The retired package sources are intentionally absent after the
        # current-only cutover. The managed legacy destination is synthetic
        # fixture state under ``destination``; its recorded origin remains the
        # lexical former package locator so upgrade ownership can be tested
        # without recreating a normative compatibility artifact.
        source = (PACKAGE_ROOT / "skills" / name).resolve(strict=False)
        destination_path = destination / ".agents" / "skills" / name
        os.symlink(source, destination_path, target_is_directory=True)
        retained.append(
            {
                "origin": str(source),
                "destination": str(destination_path.absolute()),
                "type": "skill",
                "source_kind": "directory",
                "install_scope": "both",
                "status": "created",
            }
        )
    manifest["links"] = retained
    write_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest_path


class ProfileAndSchemaTests(unittest.TestCase):
    def test_all_profile_dry_runs_have_final_counts_and_zero_commands(self) -> None:
        for profile, expected in FINAL_COUNTS.items():
            with self.subTest(profile=profile), tempfile.TemporaryDirectory(
                prefix=f"loki-profile-{profile}-"
            ) as raw_temp:
                destination = Path(raw_temp) / "consumer"
                result = run_installer(destination, profile, "--dry-run")
                self.assertEqual(0, result.returncode, result.stderr or result.stdout)
                counts = planned_type_counts(result.stdout)
                self.assertEqual(Counter(expected), counts, result.stdout)
                self.assertEqual(FINAL_TOTALS[profile], sum(counts.values()))
                self.assertNotIn("type=command ", result.stdout)
                self.assertNotIn("/.agents/commands/", result.stdout)
                self.assertFalse(destination.exists(), "dry-run wrote destination")

    def test_clean_apply_manifest_contains_only_managed_final_links(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-clean-apply-") as raw_temp:
            destination = Path(raw_temp) / "consumer"
            result = run_installer(destination, "consumer", "--yes")
            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            manifest = json.loads(
                (destination / MANIFEST_RELATIVE_PATH).read_text(encoding="utf-8")
            )
            self.assertEqual(FINAL_TOTALS["consumer"], len(manifest["links"]))
            self.assertNotIn("removed_legacy_links", manifest)
            self.assertNotIn("command", {entry["type"] for entry in manifest["links"]})
            self.assertFalse((destination / ".agents" / "commands").exists())

    def test_schema_v2_fixture_passes_explicit_validator_mode(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-schema-v2-") as raw_temp:
            fixture = build_schema_v2_fixture(Path(raw_temp))
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCOPE_VALIDATOR),
                    "--package-root",
                    str(fixture),
                    "--scope-contract-only",
                ],
                cwd=PACKAGE_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            self.assertIn("schema 2 fixture contract", result.stdout)

            skill_path = fixture / "skills" / "loki-example" / "SKILL.md"
            incompatible = skill_path.read_text(encoding="utf-8").replace(
                "hooks: {}\nshell: bash",
                "hooks: []\nshell: {}",
            )
            write_text(skill_path, incompatible)
            rejected = subprocess.run(
                [
                    sys.executable,
                    str(SCOPE_VALIDATOR),
                    "--package-root",
                    str(fixture),
                    "--scope-contract-only",
                ],
                cwd=PACKAGE_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, rejected.returncode, rejected.stdout)
            self.assertIn("hooks=[]; expected {}", rejected.stderr)
            self.assertIn("shell={}; expected bash", rejected.stderr)

    def test_schema_v2_installer_config_has_no_commands_surface(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-schema-v2-reader-") as raw_temp:
            fixture = build_schema_v2_fixture(Path(raw_temp))
            module = load_installer_module()
            config = module.read_install_scopes(fixture)
            self.assertEqual(2, config.schema_version)
            self.assertFalse(hasattr(config, "commands"))

    def test_real_inline_dependency_lists_preserve_self_healing_counts(self) -> None:
        module = load_scope_validator_module()
        self_healing = PACKAGE_ROOT / "skills" / "loki-self-healing" / "SKILL.md"
        self.assertEqual(
            [
                "lf-command-input-interview",
                "lf-framework-impact-audit",
                "lf-command-creator",
                "lf-skill-creator",
                "lf-agent-creator",
            ],
            module.parse_required_skills(self_healing),
        )
        self.assertEqual([], module.parse_required_commands(self_healing))

    def test_yaml_list_parser_supports_quoted_multiline_and_rejects_malformed(self) -> None:
        module = load_scope_validator_module()
        with tempfile.TemporaryDirectory(prefix="loki-list-parser-") as raw_temp:
            fixture = Path(raw_temp) / "SKILL.md"
            write_text(
                fixture,
                """---
required_skills:
  - "lf-one"
  - 'lf,two'
required_commands: []
---
""",
            )
            self.assertEqual(
                ["lf-one", "lf,two"], module.parse_required_skills(fixture)
            )
            self.assertEqual([], module.parse_required_commands(fixture))
            write_text(
                fixture,
                """---
required_skills: [lf-one,,lf-two]
required_commands: []
---
""",
            )
            with self.assertRaises(ValueError):
                module.parse_required_skills(fixture)

    def test_schema_v2_inline_missing_dependency_cannot_bypass_closure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-schema-v2-closure-") as raw_temp:
            fixture = build_schema_v2_fixture(Path(raw_temp))
            skill_path = fixture / "skills" / "loki-example" / "SKILL.md"
            text = skill_path.read_text(encoding="utf-8").replace(
                "required_commands: []",
                "required_commands: [loki-missing]",
            )
            write_text(skill_path, text)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCOPE_VALIDATOR),
                    "--package-root",
                    str(fixture),
                    "--scope-contract-only",
                ],
                cwd=PACKAGE_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, result.returncode, result.stdout)
            self.assertIn("required command loki-missing is not installed", result.stderr)


class ManagedInventoryUpgradeTests(unittest.TestCase):
    def test_managed_upgrade_removes_only_retired_links_and_publishes_final_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-managed-upgrade-") as raw_temp:
            destination = Path(raw_temp) / "consumer"
            manifest_path = build_managed_previous_inventory(destination)
            before = manifest_path.read_bytes()
            preview = run_installer(destination, "consumer", "--dry-run")
            self.assertEqual(0, preview.returncode, preview.stderr or preview.stdout)
            self.assertEqual(3, preview.stdout.count("status=would-remove"))
            self.assertEqual(before, manifest_path.read_bytes())
            result = run_installer(destination, "consumer", "--yes")
            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            for name in RETIRED_SKILLS:
                self.assertFalse((destination / ".agents" / "skills" / name).exists())
                self.assertFalse((destination / ".agents" / "skills" / name).is_symlink())
            for name in CURRENT_REPLACEMENTS:
                target = destination / ".agents" / "skills" / name
                self.assertTrue(target.is_symlink())
                self.assertEqual((PACKAGE_ROOT / "skills" / name).resolve(), target.resolve())
            final_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(FINAL_TOTALS["consumer"], len(final_manifest["links"]))
            destinations = {Path(entry["destination"]).name for entry in final_manifest["links"]}
            self.assertTrue(set(CURRENT_REPLACEMENTS) <= destinations)
            self.assertTrue(set(RETIRED_SKILLS).isdisjoint(destinations))
            self.assertEqual([], list(manifest_path.parent.glob("*.tmp")))

    def test_publish_fault_restores_prior_manifest_and_managed_topology(self) -> None:
        module = load_installer_module()
        with tempfile.TemporaryDirectory(prefix="loki-managed-fault-") as raw_temp:
            destination = Path(raw_temp) / "consumer"
            manifest_path = build_managed_previous_inventory(destination)
            previous = manifest_path.read_bytes()
            preview = run_installer(destination, "consumer", "--dry-run")
            self.assertEqual(0, preview.returncode, preview.stderr or preview.stdout)
            with mock.patch.object(
                module,
                "publish_staged_manifest",
                side_effect=module.InstallError("injected publication fault"),
            ):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    result = module.run(["--dest", str(destination), "--profile", "consumer", "--yes"])
            self.assertEqual(1, result)
            self.assertEqual(previous, manifest_path.read_bytes())
            for name in RETIRED_SKILLS:
                self.assertTrue((destination / ".agents" / "skills" / name).is_symlink())
            for name in CURRENT_REPLACEMENTS:
                self.assertFalse((destination / ".agents" / "skills" / name).exists())
                self.assertFalse((destination / ".agents" / "skills" / name).is_symlink())
            self.assertEqual([], list(manifest_path.parent.glob("*.tmp")))

    def test_divergent_managed_and_unmanaged_new_targets_are_refused(self) -> None:
        for case in ("divergent-managed", "unmanaged-new"):
            with self.subTest(case=case), tempfile.TemporaryDirectory(
                prefix=f"loki-managed-refusal-{case}-"
            ) as raw_temp:
                destination = Path(raw_temp) / "consumer"
                manifest_path = build_managed_previous_inventory(destination)
                before_manifest = manifest_path.read_bytes()
                if case == "divergent-managed":
                    target = destination / ".agents" / "skills" / RETIRED_SKILLS[0]
                    target.unlink()
                else:
                    target = destination / ".agents" / "skills" / CURRENT_REPLACEMENTS[0]
                outside = Path(raw_temp) / "outside"
                outside.mkdir()
                os.symlink(outside, target, target_is_directory=True)
                before_target = os.readlink(target)
                preview = run_installer(destination, "consumer", "--dry-run", "--replace")
                self.assertNotEqual(0, preview.returncode)
                result = run_installer(destination, "consumer", "--yes", "--replace")
                self.assertNotEqual(0, result.returncode)
                self.assertEqual(before_manifest, manifest_path.read_bytes())
                self.assertEqual(before_target, os.readlink(target))
                self.assertEqual([], list(manifest_path.parent.glob("*.tmp")))


class LegacyLayoutRejectionTests(unittest.TestCase):
    def test_cleanup_flag_is_not_a_cli_option(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-no-cleanup-flag-") as raw_temp:
            result = run_installer(
                Path(raw_temp) / "consumer",
                "consumer",
                "--dry-run",
                "--cleanup-legacy-commands",
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("unrecognized arguments: --cleanup-legacy-commands", result.stderr)

    def test_command_tree_is_rejected_without_writes(self) -> None:
        for case in ("absolute", "relative", "broken", "real-file", "non-empty-directory"):
            with self.subTest(case=case), tempfile.TemporaryDirectory(
                prefix=f"loki-reject-command-tree-{case}-"
            ) as raw_temp:
                fixture = build_legacy_fixture(Path(raw_temp), case)
                before_manifest = fixture.manifest_path.read_bytes()
                before_destination = (
                    os.readlink(fixture.legacy_destination)
                    if fixture.legacy_destination.is_symlink()
                    else None
                )
                result = run_installer(
                    fixture.destination_root, "consumer", "--yes", "--replace"
                )
                self.assertEqual(1, result.returncode, result.stderr or result.stdout)
                self.assertIn("legacy command tree detected", result.stderr)
                self.assertEqual(before_manifest, fixture.manifest_path.read_bytes())
                if before_destination is not None:
                    self.assertEqual(before_destination, os.readlink(fixture.legacy_destination))
                self.assertFalse((fixture.destination_root / ".agents" / "skills").exists())

    def test_legacy_skill_file_symlink_is_rejected_even_with_replace(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-reject-skill-file-") as raw_temp:
            destination = Path(raw_temp) / "consumer"
            source = PACKAGE_ROOT / "skills" / "loki-implement-feature" / "SKILL.md"
            legacy = destination / ".agents" / "skills" / "loki-implement-feature" / "SKILL.md"
            legacy.parent.mkdir(parents=True)
            os.symlink(source, legacy)
            before = os.readlink(legacy)
            result = run_installer(destination, "consumer", "--yes", "--replace")
            self.assertEqual(2, result.returncode, result.stderr or result.stdout)
            self.assertIn("legacy skill-file symlink exists", result.stdout)
            self.assertEqual(before, os.readlink(legacy))
            self.assertFalse((destination / MANIFEST_RELATIVE_PATH).exists())

    def test_parent_symlink_is_rejected_without_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-reject-parent-symlink-") as raw_temp:
            destination = Path(raw_temp) / "consumer"
            outside = Path(raw_temp) / "outside"
            outside.mkdir()
            destination.mkdir()
            os.symlink(outside, destination / ".agents")
            result = run_installer(destination, "consumer", "--yes", "--replace")
            self.assertEqual(2, result.returncode, result.stderr or result.stdout)
            self.assertIn("parent path is a symlink", result.stdout)
            self.assertTrue((destination / ".agents").is_symlink())
            self.assertEqual([], list(outside.iterdir()))

    def test_legacy_manifest_is_rejected_without_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-reject-manifest-") as raw_temp:
            destination = Path(raw_temp) / "consumer"
            manifest_path = destination / MANIFEST_RELATIVE_PATH
            manifest = {
                "install_profile": "consumer",
                "links": [{"type": "command", "destination": "/consumer/.agents/commands/loki/x.md"}],
                "removed_legacy_links": [],
            }
            write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
            before = manifest_path.read_bytes()
            result = run_installer(destination, "consumer", "--yes", "--replace")
            self.assertEqual(1, result.returncode, result.stderr or result.stdout)
            self.assertIn("legacy installation manifest contains command links", result.stderr)
            self.assertEqual(before, manifest_path.read_bytes())

    def test_legacy_manifest_cleanup_history_is_rejected_without_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-reject-manifest-history-") as raw_temp:
            destination = Path(raw_temp) / "consumer"
            manifest_path = destination / MANIFEST_RELATIVE_PATH
            manifest = {
                "install_profile": "consumer",
                "links": [],
                "removed_legacy_links": [],
            }
            write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
            before = manifest_path.read_bytes()
            result = run_installer(destination, "consumer", "--yes", "--replace")
            self.assertEqual(1, result.returncode, result.stderr or result.stdout)
            self.assertIn("legacy installation manifest contains cleanup history", result.stderr)
            self.assertEqual(before, manifest_path.read_bytes())

    def test_atomic_manifest_replace_failure_preserves_previous_bytes(self) -> None:
        module = load_installer_module()
        with tempfile.TemporaryDirectory(prefix="loki-manifest-atomic-") as raw_temp:
            destination = Path(raw_temp).resolve()
            manifest_path = destination / MANIFEST_RELATIVE_PATH
            previous = b'{"install_profile": "consumer", "links": []}\n'
            write_text(manifest_path, previous.decode("utf-8"))
            with mock.patch.object(module.os, "replace", side_effect=OSError("simulated")):
                with self.assertRaises(module.InstallError):
                    module.write_manifest(
                        destination,
                        PACKAGE_ROOT,
                        False,
                        "consumer",
                        [],
                    )
            self.assertEqual(previous, manifest_path.read_bytes())
            self.assertEqual([], list(manifest_path.parent.glob("*.tmp")))

    def test_claude_legacy_real_file_is_never_touched(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loki-claude-preserve-") as raw_temp:
            destination = Path(raw_temp) / "consumer"
            claude_file = destination / ".claude" / "commands" / "loki" / "loki-example.md"
            write_text(claude_file, "consumer owned\n")
            result = run_installer(destination, "consumer", "--yes")
            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            self.assertEqual("consumer owned\n", claude_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
