# ADR-0010: accept the SingHealth configuration-admission boundary

- Status: accepted
- Date: 25 August 2026
- Scope: H2EPR-0616 bounded configuration admission
- Resolved decisions: OD-ADM-01 through OD-ADM-04

## Context

The accepted SingHealth Scenario Configuration uses explicit institutions,
responsibility units, technical assets, flat opening records, materialized
structural variants, and a publication-facing consolidated mapping. The
existing admission schema and loader encode the different, accepted Panic of
1907 configuration shape. Rewriting either event into the other's shape would
change accepted semantics; changing the existing schema in place would change
an already published validation identity.

The compatibility review found no Contracts V1 loss. It found a project-local
configuration-admission gap: the exact SingHealth release needed a second,
explicitly selected representation profile and event-neutral graph checks.

## Decision

### `OD-ADM-01` — exact admission object

Admit only the exact accepted Scenario Configuration and release manifest.
Admission may validate and canonicalize those bytes but may not repair,
rewrite, normalize their meaning, add evidence, or fit a known outcome.

### `OD-ADM-02` — versioned project-local profile

Add the semantic Scenario Configuration schema and admission surface v0.2.
Dispatch only from the declared format identity. Retain the v0.1 schema,
Panic admission behavior and receipt, and Contracts V1 unchanged. The accepted
format token retains its `candidate` wording because admission preserves the
released document rather than silently renaming it.

### `OD-ADM-03` — static semantic-reference boundary

Validate the exact Roster and consolidated-mapping releases, the released
product types and mapping capabilities, their declared coverage, and the
configuration's internal reference graph. Do not create a carrier projection,
action or observation implementation, ParticipantArtifact, or binding.

### `OD-ADM-04` — receipt and stopping boundary

Close gates P0 through P6 with stable rejection classes, focused negative
tests, unchanged first-event regressions, and one portable receipt. A passing
receipt authorizes configuration-surface admission only. Carrier projection,
policy implementation, binding, runtime, trace, simulation, calibration, and
evaluation require later decisions.

## Consequences

The exact H2EPR-0616 configuration is now a statically admitted,
non-executable semantic input. The profile is reusable by a later event only
when that event explicitly declares the same closed shape and satisfies the
same release and graph checks; no event receives aliases, defaults, or repair.

The next legal stage may project and bind only the named three-participant
lineage. Passing admission does not change `execution_eligible`, bind any of
the nine policy meanings, or imply full-event readiness or historical or
scientific validity.
