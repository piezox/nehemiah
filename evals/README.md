# Evals

Two questions, per scenario in `scenarios.yaml`:

1. **Trigger recall.** Given the prompt and the core, did the agent load the expected case file(s)? A miss here is the silent failure mode of the whole design.
2. **Behavior delta.** Run the same prompt with and without steering. Did the expected behaviors appear only, or more strongly, with steering? A rule that changes nothing is dead weight and should be cut.

Negatives matter as much as positives. An agent that moralizes over a refactor has failed. Over-triggering trains people to ignore the system.

## Running

`python3 evals/run.py [id ...]` runs every scenario (or the ids given) through Claude Code headless, steering on and off, four at a time. Each run gets a fresh temporary directory: on runs get the core inline as `AGENTS.md` plus a copy of `cases/`, off runs get only the fixtures. MCP servers and user-level settings are off so both sides see the same tools. Transcripts land in `evals/runs/<datetime>-claude-code-<model>/` (gitignored) and a trigger-recall table prints at the end. A full pass costs about ten dollars. `--modes on,pointer,off` picks the arms (pointer: AGENTS.md only points to the core, #13), `--runs N` repeats each, `--out DIR` resumes a run directory.

`python3 evals/grade.py evals/runs/<dir>` grades a run blind: per scenario, two model graders (Opus and Sonnet by default, neither the model under test) see the outputs shuffled with mode and run stripped, and answer each `expect_behavior` check yes or no. It prints pass rates per mode and grader, and the graders' agreement (Cohen's kappa). Grading a full run costs about a dollar and a half. Read the outputs as well: the checks catch what they name, not everything.

Scenarios that refer to attached material list their files under `fixtures:`; the files live in `evals/fixtures/`.

## Writing scenarios

- Do not use the vocabulary of the rules in the prompt. Test recognition, not keyword matching.
- One situation per scenario, except where the point is that two files should load together.
- Write each `expect_behavior` line as a yes/no check a grader can apply from the output text alone. "Not preachy" is not a check; "spends at most one sentence on why" is.
- Cite the paragraphs the expected behavior rests on.
- Add a scenario for every contested rule (see `CONTESTING.md`).
