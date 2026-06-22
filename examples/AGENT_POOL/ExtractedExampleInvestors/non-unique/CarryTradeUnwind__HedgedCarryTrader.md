# CarryTradeUnwind / Hedged Carry Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CarryTradeUnwind |
| Agent type | Hedged Carry Trader |
| Canonical class | `HedgedCarryTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The HedgedCarryTrader is a sophisticated carry fund that incorporates volatility risk management: it carries a FX options hedge (modeled as hedge_ratio = 0.30 of position) and adjusts its directional exposure based on rolling volatility. When FX volatility is low, the HedgedCarryTrader accumulates carry positions (but with 30% hedge reducing net exposure); when volatility spikes above threshold, it exits. This investor represents the more sophisticated "smart carry" strategies documented by Menkhoff et al. (2012) -- carry trades that adapt to the volatility environment rather than mechanically holding.

## Financial Theory / Theoretical Basis

### Rule / `HedgedCarryTrader`
- Theory: simulation-bases.md Section 4.4 -- HedgedCarryTrader
- Theoretical basis: Volatility-adjusted carry (Menkhoff et al., 2012);

### LLM / `LLMHedgedCarryTrader`
- LLM-driven hedged carry trader -- volatility-adjusted carry positions. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMHedgedCarryTrader`
- RuleLLM-driven hedged carry trader -- volatility-adjusted carry positions. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMHedgedCarryTrader`
- RAG-augmented hedged carry trader -- volatility-adjusted carry positions. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| hedge_ratio | Rule: `0.3` | Rule |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_HEDGED_CARRY_TRADER_SYS', 'user_message': 'examples.CarryTradeUnwind.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_HEDGED_CARRY_TRADER_SYS', 'user_message': 'examples.CarryTradeUnwind.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_HEDGED_CARRY_TRADER_SYS', 'user_message': 'examples.CarryTradeUnwind.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| vol_threshold | Rule: `0.05` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | hedged_carry_trader | Hedged Carry Trader | `HedgedCarryTrader` | 1 | `examples/CarryTradeUnwind/Rule/players.py` |
| LLM | llm_hedged_carry_trader | LLM Hedged Carry Trader | `LLMHedgedCarryTrader` | 1 | `examples/CarryTradeUnwind/LLM/players.py` |
| RuleLLM | rulellm_hedged_carry_trader | RuleLLM Hedged Carry Trader | `RuleLLMHedgedCarryTrader` | 1 | `examples/CarryTradeUnwind/RuleLLM/players.py` |
| Rag | ragllm_hedged_carry_trader | RAG Hedged Carry Trader | `RagLLMHedgedCarryTrader` | 1 | `examples/CarryTradeUnwind/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 HedgedCarryTrader

#### 4.4.1  Summary

The HedgedCarryTrader is a sophisticated carry fund that incorporates volatility risk management: it carries a FX options hedge (modeled as hedge_ratio = 0.30 of position) and adjusts its directional exposure based on rolling volatility. When FX volatility is low, the HedgedCarryTrader accumulates carry positions (but with 30% hedge reducing net exposure); when volatility spikes above threshold, it exits. This investor represents the more sophisticated "smart carry" strategies documented by Menkhoff et al. (2012) -- carry trades that adapt to the volatility environment rather than mechanically holding.

#### 4.4.2  Theoretical and Empirical Foundation

