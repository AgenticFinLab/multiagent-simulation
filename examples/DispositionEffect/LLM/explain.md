# DispositionEffect LLM - LLM-Powered Disposition Effect Simulation

## What is This?

| Item               | Description                                                                                             |
|--------------------|---------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | **Disposition Effect (处置效应)** - LLM-driven tendency to sell winners too early, hold losers too long |
| **Model**          | LLM-based investors with Prospect Theory personalities + Rule-based market clearing                     |
| **Key Feature**    | Investors use LLM reasoning to exhibit asymmetric gain/loss psychology                                  |
| **Academic Value** | Tests whether LLMs can simulate Kahneman & Tversky's Prospect Theory biases                             |

## Rule-Based vs LLM-Based Comparison

| Aspect             | DispositionEffect (Rule-Based)         | DispositionEffect LLM (LLM-Based)           |
|--------------------|----------------------------------------|--------------------------------------------|
| **Decision Logic** | Fixed utility function formulas        | LLM reasons about gains/losses via prompts |
| **Investor Types** | 5 types with hardcoded strategies      | 5 types with personality-defining prompts  |
| **Behavior**       | Deterministic reference point tracking | Stochastic emotional responses             |
| **Market**         | Rule-based order clearing              | **Same** rule-based order clearing         |
| **Psychology**     | From mathematical λ=2.25 formula       | From LLM "fear of loss" reasoning          |
| **Research Value** | Mechanism validation                   | LLM emotional realism + emergent biases    |

## 5 LLM Investor Types

### Investor Type Summary

| Type                     | Strategy            | Market Effect         | System Prompt Focus                 |
|--------------------------|---------------------|-----------------------|-------------------------------------|
| **LLMDispositionBiased** | Prospect Theory     | ⭐ DISPOSITION EFFECT  | "Losses hurt 2.25x more than gains" |
| **LLMRational**          | Expected utility    | STABILIZING           | "Past prices are irrelevant"        |
| **LLMTaxAware**          | Tax-loss harvesting | ANTI-DISPOSITION      | "Sell losers for tax benefits"      |
| **LLMInstitutional**     | Process-driven      | NEUTRAL               | "Emotion has no place"              |
| **LLMLossAverse**        | Extreme risk averse | ⭐ EXTREME DISPOSITION | "I cannot afford to lose money"     |

### 1. LLMDispositionBiased (⭐ Primary Effect Driver)

**Theory**: Kahneman & Tversky (1979) Prospect Theory - λ = 2.25

| Aspect         | Description                                    |
|----------------|------------------------------------------------|
| **Effect**     | DISPOSITION EFFECT - sell winners, hold losers |
| **Psychology** | Losses hurt 2.25x more than gains              |
| **Behavior**   | Gain > 5% → Sell; Loss < -5% → Hold            |

### 2. LLMRational (Stabilizing)

**Theory**: Rational expectations - past prices don't matter for decisions.

| Aspect         | Description                          |
|----------------|--------------------------------------|
| **Effect**     | STABILIZING - trades on fundamentals |
| **Behavior**   | Buy undervalued, sell overvalued     |
| **Psychology** | No reference point dependence        |

### 3. LLMTaxAware (Anti-Disposition)

**Theory**: Tax-loss harvesting - sell losers for tax benefits.

| Aspect       | Description                             |
|--------------|-----------------------------------------|
| **Effect**   | ANTI-DISPOSITION - opposite behavior    |
| **Behavior** | Sell losers (tax benefit), hold winners |
| **Logic**    | Tax optimization, not emotion           |

### 4. LLMInstitutional (Process-Driven)

**Theory**: Professional portfolio management - systematic rebalancing.

| Aspect         | Description                          |
|----------------|--------------------------------------|
| **Effect**     | NEUTRAL - process over emotion       |
| **Behavior**   | Rebalance based on portfolio weights |
| **Psychology** | Disciplined, emotionless             |

### 5. LLMLossAverse (⭐ Extreme)

**Theory**: Extreme loss aversion - λ = 3.0

| Aspect         | Description                                |
|----------------|--------------------------------------------|
| **Effect**     | EXTREME DISPOSITION - paralyzed by loss    |
| **Psychology** | Losses feel 3x worse, cannot act           |
| **Behavior**   | At loss → NEVER sell; At gain → Sell quick |

## Market Clearing (Rule-Based)

```
Price Model:

  P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε
  
  Where:
    λ = 0.1   (price impact)
    γ = 0.02  (mean reversion)
    F = 100.0 (fundamental value)

Disposition Effect creates asymmetric selling:
  Winners → Quick selling → Price resistance at highs
  Losers → No selling → Price support at lows (artificial)
```

## Topology (Star Network)

```
                         ┌───────────────────┐
                         │      market       │ ◄── Level 0
                         └─────────┬─────────┘
                                   │
         ┌───────────┬─────────────┼─────────────┬───────────┐
         ▼           ▼             ▼             ▼           ▼
   llm_disposition llm_rational  llm_tax_aware llm_inst    llm_loss_averse
   (⭐ disposition) (stabilize)  (anti-disp)   (neutral)   (⭐ extreme)
```

## Files

| File                                                   | Purpose                          |
|--------------------------------------------------------|----------------------------------|
| `examples/DispositionEffect/LLM/players.py`             | Market + 5 LLM investor classes  |
| `examples/DispositionEffect/LLM/prompts.py`             | System and user prompt templates |
| `examples/DispositionEffect/LLM/run_disposition_llm.py` | Entry point                      |
| `configs/DispositionEffect/LLM/simulation.yml`          | Main config                      |
| `configs/DispositionEffect/LLM/players.yml`             | Player definitions + LLM config  |
| `configs/DispositionEffect/LLM/topology.yml`            | Star topology                    |

## Running

```bash
export ARK_API_KEY='your-bytedance-doubao-api-key'
python examples/DispositionEffect/LLM/run_disposition_llm.py -c configs/DispositionEffect/LLM/simulation.yml
```

## Expected LLM Behavior Patterns

| Phase       | Rounds | LLM Behavior                                              |
|-------------|--------|-----------------------------------------------------------|
| Initial     | 1-3    | LLMs establish reference points at purchase price         |
| Gains       | 4-7    | Price rises → DispositionBiased sells, LossAverse nervous |
| Losses      | 8-12   | Price falls → DispositionBiased holds, paralyzed          |
| Recovery    | 13-16  | Price recovers → Relief selling ("finally break even")    |
| Equilibrium | 17-20  | Tax-aware + Rational provide correcting trades            |

## Research Questions

| Question                                               | How to Test                                            |
|--------------------------------------------------------|--------------------------------------------------------|
| Can LLMs exhibit Prospect Theory loss aversion?        | Track selling decisions relative to reference point    |
| Does the disposition effect emerge from LLM reasoning? | Measure asymmetric holding periods (winners vs losers) |
| Can LLM tax-aware investors offset disposition bias?   | Compare portfolios with/without tax-aware agents       |
| Is LLM disposition more realistic than rule-based?     | Compare with Odean (1998) empirical findings           |

## References

| Theory                  | Application in DispositionEffect LLM         | Reference                 |
|-------------------------|---------------------------------------------|---------------------------|
| **Prospect Theory**     | LLMDispositionBiased loss aversion (λ=2.25) | Kahneman & Tversky (1979) |
| **Disposition Effect**  | Sell winners early, hold losers long        | Shefrin & Statman (1985)  |
| **Tax-Loss Harvesting** | LLMTaxAware sells losers for tax benefit    | (Tax Strategy)            |
| **Empirical Evidence**  | Documented in retail investor data          | Odean (1998)              |
