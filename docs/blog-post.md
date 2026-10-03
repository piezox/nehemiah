# Blog post — draft outline

Working title: *From reading to running: publishing a moral text as agent steering*

Thesis: a text that wants to change how AI systems behave should ship as something agents load, test, and contest, not only as something people read. The unit of publication moves from the article to the repository.

## 1. Papers are becoming agents

- Paper2Agent[^p2a] turns a paper's code into an MCP server and the paper itself into a Markdown skill[^skills] (`paper2skill`[^p2a-code]); a fresh verifier agent, distinct from the builders, tests each tool against the paper's own results before release. The reader no longer adapts the method by hand; the method arrives as a callable, tested tool. The authors ship their own paper as a skill.
- The same move is visible in how labs publish values: OpenAI's Model Spec[^modelspec] is a versioned Markdown repo with eval prompts; Claude's constitution[^constitution] is released CC0 and explains reasons rather than listing rules.
- Contrast: the Rome Call[^romecall] (2020) stayed a signed document. Principles with no executable form.

## 2. A moral text becoming steering

- What Nehemiah does: always-on core, case files loaded on situation, every rule cited by paragraph, `(ext.)` where it goes beyond the text.
- Paper2Agent packages capabilities; this packages constraints. "Tested" is harder to define for a constraint, but not undefined: the one constraint Paper2Agent measured[^p2a] (decline questions the paper cannot answer) it tested by permuting paper–question pairs, 100% correct rejection.
- Why a repo and not an essay: §107[^mh] (values set by a few become invisible infrastructure). The answer is visibility: public, versioned, contestable through issues (`CONTESTING.md`).
- Neighbours: encyclical.ai[^encyclical] (review rubric, after the fact), magnifica-humanitas-mcp[^mhmcp] (paragraph lookup at runtime). Steering during the work is the gap. encyclical and Nehemiah both take the Babel image from §7–10; encyclical links section anchors, Nehemiah cites paragraph numbers.

## 3. Does steering actually work?

- Evidence against: context files do not raise task success and cost >20% more (Gloaguen et al.[^gloaguen]); file structure has no detectable effect on adherence, and compliance decays within a session (McMillan[^mcmillan]). Paper2Agent's own ablation[^p2a-code]: replacing MCP tools with Markdown skill files dropped accuracy from 99.3% to 73.3% on AlphaGenome. That measured capabilities, not constraints, but it is the closest direct comparison of text against executable form.
  - "A callable endpoint only works if the agent decides to call it." (Claude, in a working session on this repo.) Executable form does not remove the activation problem; it moves it.
- What this repo does about it: hard stops in the core, not behind a trigger; on/off eval runs per scenario.
- What the evals show (one model): once the core is in context, activation is not the weak point. Run 3 compared the core pasted into AGENTS.md against a one-line pointer to it, three runs each, same harness: the pointer was followed 33/33 times, and case-file recall was 31/33 inline vs 32/33 pointer. Run 1's 5/9 came from its setup, not from the pointer. Behavior, graded blind by two models (kappa 0.94): 0.857 inline vs 0.78 pointer, p = 0.10 at three runs. A remote pointer (raw GitHub URL, the form encyclical.ai uses) is worse: the core was fetched in 27/33 runs, recall fell to 24/33, and WebFetch delivered a summary, with a median of 0% of rule lines verbatim. For always-on steering the files must be local; a URL works only when the user asks for it. The behavior delta (run 2) concentrates in three case files (people decisions, work automation, design review); two files change nothing the model does not already do. The core made the agent narrate its steering unprompted in about 70% of steered runs, including to a 13-year-old and inside an emotional-support reply. The rule now allows it only when stopping under a hard stop or when asked; §107 visibility moves to the deployer's disclosure line. Mentions fell from 25/33 to 15/33, all but one in hard-stop scenarios, with behavior unchanged (72/84 on the same checks).
- Open: three runs, one grader, one host. Report the numbers with those limits stated.

