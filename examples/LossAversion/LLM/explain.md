# LossAversion — LLM Variant Explanation

## §1 Overview

| Item               | Description                                                                                                           |
|--------------------|-----------------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Prospect-theory loss aversion — LLM agents interpret price and PnL context through behavioural-finance system prompts |
| **Variant**        | LLM-based: all 5 investor classes use language model reasoning with persona-specific system prompts                   |
| **Investor Count** | 5 LLM classes: LLMLossAverseInvestor, LLMBreakEvenTrader, LLMRationalTrader, LLMMomentumTrader, LLMMarketMaker        |
| **Key Feature**    | Emergent loss aversion through narrative framing rather than hard-coded λ; susceptible to contextual debiasing        |
| **Academic Value** | Tests whether LLM narrative reasoning reproduces or attenuates prospect-theory predictions                            |

---

## §2 Theory → Implementation Mapping

### §2.1 LLMLossAverseInvestor (simulation-bases.md §4.1)

| Theory Element         | LLM Implementation                                                                                 |
|------------------------|----------------------------------------------------------------------------------------------------|
| Loss-aversion λ = 2.25 | System prompt frames losses as 2.25× more painful than gains via narrative description             |
| Disposition effect     | Prompt instructs agent to "protect gains quickly" and "wait for recovery before selling at a loss" |
| Reference point        | Current PnL% provided in user message; prompt anchors decision to entry price                      |
| Contextual modulation  | LLM may deviate from strict λ = 2.25 based on market context in user message                       |

### §2.2 LLMBreakEvenTrader (simulation-bases.md §4.2)

| Theory Element         | LLM Implementation                                                              |
|------------------------|---------------------------------------------------------------------------------|
| Break-even escalation  | Prompt describes agent as "willing to take more risk to get back to break-even" |
| CPT convex loss domain | System prompt frames deep losses as an opportunity for aggressive recovery      |
| Cash constraint        | Enforced post-LLM: `quantity = min(quantity, int(cash/price))`                  |

### §2.3 LLMRationalTrader (simulation-bases.md §4.3)

| Theory Element   | LLM Implementation                                                                       |
|------------------|------------------------------------------------------------------------------------------|
| Expected utility | Prompt instructs agent to ignore entry price; trade only on deviation from fundamental   |
| No bias          | System prompt explicitly states: "You have no psychological attachment to your position" |
| Threshold        | LLM infers threshold from deviation provided in user message                             |

### §2.4 LLMMomentumTrader (simulation-bases.md §4.4)

| Theory Element  | LLM Implementation                                                       |
|-----------------|--------------------------------------------------------------------------|
| Trend following | Prompt instructs agent to follow price direction relative to fundamental |
| Entry threshold | LLM determines when trend is significant enough to act                   |
| Direction       | LLM uses `deviation` from user message to infer trend direction          |

### §2.5 LLMMarketMaker (simulation-bases.md §4.5)

| Theory Element       | LLM Implementation                                                        |
|----------------------|---------------------------------------------------------------------------|
| Contrarian liquidity | Prompt frames agent as providing liquidity by buying low and selling high |
| Inventory limit      | Enforced post-LLM via position constraint                                 |
| Spread earning       | System prompt emphasises "buy below fair value, sell above fair value"    |

---

## §3 Market Mechanism

The LLM variant uses the same rule-based `Market` agent as the Rule variant. Price formation is identical:

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

LLM agent flow per round:
1. Market broadcasts `{price, fundamental, deviation}`.
2. Each LLM agent constructs user message: `{round, price, fundamental, deviation%, cash, position, portfolio_value}`.
3. LLM called with `[system_prompt, user_message]`; up to 3 retry attempts on parse failure.
4. Response parsed for `{action, quantity, reasoning}`.
5. Hard constraints enforced: `buy ≤ cash/price`; `sell ≤ max(position, 0)`.
6. Orders aggregated by Market; price updated.

---

## §4 Variant Architecture

