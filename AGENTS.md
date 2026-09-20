# AGENTS.md

Read `core/core.md` now. It is the always-on core of this repository's steering, and it applies to you while you work here. Its router table says when to open each file in `cases/`.

## Working on this repository

The content is agent steering derived from *Magnifica Humanitas* (Leo XIV, 2026). Every rule cites the paragraph it rests on. Conventions:

- A rule that claims more than the text says is marked `(ext.)`.
- Rule changes follow `CONTESTING.md` and are recorded in `CHANGELOG.md` with the issue number.
- The router table in `core/core.md` and the `description` front matter of each case file say the same thing in two places. Change one, change the other.
- Every contested rule gets a scenario in `evals/scenarios.yaml`. Scenario prompts must not reuse the vocabulary of the rules they test.
- Do not add the encyclical text to the repo. It is © Dicastery for Communication — Libreria Editrice Vaticana and not ours to license. Paraphrase and cite by paragraph number.
- Front matter stays tool-neutral: `name` and `description` only, plus `tier` in the core files.
