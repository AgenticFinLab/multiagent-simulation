# Backend binding template

A binding names one event package, one backend, one backend configuration, one
reviewed realization, one common decision contract, the exact actor/action
surface, and all implementation source hashes.

Publish a binding only when the implementation exists. Planned backends remain
in the package catalog as `planned` and fail closed during admission.

Rule bindings declare determinism. LLM bindings declare model and prompt
provenance. RuleLLM bindings additionally declare admission and repair. No
binding may alter the shared environment, routes, observation contract, trace,
replay, or compiler.