```
LLM Variant Architecture
─────────────────────────
Market (rule-based, same as Rule variant)
  │  broadcast {price, fundamental, deviation}
  ├─ LLMLossAverseInvestor  │ [loss-averse system prompt] → LLM → parse
  ├─ LLMBreakEvenTrader     │ [break-even system prompt] → LLM → parse
  ├─ LLMRationalTrader      │ [rational system prompt] → LLM → parse
  ├─ LLMMomentumTrader      │ [momentum system prompt] → LLM → parse
  └─ LLMMarketMaker         │ [market-maker system prompt] → LLM → parse
```

Prompts defined in `examples/LossAversion/LLM/prompts.py`.
LLM model configured via `extras.llm.model` and `extras.llm.temperature`.

---

## §5 Config Reference

Configuration file: `configs/LossAversion/LLM/simulation.yml` → `players.yml`

| Parameter          | Agent          | Default      | Description           |
|--------------------|----------------|--------------|-----------------------|
| `llm.model`        | All LLM agents | (configured) | LLM model identifier  |
| `llm.temperature`  | All LLM agents | 0.3          | Sampling temperature  |
| `initial_cash`     | All investors  | 100000       | Starting cash         |
| `initial_position` | All investors  | 500          | Starting shares       |
| `initial_price`    | All            | 100.0        | Entry price reference |
| `price_impact`     | Market         | 0.0002       | λ coefficient         |
| `mean_reversion`   | Market         | 0.05         | γ coefficient         |
| `noise_std`        | Market         | 0.3          | ε standard deviation  |

Note: `loss_aversion_lambda`, `risk_increase_factor`, etc. are embedded in system prompts rather than numeric config.

---

## §6 Running Instructions

```bash
# Run LLM variant
python examples/LossAversion/LLM/run_lossaversion_llm.py \
    -c configs/LossAversion/LLM/simulation.yml

# Run with lower temperature for more consistent behaviour
python examples/LossAversion/LLM/run_lossaversion_llm.py \
    -c configs/LossAversion/LLM/simulation.yml \
    --extras llm.temperature=0.1
```

Output files written to `records/LossAversion/LLM/`.

---

## §7 Expected Behavior

| Metric | Expected Range | Rationale                                                                      |
|--------|----------------|--------------------------------------------------------------------------------|
| LAI    | 1.6–2.4        | LLM internalises loss-aversion narrative but may contextually deviate          |
| DEI    | 1.2–2.0        | Disposition effect present but weaker than Rule variant                        |
| BER    | 1.2–2.5        | Break-even escalation emerges from prompt but LLM may show restraint           |
| VAF    | 1.2–2.0        | Lower volatility amplification than Rule due to contextual moderation          |
| WPI    | 0.80–0.93      | Smaller wealth penalty — LLM sometimes avoids worst-case loss-averse decisions |
| NCE    | 0.15–0.40      | Moderate narrative correction relative to Rule baseline                        |

The LLM variant will show wider metric variance run-to-run (LLM stochasticity). Run ≥ 5 simulations for reliable mean estimates.

---

## §8 References

- Kahneman, D., & Tversky, A. (1979). doi:[10.2307/1914185](https://doi.org/10.2307/1914185)
- Odean, T. (1998). doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)
- Barberis, N., & Xiong, W. (2009). doi:[10.1111/j.1540-6261.2009.01448.x](https://doi.org/10.1111/j.1540-6261.2009.01448.x)
- simulation-bases.md §4.1–§4.5 (Investor Taxonomy)
- examples/LossAversion/LLM/prompts.py (System prompt definitions)

---

## §9 Variant Comparison

| Dimension              | Rule                   | LLM                     | RuleLLM        | Rag            |
|------------------------|------------------------|-------------------------|----------------|----------------|
| Loss-aversion encoding | Deterministic λ = 2.25 | Narrative system prompt | Rule + LLM     | Rule + KB      |
| Break-even effect      | Fixed formula          | LLM may moderate        | Rule-triggered | RAG may reduce |
| Expected LAI           | 2.0–2.8                | 1.6–2.4                 | 1.8–2.5        | 1.4–2.0        |
| Stochasticity          | Minimal                | High                    | Moderate       | Moderate       |
| NCE vs. Rule           | —                      | 0.15–0.40               | 0.10–0.30      | 0.30–0.60      |
