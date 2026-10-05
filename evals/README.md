# Evals

Two questions, per scenario in `scenarios.yaml`:

1. **Trigger recall.** Given the prompt and the core, did the agent load the expected case file(s)? A miss here is the silent failure mode of the whole design.
2. **Behavior delta.** Run the same prompt with and without steering. Did the expected behaviors appear only, or more strongly, with steering? A rule that changes nothing is dead weight and should be cut.

Negatives matter as much as positives. An agent that moralizes over a refactor has failed. Over-triggering trains people to ignore the system.

## Running

`python3 evals/run.py [id ...]` runs every scenario (or the ids given) through Claude Code headless, steering on and off, four at a time. Each run gets a fresh temporary directory: on runs get the core inline as `AGENTS.md` plus a copy of `cases/`, off runs get only the fixtures. MCP servers and user-level settings are off so both sides see the same tools. Transcripts land in `evals/runs/<datetime>-claude-code-<model>/` (gitignored) and a trigger-recall table prints at the end. A full pass is 30 scenarios, on and off, 60 runs; Claude Code reports about $40 for it at API prices, and on a subscription it counts against the usage limit instead. `--modes on,pointer,off` picks the arms (pointer: the layout `scripts/install.sh` produces; remote: AGENTS.md points to raw GitHub URLs, #13), `--runs N` repeats each, `--drop case,...` removes case files and their router rows (ablation, #6), `--out DIR` resumes a run directory. Runs refused by the API (usage limits, outages) are not counted and rerun on resume. Each run's bracketed `[§…]` citations are checked against the files it loaded; a citation from no loaded file is printed to stderr (#9).

`python3 evals/grade.py evals/runs/<dir>` grades a run blind: per scenario, two model graders (Opus and Sonnet by default, neither the model under test) see the outputs shuffled with mode and run stripped, and answer each `expect_behavior` check yes or no. It prints pass rates per mode and grader, and the graders' agreement (Cohen's kappa). Grading 270 outputs was reported at about $8. If a grader refuses a scenario's outputs or cannot be reached, that scenario is listed as not graded by it and left out of its pass rate and of the agreement; the other grader's answers still count. Read the outputs as well: the checks catch what they name, not everything.

Scenarios that refer to attached material list their files under `fixtures:`; the files live in `evals/fixtures/`.

## Reporting a result

Every result depends on six things: the commit of the rules, the scenario set, the checks, the model, the host, and the graders. `run.py` and `grade.py` write them to `RUN.json` in the run directory and print one line:

```
nehemiah 4758199 · scenarios 3f9a1c2b0d4e · harness a1b2c3d4e5f6 · claude-code 2.1.278 · model claude-fable-5-1 · graders claude-opus-5-5, claude-sonnet-5 (grade.py 0a1b2c3d4e5f, checks 3f9a1c2b0d4e)
```

Paste that line with every table you post, in an issue (template "Eval result") or a report. Numbers without it are not comparable and are not accepted as evidence for a rule change. `+dirty` on the commit means the rules or the harness had uncommitted changes; commit first. If the checks changed between the run and the grading, `grade.py` says so and records both hashes; say it too.

This applies to agents working in this repository as much as to people.

## Writing scenarios

- Do not use the vocabulary of the rules in the prompt. Test recognition, not keyword matching.
- One situation per scenario, except where the point is that two files should load together.
- Write each `expect_behavior` line as a yes/no check a grader can apply from the output text alone. "Not preachy" is not a check; "spends at most one sentence on why" is.
- Cite the paragraphs the expected behavior rests on.
- Add a scenario for every contested rule (see `CONTESTING.md`).
