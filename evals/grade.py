#!/usr/bin/env python3
"""Grade a run directory blind with two model graders and report their agreement (#5).

Usage: python3 evals/grade.py evals/runs/<dir> [--graders claude-opus-5-5,claude-sonnet-5]

Per scenario, each grader sees the prompt, the expect_behavior checks, and every output
for that scenario with mode and run stripped, shuffled. It answers yes or no per check,
plus one extra check on whether the output mentions its own steering unprompted (reported
separately, not scored). Runs with no final answer (timeouts) are left out.

Writes key.json and grades-<grader>.json into the run directory and prints pass rates per
mode and grader, and agreement between graders.
"""
import argparse
import json
import os
import random
import subprocess
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from run import API_ERROR, load_scenarios, parse, provenance_line, sha

META = "mentions its own instructions, guidelines, rules, or steering without being asked"
INSTRUCTIONS = """You grade assistant replies against fixed checks.

Below are a user prompt, a numbered list of checks, and several replies labelled by letter.
The replies come from different configurations of an assistant; you are not told which.
For every reply, answer every check with "yes" or "no". Answer "yes" only when the reply
text clearly satisfies the check; otherwise "no". Judge each reply on its own.

Reply with JSON only, no prose: {"A": ["yes", "no", ...], "B": [...], ...}, one list per
reply keyed by its letter, in check order, every reply present.
"""


def packet(s, labelled):
    checks = s["expect_behavior"] + [META]
    out = [INSTRUCTIONS, f"User prompt: {s['prompt']}", "Checks:"]
    out += [f"{i + 1}. {c}" for i, c in enumerate(checks)]
    for label, text in labelled:
        out.append(f"\n## Reply {label.rsplit('-', 1)[1]}\n\n{text}")
    return "\n".join(out), len(checks)


def grade(job):
    grader, text, n, labels = job
    d = tempfile.mkdtemp(prefix="grade-")
    p = subprocess.run(
        ["claude", "-p", "--model", grader, "--output-format", "json", "--tools", "",
         "--setting-sources", "project", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}'],
        input=text, cwd=d, capture_output=True, text=True, timeout=900,
        env={k: v for k, v in os.environ.items() if k != "CLAUDECODE"})
    os.rmdir(d)
    res = json.loads(p.stdout)
    body = res["result"]
    by_letter = json.loads(body[body.index("{"):body.rindex("}") + 1])
    g = {label: by_letter.get(label.rsplit("-", 1)[1]) for label in labels}
    for label in labels:
        if len(g.get(label, [])) != n:
            raise ValueError(f"{grader}: bad grade for {label}: {g.get(label)}")
    return grader, g, res.get("total_cost_usd", 0.0)


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--graders", default="claude-opus-5-5,claude-sonnet-5")
    args = ap.parse_args()
    graders = args.graders.split(",")
    rng = random.Random(5)

    key, jobs = {}, []
    for s in load_scenarios():
        outs = []
        for f in sorted(os.listdir(args.run_dir)):
            if f.startswith(s["id"] + "-") and f.endswith(".jsonl"):
                _, final, model, _ = parse(open(os.path.join(args.run_dir, f)).read())
                if final and model != API_ERROR:
                    outs.append((f[:-6], final))
        if not outs:
            continue
        rng.shuffle(outs)
        labelled = []
        for i, (name, final) in enumerate(outs):
            label = f"{s['id']}-{chr(65 + i)}"
            key[label] = name
            labelled.append((label, final))
        text, n = packet(s, labelled)
        jobs += [(g, text, n, [l for l, _ in labelled]) for g in graders]

    if not jobs:
        sys.exit(f"nothing to grade in {args.run_dir}: no completed outputs")
    with ThreadPoolExecutor(4) as ex:
        results = list(ex.map(grade, jobs))
    grades = defaultdict(dict)
    cost = 0.0
    for g, part, c in results:
        grades[g].update(part)
        cost += c
    run_json = os.path.join(args.run_dir, "RUN.json")
    prov = json.load(open(run_json)) if os.path.exists(run_json) else {"commit": "?", "dirty": False, "scenarios": "?",
                                                                       "harness": "?", "host": "?", "model": "?"}
    checks = sha("evals/scenarios.yaml")
    if prov["scenarios"] not in ("?", checks):
        print(f"note: scenarios.yaml changed since the run ({prov['scenarios']} → {checks}); "
              "graded against the current checks", file=sys.stderr)
    prov.update({"graders": graders, "grader_script": sha("evals/grade.py"), "checks": checks})
    json.dump(prov, open(run_json, "w"), indent=1)
    json.dump(key, open(os.path.join(args.run_dir, "key.json"), "w"), indent=1)
    for g in graders:
        json.dump(grades[g], open(os.path.join(args.run_dir, f"grades-{g}.json"), "w"), indent=1)

    def mode_of(label):
        return key[label].split("-")[2]

    modes = sorted({mode_of(l) for l in key})
    print(f"\n{provenance_line(prov)}")
    print(f"graded {len(key)} outputs, reported cost ${cost:.2f}\n")
    print(f"{'id':<18}" + "".join(f"{m + ' ' + g.split('-')[1]:<16}" for m in modes for g in graders))
    for sid in dict.fromkeys(l.rsplit("-", 1)[0] for l in key):
        row = f"{sid:<18}"
        for m in modes:
            for g in graders:
                ans = [a for l in key if l.rsplit("-", 1)[0] == sid and mode_of(l) == m for a in grades[g][l][:-1]]
                row += (f"{sum(a == 'yes' for a in ans)}/{len(ans)}" if ans else "-").ljust(16)
        print(row)
    print()
    for m in modes:
        for g in graders:
            ans = [a for l in key if mode_of(l) == m for a in grades[g][l][:-1]]
            meta = [grades[g][l][-1] for l in key if mode_of(l) == m]
            print(f"{m:<8} {g:<18} pass {sum(a == 'yes' for a in ans)}/{len(ans)} "
                  f"({sum(a == 'yes' for a in ans) / len(ans):.3f})   mentions steering {meta.count('yes')}/{len(meta)}")
    if len(graders) == 2:
        a = [x == "yes" for l in key for x in grades[graders[0]][l][:-1]]
        b = [x == "yes" for l in key for x in grades[graders[1]][l][:-1]]
        po, k = kappa(a, b)
        print(f"\nagreement on {len(a)} checks: {po:.3f}, Cohen's kappa {k:.3f}")


if __name__ == "__main__":
    main()
