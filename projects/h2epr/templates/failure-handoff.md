# Failure and resume handoff

## Exact stop state

| Field | Value |
|---|---|
| Branch, HEAD, and tree | |
| Worktree, index, and unmerged state | |
| Event, phase, and authorized endpoint | |
| Source Profile and exposure | |
| Last accepted parent identities | |
| Candidate paths and hashes | |
| Raw custody and attempt dispositions | |
| Tests completed and failed | |

## Failure ledger

| Failure ID | Typed code or observation | Direct evidence | Owning layer | Retryable? | Required condition before retry |
|---|---|---|---|---|---|
| | | | | no/yes | |

Preserve failed custody. A semantic, identity, integrity, or protected-exposure
failure is not made retryable by changing a timeout or seed.
When a materialization has `failure-receipt.json`, record its exact hash, sealed
ticks and unresolved transport. `partial_state.json` may include an unsealed
coordinate and is not a resumable authoritative checkpoint. A later retry
uses a fresh root; an open domain outcome in a valid run is not an execution
failure.

## Boundary at stop

List unfinished work, prohibited next actions, assumptions not yet admitted,
and any local-only recovery reference. State whether the candidate is
unaccepted, accepted with limitations, or invalidated by changed parents.

## Resume protocol

Recheck Git state, source/profile hashes, accepted parents, candidate hashes,
and custody existence before relying on this record. Resolve open failures at
their owning layer and rerun the named checks. Record one next legal action;
the handoff does not authorize later phases or remote operations.
