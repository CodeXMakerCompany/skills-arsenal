# Kiro agent reference

Condensed from the Kiro custom-agents docs: the creating page, the configuration reference (updated 2026-11-06), the sub-agents page (2026-11-13) and the examples page (2026-10-10). Schema: **IDE 1.0 / CLI V3**.

## Locations

| Scope | Path | Notes |
|---|---|---|
| Workspace | `<repo>/.kiro/agents/<name>.md` or `.json` | Shared through git. Loaded only when the workspace is trusted. Wins on a name clash, with a warning |
| Global | `~/.kiro/agents/<name>.md` or `.json` | All projects. Not available to Kiro Web as a primary agent |

The file name is the agent name. Nested directories are allowed: `team/planner.md` becomes `team/planner`. The default agent in the CLI is `kiro_default`.

## Fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | Optional. Comes from the file name when omitted. Keep the two equal |
| `description` | string | What it does and when to use it. Kiro routes sub-agent calls by it |
| `prompt` | string | Inline text, or `file://` resolved against the agent file's directory (`file://../shared/p.md`; an absolute path is used as-is). In `.md` the body is the prompt |
| `tools` | string[] | Visibility. Built-ins `read`, `write`, `shell`, `knowledge`. Tags `read`, `write`, `shell`, `web`, `subagent`. MCP: `@server`, `@server/tool`, `@mcp`. `@builtin` = every built-in, `*` = everything. `subagent/<name>` = may start that agent |
| `excludedTools` | string[] | Removes tools even when `tools` allows them |
| `permissions.rules[]` | object[] | `capability`, `match` (globs: paths, command prefixes, `server/tool`), `effect` (`allow` / `ask` / `deny`), optional `exclude`. Deny always wins |
| `resources` | (string \| object)[] | `file://` (loaded at start; globs allowed), `skill://` (metadata at start, body on demand; the file needs `name`/`description` front matter), and `{type: "knowledgeBase", source, name, description?, indexType: best\|fast, autoUpdate?}` |
| `hooks[]` | object[] | `name`, `trigger` (`SessionStart`, `PreToolUse`, `PostToolUse`; other triggers are listed on the hooks docs page), `matcher` (tool id, tag, `@mcp`, `@server`, `*`, or a regex), `action` `{type: "command", command}` |
| `mcpServers` | object | Per server: `command` + `args` (local), or `url` (+ `type: "http"`, `headers`) for remote. Optional: `env` (`${VAR}` expanded), `timeout` (ms, default 60000), `requestTimeout` (ms, default 120000), `oauth` `{clientId, redirectUri}`, `oauthScopes` |
| `includeMcpJson` | bool | Also load `~/.kiro/settings/mcp.json` and `<repo>/.kiro/settings/mcp.json` |
| `includePowers` | bool | Automatically include powers installed in the IDE |
| `model` | string | Must be an id that `/model` lists. An unknown id fails on the first prompt; there is no fallback |
| `welcomeMessage` | string | Shown after switching to the agent |

**Capabilities:** `fs_read`, `fs_write`, `shell`, `web_fetch`, `web_search`, `mcp`, `subagent`, `skill`, `power`, `context`, `diagnostics`, `sandbox_network`. Meta-capabilities: `all`, `builtin`, `filesystem`.

**Legacy (CLI 2.x), do not write these:** `allowedTools`, `toolsSettings`, `toolAliases`, `keyboardShortcut`, object-form `hooks` with camelCase events. CLI V3 skips a profile that has `allowedTools` but no `permissions`. `/upgrade-agent` converts the old fields and backs the original up to `<file>.json.bak`.

**Resource limits** (CLI 3.1.0+, IDE 1.4.86+): at most 32 files and 100,000 characters in total; each file is cut at 50,000 characters; files over 1 MiB are skipped.

**Sub-agent policy:** a call is checked against both the parent's policy and the sub-agent's, and the stricter result wins. When the parent has no rule for a call, Kiro prompts even if the sub-agent allows it. `--trust-all-tools` approves calls that would prompt, but `deny` still applies.

