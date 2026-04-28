# FlashCrash2010 Rag — Explain

## §1 Overview

| Item             | Description                                                                                                                                                              |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**      | Rag                                                                                                                                                                      |
| **Scenario**     | FlashCrash2010                                                                                                                                                           |
| **Phenomenon**   | May 6, 2010 Flash Crash — LLM decisions augmented by retrieved historical flash crash cases                                                                              |
| **Agent count**  | 5 types: HFTMarketMaker, MomentumChaser, FundamentalTrader, StopLossTrader, NoiseTrader                                                                                  |
| **Market model** | Same order-book depth model as Rule variant                                                                                                                              |
| **Key feature**  | Each investor retrieves historically relevant episodes before deciding; `provides_liquidity` from LLM response; historical grounding expected to moderate crash severity |
| **Determinism**  | Low-medium — RAG retrieval is deterministic; LLM reasoning is stochastic                                                                                                 |

## §2 Theory → Implementation Mapping

| Theory construct       | simulation-bases.md reference | Rag implementation                                                                                                      |
|------------------------|-------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| HFT stress withdrawal  | §4.1 HFTMarketMaker           | RAG retrieves "HFT withdrawal" cases; LLM decides `provides_liquidity` and `quantity`; Theory: simulation-bases.md §4.1 |
| Momentum amplification | §4.2 MomentumChaser           | RAG retrieves "momentum chasing" cases; LLM decides chase or hold; Theory: simulation-bases.md §4.2                     |
| Value stabilisation    | §4.3 FundamentalTrader        | RAG retrieves "flash crash recovery" cases; LLM sizes buy; Theory: simulation-bases.md §4.3                             |
| Stop-loss cascade      | §4.4 StopLossTrader           | RAG retrieves "stop-loss cascade" events; LLM decides cut timing; Theory: simulation-bases.md §4.4                      |
| Noise background       | §4.5 NoiseTrader              | RAG context minimal; LLM approximates random; Theory: simulation-bases.md §4.5                                          |
| Order-book depth       | §3 Market Design              | `agent_type` fixed per class; `provides_liquidity` from RAG-informed LLM response                                       |

## §3 RAG Retrieval Architecture

```
Investor.decide():
  1. Construct query = f(role, market_data)
     HFTMarketMaker: "HFT market maker velocity=X depth=Y — withdraw or provide?"
     StopLossTrader: "stop-loss trader price dropped X% — trigger stop?"
     FundamentalTrader: "fundamental trader price=P fundamental=F — buy opportunity?"
  2. retrieve(query) → top-k cases from historical flash crash vector store
  3. Build prompt = system_message + retrieved_cases + current_market_context
  4. llm_call(prompt) → {"quantity": int, "provides_liquidity": bool}
  5. return order with agent_type preserved
```

## §4 Key Retrieval Patterns

| Agent             | Typical query                             | Retrieved context                                 |
|-------------------|-------------------------------------------|---------------------------------------------------|
| HFTMarketMaker    | "volatility=X, velocity=Y, depth=Z"       | Historical HFT withdrawal timing from May 6, 2010 |
| MomentumChaser    | "velocity=X over lookback: follow trend?" | Historical momentum chasing patterns              |
| StopLossTrader    | "price dropped X% from entry: cut loss?"  | Cascade timing from May 6, 2010                   |
| FundamentalTrader | "price=P, fundamental=F, deviation=D"     | Flash crash recovery episodes                     |
| NoiseTrader       | "current round, price"                    | Minimal — background noise patterns               |

## §5 Key Parameters

| Parameter                       | Location   | Effect                                            |
|---------------------------------|------------|---------------------------------------------------|
| `lm_name`                       | LLM config | Model capability affects RAG reasoning quality    |
| `rag_top_k`                     | RAG config | More retrieved cases → more historically grounded |
| `rag_store_path`                | RAG config | Vector store location                             |
| `sys_message`                   | prompts.py | Agent persona                                     |
| `generation_config.temperature` | LLM config | Stochasticity of final decision                   |

## §6 Files

| File                                        | Purpose                          |
|---------------------------------------------|----------------------------------|
| `players.py`                                | Market + 5 RAG investor classes  |
| `prompts.py`                                | System and user prompt templates |
| `run_flashcrash2010_rag.py`                 | Entry point                      |
| `configs/FlashCrash2010/Rag/simulation.yml` | Main config                      |
| `configs/FlashCrash2010/Rag/players.yml`    | Agent + RAG + LLM config         |
| `simulation-bases.md`                       | Full theoretical foundations     |
| `analysis-bases.md`                         | Metrics and analysis guide       |

## §7 Running

```bash
export ARK_API_KEY='your-api-key'
python examples/FlashCrash2010/Rag/run_flashcrash2010_rag.py -c configs/FlashCrash2010/Rag/simulation.yml
```

## §8 Expected Behaviour

| Phase    | Rounds | Key observable vs Rule/RuleLLM                                     |
|----------|--------|--------------------------------------------------------------------|
| Normal   | 1–10   | Similar                                                            |
| Trigger  | 11–15  | RAG may surface prior withdrawal patterns → earlier recognition    |
| Cascade  | 16–25  | Historical cases moderate cascade; smaller depth collapse possible |
| Trough   | 26–30  | FT with historical recovery knowledge buys more aggressively       |
| Recovery | 31–50  | Fastest recovery among variants                                    |

## §9 References

1. Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). *Journal of Finance*, 72(3), 967-998. doi:10.1111/jofi.12498
2. CFTC-SEC Joint Report (2010). *Findings Regarding the Market Events of May 6, 2010.*
3. Biais, B., Foucault, T., & Moinas, S. (2015). *Journal of Financial Economics*, 116(2), 292-313. doi:10.1016/j.jfineco.2015.03.004
4. De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). *Journal of Finance*, 45(2), 379-395.
5. Shiller, R. J. (1981). *American Economic Review*, 71(3), 421-436.
6. Black, F. (1986). *Journal of Finance*, 41(3), 529-543.
