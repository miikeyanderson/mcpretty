#!/usr/bin/env python3
"""
MCP Output Renderer Hook

PostToolUse hook that pipes MCP tool responses through mcp-render
for beautiful ANSI-formatted terminal output.

Only processes responses matching schema v1.3 format.
Falls back to original output on any error.
"""

import sys
import json
import subprocess
import os
from datetime import datetime
from typing import Any

# Configuration
MCP_RENDER_PATH = os.path.expanduser("~/.claude/bin/mcp-render")
LOG_FILE = os.path.expanduser("~/.claude/logs/mcp-render-hook.log")
RENDER_TIMEOUT = 5  # seconds


def log(message: str) -> None:
    """Append timestamped message to log file."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass  # Never fail on logging


def is_schema_v1_3(data: Any) -> bool:
    """
    Validate that data matches MCP response schema v1.3.

    Required fields:
    - version: string starting with "1."
    - metadata: dict
    - content: list OR raw_text/formatted fallback
    """
    if not isinstance(data, dict):
        return False

    version = data.get("version", "")
    if not isinstance(version, str) or not version.startswith("1."):
        return False

    if "metadata" not in data or not isinstance(data.get("metadata"), dict):
        return False

    # Must have either content array or raw_text/formatted fallback
    has_content = isinstance(data.get("content"), list)
    has_fallback = "raw_text" in data or "formatted" in data

    if not has_content and not has_fallback:
        return False

    return True


def render_with_mcp_render(json_str: str) -> str | None:
    """
    Pipe JSON through mcp-render and return ANSI output.
    Returns None on any error.
    """
    if not os.path.exists(MCP_RENDER_PATH):
        log(f"mcp-render not found at {MCP_RENDER_PATH}")
        return None

    try:
        result = subprocess.run(
            ["python3", MCP_RENDER_PATH],
            input=json_str,
            capture_output=True,
            text=True,
            timeout=RENDER_TIMEOUT
        )

        if result.returncode != 0:
            log(f"mcp-render failed with code {result.returncode}: {result.stderr[:200]}")
            return None

        return result.stdout

    except subprocess.TimeoutExpired:
        log(f"mcp-render timed out after {RENDER_TIMEOUT}s")
        return None
    except Exception as e:
        log(f"mcp-render error: {e}")
        return None


def main() -> None:
    try:
        # Read hook input from stdin
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)

        tool_name = input_data.get("tool_name", "unknown")
        tool_response = input_data.get("tool_response")

        # tool_response might be a string (JSON) or already parsed dict
        if isinstance(tool_response, str):
            try:
                response_data = json.loads(tool_response)
                response_json = tool_response
            except json.JSONDecodeError:
                # Not JSON, pass through unchanged
                log(f"{tool_name}: tool_response is not JSON, passing through")
                print("{}")
                sys.exit(0)
        elif isinstance(tool_response, dict):
            response_data = tool_response
            response_json = json.dumps(tool_response)
        else:
            # Unknown format, pass through
            log(f"{tool_name}: tool_response has unexpected type {type(tool_response)}")
            print("{}")
            sys.exit(0)

        # Check if response matches schema v1.3
        if not is_schema_v1_3(response_data):
            # Not a renderable response, pass through unchanged
            # This is normal for many MCP tools - don't log as error
            print("{}")
            sys.exit(0)

        # Render through mcp-render
        rendered = render_with_mcp_render(response_json)

        if rendered is None:
            # Rendering failed, pass through original
            log(f"{tool_name}: rendering failed, using original output")
            print("{}")
            sys.exit(0)

        # Success! Return the rendered output
        hook_response = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "updatedMCPToolOutput": rendered
            }
        }

        print(json.dumps(hook_response))
        log(f"{tool_name}: successfully rendered {len(rendered)} chars")

    except json.JSONDecodeError as e:
        log(f"Failed to parse hook input: {e}")
        print("{}")
    except Exception as e:
        log(f"Unexpected error: {e}")
        print("{}")

    sys.exit(0)


if __name__ == "__main__":
    main()
