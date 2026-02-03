# MCP Render Technical Reference

## Hook Configuration

The PostToolUse hook in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__(codex|gemini-bridge)__.*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${HOME}/.claude/hooks/render-mcp-output.py"
          }
        ]
      }
    ]
  }
}
```

## Schema v1.3 Validation

The hook validates responses before rendering:

```python
def is_schema_v1_3(data: Any) -> bool:
    # Must be dict
    if not isinstance(data, dict):
        return False

    # Version must start with "1."
    version = data.get("version", "")
    if not version.startswith("1."):
        return False

    # Must have metadata dict
    if "metadata" not in data or not isinstance(data.get("metadata"), dict):
        return False

    # Must have content array OR raw_text/formatted fallback
    has_content = isinstance(data.get("content"), list)
    has_fallback = "raw_text" in data or "formatted" in data

    return has_content or has_fallback
```

## Content Types

The renderer handles various content block types:

| Type | Description | Rendered As |
|------|-------------|-------------|
| `text` | Plain text | Styled text with optional emphasis |
| `code` | Code block | Syntax-highlighted box |
| `list` | Bullet/numbered list | Tree structure with icons |
| `table` | Tabular data | Box-drawn table |
| `callout` | Info/warning/error | Colored box with icon |
| `heading` | Section header | Bold underlined text |
| `tree` | Hierarchical data | Tree connectors |

## ANSI Color Palette

```
Standard:     Black Red Green Yellow Blue Magenta Cyan White
Bright:       90-97 (bright variants)
Styles:       Bold(1) Dim(2) Italic(3) Underline(4) Strikethrough(9)
Reset:        0
```

## Box Drawing Characters

```
Rounded:  ╭ ╮ ╰ ╯
Sharp:    ┌ ┐ └ ┘
Lines:    ─ │
Joints:   ├ ┤ ┬ ┴ ┼
Double:   ═ ╞ ╡ ╪
```

## Tree Characters

```
Branch:   ├──
Last:     └──
Pipe:     │
```

## Layout Constants

```python
TREE_INDENT = 4          # Base indent for tree structure
CONNECTOR_WIDTH = 4      # Width of connector column (e.g., "├── ")
BODY_INDENT = 4          # Additional indent for wrapped body text
MIN_CONTENT_WIDTH = 20   # Minimum usable width
RESPONSIVE_THRESHOLD = 60 # Auto-switch to responsive mode
RENDER_TIMEOUT = 5       # Seconds before timeout
```

## Display Width Calculation

The renderer handles Unicode character widths:
- CJK characters: width 2
- Emoji: width 2
- Control characters: width 0
- Standard ASCII: width 1

Uses `wcwidth` library if available for accurate calculation.

## Error Handling

All errors fall back gracefully:
1. Non-JSON response: pass through unchanged
2. Non-v1.3 schema: pass through unchanged
3. Render timeout: use original JSON
4. Render failure: use original JSON

Errors are logged to `~/.claude/logs/mcp-render-hook.log`.

## Hook Response Format

Successful render returns:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "updatedMCPToolOutput": "<ANSI formatted string>"
  }
}
```

Pass-through returns empty object: `{}`
