# EquityPremium RuleLLM — Implementation Explanation

## §1 Overview

The RuleLLM variant embeds explicit allocation rules directly into LLM system prompts. Key behavioral parameters (loss_aversion thresholds, target allocations) are encoded as instructions the LLM cannot override, while LLM reasoning contextualizes quantity decisions within these constraints.

| Aspect             | Detail                                                                            |
|--------------------|-----------------------------------------------------------------------------------|
| Variant            | RuleLLM (rule-embedded LLM)                                                       |
| Simulation         | EquityPremium                                                                     |
| Decision Mechanism | Allocation rules embedded in system prompt; LLM contextualizes within constraints |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                   |
| Market Broadcast   | `stock_price`, `prev_stock_price`, `stock_return`, `bond_return`, `round`         |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMMyopicLossAverse (simulation-bases.md §4.1)

| Theory Component                               | Implementation                                                                                                                             |
|------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Myopic loss aversion (Benartzi & Thaler, 1995) | System prompt embeds: "Compute perceived_risk = vol × (1 + 2.25 × loss_prob); set target = max(0.1, 0.5 − risk_aversion × perceived_risk)" |
| Gradual rebalancing                            | Rule: "Adjust toward target by at most 30% of gap per round"                                                                               |
| LLM contextualisation                          | LLM explains its loss aversion reasoning but cannot change the evaluation formula                                                          |

### §2.2 RuleLLMLongTermInvestor (simulation-bases.md §4.2)

| Theory Component                          | Implementation                                                                                |
|-------------------------------------------|-----------------------------------------------------------------------------------------------|
| Long evaluation horizon (Samuelson, 1969) | System prompt embeds: "Maintain target_stock_pct allocation; adjust 20% of gap per round"     |
| Stable allocation                         | Rule prevents panic selling; LLM reasons about long-term outlook but follows rebalancing rule |
| LLM contextualisation                     | LLM may add narrative about why current price is a buying opportunity                         |

### §2.3 RuleLLMInstitutionalInvestor (simulation-bases.md §4.3)

| Theory Component                                | Implementation                                                                           |
|-------------------------------------------------|------------------------------------------------------------------------------------------|
| Risk-neutral benchmark (Mehra & Prescott, 1985) | System prompt embeds: "Trade proportional to excess_return = stock_return − bond_return" |
| Proportional allocation                         | Rule: "stock_qty = excess_return × multiplier, clamped to [−20, +20]"                    |
| LLM contextualisation                           | LLM contextualizes excess return signal with market narrative                            |

### §2.4 RuleLLMRiskAverseSaver (simulation-bases.md §4.4)

| Theory Component                                           | Implementation                                                                        |
|------------------------------------------------------------|---------------------------------------------------------------------------------------|
| Prospect theory bond preference (Kahneman & Tversky, 1979) | System prompt embeds: "Target 25% stock allocation; adjust only 10% of gap per round" |
| Persistent under-allocation                                | Rule locks slow rebalancing; LLM cannot override the low target                       |
| LLM contextualisation                                      | LLM reasons about preservation but cannot raise allocation above rule target          |

### §2.5 RuleLLMRationalOptimizer (simulation-bases.md §4.5)

| Theory Component                                                 | Implementation                                                                                                                   |
|------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Expected utility optimization (Black, 1986 / rational benchmark) | System prompt embeds noise-trading boundary: "Random quantity in [−noise_std, +noise_std] unless excess return signal is strong" |
| Adaptive within bounds                                           | LLM may use signal strength to directionally trade; rule bounds maximum deviation                                                |
| LLM contextualisation                                            | LLM explains reasoning process while staying within encoded quantity bounds                                                      |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) × (1 + μ_stock + demand_impact + ε(t))
```

Market is shared with Rule variant. All RuleLLM investors send `stock_qty` orders.

## §4 Variant Architecture

| Component        | Detail                                                                       |
|------------------|------------------------------------------------------------------------------|
| Base class       | `RuleLLMInvestor` → `GeneralPlayer`                                          |
| Inference        | `LangChainAPIInference` (3-attempt retry)                                    |
| Context          | `stock_price`, `stock_return`, `bond_return`, `cash`, `stock`, `round`       |
| Output parsing   | `parse_equity_premium_decision()` requires `stock_qty` and `reasoning`; player adds `strategy` |
| Rule enforcement | Thresholds and limits embedded in prompt; LLM violation → retry fallback     |

## §5 Config Reference

Config file: `configs/EquityPremium/RuleLLM/simulation.yml`

All Rule parameters plus LLM config under `extras.llm`:
- `lm_name`, `generation_config`

## §6 Running Instructions

```bash
python -m examples.EquityPremium.RuleLLM.run_equity_premium_rulellm \
    -c configs/EquityPremium/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- **SEP**: 0.04–0.07 (close to Rule baseline due to embedded allocation rules)
- **EAD stability**: Higher than pure LLM; embedded rules constrain allocation drift
- **LPI**: Similar to Rule; rebalancing rules prevent extreme under-allocation
- **PWE**: 0.85–0.97 (better than pure LLM due to rule-constrained stability)

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
