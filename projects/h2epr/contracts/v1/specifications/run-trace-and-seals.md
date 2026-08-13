# Run, trace, and seals

A `RunManifest` binds the runtime bundle, protocol identity, source kind,
policy/component versions, time boundary, and leakage preflight. Its SHA-256
preimage omits only `manifest_sha256` and explicitly operational metadata.

Trace records are append-only and globally unique by `trace_id`. Parent and
causal references resolve to an earlier record in the same trace; self,
forward, dangling, and ambiguous references are invalid. Typed payload refs,
such as `message_sent_trace_ref`, additionally match record type and message
lineage.

For every logical tick containing scientific records:

- `(logical_tick, sequence_in_tick)` is unique and strictly ordered;
- exactly one TickSeal exists;
- TickSeal is the final record of that tick; and
- no same-tick record may follow it.

RunSeal is the final trace record, lies on the last scientific tick, and has
sequence exactly one greater than the prior maximum on that tick. It binds the
complete ordered TickSeal set, run ID, manifest SHA, scientific prefix hash,
and exact unresolved communication sets.

Record hashes bind a nonrecursive preimage with the record's own hash omitted;
`previous_record_hash` forms the chain, starting from 64 zeroes. Tick and run
seals bind canonical scientific bytes. A trace may be stored as
`auditable_invalid`, but only an integrity-valid, closure-valid, eligible trace
may be consumed by the compiler or evaluator.

