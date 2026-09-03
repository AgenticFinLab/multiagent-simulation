# Decision backends

Every backend consumes the same event package and returns the same typed
participant decision. Environment admission, state reduction, transport,
trace, replay, and Generated EPG construction do not change with the backend.

The shared boundary is defined in
[participant-decision-contract.md](participant-decision-contract.md).

| Backend | Decision mechanism | Current support |
|---|---|---|
| `rule` | Declarative deterministic participant policy | Implemented framework backend; event availability is registry-specific |
| `llm` | Direct model decision | Planned; fails closed |
| `rulellm` | Model decision admitted by declared constraints | Planned; fails closed |

An event publishes a binding only when the implementation exists. Each
binding seals its package parent, backend configuration, realization, and
implementation sources. Attachment must leave the backend-neutral package
identity unchanged.

[backend-matrix.json](backend-matrix.json) is the sole backend catalog.
Use the [Rule realization](rule-realization-template.md),
[LLM prompt](llm-prompt-contract-template.md), or
[RuleLLM admission](rulellm-admission-contract-template.md) template. A
participant Definition never replaces these backend-specific products.
