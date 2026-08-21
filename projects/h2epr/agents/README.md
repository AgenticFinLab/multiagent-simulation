# H2EPR Agents

This directory is the mutable, tracked research surface for H2EPR Agent
Definitions and their supporting evidence. It borrows MASim's useful
separation between Markdown definitions and Python implementations, while
keeping H2EPR profiles event-bound until reuse is demonstrated.

Use the [Agent development workflow](WORKFLOW.md) to admit roles, organize
small research batches, promote reviewed Definitions, and prepare one
consolidated mapping after the Roster Definition release.

The current Panic of 1907 collection contains three institutional role models.
Knickerbocker Trust and the New York Clearing House form the current executable
conformance subset; National Bank of Commerce is a reviewed scholarly Definition
that has not yet been mapped into that subset. The adjacent
[population collection](../populations/README.md) contains the accepted
Knickerbocker depositor model. The work examines whether
participant-available information, persistent state, authority, procedure, and
intent/result separation can support auditable behavior. Calibration, cross-event
reuse, and additional execution approaches require separate work.

## Authority map

| Asset | Owns | Does not own |
|---|---|---|
| event roster | selected question and horizon, role dispositions, causal ownership, and release membership | participant policy, scenario state, or executable membership |
| event semantic skeleton | shared event concepts, interaction routes, ownership boundaries, and structural variants | numerical state, wire fields, policy, or realized outcomes |
| Agent Definition Markdown | representation, participant-available information semantics, decision commitments, intent meaning, assumptions, falsifiers | source status, actual world values, wire schemas, adjudicated results |
| population model Markdown | distributed choice semantics, retained heterogeneity, aggregation meaning, assumptions, and falsifiers | one collective personality, population composition, service process, or realized effects |
| `source-register.md` | adopted source identity, locator, byte hash, cited passages and source limitations | claim adjudication or behavior rules |
| `evidence-ledger.md` | claim status, participant availability, exposure, allowed use and withdrawal consequence | behavior rules or runtime values |
| `decision-situations.md` | shared research situations and perturbations | participant policy or executable scenario state |
| interface preflight | semantic inventory, route and lifecycle dependencies, skeleton compatibility, and preliminary carrier classification | wire mapping, registries, implementation, or conformance claims |
| accepted binding specification | reviewed mapping of a released Definition set, observations, commitments and intents | independent behavior semantics |
| executable mapping and carrier checks | exact-hash loading, parameter/lifecycle validation and Contracts V1 projection | new historical claims or result adjudication |
| machine contracts | encoding, type, shape, serialization and versioning | historical or behavioral claims |
| environment/reducer | authoritative business state, admissibility, effects and results | participant intent |

The Markdown Definitions are canonical for participant behavior. A binding is
valid only for the exact Definition hashes, commitment inventory, observation
and intent semantics it was reviewed against. The current `0.2.1` Definitions
have both the accepted V1 specification and a machine-readable implementation
candidate. The conservative first slice exercises only the bounded
request-to-feedback path; it is not a complete role implementation.

## Layout and naming

```text
agents/
├── README.md
├── WORKFLOW.md
├── agent-definition-template.md
├── bindings/
│   └── panic_1907/
├── defines/
│   └── panic_1907/
│       ├── README.md
│       ├── decision-situations.md
│       ├── evidence-ledger.md
│       ├── knickerbocker-trust.md
│       ├── national-bank-of-commerce.md
│       ├── new-york-clearing-house.md
│       └── source-register.md
└── rosters/
    └── panic_1907.md
```

- Definition filenames are lowercase kebab-case, matching the MASim profile
  convention. Python modules remain snake_case under `src/h2epr/agents/`.
- The event directory follows the existing `configs/panic_1907/` identifier.
- Only the role Markdown files are Agent Definitions. The source register,
  evidence ledger, and decision-situation portfolio are adjacent research
  assets with separate authority.
