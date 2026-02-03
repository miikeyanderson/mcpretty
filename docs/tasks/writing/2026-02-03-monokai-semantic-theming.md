# Monokai Extended Semantic Theming Council Writing Tasks

**Goal:** Add semantic role-based coloring to mcpretty using a Monokai Extended palette, replacing ad-hoc hardcoded colors with a structured Role → Color mapping.

**Audience:** mcpretty maintainers and users who want visually scannable, semantically meaningful terminal output from MCP tool responses.

**Scope:**
- IN: Role taxonomy, Monokai palette, classifier layer, renderer refactor, theme selection
- OUT: Custom theme JSON files (deferred), per-user role overrides (deferred), non-MCP output handling

***

## Task Dependency Graph

```
Task 7: Lock architecture + baselines
         │
         ▼
Task 1: Define Role model (v1 core)
         │
    ┌────┴────┐
    ▼         ▼
Task 2:    Task 3:
Palette    Classifier
    │         │
    └────┬────┘
         ▼
Task 4: Migrate renderer
         │
    ┌────┴────┐
    ▼         ▼
Task 5:    Task 6:
Config     Docs
```

***

## Task List

- [ ] **Task 7: Lock architecture and create baseline fixtures**
  - [ ] 1. Decide: single-file mcp-render or convert to mcpretty/ package
  - [ ] 2. Document decision rationale in code comment
  - [ ] 3. Create tests/fixtures/ directory
  - [ ] 4. Capture 3-4 golden outputs from current renderer
  - [ ] 5. Verify hook still works with chosen architecture

- [ ] **Task 1: Define semantic Role model (v1 core)** [blocked by Task 7]
  - [ ] 1. Create Role enum with core roles only
  - [ ] 2. Add struct.frame, struct.connector, struct.punctuation
  - [ ] 3. Add key.primary, key.default
  - [ ] 4. Add value.status.ok, value.status.error, value.status.warning, value.text
  - [ ] 5. Add diff.added, diff.removed, diff.header
  - [ ] 6. Document deferred roles in comments

- [ ] **Task 2: Build theme engine with terminal fallback** [blocked by Task 1]
  - [ ] 1. Add terminal capability detection (COLORTERM, TERM)
  - [ ] 2. Define Monokai hex values and 256-color/16-color fallbacks
  - [ ] 3. Create Role → Color mapping for MonokaiExtended theme
  - [ ] 4. Create Role → Color mapping for Classic theme (current behavior)
  - [ ] 5. Implement get_color(role, depth) API with depth modifiers
  - [ ] 6. Add theme selection global variable

- [ ] **Task 3: Implement classifier with precedence tests** [blocked by Task 1]
  - [ ] 1. Create classify_semantic_role(key, value, depth) function
  - [ ] 2. Implement is_status_key, is_error_like_value, is_warning_like_value, is_success_like_value
  - [ ] 3. Define precedence: error > warning > success
  - [ ] 4. Create tests/test_classifier.py with table-driven tests
  - [ ] 5. Test ambiguous cases and edge cases

- [ ] **Task 4: Migrate renderer incrementally** [blocked by Tasks 1, 2, 3]
  - [ ] 1. Add _cr() wrapper that takes Role instead of Colors.*
  - [ ] 2. Migrate render_diff() to use diff.* roles
  - [ ] 3. Verify baseline fixture parity
  - [ ] 4. Migrate render_admonition() to use value.status.* roles
  - [ ] 5. Verify baseline fixture parity
  - [ ] 6. Migrate render_table() cell coloring
  - [ ] 7. Verify baseline fixture parity
  - [ ] 8. Migrate colorize_inline() to use classifier
  - [ ] 9. Verify baseline fixture parity
  - [ ] 10. Migrate render_block() structural elements
  - [ ] 11. Final parity check: --no-color, --safe, --mode=plain

- [ ] **Task 5: Add theme selection surface** [blocked by Tasks 2, 4]
  - [ ] 1. Add --theme argument to argparse
  - [ ] 2. Add MCP_THEME environment variable support
  - [ ] 3. Implement precedence: --theme > MCP_THEME > default
  - [ ] 4. Ensure --no-color overrides theme colors
  - [ ] 5. Update --help text with theme options

- [ ] **Task 6: Update docs and install instructions** [blocked by Task 4]
  - [ ] 1. Add Themes section to README
  - [ ] 2. Document terminal requirements (truecolor recommended)
  - [ ] 3. Add inline code comments for role taxonomy
  - [ ] 4. Verify hook install still works
  - [ ] 5. Test end-to-end with real Codex/Gemini responses

***

## Monokai Extended Palette Reference

| Color       | Hex       | Role Usage                                    |
|-------------|-----------|-----------------------------------------------|
| Background  | #272822   | (terminal bg, not rendered)                   |
| Base text   | #F8F8F2   | value.text, key.default                       |
| Muted gray  | #75715E   | struct.*, noise, debug                        |
| Green       | #A6E22E   | value.status.ok, diff.added                   |
| Red/Pink    | #F92672   | value.status.error, diff.removed              |
| Orange      | #FD971F   | key.primary, mcp.tool_name (future)           |
| Yellow      | #E6DB74   | value.status.warning, diff.header             |
| Blue/Cyan   | #66D9EF   | value.url, value.path (future v1.1)           |
| Purple      | #AE81FF   | value.id, value.enum (future v1.1)            |

***

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Misclassification of values | Medium | Low | Start with minimal roles, expand in v1.1 |
| Terminal compatibility | Medium | Medium | Three-tier fallback (truecolor/256/16) |
| Regression in existing output | Low | High | Baseline fixtures + parity checks per function |
| Hook breakage if package | Low | High | Test hook after architecture decision |
| Scope creep in roles | Medium | Medium | Strict v1 core list, defer to v1.1 |

***

## Council Review Notes

**Codex (2026-02-03):**
- Recommended adding Task 0 (now Task 7) for architecture decision
- Flagged testing-too-late risk → baseline fixtures moved before refactor
- Noted terminal fallback requirement for Monokai hex colors
- Suggested staging role taxonomy to reduce misclassification risk

**Gemini:** Timed out (120s), not included in review.

***

## Execution (Council Mode)

These writing tasks are meant to be executed with a council workflow:

1. Use Claude Code Tasks as the source of truth.
2. For each Task:
   - Execute the steps.
   - Ask Codex and Gemini (via MCP) to review the changes for that Task.
   - Address issues, then mark the Task done.
3. After the final Task:
   - Ask Codex and Gemini for a high-level review of the entire plan and outcome.
   - Add any follow-up work as new Tasks.

Do not skip council reviews. If they raise issues repeatedly on similar patterns, consider updating this task list and any relevant guidelines.
