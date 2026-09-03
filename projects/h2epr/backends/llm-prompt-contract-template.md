# LLM prompt contract template

Pin the Agent/Population semantic parents, prompt renderer, structured-output
schema, model identifier, decoding settings, parser, retry policy, and failure
codes. Credentials are never tracked.

The prompt may project only declared observations, role semantics, admissible
intents, authority constraints, and current lifecycle state. It may not expose
hidden world fields, future Draft text, comparison indices, Reference data, or
another actor's private state.

Define schema rejection, repair attempts, timeout, provider unavailability,
retry exhaustion, and terminal typed failure. Do not silently call a Rule
policy or convert an invalid output into an apparently valid decision.
