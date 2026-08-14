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
contract tests use synthetic fixtures only.

The repository-local `src/h2epr/construction/` incubator is the bounded G1
implementation candidate for explicit-manifest source loading and typed,
lossless Construction IR. It enforces Reference-blind path handling, four
closed construction identities, evidence minimization and deterministic V1
synthetic snapshots. Its architecture-generic adapter may inspect only an
explicitly authorized non-Reference development manifest; full-draft-derived
outputs remain permanently demo-only. Synthetic strict-policy tests exercise
fail-closed rules, but no actual clean strict build is claimed.

The project-local G2 candidate adds declarative construction after the IR:

```text
Construction IR
  -> reviewed EntityRegistry and reversible roster/loss report
  -> generic ParticipantArtifacts and declarative Rule policies
  -> normalized, dimensionless sensitivity world
  -> three sealed construction/EventBundle profile pairs
  -> nine profile/seed execution-matrix rows
```

The three profiles are explicit assumptions, permanently
`full_draft_exposed`, `architecture_demo_only`, and not historically
calibrated. The target-derived bundles are generated only into the ignored
local evidence area; tracked G2 fixtures are synthetic. The G2 API has no
runtime entry point and does not import MASim, Ray, model, retrieval, or
evaluation code.

Neither construction layer implements or runs MASim integration, a participant
turn, reducer, tick barrier, message transport, trace, compiler, evaluator,
scenario, or experiment. Technical completion does not itself establish a
Gate decision.

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

`projects/h2epr/` is currently a repository research surface. Its G1 source is
an explicitly exposed repository-local incubator; it is not
discovered or distributed as an installed Python package by `setup.py`.
Reusable runtime/package ownership, final scenario and configuration locations,
and concrete runner/simulator classes require a later reviewed decision
informed by implementation evidence. Standard MASim scenarios in `examples/` and
top-level `configs/` remain separate unless a later reviewed architecture
decision changes that boundary.

See [ARCHITECTURE.md](ARCHITECTURE.md) for present boundaries,
[EVOLUTION.md](EVOLUTION.md) for the evolution policy, and
[tests/README.md](tests/README.md) for lightweight offline validation.
The G1 incubation rationale and pre-G3 reconsideration point are recorded in
[ADR-0001](decisions/ADR-0001-g1-project-local-incubator.md). The G2 artifact
and EventBundle seam is recorded in
[ADR-0002](decisions/ADR-0002-g2-artifacts-event-bundle-canary.md).
