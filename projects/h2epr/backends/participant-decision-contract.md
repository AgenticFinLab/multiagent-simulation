# Participant decision contract

Every backend receives one immutable observation for every active actor from a
single sealed pre-state. It returns exactly one decision record containing one
typed action intent and zero or more typed message intents.

The observation contains actor ID, logical tick, public projection, the
actor's permitted private projection, delivered messages, permitted action
types, outgoing pending lifecycles, and structured participant memory. Memory
contains previously received messages with receipt ticks and the actor's own
prior action dispositions, including rejection and no-effect results. Current
deliveries join memory before decisions; current own results become visible at
the next coordinate. An undelivered private message is invisible to its recipient.
Hidden world-state values, historical stage descriptions, Reference/evaluation
data and other actors' private reasoning are excluded. Declared event vocabulary
is exposed, including names of later capabilities and record fields. This is not
a historically prefix-clean observation surface.

The decision contains actor ID, logical tick, action type, parameters,
messages, backend identity, and an auditable reason or model record. Generated
IDs identify records but never decide precedence, allocation, or behavior.

Rule labels reason text as configured policy rationale, records matched guards
and hashes the exact observation. Generated observations and environment results,
not that rationale, support statements about what happened. Closed typed payload
fields apply where declared; content predicates inspect the latest qualifying
receipt. Shared handler information requirements are checked independently of
backend choice. A Rule-only guard or window remains policy-owned.

Backends cannot mutate the observation or world, deliver a message, admit an
action, allocate a resource, or declare success. Those operations belong to
transport, environment, and reducer.

Rule rows may have bounded activation windows and state or retained-message
guards. An accepted row completes once. A rejected row may be reconsidered
when visible information changes; the clock alone is not new information.
`no_op` is a valid wait, and an unmet descriptive outcome expectation does not
invalidate an otherwise complete, sealed, replayable run.
