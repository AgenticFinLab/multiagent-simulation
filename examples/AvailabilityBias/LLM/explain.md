# AvailabilityBias LLM — Simulation Documentation

## §1 Overview

| Item                      | Description                                                                                                                                   |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**               | LLM                                                                                                                                           |
| **Implements**            | `../simulation-bases.md`                                                                                                                      |
| **Decision Logic**        | Persona-only LLM prompts; no embedded quantitative rules; availability bias archetypes drive decisions through behavioral reasoning           |
| **Key Difference**        | Agents exhibit psychological availability bias (recency effects, media influence, analytical discipline) without formula constraints          |
| **Research Contribution** | Tests whether pure behavioral personas reproduce availability bias dynamics (overreaction, partial correction) through emergent LLM reasoning |


## §2 How Theoretical Design Is Implemented

### LLMRecentEventOverweighter: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.1 — Tversky & Kahneman, 1973)*

| Theoretical Design Element              | Implementation                                                                                     |
|-----------------------------------------|----------------------------------------------------------------------------------------------------|
| Recency amplification of salient events | Prompt: "Recent dramatic price moves feel vivid and representative — you act on them strongly"     |
| Overweights return_pct vs. deviation    | Prompt context includes `{return_pct}` prominently; agent trained to over-interpret recent returns |
| Symmetric bias (up and down)            | Prompt: "Whether prices just spiked up or crashed, you react strongly to the recent move"          |
| Fades as event recedes                  | Prompt: "As time passes without new dramatic moves, your urgency gradually fades"                  |

### LLMMediaInfluencedTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.2 — Schwarz et al., 1991; Tetlock, 2007)*

| Theoretical Design Element          | Implementation                                                                                     |
|-------------------------------------|----------------------------------------------------------------------------------------------------|
| Social amplification of deviation   | Prompt: "You track what financial media and social networks would be saying about this price move" |
| Herding under media narrative       | Prompt: "If the story is compelling, you follow the narrative even if fundamentals say otherwise"  |
| Amplified by magnitude of deviation | Prompt: "The bigger the deviation, the louder the media narrative you imagine"                     |
| Fades when narrative reverses       | Prompt: "When media coverage shifts, you follow the new narrative with equal conviction"           |

### LLMSystematicAnalyst: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.3 — Mullainathan, 2002)*

| Theoretical Design Element   | Implementation                                                                                      |
|------------------------------|-----------------------------------------------------------------------------------------------------|
| Bayesian rational processing | Prompt: "You are disciplined and rational — you ignore recent noise and focus only on fundamentals" |
| Ignores return_pct signal    | Prompt: "You do not react to short-term price moves; only fundamental deviation matters to you"     |
| Systematic counter-trading   | Prompt: "When prices deviate significantly from fundamental, you trade against the deviation"       |
| Evidence-based conviction    | Prompt: "You require clear evidence of mispricing before acting — you are not impulsive"            |

### LLMValueTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.4 — Graham, 1949)*

| Theoretical Design Element         | Implementation                                                                                         |
|------------------------------------|--------------------------------------------------------------------------------------------------------|
| Fundamental value discipline       | Prompt: "You are a value investor — you only trade when deviation from intrinsic value is significant" |
| Ignores media and recency entirely | Prompt: "You deliberately ignore recent price action and media narratives"                             |
| Deep discount/premium threshold    | Prompt: "You require a substantial margin of safety before committing capital"                         |
| Patient accumulation               | Prompt: "You are patient — you do not rush; you wait for compelling value opportunities"               |

### LLMNoiseTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.5 — Black, 1986)*

| Theoretical Design Element | Implementation                                                                          |
|----------------------------|-----------------------------------------------------------------------------------------|
| Uninformed random trader   | Prompt: "You do not have a clear strategy — you trade on gut feeling and impulse"       |
| No systematic signal       | Prompt: "Sometimes you buy into rising markets, sometimes into falling ones — randomly" |


## §3 Market Mechanism Implementation

Market mechanism is **identical** to Rule variant — only investor decision logic changes.

*(Full formula: simulation-bases.md §3.1 — P(t+1) = P(t) + 0.01·D + 0.02·(F−P) + ε)*

### LLM User Prompt Variables

| Variable            | Source                  | Format  | Notes                                                     |
|---------------------|-------------------------|---------|-----------------------------------------------------------|
| `{round}`           | market_data.round       | integer | Current simulation round                                  |
| `{price}`           | market_data.price       | float   | Current price                                             |
| `{prev_price}`      | market_data.prev_price  | float   | Previous round price                                      |
| `{return_pct}`      | market_data.return_pct  | `+.2%`  | **Unique to AvailabilityBias** — recent return percentage |
| `{deviation}`       | market_data.deviation   | `+.2%`  | Fundamental deviation signal                              |
| `{fundamental}`     | market_data.fundamental | float   | Fundamental value reference                               |
| `{cash}`            | agent state             | float   | Available cash                                            |
| `{position}`        | agent state             | float   | Current position (shares)                                 |
| `{portfolio_value}` | cash + pos × price      | float   | Total portfolio value                                     |

