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
├── defines/
│   └── panic_1907/
│       ├── knickerbocker-depositors.md
│       └── member-and-correspondent-bank-resource-decisions.md
└── interfaces/
    └── panic_1907/
        └── knickerbocker-depositors.md
```

`defines/` contains the accepted scholarly behavior model. `interfaces/`
contains the lightweight preflight used by Roster production. Exact machine
mapping and implementation wait for the event's consolidated Roster Definition
release.

## Current model

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

Drafts and detailed review records stay in the ignored local research area.
Git history records accepted population-model revisions.
