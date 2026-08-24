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
│   └── panic_1907/
│       ├── call-money-broker-borrowers.md
│       ├── call-money-lenders.md
│       ├── knickerbocker-depositors.md
│       ├── later-trust-company-depositors.md
│       └── member-and-correspondent-bank-resource-decisions.md
└── interfaces/
    └── panic_1907/
        ├── knickerbocker-depositors.md
        └── r4-trust-contagion-and-call-money.md
```

`defines/` contains the accepted scholarly behavior model. `interfaces/`
contains the lightweight preflight used by Roster production. Exact machine
mapping is now specified by the accepted event-level consolidated mapping;
executable composition still requires a separately authorized implementation
and conformance slice.

Start a new population product from the
[Population model template](population-model-template.md). It covers the
shared semantic and review requirements without forcing Agent Definition
structure or a separate document for every working stage. The accepted 1907
models predate the template and remain frozen in their accepted form; the
template is not a reason to rewrite them.

## Current models

[Knickerbocker depositors](defines/panic_1907/knickerbocker-depositors.md)
is an event-bound population of weighted choice units. It models withdrawal,
retention, pending-request discipline, and delivered-result adaptation under
explicitly uncalibrated heterogeneity. Its
[interface preflight](interfaces/panic_1907/knickerbocker-depositors.md)
records the later integration surface without selecting carriers or changing
Contracts V1.

[NYCH member and large correspondent bank resource decisions](defines/panic_1907/member-and-correspondent-bank-resource-decisions.md)
are modeled as weight-one institution-preserving choice units. The population
keeps authority, resource ownership, commitments and certificate demand with
each institution instead of inventing a collective bank personality or named
bank policies. Its accepted [combined R3 interface preflight](../agents/interfaces/panic_1907/r3-collective-trust-support.md)
also covers the trust-company committee interaction boundary.

[Later trust-company depositors](defines/panic_1907/later-trust-company-depositors.md)
are modeled as host-indexed weighted choice units. A TCA, Lincoln or other
trust depositor retains its own claim, delivered information, access and
request lifecycle; private account or result state never crosses hosts.

[Call-money lenders](defines/panic_1907/call-money-lenders.md) preserve the
lending institution, contract, controlled exposure and resource envelope.
[Broker-borrowers](defines/panic_1907/call-money-broker-borrowers.md) preserve
an authorized firm funding interface without importing customer trading or
venue policy. Their accepted
[R4 interface preflight](interfaces/panic_1907/r4-trust-contagion-and-call-money.md)
keeps call, offer, matching, booking, repayment, liquidation and market effect
under distinct owners. NYSE remains scenario-owned in this release.

All five population models belong to the Panic of 1907
[Roster Definition release v0.1](../releases/panic_1907/roster-definition-v0.1/).
They are covered by the accepted
[consolidated mapping](../agents/bindings/panic_1907/consolidated/), while
their executable composition remains pending.

Drafts and detailed review records stay in the ignored local research area.
Git history records accepted population-model revisions.