- H2EPR framework Skills use one directory per workflow. `SKILL.md` is the
  entry point; detailed research and review guidance lives in `references/`.
  The current catalog is documented in [`../skills/README.md`](../skills/README.md).

## Current assets

- [`agent-definition-template.md`](agent-definition-template.md): ten-module
  working template for event-bound scholarly and behavioral Definitions.
- [`WORKFLOW.md`](WORKFLOW.md): roster, batch, promotion, mapping, testing, and
  feedback process for repeated Agent development.
- [`rosters/panic_1907.md`](rosters/panic_1907.md): accepted H2EPR-0288
  research boundary, role dispositions, production order, and Definition
  release gate.
- [`defines/panic_1907/README.md`](defines/panic_1907/README.md): current event assets,
  authority boundaries, and implementation status.
- [`defines/panic_1907/source-register.md`](defines/panic_1907/source-register.md) and
  [`defines/panic_1907/evidence-ledger.md`](defines/panic_1907/evidence-ledger.md): adopted sources,
  claim adjudication, exposure, and bounded unresolved gaps.
- [`defines/panic_1907/decision-situations.md`](defines/panic_1907/decision-situations.md): shared role-comparison
  situations and falsification perturbations.
- [`defines/panic_1907/knickerbocker-trust.md`](defines/panic_1907/knickerbocker-trust.md) and
  [`defines/panic_1907/new-york-clearing-house.md`](defines/panic_1907/new-york-clearing-house.md):
  the current `0.2.1` Definitions in the executable two-role subset.
- [`defines/panic_1907/national-bank-of-commerce.md`](defines/panic_1907/national-bank-of-commerce.md):
  the current `0.1.0` scholarly Definition, not yet included in the executable mapping.
- [`../populations/defines/panic_1907/knickerbocker-depositors.md`](../populations/defines/panic_1907/knickerbocker-depositors.md):
  the accepted `0.1.0` event-bound population model produced by the first
  Roster batch.
- [`bindings/panic_1907/`](bindings/panic_1907/): the accepted
  Definition-to-V1 specification plus strict machine projections for the
  21-intent registry and seven lifecycle families.
- [`../scenarios/panic_1907/`](../scenarios/panic_1907/): the conservative
  non-Ray request-to-feedback implementation slice, together with the
  event-level [`semantic skeleton`](../scenarios/panic_1907/semantic-skeleton.md).

All historical outcomes used here are already exposed. This iteration is
construction and semantic falsification work, not held-out validation.

## Lightweight iteration lifecycle

The tracked paths above contain only the current accepted candidate. Do not add
`-v2`, `-old`, date-suffixed copies, or an archive directory beside them.

1. Explore and review drafts below the ignored `.local-runtime/h2epr-simulation/working/`
   area. Store adopted raw sources and sealed evidence in its evidence area.
2. Form an immutable local review snapshot with source hashes, candidate hashes,
   test results, and unresolved questions. Rejected alternatives remain local.
3. Perform a lightweight interface preflight before promotion. During Roster
   production, record mapping expectations without assigning machine fields or
   updating binding hashes.
4. Commit that coherent state. Git history is the authoritative history of
   accepted repository versions; `.local-runtime` preserves richer research and
   review history that should not burden the public tree.

After every roster row has a reviewed disposition and every admitted Agent has
an accepted Definition, form one Roster Definition release. Consolidated
mapping, carrier review, implementation, and conformance work begin from that
release under separate authorization. The current two-role implementation is
the retained reference pilot, not the per-role production pattern.

Contract successors or intentionally supported public release lines may coexist
when compatibility requires it. Mutable Agent drafts do not receive that
exception merely to retain history.

The `0.1.0-dev` three-tick path is retained under
[`tests/fixtures/agents/panic_1907/minimal_binding_v0_1/`](../tests/fixtures/agents/panic_1907/minimal_binding_v0_1/)
as a frozen engineering fixture. It is not a current Definition line and cannot
be cited as conformance evidence for any current Definition.
