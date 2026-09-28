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
  install.sh      copies core and cases into a project, points its AGENTS.md at them
  build-full.sh   concatenates everything into dist/full.md
```

Rules marked (ext.) extend the text's logic to cases it does not name.

## Using it

```
git clone https://github.com/piezox/nehemiah /tmp/nehemiah
/tmp/nehemiah/scripts/install.sh path/to/your/project
```

This copies `core/` and `cases/` into `<project>/nehemiah/`, adds a one-line pointer to the project's AGENTS.md, records the commit in `nehemiah/VERSION`, and prints your disclosure line. To pin a version, check it out before installing. To update, delete `nehemiah/` and run it again.

Measured on one model in Claude Code, 3 runs per scenario: the agent followed the pointer and read the core 33/33 times, and behaved the same as with the core pasted inline (#4, #13).

- **Keep the files local.** Pointing AGENTS.md at a URL instead (raw GitHub, a hosted SKILL.md) dropped recall from 32/33 to 24/33, and the agent received a summary of the rules rather than the rules: median 0% of lines arrived verbatim (#13). A URL is fine when a person asks for a review on purpose ("use <url> to review this design"). It does not work as steering.
- **Tools with on-demand skills or rules** (Claude Code skills, Cursor rules, Copilot instructions, Kiro steering): put `core/core.md` wherever always-on instructions live, and register each file in `cases/` as an on-demand skill or rule using its `description` as the trigger. Not yet measured.
- **No on-demand loading at all**: run `scripts/build-full.sh` and use `dist/full.md`. It removes the risk of a missed trigger but puts about 130 rules in context, and adherence falls as rule count grows. Not yet measured.

## Deploying

A steered agent does not tell people about its steering unless it stops under a hard stop or is asked. Visibility is the deployer's job [§107]: publish the disclosure line that `install.sh` prints, with the commit and any local changes, where users of the system can see it. See `CONTESTING.md`.

## Known limits

- Activation depends on the agent noticing the situation; ethical relevance is not a file glob. With the core loaded, the right case files loaded in 29–32 of 33 scenario runs. A missed trigger fails silently. That is why the hard stops live in the core.
- Measured on one model (Fable 5.1), steering raised the pass rate on file-specific scenarios from 0.53 to 0.82. Three case files add what the core cannot: `design-review`, `defense-dual-use`, `irreversible-actions`. The other six showed no measurable effect beyond the core on this model, on one scenario each; they stay until a second model has been run (#6, #10).
- Roughly a third of the rules are checkable in a transcript today. The rest depend on the agent's judgment ("flag designs that..."). `evals/` exists to find out which rules actually change behavior.
- Steering shapes behavior within what the underlying model already permits. It does not override it.

## License

Rules and code: MIT, see `LICENSE`. The encyclical itself is not covered and not included.
