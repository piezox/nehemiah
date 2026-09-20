# Nehemiah

Agent steering files derived from *Magnifica Humanitas*, Leo XIV's 2026 encyclical on safeguarding the human person in the time of artificial intelligence.

A small always-on core, plus case files that load when their situation is present. Every rule cites the paragraph it comes from.

## Why the name

The encyclical sets two building sites side by side. Babel: one language, one direction, imposed from above. And Jerusalem under Nehemiah: the wall rebuilt piece by piece, each family responsible for the stretch in front of its own house (§7–10, §13). This repository is built the second way. Each file owns one stretch of wall.

## What this is, and is not

- It is one person's translation of a moral text into agent behavior. It is not a Church document and carries no endorsement.
- The encyclical says its doctrine is a process of shared discernment, not a handbook of norms to apply (§24, §27). So these rules are a floor, and `cases/design-review.md` hands the actual judgment back to humans.
- Scope is the social principles the text applies to AI and digital systems. Doctrinal positions that do not concern agent behavior (e.g. §55, §165, §192–194) are out of scope. That is a choice, stated here so it can be argued with.
- The encyclical text is not included. It is © Dicastery for Communication, Libreria Editrice Vaticana. Read it at vatican.va. Rules here paraphrase and cite by paragraph number.

## Why it is public

§107 warns that aligning AI to values is not enough if those values are set by a few and become the invisible infrastructure of the system. §198 says it still matters to instil values and sound judgment in the systems we build.

A steering file is exactly a few people's values injected silently. The answer to both paragraphs is to make it visible: public, versioned, cited rule by rule, and open to contest. See `CONTESTING.md`.

## Layout

```
core/
  core.md         always on (mini tier, the default)
  core.nano.md    always on, for tight context budgets
cases/            loaded when the situation is present
  decisions-about-people.md
  work-automation.md
  truth-and-content.md
  data-and-attention.md
  minors.md
  irreversible-actions.md
  defense-dual-use.md
  companionship.md
  design-review.md
evals/            scenarios for trigger recall and behavior change
scripts/
  build-full.sh   concatenates everything into dist/full.md
```

Rules marked (ext.) extend the text's logic to cases it does not name.

## Using it

The files are plain Markdown with `name` and `description` front matter, which is what description-based loaders read.

- **Tools with on-demand skills or rules** (Claude Code skills, Cursor rules, Copilot instructions, Kiro steering): put `core/core.md` wherever always-on instructions live, and register each file in `cases/` as an on-demand skill or rule using its `description` as the trigger.
- **Tools with a single instruction file** (AGENTS.md and similar): paste `core/core.md`, and keep `cases/` in the repo so the agent can open them by path. The router table in the core tells it when.
- **No on-demand loading at all**: run `scripts/build-full.sh` and use `dist/full.md`. Costs more context, removes the risk of a missed trigger.

## Known limits

- Activation is the weak point. Ethical relevance is not a file glob, so loading depends on the agent noticing the situation. A missed trigger fails silently. That is why the hard stops live in the core.
- Roughly a third of the rules are checkable in a transcript today. The rest depend on the agent's judgment ("flag designs that..."). `evals/` exists to find out which rules actually change behavior.
- Steering shapes behavior within what the underlying model already permits. It does not override it.

## License

Rules and code: MIT, see `LICENSE`. The encyclical itself is not covered and not included.
