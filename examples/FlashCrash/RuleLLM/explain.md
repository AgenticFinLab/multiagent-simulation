# FlashCrash RuleLLM — Explain

## §1 Overview

| Item             | Description                                                                                                          |
|------------------|----------------------------------------------------------------------------------------------------------------------|
| **Variant**      | RuleLLM                                                                                                              |
| **Scenario**     | Flash Crash                                                                                                          |
| **Phenomenon**   | Rapid intraday price collapse and recovery — hybrid rule + LLM decision layer                                        |
| **Agent count**  | 6 types: HighFrequencyTrader, MarketMaker, AlgorithmicTrader, StopLossTrader, FundamentalTrader, RetailTrader        |
| **Market model** | Same liquidity-sensitive model as Rule variant                                                                       |
| **Key feature**  | Rule logic generates a base signal; LLM can override quantity or `provides_liquidity` via structured prompt response |
| **Determinism**  | Medium — rule provides anchor; LLM injects variability at override points                                            |

## §2 Theory → Implementation Mapping

| Theory construct           | simulation-bases.md reference | RuleLLM implementation                                                                                                            |
|----------------------------|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| Momentum detection         | §4.1 HighFrequencyTrader      | Rule computes `signal`; LLM confirms or scales `quantity`; Theory: simulation-bases.md §4.1                                       |
| Liquidity withdrawal       | §4.2 MarketMaker              | Rule sets `provides_liquidity` from `volatility_threshold`; LLM can delay or advance withdrawal; Theory: simulation-bases.md §4.2 |
| Trend amplification        | §4.3 AlgorithmicTrader        | Rule computes `trend × trend_sensitivity`; LLM validates trend direction; Theory: simulation-bases.md §4.3                        |
| Stop-loss cascade          | §4.4 StopLossTrader           | Rule checks `price < stop_price`; LLM can hold or trigger earlier; Theory: simulation-bases.md §4.4                               |
| Value stabilisation        | §4.5 FundamentalTrader        | Rule computes `deviation`; LLM sets final `quantity`; Theory: simulation-bases.md §4.5                                            |
| Noise background           | §4.6 RetailTrader             | Rule random; LLM not invoked for RetailTrader; Theory: simulation-bases.md §4.6                                                   |
| Liquidity-sensitive market | §3 Market Design              | Same formula; `provides_liquidity` sourced from LLM response field                                                                |

## §3 LLM Override Points

```
MarketMaker.decide():
  rule_signal = compute_provides_liquidity(price_return, volatility_threshold)
  llm_response = call_llm(market_context, rule_signal)
  provides_liquidity = llm_response["provides_liquidity"]  # LLM may override
  quantity = llm_response["quantity"]                       # LLM may adjust size

HighFrequencyTrader.decide():
  rule_quantity = signal × base_position_size × speed_advantage
  llm_response = call_llm(market_context, rule_quantity)
  quantity = llm_response.get("quantity", rule_quantity)    # LLM confirms or changes

StopLossTrader.decide():
  rule_triggered = price < stop_price and position > 0
  llm_response = call_llm(market_context, rule_triggered)
  quantity = llm_response["quantity"]                       # LLM decides final sell size
```

## §4 Crash Mechanism (RuleLLM Logic)

```
Phase 1 (Normal):
  Rule signal → near-zero quantity; MarketMaker provides_liquidity = True
  LLM context: normal → confirms rule

Phase 2 (Trigger):
  HFT rule signal → sell burst
  MarketMaker rule → provides_liquidity = False at threshold
  LLM may hesitate (qualitative "not yet severe enough") → withdrawal delayed

Phase 3 (Cascade):
  Rule forces stop-loss execution; LLM may reduce sell size
  provides_liquidity from LLM response determines liquidity_factor

Phase 4 (Recovery):
  Rule computes FT entry; LLM sizes up buy if "severely undervalued"
```

## §5 Key Parameters

| Parameter                       | Location           | Effect                                                 |
|---------------------------------|--------------------|--------------------------------------------------------|
| `volatility_threshold`          | MarketMaker extras | Anchor for LLM override check                          |
| `lm_name`                       | LLM config         | Model version affects override frequency               |
| `sys_message`                   | prompts.py         | LLM market-maker persona — affects withdrawal decision |
| `generation_config.temperature` | LLM config         | Higher → more LLM deviation from rule                  |

## §6 Files

| File                                        | Purpose                             |
|---------------------------------------------|-------------------------------------|
| `players.py`                                | Market + 6 RuleLLM investor classes |
| `prompts.py`                                | System and user prompt templates    |
| `run_flash_crash_rulellm.py`                | Entry point                         |
| `configs/FlashCrash/RuleLLM/simulation.yml` | Main config                         |
| `configs/FlashCrash/RuleLLM/players.yml`    | Agent + LLM config                  |
| `simulation-bases.md`                       | Full theoretical foundations        |
| `analysis-bases.md`                         | Metrics and analysis guide          |

## §7 Running

```bash
export ARK_API_KEY='your-api-key'
python examples/FlashCrash/RuleLLM/run_flash_crash_rulellm.py -c configs/FlashCrash/RuleLLM/simulation.yml
```

## §8 Expected Behaviour

| Phase    | Rounds | Key observable vs Rule                                  |
|----------|--------|---------------------------------------------------------|
| Normal   | 1–10   | Similar to Rule                                         |
| Trigger  | 11–15  | LLM may delay or advance HFT selling                    |
| Cascade  | 16–25  | `provides_liquidity` from LLM; cascade depth may differ |
| Trough   | 26–30  | Slightly shallower if LLM hesitates                     |
| Recovery | 31–50  | LLM may accelerate FT buying                            |

## §9 References

1. Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). *Journal of Finance*, 72(3), 967-998. doi:10.1111/jofi.12498
2. Grossman, S. J., & Miller, M. H. (1988). *Journal of Finance*, 43(3), 617-633. doi:10.1111/j.1540-6261.1988.tb02607.x
3. De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). *Journal of Finance*, 45(2), 379-395.
4. Brunnermeier, M. K., & Pedersen, L. H. (2005). *Journal of Finance*, 60(4), 1825-1863.
5. Shiller, R. J. (1981). *American Economic Review*, 71(3), 421-436.
6. Black, F. (1986). *Journal of Finance*, 41(3), 529-543.
