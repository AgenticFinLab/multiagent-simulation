---
name: event-scenario-design
description: Define a dataset-bounded event world and close every participant interface without choosing participant decisions.
---

# Event scenario design

Read [references/guide.md](references/guide.md) for the authority map,
timeline design, executable mechanism rules, interface-closure cases, failure
routing, and release evidence.

## Procedure

1. Pin Source Profile, roster release, participant products, registries, and
   selected simulation window.
2. Define opening context, clock, endogenous interval, exogenous schedule, and
   termination before environment code.
3. Assign authoritative ownership for world, actor, relationship, request,
   resource, transport, lifecycle, and result state.
4. Define observation projection and delivery; exclude hidden/future/protected
   information.
5. Define action/message admission, concurrency, allocation, failure routing,
   state deltas, annotations, and replay semantics.
6. Publish `scenario-mechanism.json`: typed state fields, one handler for every
   registry intent including `no_op`, parameter domains, preconditions,
   deterministic effects, message kinds, conflict policy, annotation rules,
   safety invariants and separately named outcome expectations.
7. Declare configurable dimensions and domains without selecting exact values.
8. Complete the Interface Closure and adversarial cases, including distinct
   concurrent writes, idempotent same-value writes, missing routes, and a
   terminal message barrier.
9. Publish the versioned definition release and checksums.

Return defects to participant products when scenario would need to invent an
observation, intent, authority, or behavior. Scenario owns world meaning, not
participant choice.
