---
name: experiment-planning
description: Define and admit a versioned H2EPR run matrix with package parity, seeds, model provenance, scheduling, failures, analysis contracts, and claim limits.
---

# Experiment planning

Read [references/guide.md](references/guide.md) for matrix construction,
comparison parity, custody and retry ledgers, model controls, admission
failures, and the boundary between planning and execution.

## Read first

Read `EXPERIMENT_STANDARD.md`, `BENCHMARK_PROTOCOL.md`, the selected package
and binding entries, `templates/experiment-plan.md`, and every analysis
definition named by the plan.

## Procedure

1. State the bounded comparison and its unsupported conclusions.
2. Select only accepted package/backend pairs. Pin package and binding hashes;
   never treat a planned backend as executable.
3. Give each row an explicit seed set and unique ignored custody root.
4. For LLM or RuleLLM, pin model/version, service mode, prompt and response
   contract hashes, all decoding parameters with bases, and attempt limit.
5. Form comparison groups. Require event/package/seed parity within an event;
   require distinct events, one backend, and equal seeds across events. Keep
   the complete model-control signature equal across cross-event model rows and
   between LLM and RuleLLM rows in the same within-event group.
6. Pin simulation-only and group-specific analysis contracts before results.
7. Declare concurrency, progress, wall/stall timeouts, retryable classes,
   finite retries, and preservation of failed custody.
8. Seal the plan and run `h2epr.cli admit-experiment`. Review every check in
   the admission receipt.
9. Stop after admission unless execution is separately authorized. Admission
   does not create output, prove model availability, or establish a result.

## Stop conditions

Stop on unsafe, aliased, or reused custody, identity drift, unavailable
binding, missing or unequal model controls, seed or parity mismatch, unpinned analysis, incoherent
timeouts/retries, or incomplete claim exclusions.
