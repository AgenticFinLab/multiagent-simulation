# Action, communication, and time

An `ActionIntent` or `MessageIntent` records what an agent requested. It is not
evidence that the world changed or a message arrived. The environment emits a
typed disposition after checking authority, preconditions, topology, channel,
resources, and policy. Only a reducer-approved effect changes authoritative
state.

The canary communication chain is:

```text
MessageIntent
  -> one or more append-only CommunicationDisposition entries
  -> MessageSent when accepted
  -> MessageDelivered or MessageExpired
```

Rejected, prohibited, failed, duplicate, delayed, expired, and unresolved
attempts remain auditable. `delayed` is nonterminal. At RunSeal, the exact
unresolved set is derived from each intent's latest disposition. A duplicate
may point only to a distinct, earlier intent in the same run and must preserve
the source idempotency scope.

Each canary intent has exactly one recipient. A broadcast adapter sorts and
deduplicates recipients, then deterministically creates one independent intent,
disposition, message, and terminal-ID namespace per recipient. This removes
partial-delivery ambiguity without permanently forbidding future native
broadcast semantics.

Scientific ordering uses logical tick, MASim round, execution level,
`sequence_in_tick`, and typed time intervals. Operational wall-clock timestamps
are diagnostic and excluded from scientific hashes where declared.

