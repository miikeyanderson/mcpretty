#!/bin/bash
# Baseline parity test runner for mcpretty
# Compares current renderer output against golden fixtures

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENDERER="$SCRIPT_DIR/../bin/mcp-render"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"
GOLDEN_DIR="$SCRIPT_DIR/golden"
TEMP_DIR=$(mktemp -d)

trap "rm -rf $TEMP_DIR" EXIT

passed=0
failed=0

echo "Running baseline parity tests..."
echo "================================"
echo ""

for fixture in "$FIXTURES_DIR"/*.json; do
    name=$(basename "$fixture" .json)
    golden="$GOLDEN_DIR/${name}.txt"
    actual="$TEMP_DIR/${name}.txt"

    # Generate current output
    python3 "$RENDERER" "$fixture" > "$actual" 2>&1

    # Compare (strip ANSI for structural comparison)
    golden_stripped=$(cat "$golden" | sed 's/\x1B\[[0-9;]*[mK]//g')
    actual_stripped=$(cat "$actual" | sed 's/\x1B\[[0-9;]*[mK]//g')

    if [ "$golden_stripped" = "$actual_stripped" ]; then
        echo "✓ $name"
        ((passed++))
    else
        echo "✗ $name - output differs"
        echo "  Expected: $(echo "$golden_stripped" | wc -l | tr -d ' ') lines"
        echo "  Got:      $(echo "$actual_stripped" | wc -l | tr -d ' ') lines"
        ((failed++))
    fi
done

echo ""
echo "================================"
echo "Passed: $passed, Failed: $failed"

if [ $failed -gt 0 ]; then
    exit 1
fi
