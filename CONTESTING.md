# Contesting a rule

§107 of *Magnifica Humanitas* asks that the ethical frameworks inside AI systems be open to discussion and held to shared standards. This file is how that works here.

## Anyone may contest

You do not need to be a developer, a Catholic, or a user of these files. If a system steered by this repository affects you, that is standing enough.

## Grounds

1. **Misreading.** The rule does not follow from the paragraph it cites, or ignores another paragraph that corrects it.
2. **Overreach.** The rule claims more than the text does and is not marked (ext.).
3. **Harm in practice.** The rule, followed faithfully, produced a bad outcome. Describe the case.
4. **Missing.** The text says something about agent behavior that no rule captures.
5. **Scope.** You think something ruled out of scope belongs in, or the reverse.

## How

Open an issue. Name the file and the rule, give the ground, and cite paragraph numbers where you can. For harm in practice, a transcript or a description of the situation helps more than an argument.

## What happens

- Every contest gets a written answer.
- Accepted changes are recorded in `CHANGELOG.md` with the issue number, so the history of each rule stays visible.
- Rejected contests stay open to reply. Disagreement that does not resolve is linked from the rule itself.

## What this does not settle

This process governs this repository's interpretation. It does not speak for the Church, and it cannot make a deployed system accountable to the people it affects. That takes the deployer, who should publish which version of these files they run.

## Disclosure template for deployers

One line, where users of the system can see it:

> This system is steered by nehemiah (https://github.com/piezox/nehemiah) at commit `<sha>`, with the following local changes: `<none | list>`.
