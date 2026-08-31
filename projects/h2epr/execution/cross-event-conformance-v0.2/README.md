# Three-event Rule execution conformance v0.2

This successor release compares the accepted Panic of 1907, SingHealth Data
Breach, and Samsung Galaxy Note7 battery recall full-roster Rule runs. The
accepted two-event v0.1 release remains unchanged. Version 0.2 adds a third,
independently specified consumer of the same event-neutral execution closure
contract.

## Accepted vectors

| Property | Panic of 1907 | SingHealth | Note7 |
|---|---:|---:|---:|
| actors operated | 16 | 13 | 8 |
| actor-capability bindings | 17 | 13 | 8 |
| commitments evaluated | 88 | 41 | 22 |
| selected Scenario policies exercised | 9 | 9 | 9 |
| lifecycle families realized | 13 | 11 | 12 |
| logical coordinates | 32 | 50 | 50 |
| trace records | 2,002 | 1,554 | 926 |
| generated EPG nodes | 1,392 | 752 | 374 |
| generated EPG edges | 1,121 | 623 | 302 |

These unequal values are part of the conformance result. Event identity,
roster size, commitment surface, lifecycle inventory, time, policy semantics,
state, and graph content remain event-owned parameters. Conformance requires a
common closure contract; it does not require semantic flattening or equal
counts.

## Shared contract

For every event, this release re-admits the compact run release and its exact
executable parent, then verifies:

- two fresh same-input, same-seed materializations have identical bytes and
  canonical content for all eight run documents;
- the trace uses the common 15 record types and closes with tick and run seals;
- authoritative replay reproduces the sealed final state;
- all transport intents resolve at completion;
- the generated graph uses the common nine node types and five edge relations,
  and every node, endpoint, and source trace reference resolves;
- the six compact run documents use the shared format identities; and
- MASim is consumed only through the unchanged public phased and event-process
  interfaces.

The [machine conformance document](conformance.json) records each accepted
vector and the common contract. The [manifest](manifest.json) pins all three
source run releases and this implementation. The
[substantive review](substantive-review.md) separates the engineering result
from unsupported scientific conclusions.

## What the third event tests

Note7 adds product-safety, consumer remedy, formal recall, transport warning,
emergency-order, retailer, consumer-choice, and air-operator mechanisms. Its
eight-actor topology and twelve lifecycle families differ materially from the
banking and cyber-incident events. The shared kernel required no event logic
or MASim modification; only event-specific registries, policies, state,
routes, counts, and release adapters were added.

The exercise also exposed a local environment limitation: the current
interpreter lacks the optional `lmbase` history-store dependency. The Note7
phased runner used a no-op-compatible in-memory fixture only for that unused
BaseSimulator history slot. The public scheduler, barriers, transport,
reducer, trace, sealing, replay, and graph paths ran unchanged. This should be
rechecked in a fully provisioned environment before external publication.

## Scope

This is a three-event engineering result. It strengthens evidence that the
maintained construction and execution workflow can be reused across distinct
event mechanisms. It does not establish parameter calibration, historical
fit, held-out performance, recall or policy effectiveness, causal validity,
scientific validity, or universal generality.
