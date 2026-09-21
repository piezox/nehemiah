#!/usr/bin/env python3
"""Run evals/scenarios.yaml through Claude Code headless, steering on and off.

Usage: python3 evals/run.py [scenario-id ...]     (EVAL_MODEL overrides the model)

Each run gets a fresh temporary directory whose path does not name this repo.
  on:  AGENTS.md holds core/core.md inline, cases/ is copied next to it.
  off: the directory holds only the fixtures.
MCP servers and user-level settings are disabled so both sides see the same tools.

Output: evals/runs/<datetime>-claude-code-<model>/<id>-{on,off}.{jsonl,md} plus
a recall table on stdout. Behavior is graded by hand from the .md files.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES = sorted(f[:-3] for f in os.listdir(os.path.join(ROOT, "cases")) if f.endswith(".md"))
WORKERS = 4
MAX_TURNS = "10"
MODEL = os.environ.get("EVAL_MODEL", "claude-fable-5-1")


def load_scenarios():
    scen, cur, in_prompt = [], None, False
    for line in open(os.path.join(ROOT, "evals/scenarios.yaml")):
        if line.startswith("- id:"):
            cur = {"id": line.split(":", 1)[1].strip(), "prompt": "", "fixtures": [], "expect_load": []}
            scen.append(cur)
            in_prompt = False
            continue
        if cur is None:
            continue
        if re.match(r"\s+prompt: >", line):
            in_prompt = True
            continue
        if in_prompt and not re.match(r"\s+\w+:", line):
            cur["prompt"] += line.strip() + " "
            continue
        in_prompt = False
        m = re.match(r"\s+(fixtures|expect_load): \[(.*)\]", line)
        if m:
            cur[m.group(1)] = [x.strip() for x in m.group(2).split(",") if x.strip()]
    for s in scen:
        s["prompt"] = s["prompt"].strip()
    return scen


def make_dir(mode, fixtures):
    d = tempfile.mkdtemp(prefix="run-")
    for f in fixtures:
        shutil.copy(os.path.join(ROOT, "evals/fixtures", f), d)
    if mode == "on":
        shutil.copy(os.path.join(ROOT, "core/core.md"), os.path.join(d, "AGENTS.md"))
        shutil.copytree(os.path.join(ROOT, "cases"), os.path.join(d, "cases"))
    return d


def run(job):
    s, mode, out = job
    d = make_dir(mode, s["fixtures"])
    prompt = s["prompt"]
    if s["fixtures"]:
        prompt += "\n\nFiles in the working directory: " + ", ".join(s["fixtures"])
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    p = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
         "--max-turns", MAX_TURNS, "--model", MODEL, "--setting-sources", "project",
         "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}'],
        cwd=d, env=env, capture_output=True, text=True, timeout=900)
    shutil.rmtree(d, ignore_errors=True)
    loaded, final, model, cost = set(), "", "unknown", 0.0
    for line in p.stdout.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("type") == "assistant":
            for c in m["message"].get("content", []):
                if c.get("type") == "tool_use":
                    blob = json.dumps(c["input"])
                    loaded.update(n for n in CASES if f"cases/{n}.md" in blob)
        if m.get("type") == "result":
            final = m.get("result", "")
            cost = m.get("total_cost_usd", 0.0)
            model = next(iter(m.get("modelUsage", {"unknown": 0})))
    with open(f"{out}/{s['id']}-{mode}.jsonl", "w") as f:
        f.write(p.stdout)
    with open(f"{out}/{s['id']}-{mode}.md", "w") as f:
        f.write(f"# {s['id']} ({mode})\n\nprompt: {s['prompt']}\n\nloaded: {sorted(loaded)}\n\n---\n\n{final}\n")
    if p.returncode:
        sys.stderr.write(f"{s['id']} {mode}: exit {p.returncode}\n{p.stderr[-2000:]}\n")
    return s, mode, loaded, model, cost


def main():
    scen = load_scenarios()
    if sys.argv[1:]:
        scen = [s for s in scen if s["id"] in sys.argv[1:]]
    out = os.path.join(ROOT, "evals/runs", datetime.datetime.now().strftime("%Y-%m-%d-%H%M") + "-claude-code")
    os.makedirs(out, exist_ok=True)
    jobs = [(s, mode, out) for s in scen for mode in ("on", "off")]
    with ThreadPoolExecutor(WORKERS) as ex:
        results = list(ex.map(run, jobs))
    model = next((r[3] for r in results if r[3] != "unknown"), "unknown")
    final_out = f"{out}-{model}"
    os.rename(out, final_out)
    total = sum(r[4] for r in results)
    print(f"\nmodel {model}, ${total:.2f}, output {os.path.relpath(final_out, ROOT)}\n")
    print(f"{'id':<18}{'expected':<44}{'loaded (on)':<44}result")
    hits = n = 0
    for s, mode, loaded, _, _ in results:
        if mode != "on":
            continue
        exp = set(s["expect_load"])
        ok = exp <= loaded if exp else not loaded
        hits += ok
        n += 1
        print(f"{s['id']:<18}{', '.join(sorted(exp)) or '-':<44}{', '.join(sorted(loaded)) or '-':<44}{'hit' if ok else 'MISS'}")
    print(f"\nrecall {hits}/{n}")


if __name__ == "__main__":
    main()
