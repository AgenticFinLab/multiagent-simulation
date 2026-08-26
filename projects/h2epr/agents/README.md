# H2EPR Agents

This directory contains H2EPR Agent Definitions, participant interface
accounts, rosters, and machine-facing bindings. Shared source, claim, and
decision-situation records belong to the corresponding event directory. H2EPR
borrows MASim's useful
separation between Markdown definitions and Python implementations, while
keeping H2EPR profiles event-bound until reuse is demonstrated.

Use the [Agent development workflow](WORKFLOW.md) to admit roles, organize
small research batches, promote reviewed Definitions, and prepare and review
one consolidated mapping after the Roster Definition release.

The current Panic of 1907 collection contains seven institutional or named-person
role models. Knickerbocker Trust, National Bank of Commerce, and the New York
Clearing House form the current bounded conformance subset; the older direct
KT--NYCH path remains a frozen reference. J. Pierpont Morgan, Trust Company of
America, Lincoln Trust Company, and the trust-company presidents' committee
are reviewed scholarly Definitions covered by the accepted consolidated event
mapping but not by this implementation. The adjacent
[population collection](../populations/README.md)
contains five accepted models: Knickerbocker and later-trust depositors,
member/correspondent-bank resource decisions, call-money lenders and broker-
borrowers. The work examines whether
participant-available information, persistent state, authority, procedure, and
intent/result separation can support auditable behavior. Calibration, cross-event
reuse, and additional execution approaches require separate work.

The H2EPR-0616 SingHealth collection currently contains seven office-level
Definitions and two responsibility-unit Population Models across the accepted
detection-and-escalation and classification-and-institutional-escalation
batches. Together with the reviewed non-participant dispositions, they form
the accepted [research roster v0.2](rosters/singhealth_data_breach.md) and
[Roster Definition release v0.1](../releases/singhealth_data_breach/roster-definition-v0.1/).
The accepted
[consolidated mapping v0.1](bindings/singhealth_data_breach/consolidated/)
reconciles the complete release with Contracts V1 and the Event Scenario
Definition without making the collection executable. The bounded
[SCM technical--operations--GCIO binding](bindings/singhealth_data_breach/scm-technical-operations-gcio-v0.1/)
then projects four selected intents while preserving the non-executable
full-configuration boundary.

## Authority map

| Asset | Owns | Does not own |
|---|---|---|
| event roster | selected question and horizon, role dispositions, causal ownership, and release membership | participant policy, scenario state, or executable membership |
| event semantic skeleton | shared event concepts, interaction routes, ownership boundaries, and structural variants | numerical state, wire fields, policy, or realized outcomes |
| Agent Definition Markdown | representation, participant-available information semantics, decision commitments, intent meaning, assumptions, falsifiers | source classification, actual world values, wire schemas, adjudicated results |
| population model Markdown | distributed choice semantics, retained heterogeneity, aggregation meaning, assumptions, and falsifiers | one collective personality, population composition, service process, or realized effects |
| event source register | adopted source identity, locator, byte hash, cited passages and source limitations | claim adjudication or behavior rules |
| event participant-evidence record | claim classification, participant availability, exposure, allowed use and withdrawal consequence | behavior rules or runtime values |
| event decision-situation record | shared research situations and perturbations when a separate record is useful | participant policy or executable scenario state |
| interface preflight | semantic inventory, route and lifecycle dependencies, skeleton compatibility, and preliminary carrier classification | wire mapping, registries, implementation, or conformance claims |
| accepted binding specification | reviewed mapping of a released Definition set, observations, commitments and intents | independent behavior semantics |
| executable mapping and carrier checks | exact-hash loading, parameter/lifecycle validation and Contracts V1 projection | new historical claims or result adjudication |
| machine contracts | encoding, type, shape, serialization and versioning | historical or behavioral claims |
| environment/reducer | authoritative business state, admissibility, effects and results | participant intent |

The Markdown Definitions are canonical for participant behavior. A binding is
valid only for the exact Definition hashes, commitment inventory, observation
and intent semantics it was reviewed against. Each bounded binding exercises
only its declared lineage; neither is a complete role or event implementation.

## Layout and naming

