# EquityPremium LLM — Implementation Explanation

## §1 Overview

The LLM variant replaces deterministic allocation formulas with persona-driven LLM reasoning. Each investor class encodes behavioral biases (loss aversion, horizon preference, risk attitude) in a system prompt. The LLM observes market data and reasons freely within the persona to determine stock allocation adjustments.

| Aspect             | Detail                                                                    |
|--------------------|---------------------------------------------------------------------------|
| Variant            | LLM (language-model persona)                                              |
| Simulation         | EquityPremium                                                             |
| Decision Mechanism | LLM persona system prompts — no hardcoded allocation formulas             |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                           |
| Market Broadcast   | `stock_price`, `prev_stock_price`, `stock_return`, `bond_return`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 LLMMyopicLossAverse (simulation-bases.md §4.1)

| Theory Component                               | Implementation                                                                                                |
|------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Myopic loss aversion (Benartzi & Thaler, 1995) | System prompt: "You evaluate your portfolio every single round; losses hurt 2.25x more than equivalent gains" |
| Loss aversion drives under-allocation          | Persona resists buying after negative returns; LLM reasons about emotional pain of loss                       |
| Short evaluation horizon                       | Prompt instructs: focus on current and recent returns, not long-term trends                                   |

### §2.2 LLMLongTermInvestor (simulation-bases.md §4.2)

| Theory Component                          | Implementation                                                                        |
|-------------------------------------------|---------------------------------------------------------------------------------------|
| Long evaluation horizon (Samuelson, 1969) | System prompt: "You ignore short-term volatility; focus on long-term expected return" |
| Stable high allocation                    | Persona maintains 60–80% stock target; LLM reasons about long-term compounding        |
| Counter-cyclical buying                   | Prompt instructs buying on dips that short-term investors are selling                 |

### §2.3 LLMInstitutionalInvestor (simulation-bases.md §4.3)

| Theory Component                                | Implementation                                                                   |
|-------------------------------------------------|----------------------------------------------------------------------------------|
| Risk-neutral benchmark (Mehra & Prescott, 1985) | System prompt: "You maximize expected return; you are indifferent to volatility" |
| Excess return signal                            | LLM reasons about excess return between stock and bond; allocates proportionally |
| No behavioral bias                              | Persona explicitly lacks loss aversion or inertia                                |

### §2.4 LLMRiskAverseSaver (simulation-bases.md §4.4)

| Theory Component                                           | Implementation                                                                      |
|------------------------------------------------------------|-------------------------------------------------------------------------------------|
| Prospect theory bond preference (Kahneman & Tversky, 1979) | System prompt: "You strongly prefer capital preservation; any loss is unacceptable" |
| Persistent under-allocation                                | Persona demands very high premium before buying stocks; defaults to bonds           |
| Extreme loss aversion                                      | Prompt encodes: "Even a 1% drop triggers reduction in stock position"               |

### §2.5 LLMRationalOptimizer (simulation-bases.md §4.5)

| Theory Component                                | Implementation                                                            |
|-------------------------------------------------|---------------------------------------------------------------------------|
| Noise trading / rational baseline (Black, 1986) | System prompt: "You optimize expected utility; use all available signals" |
| Adaptive allocation                             | LLM reasons about full market context; adjusts allocation dynamically     |
| Behavioral awareness                            | Persona acknowledges other investors' biases and exploits mispricings     |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) × (1 + μ_stock + demand_impact + ε(t))
demand_impact = 0.001 × sum(stock_qty_i)
```

Market class is imported from or shared with Rule/players.py. All LLM investors send `stock_qty` orders.

## §4 Variant Architecture

| Component      | Detail                                                                                     |
|----------------|--------------------------------------------------------------------------------------------|
| Base class     | `LLMInvestor` → `GeneralPlayer`                                                            |
| Inference      | `LangChainAPIInference` (3-attempt retry)                                                  |
| Context        | `stock_price`, `prev_stock_price`, `stock_return`, `bond_return`, `cash`, `stock`, `round` |
| Output parsing | `LLMInvestor._parse_response()` requires `stock_qty` and `reasoning`; player adds `strategy` |
| Retry logic    | 3 attempts; persistent parse failure raises a runtime error                                |

## §5 Config Reference

Config file: `configs/EquityPremium/LLM/simulation.yml`

LLM config under `extras.llm`:
- `lm_name`: model identifier
- `generation_config`: temperature, max_tokens etc.

## §6 Running Instructions

```bash
python -m examples.EquityPremium.LLM.run_equity_premium_llm \
    -c configs/EquityPremium/LLM/simulation.yml
```

## §7 Expected Behavior

- **Premium emergence**: LLM loss-averse personas produce 3–9% annualized premium; higher variance than Rule
- **Allocation variability**: LLMMyopicLossAverse may hold 15–55% stocks (wider range than Rule's 20–40%)
- **Horizon effect**: LLMLongTermInvestor maintains 55–75% allocation (similar to Rule)
- **SEP range**: 0.03–0.09 (wider than Rule due to LLM stochasticity)

## §8 References

See `simulation-bases.md §2` for full DOI citations for all theoretical foundations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
