---
name: Eval result
about: Report a run of the eval harness on a model, host, or deployment
title: "Eval result: <model> on <host>"
labels: eval-result
---

## Provenance

Paste the line `evals/run.py` and `evals/grade.py` print. A result without it cannot be compared with others and will be asked for it.

```
nehemiah <commit> · scenarios <hash> · harness <hash> · <host> · model <model> · graders <…> (grade.py <hash>, checks <hash>)
```

If you graded by hand, say so here in place of the graders.

## Numbers

Recall table and pass rates as printed, or your own table with the same columns. Runs per condition:

## What you saw

Anything the numbers do not show: a refusal that made no sense, a case file that loaded for no reason, a reply you would not want a user to get. Quote the reply; do not paste whole transcripts with personal data in them.

## Deployment (if this comes from real use, not the scenario set)

Version deployed (commit), how many sessions, how often each case file loaded, how often a hard stop fired. Aggregates only, no transcripts.
