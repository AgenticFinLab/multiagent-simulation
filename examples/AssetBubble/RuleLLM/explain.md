# Asset Bubble RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | Asset Bubble |
| Decision Mechanism | LLM-generated trading orders constrained by explicit scenario rules |
| Theory Reference | `examples/AssetBubble/simulation-bases.md` |
| Market Broadcast | `configs/AssetBubble/RuleLLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

The RuleLLM variant preserves the Rule market and gives each LLM investor a
dual-section prompt: `== PERSONA ==` for behavioral identity and
`== DECISION RULES ==` for the corresponding rule logic from
`simulation-bases.md §4`.

| Investor | Theory reference | Code implementation | Prompt/config mapping | Rule embedding |
|---|---|---|---|---|
| `RuleLLMMomentumSpeculator` | `simulation-bases.md §4.1` | `players.py::RuleLLMInvestor.decide()` calls the configured prompt, parses `<decision>` JSON, applies constraints, and validates the order. | `rulellm_momentum.config.extras.llm.sys_message -> RULELLM_MOMENTUM_SYS` | Momentum formula, buy/sell thresholds, leverage cap. |
| `RuleLLMRationalArbitrageur` | `simulation-bases.md §4.2` | Shared RuleLLM path; market data includes `short_cost_rate` and `bubble_ratio`. | `rulellm_arbitrageur.config.extras.llm.sys_message -> RULELLM_ARBITRAGEUR_SYS` | Deviation threshold, short-cost penalty, short-position cap. |
| `RuleLLMNoiseTrader` | `simulation-bases.md §4.3` | Shared RuleLLM path; user template supplies `net_demand`, `volume`, and recent prices. | `rulellm_noise.config.extras.llm.sys_message -> RULELLM_NOISE_SYS` | Sentiment plus herding signal. |
| `RuleLLMValueInvestor` | `simulation-bases.md §4.4` | Shared RuleLLM path; prompt instructs infrequent value trades. | `rulellm_value.config.extras.llm.sys_message -> RULELLM_VALUE_SYS` | Frequency gate and value-deviation sizing. |
| `RuleLLMLeveragedBuyer` | `simulation-bases.md §4.5` | Shared RuleLLM path; prompt checks margin call before normal momentum leverage. | `rulellm_leveraged.config.extras.llm.sys_message -> RULELLM_LEVERAGED_SYS` | Equity-ratio margin call and leveraged momentum sizing. |
| `RuleLLMConservativeHolder` | `simulation-bases.md §4.6` | Shared RuleLLM path; added to topology as `rulellm_conservative`. | `rulellm_conservative.config.extras.llm.sys_message -> RULELLM_CONSERVATIVE_SYS` | Rebalance-frequency gate and target-position rule. |

## §3 Market Mechanism

The coordinator is `players.py::Market`, matching the Rule price equation and
broadcast schema. The only runtime difference is investor decision generation:
orders come from LLM responses constrained by explicit rule text.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/AssetBubble/RuleLLM/players.py` |
| Prompt module | `examples/AssetBubble/RuleLLM/prompts.py` |
| Inference | Uses the project ARK LLM policy. |
| Output parsing | `parse_llm_response_with_thinking()` requires `<analysis>` and `<decision>`; parsed orders include `action`, `bid_price`, `quantity`, and `reasoning`, then pass `validate_order()`. |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/AssetBubble/RuleLLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/AssetBubble/RuleLLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/AssetBubble/RuleLLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/AssetBubble/RuleLLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/AssetBubble/RuleLLM/run_bubble_rulellm.py -c configs/AssetBubble/RuleLLM/simulation.yml
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
