# R4 trust-contagion and call-money interface

| Item | Value |
|---|---|
| Status | accepted Roster-production preflight |
| Event | `H2EPR-0288` |
| Roster | `v0.4` |
| Semantic skeleton | `v0.1` |
| Products | later-depositor, call-lender and broker-borrower populations `0.1.0` |

## Purpose

This preflight checks whether the three R4 population products expose a
coherent later mapping surface and whether Contracts V1 presents a concrete
carrier counterexample. It does not choose fields, add registry entries,
define executable participants or modify a contract.

## Later-depositor surface

### Inputs and state

- host institution and remaining claim identity;
- private withdrawal need;
- delivered host and public contagion signals;
- delivered, host-scoped service/access and peer-activity observations;
- own request lifecycle and delivered result; and
- pre-run response profile and conflict rule.

### Outputs

- request a positive withdrawal amount or fraction;
- retain for one decision interval; or
- await one identified pending request/result.

### Scenario ownership

Population composition, accounts, host resources, publication and delivery,
queues, admission, service, certified checks, payment, claim effects,
operational restrictions and suspension remain outside the population.

## Call-lender surface

### Inputs and state

- one institution, capability, authority and resource/exposure identity;
- delivered existing loan, contractual status and borrower request;
- delivered terms, borrower/collateral information and route;
- own qualitative term assessment under a predeclared classifier;
- existing-loan and new-lending posture; and
- call, offer, booking and repayment lifecycles and results.

### Outputs

- request information;
- continue or propose a bounded term change;
- issue a valid call/reduction notice;
- make, revise or cancel a conditional call-loan offer;
- decline a new request with a typed reason; or
- await one named lifecycle result.

### Scenario ownership

Contract truth, delivery, borrower truth, collateral control/value, route
availability, matching, booking, transfer, repayment, default and market
effects remain outside the lender.

## Broker-borrower surface

### Inputs and state

- one authorized firm/exchange-member funding interface and mandate;
- delivered call obligation and controlled resource projection;
- delivered funding routes, offers and settlement obligations;
- controlled collateral/position scope;
- call, request, offer, booking, repayment and reduction lifecycles; and
- remaining quantitative or qualitative funding gap.

### Outputs

- request clarification or renewal/replacement funding;
- submit a controlled collateral proposal;
- accept, request revision of or decline an offer;
- authorize controlled repayment;
- request an authorized bounded position reduction;
- record a typed inability when no legal response remains; or
- await one named lifecycle result.

### Scenario ownership

Obligation validity, collateral truth/value/custody, lender capacity, venue
matching, booking, transfer, repayment, trade admission/execution, settlement,
liquidation, price effects, default and insolvency remain outside the borrower.

## Venue and cross-capability boundary

NYSE is a scenario-owned venue/market process in v0.1. It exposes dated route,
rate, matching, allocation, collateral/position and settlement observations or
results; it does not choose Morgan's pool, a lender's offer or a broker's
response.

One institution may later compose several H2EPR capabilities. Composition must
preserve one participant identity and one authoritative authority/resource/
exposure state. A Trust Company of America host, a bank-resource contributor
and a call lender are capability surfaces over an institution when applicable,
not separate balance sheets or independently editable historical actors.

## Contracts V1 carrier re-check

| Interface family | Classification | Consolidated-release work |
|---|---|---|
| later-depositor population identity | `KNOWN_FIT` at participant-contract level | reuse the accepted weighted population pattern while adding mandatory host scope and preventing cross-host state |
| call-lender population identity | `KNOWN_FIT` at participant-contract level | preserve institution identity and declare capability composition rather than creating an anonymous market wallet |
| broker-borrower population identity | `KNOWN_FIT` at participant-contract level | bind the authorized funding interface and mandate to each unit; do not infer customers or positions |
| multi-capability historical participant | `MAPPING_EXTENSION_EXPECTED` | one participant identity must compose capability-specific policy/state surfaces without duplicate authority or resources |
| information and observation boundary | `KNOWN_FIT` at contract level | add event semantic domains and registry entries; retain source/as-of/freshness/host or counterparty scope |
| depositor claim/request/result lifecycle | `KNOWN_FIT_WITH_MAPPING_EXTENSION` | extend the accepted depositor lifecycle with host scope, service-unavailable and certified-check result semantics |
| call-loan and replacement-funding lifecycle | `MAPPING_EXTENSION_EXPECTED` | define contract, call, term-change, request, offer, revision, acceptance, match, booking, transfer and repayment identities |
| term and collateral assessments | `KNOWN_FIT_WITH_INTERNAL_MAPPING` | choose one canonical semantic projection and record classifier/basis; no hidden backend score or duplicate valuation truth |
| action and message intents | `KNOWN_FIT` at contract level | later semantic registry entries must carry target, parameters, authority, resource/contract refs, time, decision and idempotency |
| controlled collateral/position response | `KNOWN_FIT_WITH_CROSS_OBJECT_VALIDATION` | verify ownership/control, mandate, nonduplication and lifecycle; Agent cannot emit trade or realized sale result |
| NYSE venue/process | `MAPPING_EXTENSION_EXPECTED` in scenario semantics | define route, matching, rate, allocation, trade and settlement processes without creating an Agent identity |
| partial, unavailable, delayed, failed and expired outcomes | `KNOWN_FIT` at disposition level | later business reason mappings must preserve attempted intents and realized components |
| trace and replay | `KNOWN_FIT` at contract level | retain host/claim, loan, offer, call case, collateral, obligation, state-version, observation and causal references |

## Required later cross-object checks

1. every depositor request resolves to one host, claim, unit and active request
   lifecycle;
2. no private account, queue, access or result state crosses host scope;
3. every call/continuation/term-change resolves to one authoritative contract,
   lender, borrower, authority and exposure;
4. a market observation cannot create a call right, contractual duty, resource
   capacity or compatible-term answer;
5. each lender offer resolves to a controlled institution resource and cannot
   exceed or duplicate another commitment;
6. each borrower response resolves to an authorized mandate, obligation,
   controlled collateral/resource/position and active lifecycle;
7. acceptance, matching, booking, transfer, repayment, liquidation and effect
   cannot be emitted by the wrong participant;
8. a pool proposal or announced total cannot create an offer, match, booking
   or guaranteed funding result;
9. an institution with multiple capabilities has one identity and one
   authoritative resource/exposure truth; and
10. only delivered realized components change claims, gaps, resources,
    obligations or later behavior.

## Preflight conclusion

`NO_CONCRETE_V1_CARRIER_COUNTEREXAMPLE`

R4 adds substantial consolidated work—host-indexed population composition,
multi-capability participant composition, call-loan/funding lifecycles,
semantic intent registration and NYSE scenario mechanics—but the current V1
participant, profile, observation, intent/message, resource, disposition and
trace surfaces remain plausible carriers. The Roster Definition release pins
this surface for consolidated review; no successor seam was justified by the
R4 preflight alone.
