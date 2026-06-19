# FramingEffect / Frame Invariant Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FramingEffect |
| Agent type | Frame Invariant Trader |
| Canonical class | `FrameInvariantTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: The FrameInvariantTrader represents professional fund managers or quant traders who evaluate information by substance rather than framing. They trade contrariwise to framing-biased agents: buying when price is below fundamental (stabilizing) and selling when above (stabilizing). They represent the rational counterparty that partially constrains framing-induced mispricings. Their larger activation threshold (5% vs. 2% for biased agents) reflects the higher evidence bar rational traders require before committing capital.

## Financial Theory / Theoretical Basis

### Rule / `FrameInvariantTrader`
- Theory: simulation-bases.md Section 4.3 -- FrameInvariantTrader
- Theoretical basis: Frame-invariant rationality (Levin et al., 1998 baseline).

### LLM / `LLMFrameInvariantTrader`
- LLM-driven FrameInvariantTrader: evaluates by substance regardless of framing. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMFrameInvariantTrader`
- RuleLLM-driven FrameInvariantTrader: evaluates by substance regardless of framing. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMFrameInvariantTrader`
- RAG-augmented FrameInvariantTrader: evaluates by substance regardless of framing. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FramingEffect.LLM.prompts:LLM_FRAME_INVARIANT_TRADER_SYS', 'user_message': 'examples.FramingEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_FRAME_INVARIANT_TRADER_SYS', 'user_message': 'examples.FramingEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FramingEffect.Rag.prompts:RAGLLM_FRAME_INVARIANT_TRADER_SYS', 'user_message': 'examples.FramingEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| value_trigger | Rule: `0.04` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | frameinvarianttrader | FrameInvariantTrader | `FrameInvariantTrader` | 1 | `examples/FramingEffect/Rule/players.py` |
| LLM | frameinvarianttrader | FrameInvariantTrader | `LLMFrameInvariantTrader` | 1 | `examples/FramingEffect/LLM/players.py` |
| RuleLLM | frameinvarianttrader | FrameInvariantTrader | `RuleLLMFrameInvariantTrader` | 1 | `examples/FramingEffect/RuleLLM/players.py` |
| Rag | frameinvarianttrader | FrameInvariantTrader | `RagLLMFrameInvariantTrader` | 1 | `examples/FramingEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 FrameInvariantTrader

**Summary**: The FrameInvariantTrader represents professional fund managers or quant traders who evaluate information by substance rather than framing. They trade contrariwise to framing-biased agents: buying when price is below fundamental (stabilizing) and selling when above (stabilizing). They represent the rational counterparty that partially constrains framing-induced mispricings. Their larger activation threshold (5% vs. 2% for biased agents) reflects the higher evidence bar rational traders require before committing capital.

**Theoretical Foundation**: Frame-invariant rationality as rational benchmark in Levin et al. (1998); limits to arbitrage (Shleifer & Vishny, 1997) explain the 500-share cap.

**Activation Scenarios**:

| Market Condition                   | Response                                    | Economic Effect                                           |
|------------------------------------|---------------------------------------------|-----------------------------------------------------------|
| deviation < -0.05 (undervaluation) | Buy; qty = min(500, int(                    | deviation                                                 |
| deviation > 0.05 (overvaluation)   | Sell; qty = min(500, int(deviation x 3000)) | Stabilizing; provides supply during framing-driven buying |
|                                    | deviation                                   | <= 0.05                                                    |

## Source Docstring Excerpts

### Rule / `FrameInvariantTrader`

```text
Theory: simulation-bases.md Section 4.3 -- FrameInvariantTrader

Theoretical basis: Frame-invariant rationality (Levin et al., 1998 baseline).
Evaluates information by substance regardless of framing; computes equivalent outcomes.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMFrameInvariantTrader`

```text
LLM-driven FrameInvariantTrader: evaluates by substance regardless of framing. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMFrameInvariantTrader`

```text
RuleLLM-driven FrameInvariantTrader: evaluates by substance regardless of framing. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMFrameInvariantTrader`

```text
RAG-augmented FrameInvariantTrader: evaluates by substance regardless of framing. Theory: simulation-bases.md Section 4.3.
```
