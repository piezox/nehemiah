# An encyclical, as steering files any agent can load

*How I turned Magnifica Humanitas into files that guide an AI agent while it works, what the first runs show, and what is still open.*

I spend a good part of my days writing steering files for coding agents. They are small Markdown files that tell an agent how to behave: what to do, what never to do, when to stop and ask.

When *Magnifica Humanitas* came out in May, I read it as a text for the people who build and run AI systems. It says what those systems should never do to a person. It says what a decision about a person has to keep: a human who answers for it, a reason the person can read, a way to appeal. Those are instructions, and I wanted them in the form an agent reads while it is working.

So I built [Nehemiah](https://github.com/piezox/nehemiah)*, a small public repo. It holds the encyclical's principles as steering files, and an eval harness to check whether they change what an agent does. It is my translation, not a Church document, and it is meant to be argued with.

## Where the approach comes from

I took the shape from three things I saw this year.

The first is Paper2Agent, from Jiacheng Miao, James Zou and colleagues at Stanford (Nature 2026). It turns a research paper into an MCP server and a Markdown skill. A second agent, not the one that built the tools, tests each tool against the paper's own results before release. They also measured one constraint: the agent has to decline questions the paper cannot answer. They shuffled the paper–question pairs and got 100% correct refusals. That is what I wanted for a moral text. Decide what a pass looks like, run with and without the rule, report the difference.

The second is how labs now publish their values. OpenAI's Model Spec is a versioned Markdown repo with eval prompts. Anthropic's constitution is CC0 and explains its reasons. A rule in a repo has a history, and you can open an issue against it.

The third is the research on context files. Adherence drops as the rule count grows, and reaches zero around eighty rules for every model and format tested. In Paper2Agent's own ablation, replacing the MCP tools with Markdown skill files cost a quarter of the accuracy. Form matters as much as content.

Nehemiah puts the three together. It is a repo, so every rule is versioned and open to contest. That is what §107 of the encyclical asks for when it warns against values set by a few and turned into invisible infrastructure. And it keeps a small core always on, with the rest loaded when needed, so the agent carries about twenty rules at a time instead of a hundred and thirty.

## What Nehemiah is

The encyclical opens with two building sites. Babel: one language, one direction, imposed from above. And Jerusalem under Nehemiah: the wall rebuilt piece by piece, each family responsible for the stretch in front of its own house (§7–10, §13). The repo is built the second way. Each file owns one stretch of wall.

- A small always-on core: identity, four hard stops, a gate question, a router table.
- Nine case files that load only when their situation is present: decisions about people, work automation, truth and content, minors, irreversible actions, and so on.
- Every rule cites the paragraph it comes from. Where a rule goes beyond the text, it is marked `(ext.)`.
- An eval harness that runs every scenario with steering on and off, in isolated directories, and has the replies graded blind. The scenario prompts avoid the vocabulary of the rules they test, so the agent has to recognize the situation rather than match a keyword.
- One install command that copies the files into a project, points its AGENTS.md at them, and prints the disclosure line the deployer should publish.

Two design choices come from how agents load files. The hard stops live in the core, not behind a trigger, because a missed trigger must not remove them. And a file that changes nothing in the on/off comparison is a candidate for cutting, because dead weight teaches people to ignore the whole thing.

Two neighbours are worth knowing. [encyclical.ai](https://encyclical.ai/) reviews a design after the fact against a 30-criterion rubric. [magnifica-humanitas-mcp](https://github.com/grinnellian/magnifica-humanitas-mcp) looks up paragraphs at runtime. Nehemiah sits between them: it steers during the work and measures whether the steering took.

The encyclical text is copyrighted and not in the repo. Read it at vatican.va.

## What the runs show

One model, one host, three runs per condition. Two Claude models graded the replies blind and agreed on 92% of the checks. One of them refused to grade the dual-use scenario, so that one rests on a single grader.

- Activation works when the files are local. A one-line pointer to the core was followed 90 times out of 90, and the agent behaved the same as with the core pasted into AGENTS.md. A URL to the same files worked less well. The agent fetched it in all 33 runs, but it got a summary. In the median fetch, none of the rule lines arrived word for word, and the pass rate was 0.81 against 0.92 with local files.
- Steering changes behavior where the model has no default of its own. On scenarios built around such rules, the pass rate went from 0.39 without steering to 0.87 with it.
- Most of that comes from the core. With its case file removed, a scenario still passed at 0.77 on average. The largest losses were for data and attention, irreversible actions and design review, about 0.2 each. I kept all nine for now, because three runs cannot rank them, and "the model already does this" is true of one model.
- The hard stops held when the user pushed back with authority. "Legal signed off" did not move the rule against exploiting a low mood. Without steering, the model shipped that trigger in three runs out of three.
- One thing I did not plan: in the first runs the agent told users about its own steering in most replies, including a 13-year-old. I changed the rule. Now it mentions the steering only when it stops at a hard stop or when asked. It does so in 10 runs out of 33, all in scenarios where a hard stop applies.

Every number in this section comes from runs with this provenance line:

```text
nehemiah 31079c1 · scenarios 433ee3ca0ce8 · harness 210fd8af8310 · claude-code 2.1.289 · model claude-fable-5-1 · graders claude-opus-5-5, claude-sonnet-5 (grade.py 8f0e98504ee0, checks 433ee3ca0ce8)
```

On the model I tested, the approach works as designed.

## What is still open

A steering file works within what the model already allows. No layer of the current stack can guarantee that a rule about people is applied. Gloaguen et al. found that AGENTS.md files do not raise task success. McMillan found that compliance decays within a session. One part of Nehemiah could get a real guarantee: the destructive commands and payments in the irreversible-actions rule, which a pre-execution gate can check. Everything else gets a probability, and the harness exists to measure it.

Here are the questions I would like numbers on, from anyone working on agent evaluation, alignment, or the harnesses themselves:

- Trigger recall on its own. Did the agent notice the situation at all? That has to be measured apart from whether it behaved well once it noticed.
- Decay within a session. My pushback test is two turns apart. What happens over thirty turns, and does a hard stop in the core last longer than a rule behind a trigger?
- Constraints, not just capabilities. Every capability benchmark should have a companion that measures correct refusal and correct handoff to a human.
- Over-triggering. An agent that moralizes over a refactor has failed too. Negatives belong in the scenario set.
- Other models and other harnesses. My runs are one model in one harness, and Claude also helped write the rules, the scenarios, and the checks. I want to see the numbers when the tester and the tested are not related.

Nehemiah is built so that other people can answer these with the same tools. Every result carries the version of everything it depends on: the commit of the rules, the scenario set, the checks, the model, the host, the graders. The harness prints that line, so your numbers and mine can be compared. Four ways to add to it:

- Run it on a model or a host I did not. Post the table and the provenance line in an issue.
- Grade twenty replies by hand and compare with the model graders.
- Bring a real case. If an agent steered by these files did something wrong to you, describe it. It becomes a scenario written from your side.
- If you deploy it, share the small numbers: which version, how often each file loaded, how often a hard stop fired. No transcripts needed.

The rules themselves stay open to argument, which is what §107 asks for. If you think a rule misreads the paragraph it cites, open an issue. You do not need to be a developer or a Catholic. If a system steered by these files affects you, that is standing enough.

The repo is here: [github.com/piezox/nehemiah](https://github.com/piezox/nehemiah). Tell me what breaks.

---

*If you are curious about the name: Nehemiah was the man who rebuilt the walls of Jerusalem after the exile. The book that carries his name lists who built what, family by family, each one the stretch in front of its own house. The encyclical sets that site against Babel, where one tower went up in one language under one plan (§7–10, §13). The repo is organized the first way: one file per stretch of wall, and every stretch has a name on it.

*Disclosure: the research and drafting for this post were done with AI assistants. The blind grading was done by two Claude models, so grader and graded share a vendor. Paper2Agent figures are first-hand from the paper and its supplement. The rule-count result is from an arXiv abstract (2607.19257), not yet read in full.*

*Magnifica Humanitas was signed on 15 May 2026 and published on 25 May 2026. Paragraph references follow the vatican.va text.*
