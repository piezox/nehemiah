#!/usr/bin/env python3
"""Run evals/scenarios.yaml through Claude Code headless, steering on and off.

Usage: python3 evals/run.py [--modes on,off] [--runs N] [--out DIR] [scenario-id ...]
(EVAL_MODEL overrides the model)

Each run gets a fresh temporary directory whose path does not name this repo.
  on:      AGENTS.md holds core/core.md inline, cases/ is copied next to it.
  pointer: AGENTS.md only points to core/core.md, which is copied with cases/ (#13).
  off:     the directory holds only the fixtures.
MCP servers and user-level settings are disabled so both sides see the same tools.

Output: evals/runs/<datetime>-claude-code-<model>/<id>-<mode>[-rN].{jsonl,md} plus
a recall table on stdout. Behavior is graded by hand from the .md files.
"""
import argparse
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
TIMEOUT = 900
MODEL = os.environ.get("EVAL_MODEL", "claude-fable-5-1")
POINTER = ("Read `core/core.md` now. It is the always-on core of this repository's steering, "
           "and it applies to you while you work here. Its router table says when to open each file in `cases/`.\n")


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
    if mode == "pointer":
        with open(os.path.join(d, "AGENTS.md"), "w") as f:
            f.write(POINTER)
        os.makedirs(os.path.join(d, "core"))
        shutil.copy(os.path.join(ROOT, "core/core.md"), os.path.join(d, "core"))
    if mode != "off":
        shutil.copytree(os.path.join(ROOT, "cases"), os.path.join(d, "cases"))
    return d


def parse(stdout):
    loaded, final, model, cost = set(), "", "unknown", 0.0
    for line in stdout.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("type") == "assistant":
            model = m["message"].get("model", model)
            for c in m["message"].get("content", []):
                if c.get("type") == "tool_use":
                    blob = json.dumps(c["input"])
                    loaded.update(n for n in CASES if f"cases/{n}.md" in blob)
                    if "core/core.md" in blob:
                        loaded.add("core")
        if m.get("type") == "result":
            final = m.get("result", "")
            cost = m.get("total_cost_usd", 0.0)
    return loaded, final, model, cost


def run(job):
    s, mode, r, out = job
    name = f"{s['id']}-{mode}" + (f"-r{r}" if r else "")
    if os.path.exists(f"{out}/{name}.md"):
        loaded, _, model, cost = parse(open(f"{out}/{name}.jsonl").read())
        return s, mode, loaded, model, cost
    d = make_dir(mode, s["fixtures"])
    prompt = s["prompt"]
    if s["fixtures"]:
        prompt += "\n\nFiles in the working directory: " + ", ".join(s["fixtures"])
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    try:
        p = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
             "--max-turns", MAX_TURNS, "--model", MODEL, "--setting-sources", "project",
             "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}'],
            cwd=d, env=env, capture_output=True, text=True, timeout=TIMEOUT)
        stdout, err = p.stdout, f"exit {p.returncode}\n{p.stderr[-2000:]}" if p.returncode else ""
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout or ""
        err = f"timeout after {TIMEOUT} s"
    shutil.rmtree(d, ignore_errors=True)
    loaded, final, model, cost = parse(stdout)
    with open(f"{out}/{name}.jsonl", "w") as f:
        f.write(stdout)
    with open(f"{out}/{name}.md", "w") as f:
        f.write(f"# {name}\n\nprompt: {s['prompt']}\n\nloaded: {sorted(loaded)}\n\n---\n\n{final or err}\n")
    if err:
        sys.stderr.write(f"{name}: {err}\n")
    return s, mode, loaded, model, cost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--modes", default="on,off")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--out", help="resume into an existing run directory; finished runs are re-read, not re-run")
    args = ap.parse_args()
    modes = args.modes.split(",")
    scen = load_scenarios()
    if args.ids:
        scen = [s for s in scen if s["id"] in args.ids]
    out = args.out or os.path.join(ROOT, "evals/runs", datetime.datetime.now().strftime("%Y-%m-%d-%H%M") + "-claude-code")
    os.makedirs(out, exist_ok=True)
    runs = range(1, args.runs + 1) if args.runs > 1 else [0]
    jobs = [(s, mode, r, out) for r in runs for s in scen for mode in modes]
    with ThreadPoolExecutor(WORKERS) as ex:
        results = list(ex.map(run, jobs))
    model = next((r[3] for r in results if r[3] != "unknown"), "unknown")
    final_out = out if args.out else f"{out}-{model}"
    os.rename(out, final_out)
    total = sum(r[4] for r in results)
    print(f"\nmodel {model}, ${total:.2f}, output {os.path.relpath(final_out, ROOT)}\n")
    steered = [m for m in modes if m != "off"]
    print(f"{'id':<18}{'expected':<44}" + "".join(f"{m:<12}" for m in steered))
    hits = {m: 0 for m in steered}
    for s in scen:
        exp = set(s["expect_load"])
        row = f"{s['id']:<18}{', '.join(sorted(exp)) or '-':<44}"
        for m in steered:
            got = [l - {"core"} for x, mode, l, _, _ in results if x is s and mode == m]
            ok = sum(exp <= l if exp else not l for l in got)
            hits[m] += ok
            row += f"{ok}/{len(got)}".ljust(12)
        print(row)
    n = len(scen) * len(runs)
    print("\nrecall " + ", ".join(f"{m} {hits[m]}/{n}" for m in steered))
    if "pointer" in modes:
        core = sum("core" in l for _, mode, l, _, _ in results if mode == "pointer")
        print(f"pointer runs that read core/core.md: {core}/{n}")


if __name__ == "__main__":
    main()
