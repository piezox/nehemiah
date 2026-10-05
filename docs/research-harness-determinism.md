# Research note: harness determinism and the limits of guaranteed rule-following

Working note for the blog post. Entries marked (read) were read first-hand; (snippet) come from abstracts or search results only.

## Thesis it supports

No current layer of the stack guarantees that a rule, especially a semantic or ethical one, is applied. Each layer removes a different kind of guarantee:

1. Inference is not deterministic, even at temperature 0.
2. Instructions decay over turns and collapse as rule count grows.
3. A harness can make structure deterministic, at a model-dependent cost, but not the agent's recognition of a situation.
4. A runtime gate can only certify policies over oracle-checkable predicates. Semantic predicates live on an ROC curve and are open to representation attacks.

Almost every Nehemiah rule is a semantic predicate. The exception is the structural subset of hard stop 2 (ext.): destructive tool calls, money, sends to third parties.

## 1. Inference nondeterminism

- Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference. arXiv 2506.09501. Batch size, GPU count, GPU version change outputs at T=0. (snippet)
- Necessary but Not Sufficient: Temperature Control and Reproducibility in LLM-as-Judge Safety Evaluations. arXiv 2606.26185. 690 API calls, two providers, three tiers: 1–2 of 7 borderline items non-reproducible under forced greedy decoding. Applies to our grader. (snippet)
- Introducing Background Temperature to Characterise Hidden Randomness in LLMs. arXiv 2604.22411. (snippet)
- Enabling Determinism in LLM Inference with Verified Speculation. arXiv 2601.17768. (snippet)

## 2. Instruction decay and rule-count collapse

- Measuring and Controlling Instruction (In)Stability in Language Model Dialogs. arXiv 2402.10962. Drift within eight rounds; attention decay. (snippet)
- SysBench: Can Large Language Models Follow System Messages? arXiv 2408.10943. Constraint violation, instruction misjudgement, multi-turn instability. (snippet)
- How Format, Instruction Count, and Context Length Shape Instruction Adherence. arXiv 2607.19257. Perfect-response rate reaches zero by N=80 rules for every model, format, and placement. Argues for a small core plus on-demand files over one concatenated file. (snippet)
- How Many Instructions Can LLMs Follow at Once? arXiv 2507.11538. (snippet)
- Evaluating Language Models on Following the Instruction Hierarchy. arXiv 2502.08745. (snippet)

## 3. Harness engineering

- Dhage. Harness Engineering for Predictable Agentic Systems: An Empirical Study of Deterministic Execution Constraints. arXiv 2608.26197 (Aug 2026). Finite-state control, forced tool selection, output validation, bounded retry. First pass: better reproducibility in 1 of 4 model-task cells, worse in 2. Adding schema-validated planning: 3 of 4 cells reach Determinism Index 1.000 at N=100. Cost is model-dependent and "must be measured, not assumed." (abstract read)
- Runtime Harness Adaptation for Deterministic LLM Agents. arXiv 2605.22166. (snippet)
- Learning to Control LLM Agent Harnesses with Offline RL. arXiv 2607.05458. Separates task quality from a Harness Maturity Score. (snippet)
- Confining Nondeterminism: AI-Driven Research Systems as DBMSs. arXiv 2607.10508. LLM as a stochastic compiler that may only edit a deterministic plan. (snippet)
- Harness Engineering for Auditable Enterprise LLM Agents. arXiv 2607.08028. (snippet)

## 4. What can be enforced at all

- Ray. What Can Be Enforced? A Theory of Certified Runtime Safety for Tool-Using Agents. arXiv 2607.22868 (Jul 2026), CMU. (read)
  - T1, expressiveness: a deterministic pre-execution gate enforces exactly the nonempty safety policies whose good prefixes a register automaton recognizes from oracle predicates. Caps, revocation, authenticate-before-access: exact. "Contains PII": semantic, needs a fallible judge.
  - T2, statistical: for a fixed judge, Neyman–Pearson gives the exact miss/false-block frontier. Conformal calibration gives a marginal certificate that can degenerate to block-all. Closed loop: a 3B judge cut attack success 4.7% to 0.4% while blocking 78% of calls; task success fell on a suite with no attacks at all.
  - Adversarial: a 16-token "administrator preapproval" suffix raised miss by 0.20–0.60 for 8 of 11 judges. "Naive calibration is not a security boundary."
  - Llama-Guard-3 as agent-policy judge: miss 0.46 at 10% false block. "Text safety does not transfer to tool-call safety."
  - Proposes a minimum reporting standard for guardrails: policy language and oracle interface, target operating point not AUC, whether blocking is visible to the agent, calibration population and adversarial margin.
- Dalrymple et al. Towards Guaranteed Safe AI. arXiv 2405.06624. The program the above instantiates. (snippet)
- Formal-enforcement line, all on the oracle-checkable subset: AgentSpec (ICSE 2026, arXiv 2503.18666); FORGE, Formal Policy Enforcement for Real-World Agentic Systems (arXiv 2602.16708); Agent Behavioral Contracts (arXiv 2602.22302); Autoformalization of Agent Instructions into Policy-as-Code (arXiv 2606.26649); Towards Enforcing Company Policy Adherence in Agentic Workflows (arXiv 2507.16459); ShieldAgent (arXiv 2503.22738); A Layered Translation Method for Runtime Guardrails (arXiv 2604.05229), which reserves runtime guardrails for controls that are "observable, determinate, and time-sensitive." (snippet)

## Implications for the post and the repo

- The no-guarantee claim is a theorem for the semantic part and an empirical finding for the rest. State it that way.
- Split the rules: structurally checkable ones can compile to gates and get a real guarantee; semantic ones get an ROC and an operating point. README's "roughly a third checkable in a transcript" is the same split. Consider tagging rules as `gate` vs `judge`.
- Our evals inherit nondeterminism at both ends (agent and grader). Three runs, two graders from one vendor, one host is below the floor these papers describe.
- Adopt Ray's reporting standard for whatever numbers we publish.
- The small-core-plus-router design is supported by the rule-count collapse result. Say so.
