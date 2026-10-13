---
name: model-evaluation
description: "Compare model quality, latency, reliability and cost using held-out tasks, controlled conditions, verified scoring and regression criteria."
---
# Model evaluation

Define the intended workload and acceptance thresholds before collecting results. Include correctness, tool use, invalid inputs, safety boundaries, latency, throughput and cost where relevant.

1. Freeze a representative held-out task set and rubric, with identifiers/hashes and independently verifiable expected results. Keep training and tuning examples separate; include edge cases and unfamiliar tasks.
2. Record model revision, quantization, serving configuration, hardware, tokenizer, sampling and prompt/tool versions. Compare the same tasks under controlled conditions and disclose any differences.
3. Repeat stochastic trials. Report sample size, variance/confidence intervals and failures/timeouts. A small smoke set is not statistical proof of superiority.
4. Prefer deterministic scoring for executable answers. Check factual citations and dates against primary sources. Calibrate model judges against human labels, randomize answer order and audit disagreement/bias.
5. Compare dimensions separately. Investigate regressions before deployment; aggregate scores can hide critical failures.
6. Report observed token usage, latency distributions, resource use and provider receipts. Do not infer cost or speed from a model name. Use `token-miser` for paired usage receipts when appropriate.

Repetition or degeneration can have several causes: data, optimization, tokenizer/template, serving or sampling faults. Investigate rather than assuming excess epochs. There is no universal algebraic formula mapping data size or epochs to quality.

Publish reproducible commands/configuration, dataset provenance, exact candidate identity, results and limitations. Protect private evaluation content and do not claim unseen benchmark performance.
