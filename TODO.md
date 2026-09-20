# TODO

Open items carried over from the design conversation (2026-09-20). Delete this file once they are tracked as issues.

## Before first push

- [x] LICENSE: confirm the copyright holder name.
- [x] `cases/companionship.md`: the rule "when the person is in real distress or at risk, prioritize getting them to human help" has no paragraph behind it. Mark it (ext.).
- [x] `chmod +x scripts/build-full.sh`
- [ ] `git init -b main`, first commit, create the GitHub repo with description and topics (`agents-md`, `agent-skills`, `ai-ethics`, `magnifica-humanitas`).
- [x] GitHub code search, logged in, to check nobody has done this already: `"Magnifica Humanitas" path:AGENTS.md OR path:SKILL.md OR path:.cursor`

## Decisions to revisit

- [ ] Core has four hard stops. Started as two (people decisions, irreversible actions); fabricated content and attention/minors were added. Each stop makes the core heavier and shrinks the "object once, human decides" zone. Keep or cut.
- [ ] Front matter is `name` + `description` only, tool-neutral. Decide whether to ship per-tool adapters (Claude Code skills layout, Cursor rules, Kiro steering, Copilot instructions) or just document the mapping.
- [ ] Scope exclusions (§55, §165, §192–194) are stated in the README. Expect this to be the first thing contested.

## Evals (do this before the blog post)

- [ ] Run the 11 scenarios in one tool, steering on and off. Save transcripts under `evals/runs/`.
- [ ] Measure trigger recall first. If the router does not load the right files, nothing else matters.
- [ ] Cut rules that change nothing.
- [ ] Build a harness once the manual pass shows what is worth automating.

## Ideas

- [ ] Pair with `magnifica-humanitas-mcp` (fetches the text from vatican.va at runtime) so an agent can pull the cited paragraph when a rule fires or is contested. Keeps the encyclical text out of this repo.
- [ ] Deployers should publish which version of these files they run (see end of `CONTESTING.md`). Consider a one-line disclosure template.

## Blog post

Angle: people have made the encyclical readable by machines (EPUBs, Markdown, an MCP server); nobody has made it binding on them. The tension inside the text is the spine: §107 (values set by a few become invisible infrastructure) against §198 (instil values anyway). A public, cited, contestable steering system answers both. Be honest that §27 says the doctrine is not a handbook, so this is a translation with judgment in it, and report what the evals actually showed.