### Response Format

LLM must output canonical JSON inside `<decision>` tags:
```json
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": "string"}
```

Parsed by `parse_llm_response_with_thinking()` from `examples/llm_utils.py`.


## §4 Variant-Specific Features

- **Availability bias through persona**: `LLM_*_SYS` prompts encode the cognitive distortion directly — RecencyOverweighter's persona overweights `return_pct` without numerical formula; effect emerges from persona interpretation
- **return_pct prominently featured**: Unlike other simulations, prompt includes `{return_pct}` as a key signal; RecencyOverweighter's persona naturally gravitates to it
- **Dual-channel interaction**: LLMRecentEventOverweighter and LLMMediaInfluencedTrader may interact through price momentum — first amplifies return, second amplifies resulting deviation
- **Variable bias onset**: LLM agents may begin overreacting before or after the formula threshold; run-to-run variance is higher than Rule
- **Denial risk**: LLMSystematicAnalyst may be contaminated by availability framing in prompt context; its "rationality" can waver


## §5 Architecture Diagram

```
Round t:
  ┌─────────────────────────────────────────────────────┐
  │  Market (Rule — identical to Rule)                  │
  │  P(t+1) = P(t) + 0.01·D + 0.02·(F−P) + ε          │
  │  Broadcasts: {price, prev_price, fundamental,       │
  │               deviation, return_pct, round}         │
  └─────────────────┬───────────────────────────────────┘
                    │ market_data (includes return_pct)
        ┌───────────┼───────────────────────┐
        ▼           ▼           ▼           ▼
  ┌──────────────┐ ┌───────────────┐ ┌──────────────┐ ┌──────────────┐
  │LLMRecent     │ │LLMMedia       │ │LLMSystematic │ │LLMValue      │
  │Event         │ │Influenced     │ │Analyst        │ │Trader        │
  │Overweighter  │ │Trader         │ │(rational      │ │(value        │
  │(recency bias)│ │(media bias)   │ │ benchmark)    │ │ discipline)  │
  └──────────────┘ └───────────────┘ └──────────────┘ └──────────────┘
        │                │               │                    │
        └────────────────┴───────────────┴────────────────────┘
                         │ investor_bid orders
                         ▼
                 Market aggregates
                 LLMNoise also contributes
```


## §6 Configuration Reference

| Config Path                 | Key Parameter  | Value               | Notes                                                     |
|-----------------------------|----------------|---------------------|-----------------------------------------------------------|
| `*.extras.llm.sys_message`  | System prompt  | per agent           | Availability bias persona (no numerical formulas)         |
| `*.extras.llm.user_message` | User template  | `LLM_USER_TEMPLATE` | Includes `{return_pct}` in addition to standard variables |
| `*.extras.llm.lm_name`      | LLM model name | configured          | e.g., `doubao-pro-32k`                                    |

Full config: `configs/AvailabilityBias/LLM/players.yml`


## §7 Running Instructions

```bash
# From project root:
python examples/AvailabilityBias/LLM/run_availabilitybias_llm.py \
    -c configs/AvailabilityBias/LLM/simulation.yml

# Run analysis:
python examples/AvailabilityBias/Rule/analysis.py \
    -c configs/AvailabilityBias/LLM/simulation.yml
```

Output: `EXPERIMENT/AvailabilityBias/LLM/records/`


## §8 Expected Behavior Patterns

| Phase             | Deviation Range  | LLM-Specific Behavior                                                                            |
|-------------------|------------------|--------------------------------------------------------------------------------------------------|
| **Pre-Event**     | [−2%, +2%]       | Agents hold; LLM personas recognize stability                                                    |
| **Event Trigger** | first large move | LLMRecentEventOverweighter reacts to return_pct; may over-react before Rule's salience threshold |
| **Bias Peak**     | [3%–15%]         | LLMMediaInfluencedTrader amplifies based on deviation narrative; higher amplitude than Rule      |
| **Correction**    | Declining        | LLMSystematicAnalyst + LLMValueTrader counter-trade; may be delayed by "denial" framing          |
| **Stabilization** | Near 0%          | High variance; some runs may not fully correct within 100 rounds                                 |


## §9 References

*(Theory sections from simulation-bases.md — cross-reference only)*

- `../simulation-bases.md §4.1, §4.2` — RecencyOverweighter and MediaInfluencedTrader archetypes
- `../simulation-bases.md §4.3, §4.4` — SystematicAnalyst and ValueTrader archetypes
- `../simulation-bases.md §5` — LLM variant description
- `../analysis-bases.md §6` — Expected LLM result ranges (higher bias amplitude)
- `prompts.py → LLM_*_SYS` — Behavioral persona prompts with availability bias encoding
