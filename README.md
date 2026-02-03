# mcpretty

Pretty terminal output for MCP tools. Transforms JSON responses from Codex and Gemini into readable, styled output.

```
┌─────────────────────────────────────────────────────────┐
│  Raw JSON  ──►  mcpretty  ──►  Beautiful Terminal Output │
└─────────────────────────────────────────────────────────┘
```

## Features

- **Tree layout** — Visual hierarchy with `├──` `└──` `│` connectors
- **Box drawing** — Tables and callouts with clean borders
- **Semantic coloring** — Monokai Extended palette with role-based colors
- **Responsive** — Adapts to terminal width automatically

## Installation

**Requirements:** Python 3.9+, [Claude Code](https://github.com/anthropics/claude-code)

```bash
# Clone the repo
git clone https://github.com/miikeyanderson/mcpretty.git
cd mcpretty

# Copy to Claude Code config
cp bin/mcp-render ~/.claude/bin/
cp hooks/render-mcp-output.py ~/.claude/hooks/
mkdir -p ~/.claude/skills/mcpretty && cp skills/*.md ~/.claude/skills/mcpretty/
```

Add the hook to `~/.claude/settings.json`:

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

Once installed, MCP responses render automatically. No action needed.

### Manual usage

```bash
cat response.json | ~/.claude/bin/mcp-render
~/.claude/bin/mcp-render --no-color response.json
```

### Render modes

| Mode | Terminal | Output |
|------|----------|--------|
| `pretty` | 60+ cols | Full styling |
| `responsive` | <60 cols | Compact |
| `plain` | any | No ANSI |

Set via environment: `export MCP_RENDER_MODE=plain`

### Themes

| Theme | Description |
|-------|-------------|
| `monokai-extended` | Monokai palette with semantic role coloring (default) |
| `classic` | Original colors for backward compatibility |

Set via CLI or environment:

```bash
~/.claude/bin/mcp-render --theme=classic response.json
export MCP_THEME=monokai-extended
```

**Monokai Extended** uses semantic roles for consistent coloring:
- Success/ok → green
- Error/fail → red/pink
- Warning → yellow
- Structural elements → muted gray
- Primary keys → orange

**Terminal requirements:** For best results, use a terminal with truecolor (24-bit) support. Falls back to 256-color or basic 16-color automatically.

## How It Works

The PostToolUse hook intercepts MCP responses matching schema v1.x and pipes them through the renderer. Non-matching responses pass through unchanged.

```
MCP Tool Call → Hook → mcp-render → Styled Output
```

## License

MIT
