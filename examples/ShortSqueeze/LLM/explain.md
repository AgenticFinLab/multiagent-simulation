# ShortSqueeze LLM - LLM-Powered Short Squeeze Simulation

## What is This?

| Item               | Description                                                                               |
|--------------------|-------------------------------------------------------------------------------------------|
| **Phenomenon**     | **Short Squeeze (空头挤压)** - LLM-driven supply-demand imbalance forcing shorts to cover |
| **Model**          | LLM-based traders with short/retail/institutional personalities + Rule-based market       |
| **Key Feature**    | Investors use LLM reasoning to exhibit coordinated buying and forced short covering       |
| **Academic Value** | Tests whether LLMs can simulate GameStop-style squeeze dynamics                           |

## 5 LLM Investor Types

### Investor Type Summary

| Type                 | Strategy              | Market Effect    | System Prompt Focus               |
|----------------------|-----------------------|------------------|-----------------------------------|
| **LLMShortSeller**   | Short position holder | ⭐ SQUEEZE TARGET | "If price > $50, MUST cover"      |
| **LLMRetailCoord**   | Coordinated buying    | ⭐ SQUEEZE DRIVER | "BUY aggressively, diamond hands" |
| **LLMMomentum**      | Ride the squeeze      | AMPLIFYING       | "Positive returns: BUY"           |
| **LLMValue**         | Skeptical value       | STABILIZING      | "Squeeze is temporary"            |
| **LLMInstitutional** | Large holder          | PROFIT-TAKING    | "Price up: Take profits"          |

### Key Mechanism

```
Short Squeeze Cascade:
  1. LLMRetailCoord buys aggressively ("diamond hands")
  2. Price rises → Short interest pressure increases
  3. LLMShortSeller hits covering threshold
  4. Forced buying → More price rise → More covering
  5. LLMInstitutional profit-taking eventually slows squeeze
```

## Files

| File                                                | Purpose                          |
|-----------------------------------------------------|----------------------------------|
| `examples/ShortSqueeze/LLM/players.py`               | Market + 5 LLM investor classes  |
| `examples/ShortSqueeze/LLM/prompts.py`               | System and user prompt templates |
| `examples/ShortSqueeze/LLM/run_short_squeeze_llm.py` | Entry point                      |
| `configs/ShortSqueeze/LLM/simulation.yml`            | Main config                      |
| `configs/ShortSqueeze/LLM/players.yml`               | Player definitions + LLM config  |
| `configs/ShortSqueeze/LLM/topology.yml`              | Star topology                    |

## Running

```bash
export ARK_API_KEY='your-bytedance-doubao-api-key'
python examples/ShortSqueeze/LLM/run_short_squeeze_llm.py -c configs/ShortSqueeze/LLM/simulation.yml
```

## Expected Behavior Patterns

| Phase    | Rounds | LLM Behavior                                           |
|----------|--------|--------------------------------------------------------|
| Setup    | 1-3    | LLMShortSeller establishes short, retail starts buying |
| Build-up | 4-7    | LLMRetailCoord coordinates buying, price rises         |
| Pressure | 8-10   | Short interest > 50%, squeeze pressure builds          |
| Squeeze  | 11-14  | LLMShortSeller forced to cover, price spikes           |
| Unwind   | 15-20  | LLMInstitutional takes profits, price stabilizes       |

## References

| Theory                  | Application in ShortSqueeze LLM           | Reference        |
|-------------------------|------------------------------------------|------------------|
| **Short Squeeze**       | GameStop 2021 dynamics simulation        | (Market Event)   |
| **Coordinated Trading** | LLMRetailCoord Reddit-style coordination | SEC (2021)       |
| **Short Interest**      | LLMShortSeller covering triggers         | Market Mechanics |