```text
agents/
├── README.md
├── WORKFLOW.md
├── agent-definition-template.md
├── bindings/
│   ├── panic_1907/
│   │   ├── consolidated/
│   │   └── roster-v0.1/
│   └── singhealth_data_breach/
│       ├── README.md
│       ├── consolidated/
│       └── scm-technical-operations-gcio-v0.1/
├── defines/
│   ├── panic_1907/
│   │   ├── README.md
│   │   ├── j-pierpont-morgan.md
│   │   ├── knickerbocker-trust.md
│   │   ├── lincoln-trust-company.md
│   │   ├── national-bank-of-commerce.md
│   │   ├── new-york-clearing-house.md
│   │   ├── trust-company-presidents-committee.md
│   │   └── trust-company-of-america.md
│   └── singhealth_data_breach/
│       ├── README.md
│       └── <agent-definition>.md
├── interfaces/
│   ├── panic_1907/
│   │   ├── national-bank-of-commerce.md
│   │   ├── r2-private-and-named-trusts.md
│   │   └── r3-collective-trust-support.md
│   └── singhealth_data_breach/
│       ├── r1-detection-and-escalation.md
│       └── r2-classification-and-institutional-escalation.md
└── rosters/
    ├── panic_1907.md
    └── singhealth_data_breach.md
```

- Definition filenames are lowercase kebab-case, matching the MASim profile
  convention. Python modules remain snake_case under `src/h2epr/agents/`.
- New Definition candidates use the exact ten numbered top-level modules in
  the public template. Role-specific subsections remain flexible. All
  canonical Definitions share the same publication-facing metadata rules.
- The event directory follows the existing `configs/panic_1907/` identifier.
- A `defines/<event>/` directory contains only its concise `README.md` index and
  canonical Agent Definitions. Shared source registers, participant evidence,
  and decision-situation portfolios are event-owned research authorities under
  `events/<event>/`.
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
- [`rosters/singhealth_data_breach.md`](rosters/singhealth_data_breach.md):
  accepted H2EPR-0616 research boundary, participant and process dispositions,
  release membership, and change policy.
- [`defines/panic_1907/README.md`](defines/panic_1907/README.md): Definition
  index, authority boundaries, and relation to implemented examples.
- [`../events/panic_1907/source-register-v0.1.md`](../events/panic_1907/source-register-v0.1.md)
  and [`../events/panic_1907/participant-evidence-v0.1.md`](../events/panic_1907/participant-evidence-v0.1.md):
  adopted sources, claim adjudication, exposure, and bounded unresolved gaps.
- [`../events/panic_1907/decision-situations-v0.1.md`](../events/panic_1907/decision-situations-v0.1.md):
  shared role-comparison situations and falsification perturbations.
- [`interfaces/panic_1907/r2-private-and-named-trusts.md`](interfaces/panic_1907/r2-private-and-named-trusts.md):
  accepted semantic preflight for the Morgan, TCA, and Lincoln R2 batch; no executable mapping is implied.
- [`interfaces/panic_1907/national-bank-of-commerce.md`](interfaces/panic_1907/national-bank-of-commerce.md):
  accepted NBC compound-observation, route-hop and lifecycle preflight for consolidated mapping.
- [`interfaces/panic_1907/r3-collective-trust-support.md`](interfaces/panic_1907/r3-collective-trust-support.md):
  accepted semantic preflight for the committee and member/correspondent-bank resource-decision population.
- [`defines/panic_1907/knickerbocker-trust.md`](defines/panic_1907/knickerbocker-trust.md) and
  [`defines/panic_1907/new-york-clearing-house.md`](defines/panic_1907/new-york-clearing-house.md):
  the Definitions used by both the retained two-role reference and the bounded
  three-role lineage.
- [`defines/panic_1907/national-bank-of-commerce.md`](defines/panic_1907/national-bank-of-commerce.md):
  the scholarly Definition projected as a pure courier in the bounded
  KT--NBC--NYCH binding.
- [`defines/panic_1907/j-pierpont-morgan.md`](defines/panic_1907/j-pierpont-morgan.md),
  [`defines/panic_1907/trust-company-of-america.md`](defines/panic_1907/trust-company-of-america.md), and
  [`defines/panic_1907/lincoln-trust-company.md`](defines/panic_1907/lincoln-trust-company.md): Definitions for
  bounded private coordination, an aggregate named-trust response, and a thin
  board-authorized institutional communication interface. They are covered by
  the accepted consolidated design.
- [`defines/panic_1907/trust-company-presidents-committee.md`](defines/panic_1907/trust-company-presidents-committee.md):
  an aggregate procedural committee Definition, with advice, contributor commitment and
  resource ownership kept separate.
