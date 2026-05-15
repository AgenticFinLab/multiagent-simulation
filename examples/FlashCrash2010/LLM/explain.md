# FlashCrash2010 LLM — Explain

## §1 Overview

| Item             | Description                                                                                                                                                                      |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**      | LLM                                                                                                                                                                              |
| **Scenario**     | FlashCrash2010                                                                                                                                                                   |
| **Phenomenon**   | May 6, 2010 Flash Crash — all investor decisions driven by LLM reasoning                                                                                                         |
| **Agent count**  | 5 types: HFTMarketMaker, MomentumChaser, FundamentalTrader, StopLossTrader, NoiseTrader                                                                                          |
| **Market model** | Same order-book depth model as Rule; depth driven by volatility + `hft_participation`                                                                                            |
| **Key feature**  | LLM receives order-book context (depth, spread, volatility, hft_participation) and decides `quantity` + `provides_liquidity`; `agent_type` field preserved for depth calculation |
| **Determinism**  | Low — fully LLM-driven; run multiple seeds for statistical analysis                                                                                                              |

## §2 Theory → Implementation Mapping

| Theory construct       | simulation-bases.md reference | LLM implementation                                                                                                                  |
|------------------------|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| HFT stress withdrawal  | §4.1 HFTMarketMaker           | LLM receives `{volatility, spread, depth, velocity}`; decides `provides_liquidity` and `quantity`; Theory: simulation-bases.md §4.1 |
| Momentum amplification | §4.2 MomentumChaser           | LLM receives `{price_history, velocity}`; decides whether to chase momentum; Theory: simulation-bases.md §4.2                       |
| Value stabilisation    | §4.3 FundamentalTrader        | LLM receives `{price, fundamental, deviation}`; decides buy/sell; Theory: simulation-bases.md §4.3                                  |
| Stop-loss cascade      | §4.4 StopLossTrader           | LLM receives `{price, stop_level, position}`; decides whether to cut loss; Theory: simulation-bases.md §4.4                         |
| Noise background       | §4.5 NoiseTrader              | LLM receives minimal context; generates approximately random quantity; Theory: simulation-bases.md §4.5                             |
| Order-book depth       | §3 Market Design              | `hft_participation` computed from `agent_type == "hft"` field in LLM response                                                       |

## §3 LLM Decision Structure

```
HFTMarketMaker.decide():
  context = {price, prev_price, return_pct, spread, depth, volatility, velocity, round}
  llm_response → {"quantity": int, "provides_liquidity": bool, "agent_type": "hft"}
  # provides_liquidity=False triggers depth collapse

MomentumChaser.decide():
  context = {price_history[-lookback:], velocity, round}
  llm_response → {"quantity": int, "provides_liquidity": False, "agent_type": "hft"}

FundamentalTrader.decide():
  context = {price, fundamental, deviation, cash, position}
  llm_response → {"quantity": int, "provides_liquidity": True, "agent_type": "fundamental"}

StopLossTrader.decide():
  context = {price, stop_level, position, round}
  llm_response → {"quantity": int, "provides_liquidity": False, "agent_type": "stoploss"}

NoiseTrader.decide():
  context = {price, round}
  llm_response → {"quantity": int, "provides_liquidity": False, "agent_type": "noise"}
```

## §4 Key Parameters

| Parameter                       | Location      | Effect                                         |
|---------------------------------|---------------|------------------------------------------------|
| `lm_name`                       | LLM config    | Model capability affects crash realism         |
| `sys_message`                   | prompts.py    | Agent persona (HFT vs fundamental)             |
| `generation_config.temperature` | LLM config    | Stochasticity of decisions                     |
| `withdrawal_threshold` (hint)   | System prompt | Provided as context; LLM may or may not follow |

## §5 Files

| File                                        | Purpose                          |
|---------------------------------------------|----------------------------------|
| `players.py`                                | Market + 5 LLM investor classes  |
| `prompts.py`                                | System and user prompt templates |
| `run_flashcrash2010_llm.py`                 | Entry point                      |
| `configs/FlashCrash2010/LLM/simulation.yml` | Main config                      |
| `configs/FlashCrash2010/LLM/players.yml`    | Agent + LLM config               |
| `simulation-bases.md`                       | Full theoretical foundations     |
| `analysis-bases.md`                         | Metrics and analysis guide       |

## §6 Running

```bash
export ARK_API_KEY='your-api-key'
python examples/FlashCrash2010/LLM/run_flashcrash2010_llm.py -c configs/FlashCrash2010/LLM/simulation.yml
```

## §7 Expected Behaviour

| Phase    | Rounds | Key observable vs Rule                                     |
|----------|--------|------------------------------------------------------------|
| Normal   | 1–10   | Similar pattern; more noise in decisions                   |
| Trigger  | 11–15  | LLM MomentumChaser may hesitate or anticipate              |
| Cascade  | 16–25  | Crash depth and duration depend on LLM withdrawal judgment |
| Trough   | 26–30  | LLM FT may buy more/less aggressively                      |
| Recovery | 31–50  | Variable recovery speed                                    |

## §8 References

1. Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). *Journal of Finance*, 72(3), 967-998. doi:10.1111/jofi.12498
2. CFTC-SEC Joint Report (2010). *Findings Regarding the Market Events of May 6, 2010.*
3. Biais, B., Foucault, T., & Moinas, S. (2015). *Journal of Financial Economics*, 116(2), 292-313. doi:10.1016/j.jfineco.2015.03.004
4. De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). *Journal of Finance*, 45(2), 379-395.
5. Shiller, R. J. (1981). *American Economic Review*, 71(3), 421-436.
6. Black, F. (1986). *Journal of Finance*, 41(3), 529-543.
