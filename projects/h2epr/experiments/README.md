# Experiments

This is the publication root for admitted experiment plans, receipts, attempt
ledgers, and closeouts. It is separate from [releases/](../releases/), which
publishes one verified run, and [reports/](../reports/), which interprets
generated processes.

No experiment is current. The implemented control surface consists of:

- [EXPERIMENT_STANDARD.md](../EXPERIMENT_STANDARD.md), which defines authority,
  parity, scheduling, failure, analysis, and claim rules;
- [experiment-plan.schema.json](../schemas/experiment-plan.schema.json) and the
  read-only admission command;
- [experiment-plan.md](../templates/experiment-plan.md) and
  [experiment-closeout.md](../templates/experiment-closeout.md); and
- the [experiment-planning Skill](../skills/experiment-planning/SKILL.md).

An accepted experiment uses `experiments/<experiment-slug>/` as its sole
current path. Raw attempts and model responses stay in ignored custody. A
tracked closeout must account for every planned row and terminal disposition.
