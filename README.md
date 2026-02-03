# mcpretty

Beautiful terminal rendering for MCP tool responses. Transforms raw JSON from Codex and Gemini MCP servers into ANSI-formatted output with tree structures, box drawing, and syntax highlighting.

## What It Does

```
Raw JSON Response  →  mcpretty  →  Beautiful Terminal Output
```

Before:
```json
{"version":"1.0","metadata":{"source":"codex"},"content":[{"type":"text","text":"Hello"}]}
```

After:
```
├──
    Hello
```

## Features

- Tree connectors (`├──`, `└──`, `│`) for visual hierarchy
- Box drawing for tables and callouts
- ANSI colors for syntax highlighting
- Automatic width detection and responsive layout
- Three rendering modes: `pretty`, `responsive`, `plain`

## Installation

Copy files to your Claude Code configuration:

```bash
cp bin/mcp-render ~/.claude/bin/
cp hooks/render-mcp-output.py ~/.claude/hooks/
cp skills/*.md ~/.claude/skills/mcpretty/
```

Add the PostToolUse hook to `~/.claude/settings.json`:

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

## Usage

### Automatic (via hook)

Once installed, MCP responses from Codex/Gemini are automatically rendered.

### Manual

```bash
# Pipe JSON through renderer
cat response.json | mcp-render

# Read from file
mcp-render response.json

# Force plain mode (no ANSI)
mcp-render --no-color response.json
```

### Environment Variables

```bash
export MCP_RENDER_MODE=pretty      # Full styling (default for wide terminals)
export MCP_RENDER_MODE=responsive  # Compact styling (default for narrow terminals)
export MCP_RENDER_MODE=plain       # No ANSI codes
```

## Schema Requirements

Only renders responses matching schema v1.x:

```json
{
  "version": "1.x",
  "metadata": { ... },
  "content": [ ... ]
}
```

Non-matching responses pass through unchanged.

## Project Structure

```
mcpretty/
├── bin/
│   └── mcp-render           # Main renderer script
├── hooks/
│   └── render-mcp-output.py # PostToolUse hook
├── skills/
│   ├── SKILL.md             # Skill definition
│   └── reference.md         # Technical reference
└── README.md
```

## License

MIT
