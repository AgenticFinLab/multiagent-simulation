# Repository and experiment layout

The stable current repository boundary is:

```text
masim/                    reusable framework
examples/                 current standard MASim scenario examples
configs/                  current standard MASim run configurations
projects/h2epr/           accepted H2EPR Phase-0 V1 contract and offline tests
data/h2epr/               frozen read-only development fixtures
EXPERIMENT/H2EPR/         future generated run workspaces
simulation-results/H2EPR/ future curated release artifacts
```

Earlier Phase-0 planning proposed `projects/h2epr/scenarios/` and
`projects/h2epr/configs/` as default locations for future H2EPR assembly and
run composition. They are provisional planning defaults, not reserved paths,
installed-package ownership, or a V1 consumer compatibility promise. Neither
directory exists in the current candidate. A reviewed Phase-1 ADR, informed by
implementation and test evidence, may retain, refine, or replace them and may
choose different runtime, package, scenario, configuration, or future-test
ownership.

Research projects may combine reusable framework extensions, multiple
scenarios, compilers, evaluators, and experiment protocols; that breadth does
not belong in one ordinary example. Conversely, project-specific event
identity, participant choices, and behavior policies do not belong in generic
MASim core.

Any future code boundary must distinguish domain-neutral reusable framework
capabilities from event-specific identity and policy, keep evaluation-only
Reference readers from flowing into construction or runtime, and preserve the
accepted append-only trace/seal semantics. A separate evaluation responsibility
and an opt-in runner/simulator remain useful design constraints, but their
module and package locations are Phase-1 ADR decisions rather than Phase-0
path contracts.

`examples/` and top-level `configs/` remain the current standard MASim
convention, and this candidate places no H2EPR assembly there. A later ADR may
reconsider H2EPR-specific placement, but it must prevent duplicate source
ownership, ambiguous run configuration, and event-specific identities in
generic MASim core.

Phase-0 creates only this project contract and offline-test surface. It creates
no runnable scenario and no experiment or simulation-result directory. This
layout clarification does not authorize Phase 1 or imply runtime or scientific
readiness. Compatible implementation movement does not break V1 or create an
audit-round public version; see `projects/h2epr/EVOLUTION.md` for the public
evolution policy.
