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
Hidden world state, historical stage labels, future Draft content, Reference
data, evaluation data, and other actors' private reasoning are excluded.

The decision contains actor ID, logical tick, action type, parameters,
messages, backend identity, and an auditable reason or model record. Generated
IDs identify records but never decide precedence, allocation, or behavior.

Backends cannot mutate the observation or world, deliver a message, admit an
action, allocate a resource, or declare success. Those operations belong to
transport, environment, and reducer.

Rule rows may have bounded activation windows and state or retained-message
guards. An accepted row completes once. A rejected row may be reconsidered
when visible information changes; the clock alone is not new information.
`no_op` is a valid wait, and an unmet descriptive outcome expectation does not
invalidate an otherwise complete, sealed, replayable run.
