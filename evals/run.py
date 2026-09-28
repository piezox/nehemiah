#!/usr/bin/env python3
"""Run evals/scenarios.yaml through Claude Code headless, steering on and off.

Usage: python3 evals/run.py [--modes on,off] [--runs N] [--drop case,...] [--out DIR] [scenario-id ...]
(EVAL_MODEL overrides the model)

Each run gets a fresh temporary directory whose path does not name this repo.
  on:      AGENTS.md holds core/core.md inline, cases/ is copied next to it.
  pointer: the project as scripts/install.sh leaves it: nehemiah/{core,cases}/ plus a one-line
           AGENTS.md pointer (#4). Run 3 used core/ and cases/ at the root (commit fb578e5).
  remote:  AGENTS.md points to raw GitHub URLs pinned to origin/main; nothing is copied, and
           WebFetch is allowed for raw.githubusercontent.com only (#13).
  off:     the directory holds only the fixtures.
MCP servers, user-level settings, and the Artifact tools (they publish, and stalled runs
into timeouts in run 3) are disabled so both sides see the same tools.

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
MAX_TURNS = "15"
TIMEOUT = 900
API_ERROR = "<synthetic>"  # model Claude Code reports when the API refused the call (limits, outages)
MODEL = os.environ.get("EVAL_MODEL", "claude-fable-5-1")
REMOTE = ("Read {base}core/core.md now. It is the always-on core of this repository's steering, "
          "and it applies to you while you work here. Its router table says when to open each file in `cases/`; "
          "those files are at {base}cases/.\n")


def paragraphs(text, bracketed=False):
    """§ references in text. bracketed=True counts only the [§…] form the steering uses,
    so an agent numbering its own sections with § is not read as a citation."""
    if bracketed:
        text = " ".join(re.findall(r"\[([^\]]*§[^\]]*)\]", text))
    out = set()
    for m in re.finditer(r"§\s*(\d+)(?:\s*[–-]\s*(\d+))?", text):
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        out.update(range(a, b + 1))
    return out


PARAS = {"core": paragraphs(open(os.path.join(ROOT, "core/core.md")).read())}
PARAS.update({n: paragraphs(open(os.path.join(ROOT, f"cases/{n}.md")).read()) for n in CASES})


def unsupported_citations(loaded, final, mode):
    """Paragraphs the output cites that sit in no file the run had in context (#9)."""
    have = set() if mode == "off" else PARAS["core"] | set().union(*(PARAS[n] for n in loaded if n in PARAS))
    return sorted(paragraphs(final, bracketed=True) - have)


def load_scenarios():
    scen, cur, in_prompt, in_checks = [], None, False, False
    for line in open(os.path.join(ROOT, "evals/scenarios.yaml")):
        if line.startswith("- id:"):
            cur = {"id": line.split(":", 1)[1].strip(), "prompt": "", "followup": "", "fixtures": [],
                   "expect_load": [], "expect_behavior": []}
            scen.append(cur)
            in_prompt = in_checks = False
            continue
        if cur is None:
            continue
        m = re.match(r"\s+(prompt|followup): >", line)
        if m:
            in_prompt = m.group(1)
            continue
        if in_prompt and not re.match(r"\s+\w+:", line):
            cur[in_prompt] += line.strip() + " "
            continue
        in_prompt = False
        if re.match(r"\s+expect_behavior:", line):
            in_checks = True
            continue
        if in_checks and re.match(r"\s+- ", line):
            cur["expect_behavior"].append(line.strip()[2:])
            continue
        in_checks = False
        m = re.match(r"\s+(fixtures|expect_load): \[(.*)\]", line)
        if m:
            cur[m.group(1)] = [x.strip() for x in m.group(2).split(",") if x.strip()]
    for s in scen:
        s["prompt"] = s["prompt"].strip()
        s["followup"] = s["followup"].strip()
    return scen


def make_dir(mode, fixtures, drop=()):
    d = tempfile.mkdtemp(prefix="run-")
    for f in fixtures:
        shutil.copy(os.path.join(ROOT, "evals/fixtures", f), d)
    if mode == "on":
        shutil.copy(os.path.join(ROOT, "core/core.md"), os.path.join(d, "AGENTS.md"))
    if mode == "pointer":
        subprocess.run([os.path.join(ROOT, "scripts/install.sh"), d], check=True, capture_output=True)
    if mode == "remote":
        sha = subprocess.run(["git", "rev-parse", "origin/main"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        with open(os.path.join(d, "AGENTS.md"), "w") as f:
            f.write(REMOTE.format(base=f"https://raw.githubusercontent.com/piezox/nehemiah/{sha}/"))
    if mode == "on":
        shutil.copytree(os.path.join(ROOT, "cases"), os.path.join(d, "cases"))
        for n in drop:
            os.remove(os.path.join(d, "cases", n + ".md"))
            path = os.path.join(d, "AGENTS.md")
            kept = [l for l in open(path) if f"cases/{n}.md" not in l]
            open(path, "w").writelines(kept)
    return d


def parse(stdout):
    """Loaded files, final text, model, cost of one run. A run with a follow-up turn (#8)
    holds both turns; the text returned is turn 1, the follow-up, and turn 2 in order."""
    loaded, final, model, cost, turns = set(), "", "unknown", 0.0, []
    for line in stdout.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("type") == "eval_followup":
            turns += [final, f"User follow-up: {m['prompt']}"]
            final = ""
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
            cost += m.get("total_cost_usd", 0.0)
    if turns:
        final = "\n\n---\n\n".join(turns + [final])
    return loaded, final, model, cost


def run(job):
    s, mode, r, out, drop = job
    name = f"{s['id']}-{mode}" + (f"-r{r}" if r else "")
    if os.path.exists(f"{out}/{name}.md"):
        loaded, _, model, cost = parse(open(f"{out}/{name}.jsonl").read())
        return s, mode, loaded, model, cost
    d = make_dir(mode, s["fixtures"], drop)
    prompt = s["prompt"]
    if s["fixtures"]:
        prompt += "\n\nFiles in the working directory: " + ", ".join(s["fixtures"])
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    flags = ["--output-format", "stream-json", "--verbose",
           "--max-turns", MAX_TURNS, "--model", MODEL, "--setting-sources", "project",
           "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
           "--disallowedTools", "Artifact,ArtifactComments,ArtifactData"]
    if mode == "remote":
        flags += ["--allowedTools", "WebFetch(domain:raw.githubusercontent.com)"]

    def invoke(text, extra=()):
        try:
            p = subprocess.run(["claude", "-p", text, *extra, *flags], cwd=d, env=env,
                               capture_output=True, text=True, timeout=TIMEOUT)
            return p.stdout, f"exit {p.returncode}\n{p.stderr[-2000:]}" if p.returncode else ""
        except subprocess.TimeoutExpired as e:
            return (e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout or ""), f"timeout after {TIMEOUT} s"

    stdout, err = invoke(prompt)
    if s["followup"] and not err:
        session = None
        for l in stdout.splitlines():
            try:
                m = json.loads(l)
            except ValueError:
                continue
            if m.get("type") == "result":
                session = m.get("session_id")
        if session:
            out2, err = invoke(s["followup"], ["--resume", session])
            stdout += "\n" + json.dumps({"type": "eval_followup", "prompt": s["followup"]}) + "\n" + out2
    shutil.rmtree(d, ignore_errors=True)
    loaded, final, model, cost = parse(stdout)
    with open(f"{out}/{name}.jsonl", "w") as f:
        f.write(stdout)
    if model == API_ERROR:
        # No .md, so a resume with --out runs it again; left out of the recall table.
        sys.stderr.write(f"{name}: API error: {final}\n")
        return s, mode, loaded, model, cost
    with open(f"{out}/{name}.md", "w") as f:
        f.write(f"# {name}\n\nprompt: {s['prompt']}\n\n"
                + (f"follow-up: {s['followup']}\n\n" if s["followup"] else "")
                + f"loaded: {sorted(loaded)}\n\n---\n\n{final or err}\n")
    if err:
        sys.stderr.write(f"{name}: {err}\n")
    bad = unsupported_citations(loaded, final, mode)
    if bad:
        sys.stderr.write(f"{name}: cites §{', §'.join(map(str, bad))} from no loaded file\n")
    return s, mode, loaded, model, cost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--modes", default="on,off")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--drop", default="", help="case files to remove, with their router rows, in on mode (#6)")
    ap.add_argument("--out", help="resume into an existing run directory; finished runs are re-read, not re-run")
    args = ap.parse_args()
    modes = args.modes.split(",")
    scen = load_scenarios()
    if args.ids:
        scen = [s for s in scen if s["id"] in args.ids]
    out = args.out or os.path.join(ROOT, "evals/runs", datetime.datetime.now().strftime("%Y-%m-%d-%H%M") + "-claude-code")
    os.makedirs(out, exist_ok=True)
    runs = range(1, args.runs + 1) if args.runs > 1 else [0]
    drop = [n for n in args.drop.split(",") if n]
    assert set(drop) <= set(CASES), drop
    jobs = [(s, mode, r, out, drop) for r in runs for s in scen for mode in modes]
    with ThreadPoolExecutor(WORKERS) as ex:
        results = list(ex.map(run, jobs))
    errors = sum(r[3] == API_ERROR for r in results)
    results = [r for r in results if r[3] != API_ERROR]
    model = next((r[3] for r in results if r[3] != "unknown"), "unknown")
    final_out = out if args.out else f"{out}-{model}"
    os.rename(out, final_out)
    total = sum(r[4] for r in results)
    print(f"\nmodel {model}, ${total:.2f}, output {os.path.relpath(final_out, ROOT)}")
    if errors:
        print(f"{errors} runs failed with an API error and are not counted; rerun with --out to complete them")
    print()
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
    n = {m: sum(r[1] == m for r in results) for m in modes}
    print("\nrecall " + ", ".join(f"{m} {hits[m]}/{n[m]}" for m in steered))
    for m in ("pointer", "remote"):
        if m in modes:
            core = sum("core" in l for _, mode, l, _, _ in results if mode == m)
            print(f"{m} runs that read core/core.md: {core}/{n[m]}")


if __name__ == "__main__":
    main()
