# RuleLLM admission contract template

RuleLLM uses the same LLM proposal surface as the direct LLM backend and the
same environment as every backend. A declared admission layer validates the
proposal against actor identity, action space, authority, payload, target,
range, lifecycle, and hard participant invariants.

Pin the proposal model, prompt/parser, constraint catalog, validator source,
repair limit, rejection code, and fallback policy. A fallback may only emit a
typed failure or an explicitly declared safe intent; it may not invoke a hidden
full Rule policy and still label the result RuleLLM.

Tests cover accepted proposals, every rejection family, bounded repair,
repeated invalid output, and environment rejection after admission.
