# FlashCrash LLM - LLM-Powered Flash Crash Simulation

## What is This?

| Item               | Description                                                                        |
|--------------------|------------------------------------------------------------------------------------|
| **Phenomenon**     | **Flash Crash (闪崩)** - LLM-driven rapid price collapse and recovery in minutes   |
| **Model**          | LLM-based traders with HFT/algorithmic personalities + Rule-based market clearing  |
| **Key Feature**    | Investors use LLM reasoning to exhibit stop-loss cascades and liquidity withdrawal |
| **Academic Value** | Tests whether LLMs can simulate 2010 Flash Crash market microstructure dynamics    |

## 5 LLM Investor Types

### Investor Type Summary

| Type               | Strategy           | Market Effect         | System Prompt Focus                    |
|--------------------|--------------------|-----------------------|----------------------------------------|
| **LLMHFT**         | High-frequency     | ⭐ FLASH CRASH TRIGGER | "Execute rapidly on price moves"       |
| **LLMMarketMaker** | Liquidity provider | WITHDRAWAL → AMPLIFY  | "Won't catch falling knives"           |
| **LLMStopLoss**    | Automatic stops    | ⭐ CASCADE MECHANISM   | "Price < $95: Sell 20%"                |
| **LLMFundamental** | Value buyer        | STABILIZING           | "Flash crashes = buying opportunities" |
| **LLMAlgo**        | Algorithmic        | TREND FOLLOWING       | "Return > 1%: Buy; < -1%: Sell"        |

### Key Mechanism

```
Flash Crash Cascade:
  1. LLMHFT sells on small price drop
  2. LLMStopLoss triggers at -5% threshold
  3. LLMMarketMaker withdraws liquidity
  4. More stop-losses trigger → Cascade
  5. LLMFundamental provides eventual floor
```

## Files

| File                                            | Purpose                          |
|-------------------------------------------------|----------------------------------|
| `examples/FlashCrash/LLM/players.py`             | Market + 5 LLM investor classes  |
| `examples/FlashCrash/LLM/prompts.py`             | System and user prompt templates |
| `examples/FlashCrash/LLM/run_flash_crash_llm.py` | Entry point                      |
| `configs/FlashCrash/LLM/simulation.yml`          | Main config                      |
| `configs/FlashCrash/LLM/players.yml`             | Player definitions + LLM config  |
| `configs/FlashCrash/LLM/topology.yml`            | Star topology                    |

## Running

```bash
export ARK_API_KEY='your-bytedance-doubao-api-key'
python examples/FlashCrash/LLM/run_flash_crash_llm.py -c configs/FlashCrash/LLM/simulation.yml
```

## Expected Behavior Patterns

| Phase    | Rounds | LLM Behavior                                   |
|----------|--------|------------------------------------------------|
| Normal   | 1-3    | Normal trading, mixed decisions                |
| Trigger  | 4-5    | LLMHFT sells rapidly on initial drop           |
| Cascade  | 6-7    | LLMStopLoss triggers, LLMMarketMaker withdraws |
| Crash    | 8-9    | Maximum selling pressure, minimum liquidity    |
| Recovery | 10-12  | LLMFundamental buys, price rebounds            |

## References

| Theory                   | Application in FlashCrash LLM     | Reference               |
|--------------------------|----------------------------------|-------------------------|
| **Flash Crash**          | May 6, 2010 dynamics simulation  | CFTC-SEC (2010)         |
| **Stop-Loss Cascades**   | LLMStopLoss automatic selling    | Market Microstructure   |
| **Liquidity Withdrawal** | LLMMarketMaker "WITHDRAWN" state | Kirilenko et al. (2017) |
