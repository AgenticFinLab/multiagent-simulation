# OverconfidenceBias LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Simulation | OverconfidenceBias |
| Decision Mechanism | Persona-only LLM decisions constrained by canonical trading schema |
| Theory Reference | `simulation-bases.md §2` and `simulation-bases.md §4` |
| Market Broadcast | `price`, `fundamental`, `deviation`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 OverconfidentTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Signal overprecision | `LLM_OVERCONFIDENT_TRADER_PROMPT` frames weak evidence as meaningful. |
| Excess trading | The model chooses a schema-valid action and quantity. |
| Constraint enforcement | `LLMInvestor.decide()` caps buy/sell quantities. |

### §2.2 SelfAttributor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Skill attribution | `LLM_SELF_ATTRIBUTOR_PROMPT` asks the model to reason about success and bad luck. |
| Confidence drift | The prompt allows favorable states to reinforce exposure. |
| Schema discipline | Parser requires `action`, `bid_price`, `quantity`, `reasoning`, and `analysis`. |

### §2.3 CalibratedTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Cautious signal use | `LLM_CALIBRATED_TRADER_PROMPT` discourages small-signal overreaction. |
| Benchmark behavior | Current price and fundamental value are supplied every round. |
| Bounded orders | Player constraints enforce cash and inventory limits. |

### §2.4 ContrarianInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Overreaction fading | `LLM_CONTRARIAN_INVESTOR_PROMPT` frames deviations as possible overshoots. |
| Stabilization | Parsed orders enter the shared market. |
| Risk control | Quantity is non-negative and bounded by portfolio state. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Uninformed flow | `LLM_NOISE_TRADER_PROMPT` uses weak sentiment and random impulses. |
| Liquidity role | Orders provide background market flow. |
| Contract validity | Output must satisfy the canonical parser contract. |

## §3 Market Mechanism

The LLM variant reuses the Rule `Market` and sends canonical orders into the same price equation.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Coordinator | Rule market imported from `examples.OverconfidenceBias.Rule.players` |
| Investors | `LLMInvestor` subclasses with persona-only prompts |
| Inference | `LangChainAPIInference` from config model settings |
| Parser | `parse_llm_response_with_thinking()` |
| Output Contract | Required `action`, `bid_price`, `quantity`, `reasoning`, and `analysis` |
| Error Policy | Retryable provider errors are retried; invalid final decision contracts raise. |

## §5 Config Reference

Primary config: `configs/OverconfidenceBias/LLM/simulation.yml`. Prompt and model settings live in `configs/OverconfidenceBias/LLM/players.yml`.

## §6 Running Instructions

```bash
python examples/OverconfidenceBias/LLM/run_overconfidencebias_llm.py \
  -c configs/OverconfidenceBias/LLM/simulation.yml
```

## §7 Expected Behavior

- Persona reasoning expresses overconfidence, self-attribution, calibration, contrarian correction, or noise.
- Accepted orders use the canonical schema.
- Market outputs remain comparable with Rule.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
