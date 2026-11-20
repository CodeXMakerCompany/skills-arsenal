#!/usr/bin/env python3
"""Create, validate, wire and list Kiro custom agents.

  kiro_agent.py create   --name NAME --spec SPEC.json [--scope workspace|global]
                         [--format md|json] [--project DIR] [--force]
  kiro_agent.py validate [PATH ...] [--project DIR]
  kiro_agent.py wire     --orchestrator NAME --subagent NAME [--no-allow] [--project DIR]
  kiro_agent.py list     [--project DIR]

Paths follow https://kiro.dev/docs/custom-agents/creating/ :
  workspace  <project>/.kiro/agents/<name>.{md,json}   (wins on a name clash)
  global     ~/.kiro/agents/<name>.{md,json}
The file name is the agent name; nested dirs give names like team/planner.

Schema is IDE 1.0 / CLI V3. Legacy CLI 2.x fields are reported, not written.
Exit code: 0 clean, 1 errors found, 2 usage problem.
"""

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml  # optional; a subset parser covers the documented shapes
except ImportError:
    yaml = None

V3_FIELDS = {
    "name", "description", "prompt", "mcpServers", "tools", "excludedTools",
    "permissions", "resources", "hooks", "includeMcpJson", "includePowers",
    "model", "welcomeMessage",
}
LEGACY_FIELDS = {"allowedTools", "toolsSettings", "toolAliases", "keyboardShortcut", "useLegacyMcpJson"}
CAPABILITIES = {
    "fs_read", "fs_write", "shell", "web_fetch", "web_search", "mcp", "subagent",
    "skill", "power", "context", "diagnostics", "sandbox_network",
    "all", "builtin", "filesystem",
}
EFFECTS = {"allow", "ask", "deny"}
TOOL_TAGS = {"read", "write", "shell", "web", "subagent", "knowledge", "@builtin", "@mcp", "*"}
KNOWN_TRIGGERS = {"SessionStart", "PreToolUse", "PostToolUse"}
LEGACY_TRIGGERS = {"agentSpawn", "preToolUse", "postToolUse", "userPromptSubmit", "stop"}
SECRET_RE = re.compile(
    r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|"
    r"AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,}|Bearer\s+(?!\$\{)[A-Za-z0-9._-]{16,})"
)
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*(/[a-z0-9][a-z0-9_-]*)*$")
RESOURCE_MAX_FILES = 32
RESOURCE_MAX_TOTAL = 100_000
RESOURCE_MAX_PER_FILE = 50_000
RESOURCE_MAX_BYTES = 1024 * 1024


# --- YAML front matter --------------------------------------------------------

def _scalar(text):
    text = text.strip()
    if text == "":
        return None
    if text[0] in "[{\"":
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(f"cannot parse {text!r}; install PyYAML for full YAML")
    if text[0] == "'" and text.endswith("'"):
        return text[1:-1].replace("''", "'")
    if text in ("|", ">", "|-", ">-"):
        raise ValueError("block scalars need PyYAML")
    low = text.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def _subset_yaml(src):
    """Indentation-based YAML subset: maps, '- ' lists, JSON flow values."""
    lines = [(len(l) - len(l.lstrip(" ")), l.strip()) for l in src.splitlines()
             if l.strip() and not l.strip().startswith("#")]
    pos = 0

    def block(indent):
        nonlocal pos
        if pos >= len(lines):
            return None
        if lines[pos][1].startswith("- ") or lines[pos][1] == "-":
            out = []
            while pos < len(lines) and lines[pos][0] == indent and lines[pos][1].startswith("-"):
                item = lines[pos][1][1:].strip()
                if re.match(r"^[\w@./-]+:(\s|$)", item) and not item.startswith(("file://", "skill://")):
                    # "- key: val" opens a mapping; rewrite the line as its first key
                    lines[pos] = (indent + 2, item)
                    out.append(block(indent + 2))
                else:
                    pos += 1
                    out.append(_scalar(item))
            return out
        out = {}
        while pos < len(lines) and lines[pos][0] == indent:
            key, _, rest = lines[pos][1].partition(":")
            pos += 1
            if rest.strip():
                out[key.strip()] = _scalar(rest)
            elif pos < len(lines) and lines[pos][0] > indent:
                out[key.strip()] = block(lines[pos][0])
            elif pos < len(lines) and lines[pos][0] == indent and lines[pos][1].startswith("-"):
                out[key.strip()] = block(indent)
            else:
                out[key.strip()] = None
        return out

    result = block(lines[0][0]) if lines else {}
    if pos != len(lines):
        raise ValueError(f"unparsed front matter near {lines[pos][1]!r}; install PyYAML")
    return result


