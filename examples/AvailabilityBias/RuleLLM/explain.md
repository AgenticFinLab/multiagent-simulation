# AvailabilityBias RuleLLM — Simulation Documentation

## §1 Overview

| Item                      | Description                                                                                                                                                         |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**               | RuleLLM                                                                                                                                                             |
| **Implements**            | `../simulation-bases.md`                                                                                                                                            |
| **Decision Logic**        | LLM decisions anchored to explicit availability bias formulas embedded in system prompts; rule-constrained behavioral reasoning                                     |
| **Key Difference**        | Agents know the exact availability bias formulas but must justify decisions through behavioral framing — combines formula precision with LLM behavioral flexibility |
| **Research Contribution** | Tests whether embedding availability bias formulas into LLM prompts constrains bias variance while preserving behavioral richness                                   |


## §2 How Theoretical Design Is Implemented

### RuleLLMRecentEventOverweighter: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.1 — Tversky & Kahneman, 1973)*

| Theoretical Design Element    | Implementation                                                                                                         |
|-------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Recency amplification formula | System prompt: "Compute perceived_signal = 0.70 × return_pct + 0.30 × deviation; if > 0.02: buy; if < -0.02: sell" |
| Overweights return_pct        | Rule embedded: recent returns receive 70% of the perceived signal while deviation receives 30%                    |
| Threshold-anchored response   | Prompt: "The salience_threshold is 0.02 — only act when perceived_signal crosses this boundary"                   |
| LLM may modulate quantity     | Formula specifies direction and threshold; LLM determines quantity within reasonable bounds                            |

### RuleLLMMediaInfluencedTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.2 — Schwarz et al., 1991)*

| Theoretical Design Element     | Implementation                                                                                         |
|--------------------------------|--------------------------------------------------------------------------------------------------------|
| Media amplification formula    | System prompt: "Compute amplified_signal = 0.80 × deviation × 1.50 = 1.20 × deviation"                 |
| Threshold triggers             | Prompt: "Trade when |amplified_signal| > 0.03"                                                        |
| Social amplification grounding | Rule embedded: "social_amplification = 1.5 — social media magnifies the raw fundamental signal by 50%" |

### RuleLLMSystematicAnalyst: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.3 — Mullainathan, 2002)*

| Theoretical Design Element | Implementation                                                                          |
|----------------------------|-----------------------------------------------------------------------------------------|
| No recency signal use      | System prompt: "You must NOT use return_pct — only deviation matters for your analysis" |
| Evidence threshold         | Prompt: "Trade only when |deviation| > 0.03"                                           |
| Counter-trading direction  | Prompt: "If deviation > 0.03: sell. If deviation < −0.03: buy. No exceptions."          |

### RuleLLMValueTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.4 — Graham, 1949)*

| Theoretical Design Element | Implementation                                                                                        |
|----------------------------|-------------------------------------------------------------------------------------------------------|
| Fundamental threshold      | System prompt: "Trade only when |deviation| > 0.05"                                                   |
| Direction                  | Prompt: "deviation < -0.05: buy (deep value). deviation > +0.05: sell (overbought). Otherwise: hold." |

### RuleLLMNoiseTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.5 — Black, 1986)*

| Theoretical Design Element | Implementation                                                                         |
|----------------------------|----------------------------------------------------------------------------------------|
| Random trade probability   | System prompt: "With 30% probability, you trade randomly — buy or sell 100–500 shares" |


## §3 Market Mechanism Implementation

Market mechanism is **identical** to Rule variant — only investor decision logic changes.

*(Full formula: simulation-bases.md §3.1 — P(t+1) = P(t) + 0.02·D + 0.03·(F−P) + ε)*

### RuleLLM User Prompt Variables

Same as LLM variant, with `{return_pct}` included:

