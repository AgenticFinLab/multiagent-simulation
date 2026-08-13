# H2EPR event-process simulation

This project studies whether autonomous participant agents can reproduce the
evolution of a real social event as an auditable process, rather than produce
one plausible retrospective narrative.

The near-term research chain is:

```text
Draft EPG and frozen evidence
  -> behavior/skill distillation
  -> participant artifacts and controlled world inputs
  -> participant-agent interaction
  -> sealed simulation trace
  -> deterministic Generated EPG
  -> offline alignment with a held-out real process
```

`contracts/v1/` is the Phase-0 contract baseline. It defines construction
identity, runtime information boundaries, communication, logical time, trace
and seal rules, Generated EPG structure, and evaluation separation. The
included tests use synthetic fixtures only. They do not implement or run an
H2EPR simulator, compiler, evaluator, scenario, or experiment.

V1 is a stable consumer interface, not a frozen blueprint for the complete
H2EPR system. Passing the Phase-0 tests establishes contract consistency only;
it does not establish simulator readiness, scientific fidelity, or permission
to begin a later phase. Future scenarios, configurations, internal modules,
and tests may evolve without renaming or weakening the accepted V1 contract.
Contract-breaking changes require an explicit successor contract version;
compatible implementation changes do not create audit-round public versions.

The first future implementation target is an H2EPR-0288 Panic of 1907 Rule
canary. A later H2EPR-0616 SingHealth canary is a required anti-finance gate.
Passing these contracts is necessary, but it does not authorize a later
implementation phase or a scientific fidelity claim.

Frozen event assets remain under `data/h2epr/`. They are inputs with a strict
read-only boundary, not project source files. Evaluation references are never
construction or runtime inputs.

## Repository and packaging status

`projects/h2epr/` is currently a repository research surface. It is not
discovered or distributed as an installed Python package by `setup.py`.
Reusable runtime/package ownership, final scenario and configuration locations,
and concrete runner/simulator classes require a Phase-1 ADR informed by
implementation evidence. Standard MASim scenarios in `examples/` and
top-level `configs/` remain separate unless a later reviewed architecture
decision changes that boundary.

See [ARCHITECTURE.md](ARCHITECTURE.md) for present boundaries,
[EVOLUTION.md](EVOLUTION.md) for the evolution policy, and
[tests/README.md](tests/README.md) for lightweight offline validation.
