# FlashCrash2010 RuleLLM — Explain

## §1 Overview

| Item             | Description                                                                                                                     |
|------------------|---------------------------------------------------------------------------------------------------------------------------------|
| **Variant**      | RuleLLM                                                                                                                         |
| **Scenario**     | FlashCrash2010                                                                                                                  |
| **Phenomenon**   | May 6, 2010 Flash Crash — hybrid rule + LLM decision layer                                                                      |
| **Agent count**  | 5 types: HFTMarketMaker, MomentumChaser, FundamentalTrader, StopLossTrader, NoiseTrader                                         |
| **Market model** | Same order-book depth model as Rule variant                                                                                     |
| **Key feature**  | Rule logic generates a base signal; LLM can override `quantity` and `provides_liquidity`; `agent_type` is fixed per agent class |
| **Determinism**  | Medium — rule anchor; LLM injects variability at override points                                                                |

## §2 Theory → Implementation Mapping

| Theory construct       | simulation-bases.md reference | RuleLLM implementation                                                                                                |
|------------------------|-------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| HFT stress withdrawal  | §4.1 HFTMarketMaker           | Rule checks velocity vs `withdrawal_threshold`; LLM can advance or delay withdrawal; Theory: simulation-bases.md §4.1 |
| Momentum amplification | §4.2 MomentumChaser           | Rule computes velocity-based quantity; LLM confirms or scales; Theory: simulation-bases.md §4.2                       |
| Value stabilisation    | §4.3 FundamentalTrader        | Rule computes deviation-triggered size; LLM adjusts final buy/sell; Theory: simulation-bases.md §4.3                  |
| Stop-loss cascade      | §4.4 StopLossTrader           | Rule determines stop trigger; LLM decides whether to honour or hold; Theory: simulation-bases.md §4.4                 |
| Noise background       | §4.5 NoiseTrader              | Rule random; LLM not invoked for NoiseTrader; Theory: simulation-bases.md §4.5                                        |
| Order-book depth       | §3 Market Design              | `agent_type` fixed; `provides_liquidity` from LLM response for HFTMarketMaker                                         |

## §3 LLM Override Points

```
HFTMarketMaker.decide():
  rule_withdrawal = velocity > withdrawal_threshold
  rule_provides_liquidity = not rule_withdrawal
  llm_response = call_llm(market_context, rule_provides_liquidity)
  provides_liquidity = llm_response["provides_liquidity"]  # LLM may override
  quantity = llm_response["quantity"]

StopLossTrader.decide():
  rule_triggered = price <= stop_level and not stopped
  llm_response = call_llm(market_context, rule_triggered)
  quantity = llm_response["quantity"]   # LLM may hold or reduce sell size

FundamentalTrader.decide():
  rule_quantity = compute_order(deviation, order_size)
  llm_response = call_llm(market_context, rule_quantity)
  quantity = llm_response["quantity"]   # LLM may size up on "extreme" undervaluation
```

## §4 Crash Mechanism (RuleLLM Logic)

```
Phase 1 (Normal):
  Rule → HFTMarketMaker provides liquidity; LLM confirms
Phase 2 (Trigger):
  Rule velocity > threshold → withdraw; LLM may hesitate
Phase 3 (Cascade):
  Rule stop-loss fires; LLM may hold partially → smaller cascade volume
  provides_liquidity from LLM determines depth computation
Phase 4 (Recovery):
  Rule FT entry; LLM may increase buy size for "severe crash"
```

## §5 Key Parameters

| Parameter                       | Location              | Effect                                               |
|---------------------------------|-----------------------|------------------------------------------------------|
| `withdrawal_threshold`          | HFTMarketMaker extras | Rule anchor; LLM uses as reference                   |
| `lm_name`                       | LLM config            | Model version affects override frequency             |
| `sys_message`                   | prompts.py            | HFTMarketMaker persona — affects withdrawal judgment |
| `generation_config.temperature` | LLM config            | Higher → more deviation from rule signal             |

## §6 Files

| File                                            | Purpose                             |
|-------------------------------------------------|-------------------------------------|
| `players.py`                                    | Market + 5 RuleLLM investor classes |
| `prompts.py`                                    | System and user prompt templates    |
| `run_flashcrash2010_rulellm.py`                 | Entry point                         |
| `configs/FlashCrash2010/RuleLLM/simulation.yml` | Main config                         |
| `configs/FlashCrash2010/RuleLLM/players.yml`    | Agent + LLM config                  |
| `simulation-bases.md`                           | Full theoretical foundations        |
| `analysis-bases.md`                             | Metrics and analysis guide          |

## §7 Running

```bash
export ARK_API_KEY='your-api-key'
python examples/FlashCrash2010/RuleLLM/run_flashcrash2010_rulellm.py -c configs/FlashCrash2010/RuleLLM/simulation.yml
```

## §8 Expected Behaviour

| Phase    | Rounds | Key observable vs Rule                        |
|----------|--------|-----------------------------------------------|
| Normal   | 1–10   | Similar to Rule                               |
| Trigger  | 11–15  | LLM may delay HFT withdrawal by 1–3 rounds    |
| Cascade  | 16–25  | Smaller cascade if LLM holds some stop-losses |
| Trough   | 26–30  | Shallower than Rule                           |
| Recovery | 31–50  | Slightly faster — LLM sizes up FT buying      |

## §9 References

1. Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). *Journal of Finance*, 72(3), 967-998. doi:10.1111/jofi.12498
2. CFTC-SEC Joint Report (2010). *Findings Regarding the Market Events of May 6, 2010.*
3. Biais, B., Foucault, T., & Moinas, S. (2015). *Journal of Financial Economics*, 116(2), 292-313. doi:10.1016/j.jfineco.2015.03.004
4. De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). *Journal of Finance*, 45(2), 379-395.
5. Shiller, R. J. (1981). *American Economic Review*, 71(3), 421-436.