| Variable            | Source                  | Format  | Notes                                                     |
|---------------------|-------------------------|---------|-----------------------------------------------------------|
| `{round}`           | market_data.round       | integer | Current simulation round                                  |
| `{price}`           | market_data.price       | float   | Current price                                             |
| `{return_pct}`      | market_data.return_pct  | `+.2%`  | Recent return — key input for RecencyOverweighter formula |
| `{deviation}`       | market_data.deviation   | `+.2%`  | Fundamental deviation signal                              |
| `{fundamental}`     | market_data.fundamental | float   | Fundamental value reference                               |
| `{cash}`            | agent state             | float   | Available cash                                            |
| `{position}`        | agent state             | float   | Current position                                          |
| `{portfolio_value}` | cash + pos × price      | float   | Total portfolio value                                     |

### Response Format

```json
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": "string"}
```


## §4 Variant-Specific Features

- **Formula-embedded availability channels**: Both availability channels (recency and media) have their exact formulas embedded as directives — agents compute them explicitly in reasoning
- **SystematicAnalyst isolation**: Prompt explicitly prohibits return_pct use — tests whether rule embedding prevents availability contamination in the rational benchmark agent
- **Intermediate bias amplitude**: Rule constraints prevent extreme overreaction; LLM behavioral framing preserves some variance


## §5 Architecture Diagram

```
Round t:
  ┌─────────────────────────────────────────────────────┐
  │  Market (Rule — identical to Rule)                  │
  │  Broadcasts: {price, prev_price, fundamental,       │
  │               deviation, return_pct, round}         │
  └─────────────────┬───────────────────────────────────┘
                    │ market_data
        ┌───────────┼───────────────────────┐
        ▼           ▼           ▼           ▼
  ┌────────────────┐ ┌──────────────────┐ ┌────────────────┐ ┌────────────────┐
  │RuleLLMRecent   │ │RuleLLMMedia      │ │RuleLLMSystem   │ │RuleLLMValue    │
  │EventOverweight │ │InfluencedTrader  │ │aticAnalyst     │ │Trader          │
  │(formula        │ │(formula          │ │(no return_pct  │ │(|dev|>0.05)    │
  │ embedded)      │ │ embedded)        │ │ rule enforced) │ │                │
  └────────────────┘ └──────────────────┘ └────────────────┘ └────────────────┘
```


## §6 Configuration Reference

| Config Path                 | Key Parameter | Value                   | Notes                                         |
|-----------------------------|---------------|-------------------------|-----------------------------------------------|
| `*.extras.llm.sys_message`  | System prompt | per agent               | Availability bias persona + embedded formulas |
| `*.extras.llm.user_message` | User template | `RULELLM_USER_TEMPLATE` | Includes `{return_pct}`                       |

Full config: `configs/AvailabilityBias/RuleLLM/players.yml`


## §7 Running Instructions

```bash
python examples/AvailabilityBias/RuleLLM/run_availabilitybias_rulellm.py \
    -c configs/AvailabilityBias/RuleLLM/simulation.yml
```

Output: `EXPERIMENT/AvailabilityBias/RuleLLM/records/`


## §8 Expected Behavior Patterns

| Phase             | Deviation Range  | RuleLLM-Specific Behavior                                                                       |
|-------------------|------------------|-------------------------------------------------------------------------------------------------|
| **Pre-Event**     | [−2%, +2%]       | Agents hold; rule thresholds prevent spurious trading                                           |
| **Event Trigger** | First large move | RecencyOverweighter computes formula explicitly; activates at or near ±0.02 perceived_signal    |
| **Bias Peak**     | [3%–10%]         | Tighter range than LLM; formula anchoring prevents extreme amplification                        |
| **Correction**    | Declining        | SystematicAnalyst cites "deviation > 0.03 threshold" in reasoning; correction is formula-guided |
| **Stabilization** | Near 0%          | More predictable than LLM; lower variance across runs                                           |


## §9 References

- `../simulation-bases.md §4.1–§4.5` — Investor archetype specifications
- `../simulation-bases.md §5` — RuleLLM variant description
- `../analysis-bases.md §6` — Expected RuleLLM result ranges
- `prompts.py → RULELLM_*_SYS` — Rule-embedded availability bias persona prompts
