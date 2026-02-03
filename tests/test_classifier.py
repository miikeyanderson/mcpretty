#!/usr/bin/env python3
"""
Tests for semantic classifier.

Table-driven tests covering:
- Key classification (primary vs default)
- Value classification with precedence (error > warning > success)
- Diff line classification
- Edge cases and ambiguous inputs
"""

import sys
import os
import importlib.util
import importlib.machinery

# Import from mcp-render (has hyphen, need special loading)
render_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "mcp-render")
loader = importlib.machinery.SourceFileLoader("mcp_render", render_path)
spec = importlib.util.spec_from_loader("mcp_render", loader)
mcp_render = importlib.util.module_from_spec(spec)
sys.modules["mcp_render"] = mcp_render
spec.loader.exec_module(mcp_render)

Role = mcp_render.Role
classify_key = mcp_render.classify_key
classify_value = mcp_render.classify_value
classify_diff_line = mcp_render.classify_diff_line
is_primary_key = mcp_render.is_primary_key
is_error_like = mcp_render.is_error_like
is_warning_like = mcp_render.is_warning_like
is_success_like = mcp_render.is_success_like


# ============================================================================
# Key Classification Tests
# ============================================================================

KEY_TEST_CASES = [
    # (input_key, expected_role, description)
    ("status", Role.KEY_PRIMARY, "primary key: status"),
    ("error", Role.KEY_PRIMARY, "primary key: error"),
    ("result", Role.KEY_PRIMARY, "primary key: result"),
    ("tool", Role.KEY_PRIMARY, "primary key: tool"),
    ("type", Role.KEY_PRIMARY, "primary key: type"),
    ("code", Role.KEY_PRIMARY, "primary key: code"),
    ("message", Role.KEY_PRIMARY, "primary key: message"),
    ("STATUS", Role.KEY_PRIMARY, "case insensitive: STATUS"),
    ("Error", Role.KEY_PRIMARY, "case insensitive: Error"),

    ("name", Role.KEY_DEFAULT, "default key: name"),
    ("description", Role.KEY_DEFAULT, "default key: description"),
    ("id", Role.KEY_DEFAULT, "default key: id"),
    ("timestamp", Role.KEY_DEFAULT, "default key: timestamp"),
    ("", Role.KEY_DEFAULT, "empty string"),
]


def test_key_classification():
    """Test key classification."""
    passed = 0
    failed = 0

    for key, expected, desc in KEY_TEST_CASES:
        result = classify_key(key)
        if result == expected:
            passed += 1
        else:
            print(f"FAIL: {desc}")
            print(f"  Input: {repr(key)}")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")
            failed += 1

    return passed, failed


# ============================================================================
# Value Classification Tests
# ============================================================================

VALUE_TEST_CASES = [
    # (input_value, expected_role, description)

    # Error cases
    ("error", Role.VALUE_STATUS_ERROR, "error keyword"),
    ("Error occurred", Role.VALUE_STATUS_ERROR, "error in sentence"),
    ("failed", Role.VALUE_STATUS_ERROR, "failed keyword"),
    ("FAILED", Role.VALUE_STATUS_ERROR, "FAILED uppercase"),
    ("failure", Role.VALUE_STATUS_ERROR, "failure keyword"),
    ("exception thrown", Role.VALUE_STATUS_ERROR, "exception keyword"),
    ("invalid input", Role.VALUE_STATUS_ERROR, "invalid keyword"),
    ("HTTP 403", Role.VALUE_STATUS_ERROR, "HTTP 403 with prefix"),
    ("status 404", Role.VALUE_STATUS_ERROR, "status 404"),
    ("500 Internal Server Error", Role.VALUE_STATUS_ERROR, "HTTP 500 with message"),
    (False, Role.VALUE_STATUS_ERROR, "boolean False"),
    ("aborted", Role.VALUE_STATUS_ERROR, "aborted keyword"),
    ("crashed", Role.VALUE_STATUS_ERROR, "crashed keyword"),

    # Warning cases
    ("warning", Role.VALUE_STATUS_WARNING, "warning keyword"),
    ("Warning: low memory", Role.VALUE_STATUS_WARNING, "warning in sentence"),
    ("partial", Role.VALUE_STATUS_WARNING, "partial keyword"),
    ("pending", Role.VALUE_STATUS_WARNING, "pending keyword"),
    ("timeout", Role.VALUE_STATUS_WARNING, "timeout keyword"),
    ("deprecated", Role.VALUE_STATUS_WARNING, "deprecated keyword"),
    ("skipped", Role.VALUE_STATUS_WARNING, "skipped keyword"),

    # Success cases
    ("ok", Role.VALUE_STATUS_OK, "ok keyword"),
    ("OK", Role.VALUE_STATUS_OK, "OK uppercase"),
    ("success", Role.VALUE_STATUS_OK, "success keyword"),
    ("completed", Role.VALUE_STATUS_OK, "completed keyword"),
    ("passed", Role.VALUE_STATUS_OK, "passed keyword"),
    ("HTTP 200", Role.VALUE_STATUS_OK, "HTTP 200 with prefix"),
    ("status 201", Role.VALUE_STATUS_OK, "status 201"),
    ("HTTP/1.1 201 Created", Role.VALUE_STATUS_OK, "HTTP 201 with version"),
    (True, Role.VALUE_STATUS_OK, "boolean True"),
    ("ready", Role.VALUE_STATUS_OK, "ready keyword"),
    ("healthy", Role.VALUE_STATUS_OK, "healthy keyword"),

    # Default/text cases - including false positive guards
    ("hello world", Role.VALUE_TEXT, "plain text"),
    ("some random string", Role.VALUE_TEXT, "random string"),
    (123, Role.VALUE_TEXT, "integer"),
    (3.14, Role.VALUE_TEXT, "float"),
    (None, Role.VALUE_TEXT, "None"),
    ("", Role.VALUE_TEXT, "empty string"),
    ("took 500 ms", Role.VALUE_TEXT, "500 ms is metric not error"),
    ("200 items", Role.VALUE_TEXT, "200 items is count not success"),
    ("not good", Role.VALUE_TEXT, "good removed to avoid false positives"),
]


