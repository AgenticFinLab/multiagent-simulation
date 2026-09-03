# Participant decision contract

Every backend receives one immutable observation for every active actor from a
single sealed pre-state. It returns exactly one decision record containing one
typed action intent and zero or more typed message intents.

The observation contains actor ID, logical tick, public projection, the
actor's permitted private projection, delivered messages, permitted action
types, and references to relevant pending lifecycles. It excludes hidden world
state, undelivered messages, future Draft content, Reference data, evaluation
data, and other actors' private reasoning.

The decision contains actor ID, logical tick, action type, parameters,
messages, backend identity, and an auditable reason or model record. Generated
IDs identify records but never decide precedence, allocation, or behavior.

Backends cannot mutate the observation or world, deliver a message, admit an
action, allocate a resource, or declare success. Those operations belong to
transport, environment, and reducer.