## 4. Invitation

- Contest a rule by opening an issue. Rules change with a changelog entry and an eval scenario.

## Open items

- Publication date: vatican.va URL and `core/core.md` say 15 May 2026; Wikipedia says published 25 May. Confirm (likely signed vs released).
- Nature news piece on Paper2Agent (paywalled) not yet read.
- Authorship disclosure for the post itself: one line saying the research and drafting were done with Claude, and quotes from Claude are attributed inline. Paper2Agent figures above are first-hand from the paper and supplement bundled in their repo (`skills/paper2agent/paper2agent-paper/references/`).
- Sources marked (snippet) below come from search results, not a first-hand read.

## Further reading

Not yet cited in the text.

- Context files in practice: Treude, Baltes, Cheong, [*Operationalizing Ethics for AI Agents: How Developers Encode Values into Repository Context Files*](https://arxiv.org/abs/2605.05584), arXiv 2605.05584 (2026); [*Agent READMEs: An Empirical Study of Context Files for Agentic Coding*](https://arxiv.org/abs/2511.12884), arXiv 2511.12884 (snippet).
- Governance and contestability: Huang et al., [*Collective Constitutional AI*](https://arxiv.org/abs/2406.07814), FAccT 2024 (snippet); Abiri, [*Public Constitutional AI*](https://arxiv.org/abs/2406.16696) (snippet); Caputo, [*Alignment as Jurisprudence*](https://arxiv.org/abs/2605.08416), Yale J. Law & Tech. 27:390.
- Church documents: DDF / DCE, *Antiqua et nova* (Jan 2025) (snippet).

[^p2a]: Miao, Davis, Zhang, Pritchard, Zou. [*Reimagining research papers as interactive and reliable AI agents*](https://www.nature.com/articles/s41586-026-11044-y). Nature (2026). [Preprint](https://arxiv.org/abs/2509.06917).
[^skills]: [Agent Skills specification](https://agentskills.io/specification). (snippet)
[^p2a-code]: [Paper2Agent code](https://github.com/jmiao24/Paper2Agent), [live agent](https://paper2agent.ai/live). Markdown-skill ablation and out-of-scope benchmark: supplement, ablation and robustness notes bundled in the repo.
[^modelspec]: [OpenAI Model Spec](https://github.com/openai/model_spec): CC0, versioned, eval prompts. (snippet)
[^constitution]: Anthropic, [Claude's Constitution](https://www-cdn.anthropic.com/cffd979fd050fbc0d8874b8c58b24cc10554e208/claudes-constitution_webPDF_26-01.26a.pdf): Jan 2026, CC0. (snippet)
[^romecall]: [Rome Call for AI Ethics](https://www.romecall.org/) (2020). (snippet)
[^mh]: Leo XIV, [*Magnifica Humanitas*](https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html). Cited by paragraph number (§).
[^encyclical]: [mrjf/encyclical](https://github.com/mrjf/encyclical), [encyclical.ai](https://encyclical.ai/): review skill, 30-criterion rubric scored 0–3 into a deterministic 0–100 Babel-to-Jerusalem score, deal-breaker flags, issue-driven reviews, integration tests across Codex, Claude, and Copilot CLIs.
[^mhmcp]: [grinnellian/magnifica-humanitas-mcp](https://github.com/grinnellian/magnifica-humanitas-mcp): runtime paragraph lookup from vatican.va.
[^gloaguen]: Gloaguen, Mündler, Müller, Raychev, Vechev. [*Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?*](https://arxiv.org/abs/2602.11988) arXiv 2602.11988 (2026). (snippet)
[^mcmillan]: McMillan. [*Instruction Adherence in Coding Agent Configuration Files: A Factorial Study of Four File-Structure Variables*](https://arxiv.org/abs/2605.10039). arXiv 2605.10039 (2026).
