# AnchoringEffect / Momentum Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AnchoringEffect |
| Agent type | Momentum Trader |
| Canonical class | `MomentumTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

MomentumTrader represents the short-horizon trend follower who ignores both fundamentals and anchors, trading purely on round-to-round price changes. In the AnchoringEffect context, MomentumTrader plays an amplifying role: when anchoring creates slow upward price drift, MomentumTrader buys into the trend, extending the overvaluation; when correction begins, MomentumTrader sells, potentially accelerating the mean-reversion. Its effect is context-dependent -- it can be both destabilising (extending bubbles) and stabilising (accelerating corrections), depending on the direction of the prevailing trend.

## Financial Theory / Theoretical Basis

### Rule / `MomentumTrader`
- Theoretical basis: simulation-bases.md Section 2.5 (Jegadeesh & Titman, 1993).
- Decision rule (simulation-bases.md Section 4.4 -- Rule-Based Behavior):

### LLM / `LLMMomentumTrader`
- LLM-driven momentum trader -- follows price trends. Theory: simulation-bases.md Section 4.4 -- MomentumTrader.

### RuleLLM / `RuleLLMMomentumTrader`
- RuleLLM momentum trader -- follows price trends. Theory: simulation-bases.md Section 4.4 -- MomentumTrader.

### Rag / `RagLLMMomentumTrader`
- RAG-augmented momentum trader -- follows price trends. Theory: simulation-bases.md Section 4.4 -- MomentumTrader.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| entry_threshold | Rule: `0.02`<br>RuleLLM: `0.02`<br>Rag: `0.02` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AnchoringEffect.LLM.prompts:LLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.AnchoringEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_MOMENTUM_TRADER_SYS', 'user_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AnchoringEffect.Rag.prompts:RAG_MOMENTUM_TRADER_SYS', 'user_message': 'examples.AnchoringEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentum_trader | Momentum Trader | `MomentumTrader` | 2 | `examples/AnchoringEffect/Rule/players.py` |
| LLM | momentum_trader | Momentum Trader | `LLMMomentumTrader` | 2 | `examples/AnchoringEffect/LLM/players.py` |
| RuleLLM | rulellm_momentum | RuleLLM Momentum Trader | `RuleLLMMomentumTrader` | 2 | `examples/AnchoringEffect/RuleLLM/players.py` |
| Rag | ragllm_momentum | RAG Momentum Trader | `RagLLMMomentumTrader` | 2 | `examples/AnchoringEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 MomentumTrader

#### 4.4.1  Summary

MomentumTrader represents the short-horizon trend follower who ignores both fundamentals and anchors, trading purely on round-to-round price changes. In the AnchoringEffect context, MomentumTrader plays an amplifying role: when anchoring creates slow upward price drift, MomentumTrader buys into the trend, extending the overvaluation; when correction begins, MomentumTrader sells, potentially accelerating the mean-reversion. Its effect is context-dependent -- it can be both destabilising (extending bubbles) and stabilising (accelerating corrections), depending on the direction of the prevailing trend.

#### 4.4.2  Theoretical and Empirical Foundation

**Short-Horizon Momentum**:
- Theory / Study: Momentum Premium in Equities
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Stocks with strong recent performance tend to continue outperforming in the near term. Momentum traders who follow price trends create self-reinforcing demand during trending periods and sudden reversals when the trend breaks.
- Mathematical Formulation: `return_pct = (price - prev_price) / prev_price`; `trade when |return_pct| > entry_threshold (0.02)`.
- Empirical Evidence: Jegadeesh & Titman (1993) document 12.01% annualised momentum return for 6-month formation/6-month holding periods. For the very short 1-round momentum window used in this simulation, the effect is noisier but consistent with positive autocorrelation documented by Lo & MacKinlay (1988).
- Relevance to This Investor: `entry_threshold = 0.02` (2% price change triggers trade); position size proportional to return magnitude; direction follows price trend.

