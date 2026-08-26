# H2EPR populations

Population models represent heterogeneous participants whose collective
response matters but whose individual historical reconstruction is neither
necessary nor supported by the available evidence.

They complement Agent Definitions. An Agent has a defensible individual or
institutional decision interface; a population model preserves distributed
choices without giving the population one voice, one belief, or one authority.
The scenario remains responsible for population composition, message delivery,
operational processes, adjudication, and realized effects.

## Layout

```text
populations/
├── README.md
├── population-model-template.md
├── defines/
│   ├── panic_1907/
│   │   └── <population-model>.md
│   └── singhealth_data_breach/
│       └── <population-model>.md
└── interfaces/
    └── <event>/
        └── <interface-account>.md
```

`defines/` contains the scholarly behavior model. Current event-level
interface guides organize participant interactions for external readers. The
files under `interfaces/` retain population-specific integration reviews used
during roster construction, including exact release-time preflights where a
manifest pins them. Machine mapping remains separate from both.

Start a new population product from the
[Population model template](population-model-template.md). It covers the
shared semantic and review requirements without forcing Agent Definition
semantics or a separate document for every working stage. Every canonical
population model uses its exact ten-module reading order. Standard and deep
profiles change research and review depth, not the publication-facing
structure, and impose no minimum section length or number of mechanisms,
parameters, or cases.

## Current models

[Knickerbocker depositors](defines/panic_1907/knickerbocker-depositors.md)
is an event-bound population of weighted choice units. It models withdrawal,
retention, pending-request discipline, and delivered-result adaptation under
explicitly uncalibrated heterogeneity. Its
interaction with host service and result ownership is summarized in the
[Panic participant interface guide](../agents/interfaces/panic_1907/). The
population-specific preflight remains an exact Roster-release input.

[NYCH member and large correspondent bank resource decisions](defines/panic_1907/member-and-correspondent-bank-resource-decisions.md)
are modeled as weight-one institution-preserving choice units. The population
keeps authority, resource ownership, commitments and certificate demand with
each institution instead of inventing a collective bank personality or named
bank policies. The [Panic participant interface guide](../agents/interfaces/panic_1907/)
also covers the trust-company committee interaction boundary.

[Later trust-company depositors](defines/panic_1907/later-trust-company-depositors.md)
are modeled as host-indexed weighted choice units. A TCA, Lincoln or other
trust depositor retains its own claim, delivered information, access and
request lifecycle; private account or result state never crosses hosts.

[Call-money lenders](defines/panic_1907/call-money-lenders.md) preserve the
lending institution, contract, controlled exposure and resource envelope.
[Broker-borrowers](defines/panic_1907/call-money-broker-borrowers.md) preserve
an authorized firm funding interface without importing customer trading or
venue policy. Their
[Panic participant interface guide](../agents/interfaces/panic_1907/)
keeps call, offer, matching, booking, repayment, liquidation, and market effect
under distinct owners. The exact R4 preflight remains a release-time record,
and NYSE remains Scenario-owned.

[IHiS technical administration and line security staff](defines/singhealth_data_breach/technical-administration-and-line-security-staff.md)
are represented as event-time technical responsibility units across
application/database, Citrix/infrastructure, and security-engineering/CERT
functions. Units retain their own observations, local assessment, authority,
and response intents; population composition, assignments, delivery, technical
execution, and effects remain scenario-owned. The model covers the first
technical participant batch within the accepted H2EPR-0616 semantic roster.

[IHiS operational and SCM management](defines/singhealth_data_breach/ihis-operational-and-scm-management.md)
preserves distinct infrastructure, application-service, and cluster-
operational responsibility units that integrate technical accounts, seek
verification, convene review, assign follow-up, or route a qualified concern.
Its aggregation never becomes a single IHiS management actor.

Both SingHealth models belong to its
[Roster Definition release v0.1](../releases/singhealth_data_breach/roster-definition-v0.1/),
alongside seven office-level Agent Definitions and reviewed dispositions for
the event's non-participant processes and cohorts. Their cross-role routes are
organized by the
[SingHealth participant interface guide](../agents/interfaces/singhealth_data_breach/).

The five Panic of 1907 population models belong to its
[Roster Definition release v0.1](../releases/panic_1907/roster-definition-v0.1/).
Their machine-facing relationships are recorded in the
[consolidated mapping](../agents/bindings/panic_1907/consolidated/).

The [publication standard](../PUBLICATION_STANDARD.md) governs the public model
surface; the [Agent workflow](../agents/WORKFLOW.md) governs research, review,
and integration records.

For a new or changed model, run the shared publication-profile checker from
the repository root:

```bash
python -m h2epr.agents.definition_profile --kind population \
  path/to/population-model.md
```

The check enforces the common population reading structure and public surface;
it does not replace evidence, behavior, or interface review.