- [`defines/singhealth_data_breach/`](defines/singhealth_data_breach/): seven
  office-level Definitions in the accepted H2EPR-0616 semantic roster. Their
  shared
  [R1](interfaces/singhealth_data_breach/r1-detection-and-escalation.md) and
  [R2](interfaces/singhealth_data_breach/r2-classification-and-institutional-escalation.md)
  accounts describe the semantic routes among them and the two population
  models.
- [`../releases/singhealth_data_breach/roster-definition-v0.1/`](../releases/singhealth_data_breach/roster-definition-v0.1/):
  hash-pinned, non-executable inventory of the complete H2EPR-0616 semantic
  roster and its non-participant dispositions.
- [`bindings/singhealth_data_breach/consolidated/`](bindings/singhealth_data_breach/consolidated/):
  accepted non-executable full-Roster mapping, Contracts V1 carrier decision,
  release-interface inventory, and owner-resolution record.
- [`bindings/singhealth_data_breach/scm-technical-operations-gcio-v0.1/`](bindings/singhealth_data_breach/scm-technical-operations-gcio-v0.1/):
  exact three-participant binding for four source-preserving finding,
  verification, escalation, and clarification intents, with event-qualified
  catalog derivation and focused Contracts V1 checks.
- [`../populations/defines/panic_1907/knickerbocker-depositors.md`](../populations/defines/panic_1907/knickerbocker-depositors.md):
  the event-bound Knickerbocker depositor population model.
- [`../populations/defines/panic_1907/member-and-correspondent-bank-resource-decisions.md`](../populations/defines/panic_1907/member-and-correspondent-bank-resource-decisions.md):
  the institution-preserving resource-decision population.
- [`../populations/defines/panic_1907/later-trust-company-depositors.md`](../populations/defines/panic_1907/later-trust-company-depositors.md),
  [`../populations/defines/panic_1907/call-money-lenders.md`](../populations/defines/panic_1907/call-money-lenders.md), and
  [`../populations/defines/panic_1907/call-money-broker-borrowers.md`](../populations/defines/panic_1907/call-money-broker-borrowers.md):
  the host-contagion and call-money population models.
- [`../populations/interfaces/panic_1907/r4-trust-contagion-and-call-money.md`](../populations/interfaces/panic_1907/r4-trust-contagion-and-call-money.md):
  accepted R4 semantic preflight, including the scenario-owned NYSE boundary.
- [`../releases/panic_1907/roster-definition-v0.1/`](../releases/panic_1907/roster-definition-v0.1/):
  hash-pinned semantic release and sole consolidated-mapping input inventory.
- [`bindings/panic_1907/consolidated/`](bindings/panic_1907/consolidated/):
  accepted non-executable full-Roster mapping, carrier decision, hashes and
  owner-resolution record.
- [`bindings/panic_1907/roster-v0.1/`](bindings/panic_1907/roster-v0.1/):
  conformance-only machine profile for the accepted release. Its loader
  hash-checks all twelve products, derives the release-wide observation and
  intent identities, and exercises bounded identity, scope, authority,
  resource, lifecycle and replay cases without selecting a policy.
- [`bindings/panic_1907/`](bindings/panic_1907/): the retained two-role
  Definition-to-V1 specification plus strict machine projections for the
  21-intent registry and seven lifecycle families.
- [`../scenarios/panic_1907/`](../scenarios/panic_1907/): the conservative
  non-Ray request-to-feedback implementation slice, together with the
  event-level [`semantic skeleton`](../scenarios/panic_1907/semantic-skeleton.md).

All historical outcomes used here are already exposed. This iteration is
construction and semantic falsification work, not held-out validation.

For a new Definition candidate, run the lightweight public-profile check from
the repository root:

```bash
python -m h2epr.agents.definition_profile path/to/candidate.md
```

The checker validates module order, overview fields, observation and intent
inventories, Decision Commitment links, and the absence of project-only
metadata. It applies the publication-surface check to all canonical participant
models and does not replace scholarly review.

## Contribution and release records

Canonical participant files contain the current scholarly account rather than
an archive of drafts. The [publication standard](../PUBLICATION_STANDARD.md)
defines their public surface, and the [Agent workflow](WORKFLOW.md) describes
research, review, integration, and release. Exact identities, hashes,
compatibility lines, and test fixtures remain in the manifests, bindings, and
test records that need them.