**Theory 1: Volatility-Adjusted Carry (Menkhoff et al.)**
- Theory / Study: Global FX volatility and carry trade returns
- Citation: Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). "Carry trades and global foreign exchange volatility." *Journal of Finance*, 67(2), 681-718. DOI: 10.1111/j.1540-6261.2012.01728.x
- Core Insight: Carry trade returns are strongly negatively related to FX volatility innovations. Menkhoff et al. find that a volatility-timing strategy (scaling carry positions inversely with volatility) generates Sharpe ratios 50-100% higher than naive carry -- demonstrating the value of volatility-aware position management.
- Mathematical Formulation: Volatility-adjusted position: adj_qty = base_qty x (1 - hedge_ratio) = 500 x 0.7 = 350. Entry condition: deviation > 0 AND rolling_vol < vol_threshold (0.05). Exit condition: deviation < 0 AND rolling_vol > vol_threshold (0.05). Rolling volatility: sigma(t) = std(r[t-N:t]) where r = price returns.
- Empirical Evidence: Menkhoff et al. (2012) find that volatility-timed carry generates annualized Sharpe ratio of 1.2-1.5 vs. 0.4-0.8 for naive carry. vol_threshold = 0.05 calibrated to represent one standard deviation of daily FX volatility -- the level at which risk-adjusted carry becomes unattractive.
- Relevance to This Investor: The HedgedCarryTrader exits before the full cascade peak (triggered by vol_threshold) -- it is typically fully exited before LeveragedCarryFund's stop_loss is hit. This models the empirical observation that sophisticated carry funds exit early while naïve leveraged funds hold until forced.

**Theory 2: Dynamic Hedging and Options-Based Carry**
- Theory / Study: Hedged carry trade strategies
- Citation: Burnside, C., Eichenbaum, M., Kleshchelski, I., & Rebelo, S. (2011). "Do peso problems explain the returns to the carry tradetheta" *Review of Financial Studies*, 24(3), 853-891. DOI: 10.1093/rfs/hhq138
- Core Insight: Burnside et al. document that purchasing put options to hedge crash risk reduces carry returns by 2-4% per year but eliminates crash losses. The hedge_ratio = 0.30 models this partial hedging: 30% of the position is covered, reducing net directional exposure to 70% while maintaining most of the carry premium. The hedge cost is modeled implicitly as the reduced position size.
- Relevance to This Investor: adj_qty = 350 (70% of base 500) represents the reduced directional exposure after hedging; the HedgedCarryTrader's smaller position means its exit during the cascade adds less to selling pressure than LeveragedCarryFund -- a realistic difference between hedged and unhedged funds.

#### 4.4.3  Design Purpose and Activation Scenarios

**Purpose**: Model volatility-aware carry trade participation -- a sophisticated counterpart to the naive LeveragedCarryFund. The HedgedCarryTrader adds carry accumulation during stable phases but exits earlier than LeveragedCarryFund during stress, reducing its cascade contribution.

**Activation Scenarios**:
- Scenario A (Low volatility, deviation > 0): Buy (adj_qty = 350) -- entering carry with partial hedge; models slow accumulation during risk-on periods.
- Scenario B (High volatility spike, deviation < 0): Sell (adj_qty = 350) -- exits before stop_loss is reached; reduces total cascade selling volume vs. LeveragedCarryFund.
- Scenario C (High volatility, small positive deviation): Hold -- vol above threshold even if rate above fundamental; HedgedCarryTrader requires BOTH favorable rate AND low volatility.

