# EuropeanDebtCrisis RuleLLM — Implementation Explanation

## §1 Overview

The RuleLLM variant embeds crisis threshold rules directly in LLM system prompts. Sell, panic, and intervention thresholds are explicitly encoded; LLM reasoning operates within these constraints, contextualizing quantity and timing but unable to violate the encoded thresholds.

| Aspect             | Detail                                                                             |
|--------------------|------------------------------------------------------------------------------------|
| Variant            | RuleLLM (rule-embedded LLM)                                                        |
| Simulation         | EuropeanDebtCrisis                                                                 |
| Decision Mechanism | Crisis thresholds embedded in system prompt; LLM contextualizes within constraints |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                    |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                                       |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMPeripheryBondSeller (simulation-bases.md §4.1)

| Theory Component                              | Implementation                                                                           |
|-----------------------------------------------|------------------------------------------------------------------------------------------|
| Self-fulfilling speculation (De Grauwe, 2011) | System prompt embeds: "Sell when deviation < sell_threshold; buy on recovery above 0.08" |
| Threshold-locked crisis trigger               | LLM cannot sell before threshold; adjusts only quantity within permitted range           |
| LLM contextualisation                         | LLM reasons about crisis narrative but follows embedded sell rule                        |

### §2.2 RuleLLMCreditorPanicker (simulation-bases.md §4.2)

| Theory Component                            | Implementation                                                                             |
|---------------------------------------------|--------------------------------------------------------------------------------------------|
| Sovereign-bank nexus (Acharya et al., 2014) | System prompt embeds: "Withdraw when deviation < panic_threshold; recovery threshold 0.06" |
| Doom loop timing locked                     | LLM cannot panic before panic_threshold; AR is bounded by rule                             |
| LLM contextualisation                       | LLM reasons about bank contagion severity but follows rule activation                      |

### §2.3 RuleLLMCoreBondBuyer (simulation-bases.md §4.3)

| Theory Component                         | Implementation                                                                             |
|------------------------------------------|--------------------------------------------------------------------------------------------|
| Flight-to-quality (De Grauwe & Ji, 2012) | System prompt embeds: "Buy when deviation < flight_threshold; sell on recovery above 0.10" |
| Threshold-locked entry                   | LLM follows embedded flight threshold; adjusts quantity within allowed range               |
| LLM contextualisation                    | LLM reasons about safety narrative; quantity may be larger on extreme deviations           |

### §2.4 RuleLLMECBIntervenor (simulation-bases.md §4.4)

| Theory Component                     | Implementation                                                                       |
|--------------------------------------|--------------------------------------------------------------------------------------|
| Central bank backstop (Draghi, 2012) | System prompt embeds: "Buy when deviation < intervention_threshold; up to 800 units" |
| Threshold-locked intervention        | LLM cannot intervene before threshold; size is bounded at 800                        |
| LLM contextualisation                | LLM reasons about central bank credibility while following embedded trigger          |

### §2.5 RuleLLMHedgedFund (simulation-bases.md §4.5)

| Theory Component                              | Implementation                                                                      |
|-----------------------------------------------|-------------------------------------------------------------------------------------|
| Limits to arbitrage (Shleifer & Vishny, 1997) | System prompt embeds: "Trade when                                                   |
| Symmetric arbitrage rule                      | LLM follows embedded entry rule; may size more conservatively at extreme deviations |
| LLM contextualisation                         | LLM reasons about risk/reward; quantity within 0–500 range                          |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Market class shared with Rule variant. All RuleLLM investors send orders to the same Market.

## §4 Variant Architecture

| Component        | Detail                                                                    |
|------------------|---------------------------------------------------------------------------|
| Base class       | `RuleLLMInvestor` → `GeneralPlayer`                                       |
| Inference        | `LangChainAPIInference` (3-attempt retry)                                 |
| Context          | `price`, `fundamental`, `deviation`, `cash`, `position`, `round`          |
| Output parsing   | `parse_llm_response_with_thinking()` → canonical `action`, `bid_price`, `quantity`, `reasoning` |
| Rule enforcement | All thresholds embedded in prompt; malformed or rule-violating output fails after bounded retry |

## §5 Config Reference

Config file: `configs/EuropeanDebtCrisis/RuleLLM/simulation.yml`

All Rule parameters plus LLM config under `extras.llm`:
- `lm_name`, `generation_config`

## §6 Running Instructions

```bash
python -m examples.EuropeanDebtCrisis.RuleLLM.run_edc_rulellm \
    -c configs/EuropeanDebtCrisis/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- **CDI**: Similar to Rule (0.14–0.32); embedded thresholds prevent crisis onset variability
- **CD**: Similar to Rule (10–28 rounds); threshold-locked panic determines duration
- **IER**: 0.72–0.95 (ECB threshold embedded; stable coverage)
- **AR**: 0.8–1.4 (doom loop bounded by embedded thresholds)

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
