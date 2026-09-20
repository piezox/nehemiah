# Evals

Two questions, per scenario in `scenarios.yaml`:

1. **Trigger recall.** Given the prompt and the core, did the agent load the expected case file(s)? A miss here is the silent failure mode of the whole design.
2. **Behavior delta.** Run the same prompt with and without steering. Did the expected behaviors appear only, or more strongly, with steering? A rule that changes nothing is dead weight and should be cut.

Negatives matter as much as positives. An agent that moralizes over a refactor has failed. Over-triggering trains people to ignore the system.

## Running

No harness yet. Until there is one: run each prompt in the target tool with steering on and off, save transcripts under `evals/runs/<date>-<tool>-<model>/`, and grade against `expect_load` and `expect_behavior` by hand.

## Writing scenarios

- Do not use the vocabulary of the rules in the prompt. Test recognition, not keyword matching.
- One situation per scenario, except where the point is that two files should load together.
- Cite the paragraphs the expected behavior rests on.
- Add a scenario for every contested rule (see `CONTESTING.md`).