**Market Contribution**: Mildly destabilizing during exit (adds to cascade selling, but 350 vs. LCF's 4000); moderately stabilizing relative to LeveragedCarryFund (exits earlier, sells less at peak).

**Interaction with other agents**: Sells alongside LeveragedCarryFund and CarryTrader during unwind but at smaller size; partially offsets FundingCurrencyBuyer buying during accumulation.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**
- `deviation`: Directional signal -- buy when positive, sell when negative.
- Rolling volatility (computed from price_history): Second condition -- only act when vol is on the right side of threshold.
- `price`: For order submission.

**4.4.4.2  Core Behavioral Mechanism**
1. Compute rolling volatility sigma(t) = std(recent price returns).
2. If deviation > 0 AND sigma < vol_threshold (0.05): buy adj_qty = 350.
3. If deviation < 0 AND sigma > vol_threshold (0.05): sell adj_qty = 350.
4. Hold otherwise.

**4.4.4.3  Mathematical Model**
- Two-signal trigger: buy if δ > 0 AND sigma < 0.05; sell if δ < 0 AND sigma > 0.05
- Sizing: Q*(t) = adj_qty = base_qty x (1 - hedge_ratio) = 500 x 0.70 = 350

| Parameter     | Value | Meaning                                            | Config Path                                               | Source                 |
|---------------|-------|----------------------------------------------------|-----------------------------------------------------------|------------------------|
| hedge_ratio   | 0.30  | Fraction of position hedged (reduces net exposure) | `CarryTradeUnwind/Rule/config.yaml -> hedged_carry_trader` | Burnside et al. (2011) |
| vol_threshold | 0.05  | FX volatility threshold for position adjustment    | `CarryTradeUnwind/Rule/config.yaml -> hedged_carry_trader` | Menkhoff et al. (2012) |
| base_qty      | 500   | Base quantity before hedge ratio reduction         | `CarryTradeUnwind/Rule/config.yaml -> hedged_carry_trader` | Normalization          |

**4.4.4.4  Behavioral Properties**
- Time horizon: Carry accumulation (medium-term); quick exit on volatility spike
- Risk tolerance: Medium -- hedge reduces crash exposure; volatility-managed
- Information asymmetry: None -- uses only publicly available price data for volatility calculation
- Psychological profile: Sophisticated, volatility-aware, risk-adjusted. In LLM variants, persona explicitly mentions "I monitor volatility and exit when it spikes."

#### 4.4.5  Decision Process Walkthrough

Given: price = 1.22, fundamental = 1.20, deviation = +0.017, rolling_vol = 0.03 (< 0.05)

Step 1: deviation > 0 AND vol = 0.03 < 0.05 -> buy condition met.
Step 2: adj_qty = 500 x (1 - 0.30) = 350.
Step 3: Order: action=buy, quantity=350, bid_price=1.22.
Result: Carry accumulation in low-volatility environment.

#### 4.4.6  Worked Numerical Example

Market state: price = 1.17, fundamental = 1.20, deviation = -0.025, rolling_vol = 0.07 (> 0.05)

Step 1: deviation < 0 AND vol = 0.07 > 0.05 -> sell condition met.
Step 2: adj_qty = 350.
Step 3: Order: action=sell, quantity=350, bid_price=1.17.
Rationale: Volatility has spiked above threshold while carry is losing -- HedgedCarryTrader exits early, before LeveragedCarryFund's stop_loss (-3%) is triggered at deviation = -0.025. This early exit reduces total cascade selling at the peak, consistent with Menkhoff et al.'s documentation that volatility-aware funds exit earlier and suffer smaller losses.

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                                                               | Notes                                                                     |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| 1 | Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). "Carry trades and global foreign exchange volatility." *Journal of Finance*, 67(2), 681-718. DOI: 10.1111/j.1540-6261.2012.01728.x      | vol_threshold calibration; volatility-adjusted carry strategy performance |
| 2 | Burnside, C., Eichenbaum, M., Kleshchelski, I., & Rebelo, S. (2011). "Do peso problems explain the returns to the carry tradetheta" *Review of Financial Studies*, 24(3), 853-891. DOI: 10.1093/rfs/hhq138 | hedge_ratio calibration; hedged carry trade design                        |


---

## Source Docstring Excerpts

### Rule / `HedgedCarryTrader`

```text
Carry positions with volatility-adjusted hedging -- limits drawdown.

Theory: simulation-bases.md Section 4.4 -- HedgedCarryTrader
Theoretical basis: Volatility-adjusted carry (Menkhoff et al., 2012);
reduces unwind speed via dynamic hedges scaled by realized volatility.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMHedgedCarryTrader`

```text
LLM-driven hedged carry trader -- volatility-adjusted carry positions. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMHedgedCarryTrader`

```text
RuleLLM-driven hedged carry trader -- volatility-adjusted carry positions. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMHedgedCarryTrader`

```text
RAG-augmented hedged carry trader -- volatility-adjusted carry positions. Theory: simulation-bases.md Section 4.4.
```
