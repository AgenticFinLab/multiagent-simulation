# Population model template

Use this template when an event depends on distributed choices but the evidence
does not support, or the question does not require, reconstructing every actor
as a named Agent. A population model represents heterogeneous choice units; it
must not give a group one personality, belief, account, or authority.

Keep a standard model short. Combine sections when ownership remains clear,
and omit prompts that do not affect the event question. The template sets no
minimum number of cases, mechanisms, profiles, or parameters. Use a deep
record only when representation novelty, causal centrality, or evidence risk
warrants it.

## Model overview

| Field | Value |
|---|---|
| Model name | |
| Event and modeled interval | |
| Choice unit | |
| Host, institution, or account scope | |
| Causal role in the event | |
| Evidence and outcome-exposure boundary | |
| Identity, version, and status | |

## 1. Scope and representation

State what one choice unit represents and why a population is preferable to a
named Agent or a scenario-owned process. Define inclusion, exclusion,
aggregation, host boundaries, and any weights. Name the evidence or causal
finding that would require splitting the population or changing its
representation.

Do not infer a collective decision-maker from a shared label. Authority,
claims, balances, obligations, and private state remain with the units or their
explicit institutional owner.

## 2. Evidence and institutional basis

Reference the adopted source and claim records that support this model. State
the institutional rules, observed regularities, disputes, and assumptions that
matter to its use. Preserve participant-time and source-use limits; do not copy
the evidence ledger into this document.

Separate historical facts, theoretical mechanisms, estimates, analogies, and
modeling assumptions. Describe uncertainty where the evidence cannot support a
single interpretation.

## 3. Information, private state, and heterogeneity

Define what a unit can observe at the modeled time, including missing, delayed,
or stale information. For each behaviorally material private state, state its
owner, initialization basis, update rule, and isolation boundary.

Describe only the heterogeneity needed for the event question. Profiles,
weights, thresholds, or distributions need a semantic interpretation and an
evidence status, but not invented numerical calibration. Units must not read
one another's hidden state or a later historical outcome.

## 4. Behavior and choice

Describe the decision situations, competing mechanisms, available choices,
selection basis, fallback, abstention, and conditions for revisiting a choice.
Connect each material mechanism to evidence or theory and state where it is
expected to fail.

The model should preserve individual variation while making the aggregate
response interpretable. It need not assign every unit a unique biography or
fixed policy.

## 5. Intent, result, and scenario boundary

List the domain intents produced by a choice unit and the observations or state
that may influence them. Keep delivery, matching, queues, market processes,
adjudication, resource effects, and realized results with the scenario unless
the roster assigns them elsewhere.

Explain how unit choices may be aggregated for analysis without turning that
aggregation into a new actor. A requested action, an accepted request, and its
realized effect are distinct.

## 6. Cases, uncertainty, and falsification

Use a small set of high-information situations to show how information,
heterogeneity, missing data, competing mechanisms, and adverse results change
the model's choices. Label any exposed outcome used to construct a case.

State plausible alternatives and observations that would revise the mechanism,
the heterogeneity model, or the population representation. Add numerical
sensitivity or calibration only when a later research question requires it.

## 7. Limitations, provenance, and review

State what the model does not claim, including any limits on historical
realism, prediction, calibration, or transfer. Record the accepted claim and
source identities, the method baseline, and the review verdict.

A standard model may use a concise batch-level review. Use a separate review
record for a deep model when a material representation, evidence, or causal
judgment needs independent treatment.

## Interface handoff

Record only the semantic surface needed for later event integration.

| Surface | Meaning and owner |
|---|---|
| observations and timing | |
| private state and isolation | |
| intents and counterparties | |
| routes and scenario dependencies | |
| authority, resources, and lifecycles | |
| aggregation or analysis output | |
| interface classification | `KNOWN_FIT`, `MAPPING_EXTENSION_EXPECTED`, or `CONCRETE_CARRIER_COUNTEREXAMPLE` |

This handoff does not select wire fields, policy classes, parameters, or
runtime bindings. Population units may later be instantiated by an accepted
configuration, but this template does not prescribe their executable form.

## Completion check

A population model is ready for promotion when:

- the evidence question is closed for its stated use;
- the representation preserves meaningful heterogeneity and ownership;
- information, private state, intent, scenario process, and result are
  separated;
- mechanisms, uncertainty, alternatives, and revision conditions are clear;
- review depth matches the selected production profile; and
- the interface handoff closes without inventing implementation semantics.

The Agent Definition ten-module profile applies only if the roster later
changes this product into an Agent Definition.
