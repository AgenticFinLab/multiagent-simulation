# API and RAG Contract Gates

## Purpose

Use these gates for API rows: `LLM`, `RuleLLM`, and `Rag`. They prevent known
prompt/parser/config failures before a full 200-round run starts.

## Gate 1: API Prompt And Parser Contract

For API rows, inspect effective prompts and players:

- Every `extras.llm.sys_message` and `extras.llm.user_message` reference
  resolves, unless the player intentionally uses class-level or dynamic prompts.
- `lm_name` is the intended model, currently
  `ark/doubao-seed-2-0-mini-260428`.
- Fields read as `decision["field"]` or `order["field"]` are produced by the
  parser or required by the effective prompt.
- Trading rows request exactly the trading fields consumed by code:
  `action`, `bid_price` if used, `quantity`, `reasoning`, and scenario-specific
  extras such as `provides_liquidity` only when consumed.
- Current-market quantity schemas that explicitly do not consume price fields
  must use a quantity-order parser and must not reuse a canonical parser that
  requires `bid_price`.
- Dynamic user prompts built inside `players.py` must not narrow or contradict
  the schema already stated in system prompts. The most recent failure pattern
  was a correct system prompt but a dynamic user prompt that only requested
  `action` and `quantity`, causing missing `reasoning` at order construction.
- Fallback decisions must contain the same fields later recorded into orders.
  A fallback that returns only `action` and `quantity` is not valid when the
  order writes `decision["reasoning"]` or other consumed fields.
- Special schemas such as `RumorSpread` and `EchoChamber` are checked against
  their scenario parser; do not force canonical trading fields into them.

If one row reveals a shared missing field, run a static audit over related rows
before patching only the observed row.

Manually walk every planned row's `analysis.py`, `players.py`, and prompt/parser pair before launching API batches: confirm every field written by an order or `decision` dict is consumed downstream, and every field consumed downstream is written. For special-schema scenarios (`RumorSpread`, `EchoChamber`), check against the scenario's own parser rather than forcing canonical trading fields.

## Gate 2: RAG Assets And Embedding

For each `Rag` row:

- `knowledge` and `private_knowledge.rag` resolve to usable directories.
- `examples/document-sources/MinerU_processed` exists and has files.
- `examples/document-sources/rag_index` exists or can be built.
- Embedding config is:

```yaml
embed_type: "litellm"
embed_model: "openai/hunyuan-embedding"
embed_api_key: "{{ HUNYUAN_API_KEY }}"
```

- Hunyuan key is set on the machine.

RAG rows should be launched more conservatively than nonRAG rows because native
thread aborts can appear after many successful rounds.