**Momentum-Anchoring Interaction**:
- Theory / Study: Interaction of Momentum and Fundamental Anchoring
- Citation: Barberis, N., Shleifer, A., & Vishny, R. W. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0
- Core Insight: Conservatism (underreaction, similar to anchoring) combined with representativeness (overreaction to trends) produces a two-phase price pattern: initial underreaction followed by momentum, then eventual mean reversion. In the AnchoringEffect simulation, anchoring agents produce the initial underreaction, and MomentumTrader provides the momentum phase that extends it.
- Empirical Evidence: Barberis et al. (1998) calibrate their model to explain why returns exhibit short-run momentum (consistent with MomentumTrader's trend-following) and long-run mean reversion (consistent with eventual correction by RationalUpdater and gamma-term).
- Relevance to This Investor: MomentumTrader's interaction with anchoring agents produces the Barberis-Shleifer-Vishny two-phase pattern: underreaction (anchoring) -> momentum extension (MomentumTrader amplifies slow drift) -> correction (RationalUpdater + gamma).

#### 4.4.3  Design Purpose and Activation Scenarios

Purpose: MomentumTrader introduces trend-following demand that amplifies price trends in either direction. Its presence prevents the anchoring simulation from being too "clean" (a simple exponential decay toward fundamental) and models the realistic interaction of multiple behavioral biases.

Activation Scenarios:
- Price rising > 2% in last round: Buys; amplifies upward trend (potentially extending overvaluation).
- Price falling > 2% in last round: Sells; amplifies downward trend (potentially accelerating correction).
- Price change within ±2%: Holds.

Market Contribution: **Neutral to Amplifying** -- can destabilise (extending bubbles) or stabilise (accelerating corrections) depending on trend direction. Net contribution over the full simulation is approximately neutral.

Interaction with other agents: When price is drifting down toward fundamental, MomentumTrader sells alongside RationalUpdater -- briefly accelerating correction. When price is rising, it buys alongside AnchoredTrader -- briefly extending the mispricing.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**

| Signal       | Type       | Rationale                                                              |
|--------------|------------|------------------------------------------------------------------------|
| `price`      | Continuous | Current price; numerator of return calculation                         |
| `prev_price` | Continuous | Previous price; denominator of return; required for signal computation |

Does NOT use: `fundamental`, `deviation`, `anchor`. Pure price-trend agent with no fundamental grounding.

**4.4.4.2  Core Behavioral Mechanism**

Simple single-round momentum: if price rose more than 2% from last round, buy; if fell more than 2%, sell; otherwise hold. Size proportional to return magnitude.

**4.4.4.3  Mathematical Model**

- Decision variable: Q*(t)
- Trigger: `return_pct = (price - prev_price) / prev_price`; trade if `|return_pct| > 0.02`
- Sizing: `Q*(t) = min(base_position_size, abs(return_pct) x 1000)`
- State variables: None
- Key parameter: `entry_threshold = 0.02` (Jegadeesh & Titman: 2% threshold consistent with 1-round momentum signal)

**4.4.4.4  Behavioral Properties**

- Time horizon: Very short-term -- single-round price change
- Risk tolerance: High -- acts on 2% price changes without fundamental check
- Information asymmetry: None -- purely reactive to public price data
- Psychological profile: Recency bias; trend extrapolation; consistent with the "representativeness" component of Barberis et al. (1998)

#### 4.4.5  Decision Process Walkthrough

```
Given:  price = 103.0,  prev_price = 100.5,  entry_threshold = 0.02

Step 1: Compute return
        return_pct = (103.0 - 100.5) / 100.5 = 0.0249

Step 2: Compare to threshold
        0.0249 > 0.02 -> buy condition satisfied

Step 3: Compute quantity
        Q* = min(20.0, 0.0249 x 1000) = min(20.0, 24.9) = 20 shares

Result: Buys 20 shares; adds to upward pressure; extends the overvaluation slightly
```

#### 4.4.6  Worked Numerical Example

```
Market state:  price = 99.0 (correction phase),  prev_price = 101.5
  return_pct = (99.0 - 101.5) / 101.5 = -0.0246  (<-0.02 -> sell)
  Q* = min(20.0, 0.0246 x 1000) = 20 shares (sell)

Decision: action = sell, quantity = 20, bid_price = 99.0
Rationale: Price fell 2.5% in last round; MomentumTrader follows the correction downward,
amplifying the mean-reversion that RationalUpdater initiated. This is the Barberis et al. (1998)
"correction phase" where momentum reinforces the return to fundamental value.
```

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                                           | Notes                                                                  |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 1 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x           | Core momentum theory; calibrates entry_threshold = 0.02                |
| 2 | Barberis, N., Shleifer, A., & Vishny, R. W. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Grounds anchoring-momentum interaction in a coherent behavioural model |

---

## Source Docstring Excerpts

### Rule / `MomentumTrader`

```text
Follows price trends -- buys when price rises, sells when it falls.

Implements simulation-bases.md Section 4.4 -- MomentumTrader.
Theoretical basis: simulation-bases.md Section 2.5 (Jegadeesh & Titman, 1993).

Decision rule (simulation-bases.md Section 4.4 -- Rule-Based Behavior):
    return_pct = (price - prev_price) / prev_price
    if abs(return_pct) > entry_threshold: follow momentum direction
    quantity = min(base_position_size, abs(return_pct) * 1000)

Parameters (simulation-bases.md Section 6):
    entry_threshold: 0.02 (2% return triggers momentum entry)
    base_position_size: loaded from extras["base_position_size"]
```

### LLM / `LLMMomentumTrader`

```text
LLM-driven momentum trader -- follows price trends. Theory: simulation-bases.md Section 4.4 -- MomentumTrader.
```

### RuleLLM / `RuleLLMMomentumTrader`

```text
RuleLLM momentum trader -- follows price trends. Theory: simulation-bases.md Section 4.4 -- MomentumTrader.
```

### Rag / `RagLLMMomentumTrader`

```text
RAG-augmented momentum trader -- follows price trends. Theory: simulation-bases.md Section 4.4 -- MomentumTrader.
```
