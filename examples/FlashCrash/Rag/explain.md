# FlashCrash Rag — Explain

## §1 Overview

| Item             | Description                                                                                                                               |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**      | Rag                                                                                                                                       |
| **Scenario**     | Flash Crash                                                                                                                               |
| **Phenomenon**   | Rapid intraday price collapse and recovery — LLM decisions augmented by retrieved historical flash crash cases                            |
| **Agent count**  | 6 types: HighFrequencyTrader, MarketMaker, AlgorithmicTrader, StopLossTrader, FundamentalTrader, RetailTrader                             |
| **Market model** | Same liquidity-sensitive model as Rule/RuleLLM                                                                                            |
| **Key feature**  | Each investor retrieves relevant historical episodes (May 6 2010, Aug 2015, etc.) before deciding; `provides_liquidity` from LLM response |
| **Determinism**  | Low-medium — RAG retrieval is deterministic; LLM reasoning is stochastic                                                                  |

## §2 Theory → Implementation Mapping

| Theory construct           | simulation-bases.md reference | Rag implementation                                                                                                               |
|----------------------------|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Momentum detection         | §4.1 HighFrequencyTrader      | RAG retrieves "HFT momentum burst" cases; LLM decides `quantity`; Theory: simulation-bases.md §4.1                               |
| Liquidity withdrawal       | §4.2 MarketMaker              | RAG retrieves "market-maker withdrawal" cases; LLM decides `provides_liquidity` and `quantity`; Theory: simulation-bases.md §4.2 |
| Trend amplification        | §4.3 AlgorithmicTrader        | RAG retrieves "algorithmic trend-following" cases; LLM confirms trend direction; Theory: simulation-bases.md §4.3                |
| Stop-loss cascade          | §4.4 StopLossTrader           | RAG retrieves "stop-loss cascade" events; LLM decides cut-loss timing; Theory: simulation-bases.md §4.4                          |
| Value stabilisation        | §4.5 FundamentalTrader        | RAG retrieves "flash crash recovery" cases; LLM sizes buy; Theory: simulation-bases.md §4.5                                      |
| Noise background           | §4.6 RetailTrader             | RAG provides low-signal context; LLM generates random-like decision; Theory: simulation-bases.md §4.6                            |
| Liquidity-sensitive market | §3 Market Design              | `provides_liquidity` from LLM response field `decision["provides_liquidity"]`                                                    |

## §3 RAG Retrieval Architecture

```
Investor.decide():
  1. Construct query = f(current market_data, agent_role)
     e.g. "market maker during high volatility with price_return=0.015"
  2. retrieve(query) → top-k historical cases from vector store
     e.g. ["May 6 2010: HFT withdrew at velocity=0.012, spread widened 20×",
           "Aug 24 2015: ETF market makers withdrew, NAV diverged"]
  3. Build prompt = system_message + retrieved_cases + current_market_context
  4. llm_call(prompt) → {"quantity": Q, "provides_liquidity": bool}
  5. return {"quantity": Q, "provides_liquidity": bool, ...}
```

## §4 Key Retrieval Patterns

| Agent               | Typical query                                    | Retrieved context                |
|---------------------|--------------------------------------------------|----------------------------------|
| MarketMaker         | "volatility=X, velocity=Y: withdraw or provide?" | Historical HFT withdrawal events |
| HighFrequencyTrader | "momentum=X: HFT entry signal"                   | HFT burst patterns               |
| StopLossTrader      | "price dropped X% from entry: cut loss?"         | Historical cascade timing        |
| FundamentalTrader   | "price=P, fundamental=F: buy opportunity?"       | Flash crash recovery episodes    |
| AlgorithmicTrader   | "trend=X over N rounds: follow?"                 | Algorithmic momentum cases       |

## §5 Key Parameters

| Parameter                       | Location   | Effect                                          |
|---------------------------------|------------|-------------------------------------------------|
| `lm_name`                       | LLM config | Model version affects RAG quality and reasoning |
| `rag_top_k`                     | RAG config | Number of retrieved cases                       |
| `rag_store_path`                | RAG config | Vector store location                           |
| `sys_message`                   | prompts.py | Agent persona for RAG-augmented prompt          |
| `generation_config.temperature` | LLM config | Stochasticity of final decision                 |

## §6 Files

| File                                    | Purpose                          |
|-----------------------------------------|----------------------------------|
| `players.py`                            | Market + 6 RAG investor classes  |
| `prompts.py`                            | System and user prompt templates |
| `run_flash_crash_ragllm.py`             | Entry point                      |
| `configs/FlashCrash/Rag/simulation.yml` | Main config                      |
| `configs/FlashCrash/Rag/players.yml`    | Agent + RAG + LLM config         |
| `simulation-bases.md`                   | Full theoretical foundations     |
| `analysis-bases.md`                     | Metrics and analysis guide       |

## §7 Running

```bash
export ARK_API_KEY='your-api-key'
python examples/FlashCrash/Rag/run_flash_crash_ragllm.py -c configs/FlashCrash/Rag/simulation.yml
```

## §8 Expected Behaviour

| Phase    | Rounds | Key observable vs Rule/RuleLLM                                 |
|----------|--------|----------------------------------------------------------------|
| Normal   | 1–10   | Similar to Rule                                                |
| Trigger  | 11–15  | RAG may surface prior crash patterns → earlier or later action |
| Cascade  | 16–25  | Historical cases may moderate cascade depth                    |
| Trough   | 26–30  | RAG-informed FT may buy more aggressively                      |
| Recovery | 31–50  | Potentially fastest recovery (history-guided)                  |

## §9 References

1. Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). *Journal of Finance*, 72(3), 967-998. doi:10.1111/jofi.12498
2. CFTC-SEC Joint Report (2010). *Findings Regarding the Market Events of May 6, 2010.*
3. Grossman, S. J., & Miller, M. H. (1988). *Journal of Finance*, 43(3), 617-633. doi:10.1111/j.1540-6261.1988.tb02607.x
4. De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). *Journal of Finance*, 45(2), 379-395.
5. Shiller, R. J. (1981). *American Economic Review*, 71(3), 421-436.
6. Black, F. (1986). *Journal of Finance*, 41(3), 529-543.
