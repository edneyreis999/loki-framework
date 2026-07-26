#!/usr/bin/env python3
"""Validate the generated RPG Maker MZ plugins.js envelope without executing it."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


class EnvelopeError(ValueError):
    """Raised when plugins.js is outside the accepted generated envelope."""


def _skip_trivia(text: str, start: int) -> int:
    """Skip whitespace and JavaScript comments outside the JSON payload."""

    index = start
    length = len(text)
    while index < length:
        if text[index].isspace():
            index += 1
            continue
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            index = length if newline < 0 else newline + 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                raise EnvelopeError("unterminated block comment")
            index = end + 2
            continue
        break
    return index


def _skip_whitespace(text: str, start: int) -> int:
    """Skip whitespace where comments are forbidden inside the declaration."""

    index = start
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _expect_literal(text: str, index: int, literal: str) -> int:
    if not text.startswith(literal, index):
        raise EnvelopeError(f"expected {literal!r}")
    return index + len(literal)


def _reject_non_json_constant(value: str) -> None:
    raise EnvelopeError(f"non-JSON constant {value!r}")


def _decode_json_payload(
    decoder: json.JSONDecoder, text: str, index: int
) -> tuple[Any, int]:
    """Decode JSON while normalizing parser failures to concise diagnostics."""

    try:
        return decoder.raw_decode(text, index)
    except json.JSONDecodeError as exc:
        raise EnvelopeError(
            f"invalid JSON payload at line {exc.lineno} column {exc.colno}"
        ) from None
    except RecursionError:
        raise EnvelopeError("JSON payload exceeds the parser nesting limit") from None


def parse_plugins_js_envelope(text: str) -> list[dict[str, Any]]:
    """Return the JSON plugin array only for the canonical non-executable shape."""

    index = _skip_trivia(text, 0)
    index = _expect_literal(text, index, "var")
    if index < len(text) and (text[index].isalnum() or text[index] in "_$"):
        raise EnvelopeError("expected keyword boundary after 'var'")

    index = _skip_whitespace(text, index)
    index = _expect_literal(text, index, "$plugins")
    if index < len(text) and (text[index].isalnum() or text[index] in "_$"):
        raise EnvelopeError("expected identifier boundary after '$plugins'")

    index = _skip_whitespace(text, index)
    index = _expect_literal(text, index, "=")
    index = _skip_whitespace(text, index)
    if index >= len(text) or text[index] != "[":
        raise EnvelopeError("expected a JSON array payload")

    decoder = json.JSONDecoder(parse_constant=_reject_non_json_constant)
    payload, index = _decode_json_payload(decoder, text, index)

    if not isinstance(payload, list):
        raise EnvelopeError("payload must be an array")
    if any(not isinstance(plugin, dict) for plugin in payload):
        raise EnvelopeError("payload entries must all be objects")

    index = _skip_whitespace(text, index)
    index = _expect_literal(text, index, ";")
    index = _skip_trivia(text, index)
    if index != len(text):
        raise EnvelopeError("unexpected statement or token outside the declaration")
    return payload


def validate_file(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"plugins.js envelope error: {exc}", file=sys.stderr)
        return 2

    try:
        payload = parse_plugins_js_envelope(text)
    except (EnvelopeError, json.JSONDecodeError, RecursionError) as exc:
        print(f"invalid plugins.js envelope: {exc}", file=sys.stderr)
        return 1

    print(f"editor-structural: valid; plugin_objects={len(payload)}")
    return 0


def self_test() -> None:
    canonical = (
        'var $plugins = [{"name":"Core","status":true,"description":"",'
        '"parameters":{"Mode":"safe"}}];'
    )
    comments = (
        "/* generated */\n// peripheral before\n var $plugins"
        '= [ {"name":"Core","status":false,"description":"","parameters":{}} ] '
        "; // peripheral after\n/* end */\n"
    )
    token_string = (
        'var $plugins = [{"name":"Tokens","status":true,"description":"",'
        '"parameters":{"Text":"; ] $plugins.push({code: true}); '
        'require(\\"fs\\")"}}];'
    )
    cases: list[tuple[str, str, bool]] = [
        ("canonical", canonical, True),
        ("peripheral-comments-and-whitespace", comments, True),
        ("comment-between-var-and-binding", "var /* no */ $plugins = [];", False),
        ("comment-between-binding-and-equals", "var $plugins /* no */ = [];", False),
        ("comment-between-equals-and-payload", "var $plugins = /* no */ [];", False),
        ("comment-between-payload-and-semicolon", "var $plugins = [] /* no */ ;", False),
        ("statement-before", "void 0;\n" + canonical, False),
        ("statement-after", canonical + "\nvoid 0;", False),
        ("push-after", canonical + "\n$plugins.push({});", False),
        ("second-declaration", canonical + "\nvar $plugins = [];", False),
        ("second-assignment", canonical + "\n$plugins = [];", False),
        ("truncated", canonical[:-2], False),
        ("strings-with-tokens", token_string, True),
        ("invalid-payload-syntax", 'var $plugins = [{"name":}];', False),
        ("invalid-payload-entry", 'var $plugins = [null];', False),
    ]

    results: list[str] = []
    for name, source, expected_valid in cases:
        try:
            parse_plugins_js_envelope(source)
        except EnvelopeError:
            actual_valid = False
        else:
            actual_valid = True
        if actual_valid != expected_valid:
            raise AssertionError(
                f"{name}: expected valid={expected_valid}, received valid={actual_valid}"
            )
        results.append(name)

    peripheral_comments = "// peripheral\n" * 1500
    comment_stress = peripheral_comments + canonical + "\n" + peripheral_comments
    first_stress_result = parse_plugins_js_envelope(comment_stress)
    second_stress_result = parse_plugins_js_envelope(comment_stress)
    if first_stress_result != second_stress_result:
        raise AssertionError("peripheral-comment stress result was not deterministic")
    results.append("1500-plus-peripheral-comments-deterministic")

    class RecursionLimitDecoder(json.JSONDecoder):
        def raw_decode(self, text: str, index: int) -> tuple[Any, int]:
            raise RecursionError("synthetic parser limit")

    try:
        _decode_json_payload(RecursionLimitDecoder(), "[]", 0)
    except EnvelopeError as exc:
        if str(exc) != "JSON payload exceeds the parser nesting limit":
            raise AssertionError(f"unexpected nesting-limit diagnostic: {exc}") from None
    except (json.JSONDecodeError, RecursionError) as exc:
        raise AssertionError(f"uncaptured parser limit: {type(exc).__name__}") from None
    else:
        raise AssertionError("nesting-limit fixture was accepted")
    results.append("nesting-limit-concise-diagnostic")

    with tempfile.TemporaryDirectory(prefix="plugins-js-envelope-") as temp_dir:
        marker = Path(temp_dir) / "executed"
        escaped_marker = json.dumps(str(marker))
        executable = (
            f'require("fs").writeFileSync({escaped_marker}, "executed");\n'
            + canonical
        )
        try:
            parse_plugins_js_envelope(executable)
        except EnvelopeError:
            pass
        else:
            raise AssertionError("executable rejection fixture was accepted")
        if marker.exists():
            raise AssertionError("rejection path executed JavaScript")

        code_as_data = "var $plugins = " + json.dumps(
            [
                {
                    "name": "NoExec",
                    "status": True,
                    "description": "",
                    "parameters": {
                        "Code": (
                            f'require("fs").writeFileSync({escaped_marker}, "executed");'
                        )
                    },
                }
            ],
            separators=(",", ":"),
        ) + ";"
        parse_plugins_js_envelope(code_as_data)
        if marker.exists():
            raise AssertionError("JSON extraction executed parameter content")
        results.append("rejection-and-extraction-do-not-execute")

    print(f"self-test passed: {len(results)} case(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugins_js", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        if args.plugins_js is not None:
            parser.error("plugins_js cannot be combined with --self-test")
        try:
            self_test()
        except (AssertionError, EnvelopeError, json.JSONDecodeError, RecursionError) as exc:
            print(f"self-test failed: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.plugins_js is None:
        parser.error("plugins_js is required unless --self-test is used")
    return validate_file(args.plugins_js)


if __name__ == "__main__":
    sys.exit(main())
