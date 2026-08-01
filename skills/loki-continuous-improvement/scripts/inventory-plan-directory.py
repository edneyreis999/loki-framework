#!/usr/bin/env python3
"""Create a deterministic, payload-safe source manifest for one complete plan."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath


SCHEMA_VERSION = "1"
EXCLUDED_NAMESPACE = "continuous-improvement/"
TEXT_SUFFIXES = {
    ".bash", ".cfg", ".conf", ".css", ".csv", ".html", ".ini", ".js",
    ".json", ".jsx", ".markdown", ".md", ".mjs", ".py", ".sh", ".sql", ".toml",
    ".ts", ".tsv", ".tsx", ".txt", ".xml", ".yaml", ".yml", ".zsh",
}
SENSITIVE_NAME_RE = re.compile(
    r"(^|[._-])(secret|secrets|credential|credentials|private[-_]?key|id_rsa|id_ed25519)([._-]|$)",
    re.IGNORECASE,
)
MANAGED_MARKER_NAME = "managed-namespace.xml"
MANAGED_MARKER_ROOT = "continuous_improvement_namespace"
MANAGED_OWNER = "loki-continuous-improvement"
RUN_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


class InventoryError(ValueError):
    """Closed failure for an unsafe or invalid plan inventory."""


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _normalized_relative(root: Path, path: Path) -> str:
    relative = path.relative_to(root).as_posix()
    normalized = PurePosixPath(relative).as_posix()
    if normalized in {"", "."} or normalized.startswith("../") or "/../" in normalized:
        raise InventoryError("path escapes the complete plan root")
    return normalized


def _initial_family(path: Path, payload: bytes) -> tuple[str, str]:
    name = path.name
    if name == ".env" or SENSITIVE_NAME_RE.search(name):
        return "blocked", "sensitive-name"
    if b"\x00" in payload:
        return "blocked", "binary-nul"
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return "blocked", "unknown-schema"
    try:
        payload.decode("utf-8")
    except UnicodeDecodeError:
        return "blocked", "invalid-utf8"
    return "recognized-text", "eligible"


def _validate_run_id(run_id: str) -> str:
    if not RUN_ID_RE.fullmatch(run_id):
        raise InventoryError("run_id must be one safe ASCII path segment")
    if unicodedata.normalize("NFKC", run_id) != run_id or run_id in {".", ".."}:
        raise InventoryError("run_id must be one safe ASCII path segment")
    if Path(run_id).is_absolute() or len(Path(run_id).parts) != 1 or "/" in run_id or "\\" in run_id:
        raise InventoryError("run_id must be one safe ASCII path segment")
    return run_id


def _marker_bytes() -> bytes:
    marker = ET.Element(
        MANAGED_MARKER_ROOT,
        {"schema_version": SCHEMA_VERSION, "owner": MANAGED_OWNER},
    )
    return canonical_xml(marker)


def _validate_marker(marker_path: Path) -> None:
    if marker_path.is_symlink() or not marker_path.is_file():
        raise InventoryError("managed-namespace-marker-invalid")
    try:
        marker = ET.parse(marker_path).getroot()
    except (OSError, ET.ParseError) as error:
        raise InventoryError("managed-namespace-marker-invalid") from error
    if (
        marker.tag != MANAGED_MARKER_ROOT
        or marker.attrib != {"schema_version": SCHEMA_VERSION, "owner": MANAGED_OWNER}
        or list(marker)
        or (marker.text or "").strip()
    ):
        raise InventoryError("managed-namespace-marker-invalid")


def _validate_managed_namespace(plan_root: Path) -> str:
    namespace = plan_root / "continuous-improvement"
    if not namespace.exists():
        return "absent"
    if namespace.is_symlink() or not namespace.is_dir():
        raise InventoryError("managed-namespace-collision")
    children = sorted(item.name for item in namespace.iterdir())
    if MANAGED_MARKER_NAME not in children or any(
        child not in {MANAGED_MARKER_NAME, "runs"} for child in children
    ):
        raise InventoryError("managed-namespace-collision")
    _validate_marker(namespace / MANAGED_MARKER_NAME)
    runs = namespace / "runs"
    if runs.exists() and (runs.is_symlink() or not runs.is_dir()):
        raise InventoryError("managed-namespace-collision")
    return "managed"


def _resolve_run_output(plan_root: Path, run_id: str) -> tuple[Path, Path]:
    safe_run_id = _validate_run_id(run_id)
    runs = (plan_root / "continuous-improvement" / "runs").resolve(strict=False)
    lexical_run_directory = runs / safe_run_id
    if lexical_run_directory.is_symlink():
        raise InventoryError("selected run directory must not be a symlink")
    run_directory = lexical_run_directory.resolve(strict=False)
    output = (run_directory / "source-manifest.xml").resolve(strict=False)
    try:
        run_directory.relative_to(runs)
    except ValueError as error:
        raise InventoryError("run output escapes the managed runs root") from error
    if run_directory.parent != runs or output.parent != run_directory:
        raise InventoryError("run output escapes the managed runs root")
    return run_directory, output


def _ensure_managed_namespace(plan_root: Path) -> None:
    namespace = plan_root / "continuous-improvement"
    state = _validate_managed_namespace(plan_root)
    if state == "managed":
        return
    namespace.mkdir()
    marker = namespace / MANAGED_MARKER_NAME
    temporary = namespace / f".{MANAGED_MARKER_NAME}.tmp"
    temporary.write_bytes(_marker_bytes())
    ET.parse(temporary)
    os.replace(temporary, marker)
    _validate_managed_namespace(plan_root)


def inventory(plan_directory: Path, run_id: str) -> ET.Element:
    run_id = _validate_run_id(run_id)
    if plan_directory.is_symlink():
        raise InventoryError("plan_directory must not be a symlink")
    root = plan_directory.resolve(strict=True)
    if not root.is_dir():
        raise InventoryError("plan_directory must be a readable directory")
    _validate_managed_namespace(root)

    records: list[dict[str, object]] = []
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        directories.sort()
        files.sort()
        if current_path == root:
            directories[:] = [name for name in directories if name != "continuous-improvement"]
        for directory in directories:
            candidate = current_path / directory
            if candidate.is_symlink():
                raise InventoryError(f"symlink source is forbidden: {_normalized_relative(root, candidate)}")
        for filename in files:
            source = current_path / filename
            if source.is_symlink():
                raise InventoryError(f"symlink source is forbidden: {_normalized_relative(root, source)}")
            if not source.is_file():
                raise InventoryError(f"non-regular source is forbidden: {_normalized_relative(root, source)}")
            payload = source.read_bytes()
            relative = _normalized_relative(root, source)
            family, safety = _initial_family(source, payload)
            records.append(
                {
                    "path": relative,
                    "sha256": _sha256(payload),
                    "size": len(payload),
                    "initial_family": family,
                    "safety": safety,
                }
            )

    records.sort(key=lambda record: str(record["path"]))
    tree_payload = "".join(
        f"{record['path']}\0{record['sha256']}\0{record['size']}\0"
        f"{record['initial_family']}\0{record['safety']}\n"
        for record in records
    ).encode("utf-8")

    document = ET.Element(
        "source_manifest",
        {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "plan_path": root.as_posix(),
            "excluded_namespace": EXCLUDED_NAMESPACE,
            "source_tree_digest": _sha256(tree_payload),
        },
    )
    ET.SubElement(
        document,
        "totals",
        {"discovered_files": str(len(records)), "discovered_bytes": str(sum(int(r["size"]) for r in records))},
    )
    files_element = ET.SubElement(document, "files")
    for record in records:
        ET.SubElement(files_element, "file", {key: str(value) for key, value in record.items()})
    return document


def canonical_xml(element: ET.Element) -> bytes:
    raw = ET.tostring(element, encoding="unicode", short_empty_elements=True)
    canonical = ET.canonicalize(raw, strip_text=True)
    return (canonical + "\n").encode("utf-8")


def _assert_error(callable_object, expected: str) -> None:
    try:
        callable_object()
    except (InventoryError, FileNotFoundError) as error:
        if expected not in str(error):
            raise AssertionError(f"expected {expected!r}, got {error!r}") from error
    else:
        raise AssertionError(f"expected failure containing {expected!r}")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "plan"
        root.mkdir()
        (root / "analysis.md").write_text("approved analysis\n", encoding="utf-8")
        (root / "copy.md").write_text("approved analysis\n", encoding="utf-8")
        (root / "empty.txt").write_bytes(b"")
        (root / "module.mjs").write_text("export const approved = true;\n", encoding="utf-8")
        (root / "payload.bin").write_bytes(b"safe?\x00no")
        (root / "credentials.txt").write_text("redacted", encoding="utf-8")
        namespace = root / "continuous-improvement"
        namespace.mkdir()
        (namespace / MANAGED_MARKER_NAME).write_bytes(_marker_bytes())
        managed = namespace / "runs" / "run-old"
        managed.mkdir(parents=True)
        (managed / "run-state.xml").write_text("<ignored/>", encoding="utf-8")

        first = inventory(root, "run-test")
        second = inventory(root, "run-test")
        assert canonical_xml(first) == canonical_xml(second)
        files = first.findall("./files/file")
        assert [item.get("path") for item in files] == sorted(item.get("path") for item in files)
        assert all(not item.get("path", "").startswith(EXCLUDED_NAMESPACE) for item in files)
        by_path = {item.get("path"): item for item in files}
        assert by_path["analysis.md"].get("sha256") == by_path["copy.md"].get("sha256")
        assert by_path["analysis.md"].get("size") == by_path["copy.md"].get("size")
        assert by_path["empty.txt"].get("initial_family") == "recognized-text"
        assert by_path["module.mjs"].get("initial_family") == "recognized-text"
        assert by_path["module.mjs"].get("safety") == "eligible"
        assert by_path["payload.bin"].get("safety") == "binary-nul"
        assert by_path["credentials.txt"].get("safety") == "sensitive-name"
        ET.fromstring(canonical_xml(first))

        symlink_root = Path(temporary) / "symlink-plan"
        symlink_root.mkdir()
        (symlink_root / "real.md").write_text("x", encoding="utf-8")
        (symlink_root / "link.md").symlink_to(symlink_root / "real.md")
        _assert_error(lambda: inventory(symlink_root, "run"), "symlink source")

        collision_root = Path(temporary) / "collision-plan"
        collision_root.mkdir()
        (collision_root / "continuous-improvement").write_text("unmanaged", encoding="utf-8")
        _assert_error(lambda: inventory(collision_root, "run"), "managed-namespace-collision")

        unmanaged_child = Path(temporary) / "unmanaged-child"
        unmanaged_child.mkdir()
        (unmanaged_child / "continuous-improvement").mkdir()
        (unmanaged_child / "continuous-improvement" / "notes.md").write_text("x", encoding="utf-8")
        _assert_error(lambda: inventory(unmanaged_child, "run"), "managed-namespace-collision")

        empty_namespace = Path(temporary) / "empty-namespace"
        empty_namespace.mkdir()
        (empty_namespace / "continuous-improvement").mkdir()
        _assert_error(lambda: inventory(empty_namespace, "run"), "managed-namespace-collision")

        runs_only = Path(temporary) / "runs-only"
        runs_only.mkdir()
        (runs_only / "continuous-improvement" / "runs").mkdir(parents=True)
        _assert_error(lambda: inventory(runs_only, "run"), "managed-namespace-collision")

        foreign_tree = Path(temporary) / "foreign-tree"
        foreign_tree.mkdir()
        foreign_run = foreign_tree / "continuous-improvement" / "runs" / "foreign"
        foreign_run.mkdir(parents=True)
        (foreign_run / "foreign.txt").write_text("foreign", encoding="utf-8")
        _assert_error(lambda: inventory(foreign_tree, "run"), "managed-namespace-collision")

        invalid_marker = Path(temporary) / "invalid-marker"
        invalid_marker.mkdir()
        (invalid_marker / "continuous-improvement").mkdir()
        (invalid_marker / "continuous-improvement" / MANAGED_MARKER_NAME).write_text(
            '<continuous_improvement_namespace schema_version="9" owner="foreign"/>',
            encoding="utf-8",
        )
        _assert_error(lambda: inventory(invalid_marker, "run"), "managed-namespace-marker-invalid")

        for unsafe_id in ("", ".", "..", "/tmp/escape", "../escape", "a/b", "a\\b", "é", "．"):
            _assert_error(lambda value=unsafe_id: inventory(root, value), "run_id")

        fresh = Path(temporary) / "fresh-plan"
        fresh.mkdir()
        (fresh / "source.md").write_text("source", encoding="utf-8")
        run_directory, output = _resolve_run_output(fresh.resolve(), "run-safe")
        assert run_directory.parent == (fresh / "continuous-improvement" / "runs").resolve(strict=False)
        assert output.parent == run_directory
        _ensure_managed_namespace(fresh.resolve())
        assert inventory(fresh, "run-safe").get("run_id") == "run-safe"

        symlink_runs = fresh / "continuous-improvement" / "runs"
        symlink_runs.mkdir()
        internal_target = symlink_runs / "internal-target"
        internal_target.mkdir()
        (symlink_runs / "internal-alias").symlink_to(internal_target, target_is_directory=True)
        _assert_error(
            lambda: _resolve_run_output(fresh.resolve(), "internal-alias"),
            "selected run directory must not be a symlink",
        )
        external_target = Path(temporary) / "external-run"
        external_target.mkdir()
        (symlink_runs / "external-alias").symlink_to(external_target, target_is_directory=True)
        _assert_error(
            lambda: _resolve_run_output(fresh.resolve(), "external-alias"),
            "selected run directory must not be a symlink",
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-directory", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--output", type=Path, help="Optional manifest path inside the selected run namespace")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print("inventory-plan-directory self-test: pass")
        return 0
    if args.plan_directory is None or args.run_id is None:
        raise InventoryError("--plan-directory and --run-id are required")
    if args.plan_directory.is_symlink():
        raise InventoryError("plan_directory must not be a symlink")
    root = args.plan_directory.resolve(strict=True)
    _validate_run_id(args.run_id)
    _validate_managed_namespace(root)
    allowed_parent, expected_output = _resolve_run_output(root, args.run_id)
    payload = canonical_xml(inventory(root, args.run_id))
    if args.output is None:
        sys.stdout.buffer.write(payload)
        return 0
    output = args.output.resolve(strict=False)
    if output != expected_output:
        raise InventoryError("output must be the selected run's source-manifest.xml")
    _ensure_managed_namespace(root)
    runs = allowed_parent.parent
    runs.mkdir(exist_ok=True)
    allowed_parent.mkdir(exist_ok=True)
    temporary = output.with_suffix(".xml.tmp")
    temporary.write_bytes(payload)
    ET.parse(temporary)
    os.replace(temporary, output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (InventoryError, OSError, ET.ParseError) as error:
        print(f"inventory-plan-directory: blocked: {error}", file=sys.stderr)
        raise SystemExit(2)