# Precedence test cases (error > warning > success)
PRECEDENCE_TEST_CASES = [
    # (input_value, expected_role, description)
    ("error warning", Role.VALUE_STATUS_ERROR, "error+warning → error wins"),
    ("failed successfully", Role.VALUE_STATUS_ERROR, "failed+success → error wins"),
    ("warning ok", Role.VALUE_STATUS_WARNING, "warning+ok → warning wins"),
    ("warning success", Role.VALUE_STATUS_WARNING, "warning+success → warning wins"),
]


def test_value_classification():
    """Test value classification."""
    passed = 0
    failed = 0

    for value, expected, desc in VALUE_TEST_CASES + PRECEDENCE_TEST_CASES:
        result = classify_value(value)
        if result == expected:
            passed += 1
        else:
            print(f"FAIL: {desc}")
            print(f"  Input: {repr(value)}")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")
            failed += 1

    return passed, failed


# ============================================================================
# Diff Line Classification Tests
# ============================================================================

DIFF_TEST_CASES = [
    # (input_line, expected_role, description)
    ("+added line", Role.DIFF_ADDED, "added line"),
    ("+", Role.DIFF_ADDED, "added empty line"),
    ("-removed line", Role.DIFF_REMOVED, "removed line"),
    ("-", Role.DIFF_REMOVED, "removed empty line"),
    ("@@@ -1,3 +1,4 @@@", Role.DIFF_HEADER, "hunk header"),
    ("@@ -10,5 +10,7 @@", Role.DIFF_HEADER, "standard hunk"),
    ("--- a/file.py", Role.DIFF_HEADER, "file header old"),
    ("+++ b/file.py", Role.DIFF_HEADER, "file header new"),
    (" context line", Role.DIFF_CONTEXT, "context line"),
    ("unchanged", Role.DIFF_CONTEXT, "plain context"),
]


def test_diff_classification():
    """Test diff line classification."""
    passed = 0
    failed = 0

    for line, expected, desc in DIFF_TEST_CASES:
        result = classify_diff_line(line)
        if result == expected:
            passed += 1
        else:
            print(f"FAIL: {desc}")
            print(f"  Input: {repr(line)}")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")
            failed += 1

    return passed, failed


# ============================================================================
# Main
# ============================================================================

def main():
    print("Running classifier tests...")
    print("=" * 40)
    print()

    total_passed = 0
    total_failed = 0

    print("Key classification:")
    p, f = test_key_classification()
    total_passed += p
    total_failed += f
    print(f"  {p} passed, {f} failed")
    print()

    print("Value classification:")
    p, f = test_value_classification()
    total_passed += p
    total_failed += f
    print(f"  {p} passed, {f} failed")
    print()

    print("Diff classification:")
    p, f = test_diff_classification()
    total_passed += p
    total_failed += f
    print(f"  {p} passed, {f} failed")
    print()

    print("=" * 40)
    print(f"Total: {total_passed} passed, {total_failed} failed")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