def parse_front_matter(text):
    if not text.startswith("---"):
        raise ValueError("Markdown agent must start with a '---' YAML front matter block")
    parts = re.split(r"^---[ \t]*$", text, maxsplit=2, flags=re.M)
    if len(parts) < 3:
        raise ValueError("front matter is not closed with '---'")
    fm, body = parts[1], parts[2].lstrip("\n")
    data = yaml.safe_load(fm) if yaml else _subset_yaml(fm)
    if not isinstance(data, dict):
        raise ValueError("front matter must be a mapping")
    return data, body


def _yaml_scalar(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if re.fullmatch(r"[A-Za-z0-9_./@:+-][A-Za-z0-9_./@:+ -]*", s) and not s.endswith(" ") \
            and s.lower() not in ("true", "false", "null", "yes", "no", "on", "off") \
            and ": " not in s and not re.fullmatch(r"-?\d+(\.\d+)?", s):
        return s
    return json.dumps(s, ensure_ascii=False)


def dump_yaml(value, indent=0):
    """Block YAML in the shape the Kiro docs use; flat lists stay on one line."""
    pad = " " * indent
    out = []
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, dict) and v:
                out.append(f"{pad}{k}:")
                out.extend(dump_yaml(v, indent + 2))
            elif isinstance(v, list) and any(isinstance(i, (dict, list)) for i in v):
                out.append(f"{pad}{k}:")
                out.extend(dump_yaml(v, indent + 2))
            elif isinstance(v, list):
                out.append(f"{pad}{k}: " + json.dumps(v, ensure_ascii=False))
            else:
                out.append(f"{pad}{k}: {_yaml_scalar(v)}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                sub = dump_yaml(item, indent + 2)
                out.append(f"{pad}- " + sub[0].lstrip())
                out.extend(sub[1:])
            else:
                out.append(f"{pad}- {_yaml_scalar(item)}")
    return out


# --- paths --------------------------------------------------------------------

def agents_dir(scope, project):
    if scope == "global":
        return Path.home() / ".kiro" / "agents"
    return Path(project).resolve() / ".kiro" / "agents"


def scopes(project):
    """Workspace then global; one entry when the project is $HOME and both are the same dir."""
    if agents_dir("workspace", project) == agents_dir("global", project):
        return ("global",)
    return ("workspace", "global")


def find_agent(name, project):
    """Resolve a name the way Kiro does: workspace first, then global."""
    for scope in scopes(project):
        for ext in (".md", ".json"):
            p = agents_dir(scope, project) / f"{name}{ext}"
            if p.exists():
                return p, scope
    return None, None


def agent_name(path):
    path = Path(path).resolve()
    for parent in path.parents:
        if parent.name == "agents" and parent.parent.name == ".kiro":
            return str(path.relative_to(parent).with_suffix(""))
    return path.stem


def load(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("file is empty, so Kiro has no agent to load")
    if path.suffix == ".json":
        return json.loads(text), None
    return parse_front_matter(text)


def save(path, config, body=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        fm = "\n".join(dump_yaml(config))
        path.write_text(f"---\n{fm}\n---\n\n{(body or '').strip()}\n", encoding="utf-8")


# --- validation ---------------------------------------------------------------

class Report:
    def __init__(self, path):
        self.path, self.errors, self.warnings = path, [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def print(self):
        status = "FAIL" if self.errors else ("WARN" if self.warnings else "OK")
        print(f"[{status}] {self.path}")
        for m in self.errors:
            print(f"   error: {m}")
        for m in self.warnings:
            print(f"   warn:  {m}")


def _walk_strings(value, where=""):
    if isinstance(value, str):
        yield where, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _walk_strings(v, f"{where}.{k}" if where else k)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _walk_strings(v, f"{where}[{i}]")


def check_tools(cfg, r):
    tools = cfg.get("tools")
    if tools is None:
        r.warn("no 'tools' list; state the tools explicitly so access is reviewable")
        return
    if not isinstance(tools, list) or not all(isinstance(t, str) for t in tools):
        r.err("'tools' must be a list of strings")
        return
    servers = set((cfg.get("mcpServers") or {}).keys())
    for t in tools:
        if t in ("*", "@builtin"):
            r.warn(f"tool '{t}' grants everything it covers, including invoke_sub_agent "
                   "(can start any agent); list tools by name instead")
        elif t.startswith("subagent/") or t in TOOL_TAGS:
            continue
        elif t.startswith("@"):
            server = t[1:].split("/", 1)[0]
            if servers and server not in servers and not cfg.get("includeMcpJson"):
                r.warn(f"tool '{t}' names MCP server '{server}', which is not in mcpServers "
                       "and includeMcpJson is not true")
        elif "/" in t:
            r.err(f"tool '{t}' looks like an MCP selector without '@'; use '@{t}'")
        else:
            r.warn(f"tool '{t}' is not a documented built-in or tag; check it in /docs/tools/")
    if "subagent" in tools:
        r.warn("bare 'subagent' lets this agent start any agent; list 'subagent/<name>' entries")


def check_permissions(cfg, r):
    perms = cfg.get("permissions")
    tools = cfg.get("tools") or []
    if perms is None:
        if any(t in ("shell", "write", "*", "@builtin") for t in tools):
            r.warn("write/shell tools with no permissions block: every call prompts. "
                   "Pre-approve the narrow set the agent needs and deny the dangerous ones")
        return
    rules = perms.get("rules") if isinstance(perms, dict) else None
    if not isinstance(rules, list):
        r.err("'permissions' must be an object with a 'rules' list")
        return
    shell_denies = False
    for i, rule in enumerate(rules):
        tag = f"permissions.rules[{i}]"
        if not isinstance(rule, dict):
            r.err(f"{tag} must be an object")
            continue
        cap, eff, match = rule.get("capability"), rule.get("effect"), rule.get("match")
        if cap not in CAPABILITIES:
            hint = " (did you mean fs_write?)" if cap == "write" else \
                   " (did you mean fs_read?)" if cap == "read" else ""
            r.err(f"{tag}.capability '{cap}' is not a Kiro capability{hint}")
        if eff not in EFFECTS:
            r.err(f"{tag}.effect must be one of allow, ask, deny (got {eff!r})")
        if match is not None and (not isinstance(match, list) or not all(isinstance(m, str) for m in match)):
            r.err(f"{tag}.match must be a list of glob strings")
            match = []
        match = match or []
        if eff == "allow" and cap in ("all", "builtin", "shell", "fs_write", "mcp") and (not match or "*" in match):
            r.warn(f"{tag} allows every '{cap}' call; narrow 'match' to the commands or paths needed")
        if cap == "shell" and eff == "deny":
            shell_denies = True
    if "shell" in tools and not shell_denies:
        r.warn("shell is allowed but nothing is denied; add a deny rule for "
               "destructive commands such as 'rm -rf *', 'sudo *', 'git push *'")


def check_resources(cfg, r, base, verifiable):
    res = cfg.get("resources")
    if res is None:
        return
    if not isinstance(res, list):
        r.err("'resources' must be a list")
        return
    files, total = [], 0
    for i, item in enumerate(res):
        tag = f"resources[{i}]"
        if isinstance(item, dict):
            if item.get("type") != "knowledgeBase":
                r.err(f"{tag} object must have type 'knowledgeBase'")
            for f in ("source", "name"):
                if not item.get(f):
                    r.err(f"{tag} knowledgeBase needs '{f}'")
            if item.get("indexType") not in (None, "best", "fast"):
                r.err(f"{tag}.indexType must be 'best' or 'fast'")
            continue
        if not isinstance(item, str):
            r.err(f"{tag} must be a string or a knowledgeBase object")
            continue
        if item.startswith("file://"):
            pattern = item[len("file://"):]
            if not verifiable and not os.path.isabs(pattern):
                continue
            full = pattern if os.path.isabs(pattern) else str(base / pattern)
            hits = sorted(p for p in glob.glob(full, recursive=True) if os.path.isfile(p))
            if not hits:
                r.warn(f"{tag} '{item}' matches no files under {base}")
            files.extend(hits)
        elif item.startswith("skill://"):
            target = item[len("skill://"):]
            if any(c in target for c in "*?") and verifiable:
                for p in glob.glob(str(base / target), recursive=True):
                    head = Path(p).read_text(encoding="utf-8", errors="replace")[:2000]
                    if not re.search(r"^name:", head, re.M) or not re.search(r"^description:", head, re.M):
                        r.err(f"{tag} skill {p} lacks 'name'/'description' front matter")
        else:
            r.err(f"{tag} '{item}' must start with file:// or skill://")
    seen = []
    for p in files:
        if p in seen:
            continue
        seen.append(p)
        size = os.path.getsize(p)
        if size > RESOURCE_MAX_BYTES:
            r.warn(f"resource {p} is over 1 MiB and will be skipped")
            continue
        chars = len(Path(p).read_text(encoding="utf-8", errors="replace"))
        if chars > RESOURCE_MAX_PER_FILE:
            r.warn(f"resource {p} has {chars} chars; Kiro truncates at {RESOURCE_MAX_PER_FILE}")
        total += min(chars, RESOURCE_MAX_PER_FILE)
    if len(seen) > RESOURCE_MAX_FILES:
        r.warn(f"resources expand to {len(seen)} files; Kiro loads at most {RESOURCE_MAX_FILES}")
    if total > RESOURCE_MAX_TOTAL:
        r.warn(f"resources total ~{total} chars; Kiro stops at {RESOURCE_MAX_TOTAL}. "
               "Move bulk docs to skill:// or a knowledgeBase")


def check_hooks(cfg, r):
    hooks = cfg.get("hooks")
    if hooks is None:
        return
    if isinstance(hooks, dict):
        r.warn("object-form hooks are CLI 2.x legacy; use the array form (/upgrade-agent converts)")
        return
    if not isinstance(hooks, list):
        r.err("'hooks' must be a list")
        return
    for i, h in enumerate(hooks):
        tag = f"hooks[{i}]"
        if not isinstance(h, dict):
            r.err(f"{tag} must be an object")
            continue
        for f in ("name", "trigger", "action"):
            if not h.get(f):
                r.err(f"{tag} needs '{f}'")
        trig = h.get("trigger")
        if trig in LEGACY_TRIGGERS:
            r.warn(f"{tag}.trigger '{trig}' is the CLI 2.x camelCase name; V3 uses PascalCase")
        elif trig and trig not in KNOWN_TRIGGERS:
            r.warn(f"{tag}.trigger '{trig}' is not one the agent docs show; check /docs/hooks/types/")
        act = h.get("action") or {}
        if isinstance(act, dict) and act.get("type") == "command" and not act.get("command"):
            r.err(f"{tag}.action of type command needs 'command'")
        if h.get("matcher") and trig == "SessionStart":
            r.warn(f"{tag}.matcher has no effect on SessionStart")


def check_mcp(cfg, r):
    servers = cfg.get("mcpServers")
    if servers is None:
        return
    if not isinstance(servers, dict):
        r.err("'mcpServers' must be an object keyed by server name")
        return
    for name, s in servers.items():
        if not isinstance(s, dict):
            r.err(f"mcpServers.{name} must be an object")
            continue
        if not s.get("command") and not s.get("url"):
            r.err(f"mcpServers.{name} needs 'command' (local) or 'url' (remote)")
        for k, v in (s.get("env") or {}).items():
            if isinstance(v, str) and v and "${" not in v and re.search(r"(TOKEN|SECRET|PASSWORD|KEY|PAT)", k):
                r.err(f"mcpServers.{name}.env.{k} holds a literal value; use \"${{{k}}}\"")


def validate(path, project):
    path = Path(path)
    r = Report(path)
    try:
        cfg, body = load(path)
    except (ValueError, json.JSONDecodeError) as e:
        r.err(str(e))
        return r
    if yaml is None and path.suffix == ".md":
        r.warn("PyYAML not installed; parsed with the built-in subset parser")

    name = agent_name(path)
    if not NAME_RE.match(name):
        r.warn(f"agent name '{name}' (from the file name) is not lowercase kebab-case")
    if cfg.get("name") and cfg["name"] not in (name, name.split("/")[-1]):
        r.warn(f"name field '{cfg['name']}' differs from the file name '{name}'. "
               "the docs make the file name the agent name; rename one so they agree")

    for k in cfg:
        if k in LEGACY_FIELDS:
            r.warn(f"'{k}' is CLI 2.x legacy and ignored by IDE 1.0 / CLI V3")
        elif k not in V3_FIELDS:
            r.warn(f"unknown field '{k}'")
    if "allowedTools" in cfg and "permissions" not in cfg:
        r.err("allowedTools without a permissions block: CLI V3 skips this profile. "
              "Convert it to permissions.rules (/upgrade-agent does this)")

    desc = cfg.get("description")
    if not desc:
        r.err("no description. Kiro picks sub-agents by it, and people pick agents by it")
    elif len(desc) < 30:
        r.warn("description is short; say what it does and when to use it")

    prompt = cfg.get("prompt")
    if path.suffix == ".md":
        if prompt:
            r.warn("Markdown agent sets 'prompt' in front matter; put the prompt in the body")
        if not (body or "").strip() and not prompt:
            r.err("Markdown body is empty, so the agent has no system prompt")
    elif not prompt:
        r.err("no 'prompt'")
    if isinstance(prompt, str) and prompt.startswith("file://"):
        p = prompt[len("file://"):]
        target = Path(p) if os.path.isabs(p) else path.parent / p
        if not target.exists():
            r.err(f"prompt file {target} does not exist")

    if "model" in cfg and not isinstance(cfg["model"], str):
        r.err("'model' must be a string model id")

    check_tools(cfg, r)
    check_permissions(cfg, r)
    is_workspace = ".kiro/agents" in str(path.resolve()) and not str(path.resolve()).startswith(
        str(Path.home() / ".kiro"))
    base = path.resolve().parents[len(Path(name).parts) + 1] if is_workspace else Path(project)
    check_resources(cfg, r, base, verifiable=is_workspace)
    check_hooks(cfg, r)
    check_mcp(cfg, r)

    for where, s in _walk_strings(cfg):
        if SECRET_RE.search(s):
            r.err(f"{where} looks like a literal secret; reference an env var with ${{VAR}}")
    if body and SECRET_RE.search(body):
        r.err("prompt body contains what looks like a literal secret")

    other = "global" if is_workspace else "workspace"
    for ext in (".md", ".json"):
        twin = agents_dir(other, project) / f"{name}{ext}"
        if twin.exists() and twin.resolve() != path.resolve():
            r.warn(f"same name exists in {other} scope ({twin}); the workspace one wins")
    twin = path.with_suffix(".json" if path.suffix == ".md" else ".md")
    if twin.exists():
        r.err(f"{twin.name} defines the same agent in the same directory; keep one")
    return r


# --- commands -----------------------------------------------------------------

def cmd_create(a):
    if not NAME_RE.match(a.name):
        sys.exit(f"name '{a.name}' must be lowercase kebab-case (nested: team/planner)")
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    spec.pop("name", None)
    unknown = set(spec) - V3_FIELDS
    if unknown & LEGACY_FIELDS:
        sys.exit(f"spec uses legacy fields {sorted(unknown & LEGACY_FIELDS)}; write permissions.rules instead")
    # nested names (team/planner) come from the path, so leave the field out
    config = spec if "/" in a.name else {"name": a.name, **spec}

    path = agents_dir(a.scope, a.project) / f"{a.name}.{a.format}"
    twin = path.with_suffix(".json" if a.format == "md" else ".md")
    if twin.exists():
        sys.exit(f"{twin} already defines this agent; delete it or use --format {twin.suffix[1:]}")
    if path.exists() and path.stat().st_size and not a.force:
        sys.exit(f"{path} already exists; pass --force to replace it")

    body = None
    if a.format == "md":
        body = config.pop("prompt", "") or ""
        if body.startswith("file://"):
            sys.exit("Markdown agents carry the prompt in the body; inline it or use --format json")
    save(path, config, body)
    print(f"wrote {path}")
    r = validate(path, a.project)
    r.print()
    return 1 if r.errors else 0


def cmd_validate(a):
    paths = [Path(p) for p in a.paths]
    if not paths:
        for scope in scopes(project=a.project):
            d = agents_dir(scope, a.project)
            paths += sorted(p for p in d.rglob("*") if p.suffix in (".md", ".json"))
    if not paths:
        print("no agents found")
        return 0
    failed = 0
    for p in paths:
        r = validate(p, a.project)
        r.print()
        failed += bool(r.errors)
    print(f"\n{len(paths)} checked, {failed} with errors")
    return 1 if failed else 0


def cmd_wire(a):
    orch, _ = find_agent(a.orchestrator, a.project)
    sub, sub_scope = find_agent(a.subagent, a.project)
    if not orch:
        sys.exit(f"orchestrator '{a.orchestrator}' not found in workspace or global agents")
    if not sub:
        sys.exit(f"sub-agent '{a.subagent}' not found; create it first")
    cfg, body = load(orch)
    tools = cfg.setdefault("tools", [])
    entry = f"subagent/{a.subagent}"
    if entry not in tools:
        tools.append(entry)
    broad = [t for t in tools if t in ("*", "@builtin", "subagent")]
    if not a.no_allow:
        rules = cfg.setdefault("permissions", {}).setdefault("rules", [])
        rule = next((x for x in rules if x.get("capability") == "subagent" and x.get("effect") == "allow"), None)
        if rule is None:
            rules.append({"capability": "subagent", "match": [a.subagent], "effect": "allow"})
        elif a.subagent not in rule.setdefault("match", []):
            rule["match"].append(a.subagent)
    save(orch, cfg, body)
    print(f"wired {a.subagent} ({sub_scope}: {sub}) into {orch}")
    if broad:
        print(f"note: {orch.name} also has {broad}, which can start any agent; "
              "remove it to make the subagent/<name> list the real limit")
    r = validate(orch, a.project)
    r.print()
    return 1 if r.errors else 0


def cmd_list(a):
    seen = {}
    for scope in reversed(scopes(a.project)):
        d = agents_dir(scope, a.project)
        for p in sorted(d.rglob("*")) if d.exists() else []:
            if p.suffix in (".md", ".json"):
                seen.setdefault(agent_name(p), []).append((scope, p))
    for name, entries in sorted(seen.items()):
        winner = next((e for e in entries if e[0] == "workspace"), entries[0])
        shadow = " (shadows global)" if len(entries) > 1 else ""
        print(f"{name:32} {winner[0]:9} {winner[1]}{shadow}")
    if not seen:
        print("no agents found")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=os.getcwd(), help="workspace root (default: cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="write a new agent at the documented path")
    c.add_argument("--name", required=True)
    c.add_argument("--spec", required=True, help="JSON file with the agent fields (prompt included)")
    c.add_argument("--scope", choices=["workspace", "global"], default="workspace")
    c.add_argument("--format", choices=["md", "json"], default="md")
    c.add_argument("--force", action="store_true")

    v = sub.add_parser("validate", help="check agents against the V3 schema and best practices")
    v.add_argument("paths", nargs="*")

    w = sub.add_parser("wire", help="let an orchestrator delegate to a sub-agent")
    w.add_argument("--orchestrator", required=True)
    w.add_argument("--subagent", required=True)
    w.add_argument("--no-allow", action="store_true", help="keep the start prompt (no allow rule)")

    sub.add_parser("list", help="show agents and which scope wins")

    for p in (c, v, w, sub.choices["list"]):
        p.add_argument("--project", default=argparse.SUPPRESS)

    a = ap.parse_args()
    return {"create": cmd_create, "validate": cmd_validate, "wire": cmd_wire, "list": cmd_list}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
