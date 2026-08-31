# Samsung Galaxy Note7 event semantic skeleton

## Boundary and clocks

The skeleton covers launch and incident signals through the U.S. transport
order becoming effective on 15 October 2016. Event time, participant
availability, source publication time, and research access time remain
separate. January 2017 diagnosis and remediation are retrospective only.

## Shared concepts

| Concept | Owner | Invariant |
|---|---|---|
| safety signal | Evidence owns provenance; Scenario owns delivery | reported, received, investigated, and verified are distinct |
| investigation state | Investigating participant owns its assessment; Scenario owns delivered findings | no participant reads another's private investigation |
| product-flow state | Scenario owns authoritative sales, shipment, exchange, production, and return states | a participant emits an intent, not the resulting state |
| recall state | Scenario owns jurisdiction-specific legal state after a valid authority intent | corporate program, warning, formal recall, and expanded recall differ |
| remedy lifecycle | Participant owns offer or selection intent; Scenario owns eligibility, stock, handoff, and completion | offer, availability, choice, execution, and effectiveness differ |
| transport issuance | CAAC or U.S. DOT Agent owns its issuance intent | jurisdiction and authority cannot be merged |
| transport lifecycle | Scenario owns publication, delivery, effect, duties, enforcement, and results | lifecycle begins only after valid issuance |
| incident and device process | Scenario/exogenous owner | failures are not generated to force the known outcome |
| intent lifecycle | Sender owns the intent; Scenario owns delivery and disposition | pending, partial, failed, expired, cancelled, superseded, and completed differ |

## Main routes

```text
incident signal -> Samsung investigation interface
Samsung product intent -> regional units / intermediaries / consumers
Samsung and incident records -> CPSC recall interface
CPSC authority intent -> recall lifecycle -> intermediaries / consumers
safety and recall predicates -> CAAC or U.S. DOT issuance interface
transport authority intent -> jurisdictional lifecycle -> operators / travelers
recipient result or new signal -> participant-local reconsideration
```

No route implies delivery, shared interpretation, compliance, or effect.
Scenario owns institutions, relationships, inventory, device identity,
physical transitions, message transport, legal admissibility, execution,
results, time, exogenous signals, and termination. Participants own only the
choices and private qualitative state declared by their products.

## Structural variants and termination

The later Scenario may select bounded variants for local remedy availability,
message delivery, operator procedure, and incident-signal arrival. It may not
select a known outcome as participant policy. The core process terminates only
after the clock reaches the accepted boundary and all required authority and
intent lifecycles are either resolved or explicitly retained as unresolved.
