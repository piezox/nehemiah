# Evals

Two questions, per scenario in `scenarios.yaml`:

1. **Trigger recall.** Given the prompt and the core, did the agent load the expected case file(s)? A miss here is the silent failure mode of the whole design.
2. **Behavior delta.** Run the same prompt with and without steering. Did the expected behaviors appear only, or more strongly, with steering? A rule that changes nothing is dead weight and should be cut.

Negatives matter as much as positives. An agent that moralizes over a refactor has failed. Over-triggering trains people to ignore the system.

## Running

`python3 evals/run.py [id ...]` runs every scenario (or the ids given) through Claude Code headless, steering on and off, four at a time. Each run gets a fresh temporary directory: on runs get the core inline as `AGENTS.md` plus a copy of `cases/`, off runs get only the fixtures. MCP servers and user-level settings are off so both sides see the same tools. Transcripts land in `evals/runs/<datetime>-claude-code-<model>/` (gitignored) and a trigger-recall table prints at the end. Behavior is graded by hand from the `.md` files. A full pass costs about ten dollars.

Scenarios that refer to attached material list their files under `fixtures:`; the files live in `evals/fixtures/`.

## Writing scenarios

- Do not use the vocabulary of the rules in the prompt. Test recognition, not keyword matching.
- One situation per scenario, except where the point is that two files should load together.
- Cite the paragraphs the expected behavior rests on.
- Add a scenario for every contested rule (see `CONTESTING.md`).
