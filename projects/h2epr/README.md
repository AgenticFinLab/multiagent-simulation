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

The G3 engineering baseline consumes one sealed G2 matrix row through an
opt-in paired phased runtime:

```text
RuntimeScenarioBundle + profile/seed row
  -> H2EPR Rule participants
  -> ten ordered per-tick barriers
  -> authoritative world reduction and delayed-message transport
  -> hash-chained trace, TickSeals and RunSeal
  -> deterministic replay and generated-only P007 annotations
```

Domain-neutral runtime values, transport, reduction, trace and seal mechanics
live under `masim.integrations.event_process`; the H2EPR adapter, fixed Rule
policy, world effects, P007 detectors and runner remain under
`src/h2epr/runtime/`. The standard `GeneralSimulator` path is unchanged. The
accepted canary runs 41 logical ticks across the nine profile/seed rows and is
Rule-only, Reference-blind, `full_draft_exposed`, `architecture_demo_only`, and
not historically calibrated. It proves an executable deterministic engineering
chain, not historical fidelity or scientific readiness.

V1 is a stable consumer interface, not a frozen blueprint for the complete
H2EPR system. Passing the Phase-0 tests establishes contract consistency only;
it does not establish simulator readiness, scientific fidelity, or permission
to begin a later phase. Future scenarios, configurations, internal modules,
and tests may evolve without renaming or weakening the accepted V1 contract.
Contract-breaking changes require an explicit successor contract version;
compatible implementation changes do not create audit-round public versions.

The current implementation target is the H2EPR-0288 Panic of 1907 Rule canary.
Its next compiler stage must normalize and validate the immutable G3 output
package before producing a deterministic Generated EPG. A later H2EPR-0616
SingHealth canary remains a required anti-finance gate. Passing an engineering
Gate does not authorize a later phase or a scientific fidelity claim.

Frozen event assets remain under `data/h2epr/`. They are inputs with a strict
read-only boundary, not project source files. Evaluation references are never
construction or runtime inputs.

## Repository and packaging status

`projects/h2epr/` is a repository research surface. Its project-specific G1–G3
source is explicitly repository-local and is not discovered or distributed as
an installed Python package by `setup.py`. The reviewed G3 placement keeps
domain-neutral event-process integration in the distributable `masim` package
and H2EPR-specific runtime/configuration under the project root. This split is
an evolvable canary boundary, not a permanent package guarantee. Standard MASim
scenarios in `examples/` and top-level `configs/` remain separate.

See [ARCHITECTURE.md](ARCHITECTURE.md) for present boundaries,
[EVOLUTION.md](EVOLUTION.md) for the evolution policy, and
[tests/README.md](tests/README.md) for lightweight offline validation.
The G1 incubation rationale and pre-G3 reconsideration point are recorded in
[ADR-0001](decisions/ADR-0001-g1-project-local-incubator.md). The G2 artifact
and EventBundle seam is recorded in
[ADR-0002](decisions/ADR-0002-g2-artifacts-event-bundle-canary.md). The adopted
G3 phased-runtime split is recorded in
[ADR-0003](decisions/ADR-0003-g3-phased-runtime-placement.md).
