# Asset Bubble LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | Asset Bubble |
| Decision Mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning |
| Theory Reference | `examples/AssetBubble/simulation-bases.md` |
| Market Broadcast | `configs/AssetBubble/LLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

The LLM variant preserves the Rule market coordinator but delegates investor
decisions to persona-only prompts. Prompts describe investor character and risk
style without embedding the deterministic Rule formulas.

| Investor | Theory reference | Code implementation | Prompt/config mapping | Decision contract |
|---|---|---|---|---|
| `LLMGreaterFoolSpeculator` | `simulation-bases.md §4.1` | `players.py::LLMInvestor.decide()` calls the configured prompt and parses `<decision>` JSON. | `llm_greater_fool.config.extras.llm.sys_message -> LLM_GREATER_FOOL_SYS` | Momentum persona emits `action`, `bid_price`, `quantity`, `reasoning`. |
| `LLMRationalArbitrageur` | `simulation-bases.md §4.2` | Same shared LLM decision path; portfolio constraints are applied after parsing. | `llm_arbitrageur.config.extras.llm.sys_message -> LLM_ARBITRAGEUR_SYS` | Fundamental-value analyst persona. |
| `LLMSentimentTrader` | `simulation-bases.md §4.3` | Same shared LLM decision path; market state includes `net_demand` and `return_pct`. | `llm_sentiment.config.extras.llm.sys_message -> LLM_SENTIMENT_SYS` | Sentiment/crowd-following persona. |
| `LLMValueInvestor` | `simulation-bases.md §4.4` | Same shared LLM decision path; user template supplies price, fundamental, and portfolio state. | `llm_value.config.extras.llm.sys_message -> LLM_VALUE_SYS` | Patient value-investing persona. |
| `LLMLeveragedSpeculator` | `simulation-bases.md §4.5` | Same shared LLM decision path; prompt highlights portfolio-value risk. | `llm_leveraged.config.extras.llm.sys_message -> LLM_LEVERAGED_SYS` | Leveraged trader persona. |
| `LLMConservativeHolder` | `simulation-bases.md §4.6` | Same shared LLM decision path; added to topology as `llm_conservative`. | `llm_conservative.config.extras.llm.sys_message -> LLM_CONSERVATIVE_SYS` | Conservative allocation persona. |

## §3 Market Mechanism

The coordinator is `players.py::Market`, which retains the same price formation
as `Rule/players.py::Market`: demand impact, weak mean reversion toward the
growing fundamental, and Gaussian noise. Investor turns are LLM-generated, but
the market consumes the same canonical trading order fields as the Rule baseline.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/AssetBubble/LLM/players.py` |
| Prompt module | `examples/AssetBubble/LLM/prompts.py` |
| Inference | Uses the project ARK LLM policy. |
| Output parsing | `parse_llm_response_with_thinking()` requires `<analysis>` and `<decision>`; the decision JSON is then validated against `masim.format.order.validate_order`. |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/AssetBubble/LLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/AssetBubble/LLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/AssetBubble/LLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/AssetBubble/LLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/AssetBubble/LLM/run_bubble_llm.py -c configs/AssetBubble/LLM/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/AssetBubble/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/AssetBubble/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
