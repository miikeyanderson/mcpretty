---
name: mcp-render
description: MCP output rendering system. Loaded when using Codex or Gemini MCP tools. Explains beautiful ANSI-formatted terminal output that replaces raw JSON.
disable-model-invocation: true
user-invocable: false
---

# MCP Output Rendering

MCP responses from Codex and Gemini are automatically rendered as beautiful terminal output instead of raw JSON. This happens transparently via a PostToolUse hook.

## What You're Seeing

When you invoke Codex or Gemini MCP tools, the raw JSON response is transformed into:

```
    ├──
        Section Title
        Body text that wraps cleanly without
        breaking the tree structure...

    └──
        Final Section
        More content here.
```

The output uses:
- **Tree connectors** (`├──`, `└──`, `│`) for visual hierarchy
- **Box drawing** for tables and callouts
- **ANSI colors** for syntax highlighting and emphasis
- **Icons** for status indicators and semantic markers

## Rendering Modes

Three output modes are available:

| Mode | When Used | Features |
|------|-----------|----------|
| `pretty` | Wide terminals (60+ cols) | Full boxes, line numbers, all styling |
| `responsive` | Narrow terminals (<60 cols) | Colors but simplified layout, no right borders |
| `plain` | Explicitly requested | ASCII-only, no ANSI codes |

## Themes

Two color themes are available:

| Theme | Description |
|-------|-------------|
| `monokai-extended` | Monokai palette with semantic role coloring (default) |
| `classic` | Original colors for backward compatibility |

**Monokai Extended** applies colors based on semantic meaning:
- Success/ok values → green
- Error/fail values → red/pink
- Warnings → yellow
- Structural elements → muted gray
- Primary keys → orange

## Controlling Output

### Environment Variables

```bash
# Force a specific mode
export MCP_RENDER_MODE=pretty      # Full styling
export MCP_RENDER_MODE=responsive  # Compact styling
export MCP_RENDER_MODE=plain       # No ANSI codes

# Set color theme
export MCP_THEME=monokai-extended  # Default
export MCP_THEME=classic           # Original colors
```

### Command Line (Direct Usage)

```bash
# Pipe JSON through renderer
cat response.json | ~/.claude/bin/mcp-render
~/.claude/bin/mcp-render --mode plain response.json
~/.claude/bin/mcp-render --theme classic response.json
~/.claude/bin/mcp-render --no-color response.json
```

## Connector-Only Layout

The tree structure uses a **connector-only layout** principle: connectors never share a line with wrap-eligible text. This ensures:

1. **Clean wrapping** - Text wraps naturally without breaking visual structure
2. **Consistent indentation** - Body text aligns under section titles
3. **No jagged edges** - Tree lines remain intact regardless of content length

```
CORRECT (connector-only):          WRONG (mixed):
    ├──                            ├── Title with very
        Title                           long text breaks
        Body text here...               the tree badly
```

## Schema Requirements

Only responses matching **schema v1.3** are rendered:

```json
{
  "version": "1.x",
  "metadata": { ... },
  "content": [ ... ]
}
```

Responses without this structure pass through unchanged.

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌───────────────┐
│  MCP Tool Call  │────►│  PostToolUse Hook    │────►│  mcp-render   │
│  (Codex/Gemini) │     │  render-mcp-output.py│     │  (renderer)   │
└─────────────────┘     └──────────────────────┘     └───────────────┘
                                │                           │
                                │ validates schema          │ outputs ANSI
                                │ v1.3 format              │ formatted text
                                ▼                           ▼
                        ┌──────────────────────────────────────────────┐
                        │             Terminal Output                   │
                        │  Beautiful formatted response instead of JSON │
                        └──────────────────────────────────────────────┘
```

## File Locations

| Component | Path |
|-----------|------|
| PostToolUse Hook | `~/.claude/hooks/render-mcp-output.py` |
| Renderer Binary | `~/.claude/bin/mcp-render` |
| Hook Log | `~/.claude/logs/mcp-render-hook.log` |
| Settings | `~/.claude/settings.json` (hooks section) |

## Troubleshooting

### Raw JSON Still Showing

1. Check hook is registered: `jq '.hooks.PostToolUse' ~/.claude/settings.json`
2. Verify schema version in response starts with "1."
3. Check log: `tail ~/.claude/logs/mcp-render-hook.log`

### Garbled Output

1. Try plain mode: `export MCP_RENDER_MODE=plain`
2. Check terminal supports ANSI: `echo -e "\033[1mBold\033[0m"`
3. Ensure UTF-8 locale: `echo $LANG`

### Slow Rendering

The renderer has a 5-second timeout. If responses are large:
1. Check `~/.claude/logs/mcp-render-hook.log` for timeout messages
2. Consider using plain mode for very large responses