## Commands

| Where | Command |
|---|---|
| CLI chat | `/agent create <name> [-D desc] [-m mcp-server] [--directory workspace\|global\|./path] [--from template] [--manual]`. Without `--directory`, the file goes to **global** |
| Terminal | `kiro-cli agent create <name> [--directory …] [--from …]` · `kiro-cli agent list` · `kiro-cli --agent <name>` |
| CLI chat | `/agent swap [name]` · `/agent list` · `/agent schema` · `/upgrade-agent` · `/model` |
| IDE | The agent picker in the chat bar. The change applies from the next message |

The script in this skill writes the file directly. That is equivalent to `/agent create --manual` without the editor round trip, and it works when no CLI is installed.

## Archetypes

Each spec is the input to `kiro_agent.py create --spec`. Cut what the job does not need.

### Read-only reviewer

```json
{
  "description": "Reviews the current diff for correctness and security issues and returns findings ranked by severity with file:line. Never edits files. Use before opening a PR.",
  "tools": ["read", "shell"],
  "permissions": {
    "rules": [
      { "capability": "shell", "match": ["git diff *", "git log *", "git show *", "rg *", "grep *", "ls *"], "effect": "allow" },
      { "capability": "shell", "match": ["rm *", "sudo *", "git push *", "git commit *", "git reset *"], "effect": "deny" },
      { "capability": "fs_write", "match": ["**"], "effect": "deny" }
    ]
  },
  "resources": ["file://CONTRIBUTING.md"],
  "prompt": "You are a code reviewer. ..."
}
```

### Scoped implementer

```json
{
  "description": "Implements backend changes in src/ and tests/ for the Node.js API, runs the test suite, and reports what changed. Use for backend tickets once requirements are clear.",
  "tools": ["read", "write", "shell"],
  "permissions": {
    "rules": [
      { "capability": "fs_write", "match": ["src/**", "tests/**"], "effect": "allow" },
      { "capability": "shell", "match": ["npm test", "npm run lint", "git status", "git diff *"], "effect": "allow" },
      { "capability": "shell", "match": ["rm -rf *", "sudo *", "git push *"], "effect": "deny" },
      { "capability": "fs_write", "match": [".env*", "**/*.pem"], "effect": "deny" }
    ]
  },
  "resources": ["file://README.md", "file://docs/architecture.md"],
  "hooks": [
    { "name": "git-status", "trigger": "SessionStart", "action": { "type": "command", "command": "git status --porcelain" } }
  ],
  "prompt": "You are a backend engineer. ..."
}
```

### Orchestrator

Create the sub-agents first, then the orchestrator with only `read` in `tools`, then run `wire` once per sub-agent. Do not add `*`, `@builtin` or a bare `subagent`.

```json
{
  "description": "Splits a ticket into review, implementation and test steps, delegates each to the matching sub-agent, and returns one consolidated report. Use for multi-step tickets.",
  "tools": ["read"],
  "prompt": "You coordinate. You do not edit code yourself. ..."
}
```

```bash
python3 $S wire --orchestrator lead --subagent code-reviewer --project <repo>
python3 $S wire --orchestrator lead --subagent backend-dev   --project <repo>
```

Then add to the **orchestrator's** `permissions.rules` any allow rules the sub-agents need in order to run without prompting, such as `npm test` for `backend-dev`.

### MCP-backed agent

```json
{
  "description": "Answers questions about open GitHub issues and searches them. Read-only on GitHub.",
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_PAT}" }
    }
  },
  "tools": ["read", "@github/issue_read", "@github/search_issues"],
  "permissions": {
    "rules": [
      { "capability": "mcp", "match": ["github/issue_read", "github/search_issues"], "effect": "allow" }
    ]
  },
  "prompt": "You research GitHub issues. ..."
}
```

When an OAuth server asks for login, run `/mcp` in the CLI.
