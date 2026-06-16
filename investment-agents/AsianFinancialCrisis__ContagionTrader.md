# AsianFinancialCrisis / Contagion Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AsianFinancialCrisis |
| Agent type | Contagion Trader |
| Canonical class | `ContagionTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

ContagionTrader represents the cross-border investor who spreads financial stress from one market to related regional markets, modelling the contagion transmission channel documented in Kaminsky & Reinhart (1999). Unlike HotMoneyFunder who responds purely to absolute deviation, ContagionTrader uses a composite signal that combines fundamental stress (deviation) with momentum (price_return). This dual-signal design implements the Kaminsky-Reinhart finding that contagion spreads through both fundamental linkages and investor panic/portfolio rebalancing simultaneously.

## Financial Theory / Theoretical Basis

### Rule / `ContagionTrader`
- Theory: simulation-bases.md Section 4.2 -- ContagionTrader
- Theoretical Basis: Financial contagion (Kaminsky & Reinhart, 1999)

### LLM / `LLMContagionTrader`
- LLM-driven contagion trader -- spreads selling across borders. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMContagionTrader`
- RuleLLM contagion trader with explicit signal formula rules. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMContagionTrader`
- RAG-augmented contagion trader -- spreads selling across borders. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| contagion_threshold | Rule: `-0.025` | Rule |
| contagion_weight | Rule: `0.6` | Rule |
| cross_border_sensitivity | Rule: `0.4` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `600000.0`<br>LLM: `600000.0`<br>RuleLLM: `600000.0`<br>Rag: `600000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `4000.0`<br>LLM: `4000.0`<br>RuleLLM: `4000.0`<br>Rag: `4000.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_CONTAGION_TRADER_SYS', 'user_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_CONTAGION_TRADER_SYS', 'user_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_CONTAGION_TRADER_SYS', 'user_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sell_ratio | Rule: `0.5` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | contagion_trader | Contagion Trader | `ContagionTrader` | 2 | `examples/AsianFinancialCrisis/Rule/players.py` |
| LLM | contagion_trader | Contagion Trader | `LLMContagionTrader` | 2 | `examples/AsianFinancialCrisis/LLM/players.py` |
| RuleLLM | contagion_trader | Contagion Trader | `RuleLLMContagionTrader` | 2 | `examples/AsianFinancialCrisis/RuleLLM/players.py` |
| Rag | ragllm_contagion_trader | RAG Contagion Trader | `RagLLMContagionTrader` | 2 | `examples/AsianFinancialCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 ContagionTrader

#### 4.2.1  Summary

ContagionTrader represents the cross-border investor who spreads financial stress from one market to related regional markets, modelling the contagion transmission channel documented in Kaminsky & Reinhart (1999). Unlike HotMoneyFunder who responds purely to absolute deviation, ContagionTrader uses a composite signal that combines fundamental stress (deviation) with momentum (price_return). This dual-signal design implements the Kaminsky-Reinhart finding that contagion spreads through both fundamental linkages and investor panic/portfolio rebalancing simultaneously.

#### 4.2.2  Theoretical and Empirical Foundation

**Twin Crises and Contagion Transmission**:
- Theory / Study: Financial Contagion via Common Creditors and Portfolio Rebalancing
- Citation: Kaminsky, G. L., & Reinhart, C. M. (1999). The twin crises. *American Economic Review*, 89(3), 473-500. https://doi.org/10.1257/aer.89.3.473
- Core Insight: Financial contagion spreads through three channels: trade linkages, common creditor rebalancing, and pure panic. The "twin crises" pattern (currency + banking) arises because the same shock triggers simultaneous currency defense and banking sector stress. Contagion requires both a stress signal AND a momentum trigger -- neither alone is sufficient for cross-border spread.
- Mathematical Formulation: `contagion_signal = 0.60 x deviation + 0.40 x price_return`. The 60/40 split assigns primary weight to fundamental stress (deviation) and secondary weight to momentum (portfolio rebalancing signal).
- Empirical Evidence: Kaminsky & Reinhart (1999) study 76 currency crises and 26 banking crises (1970-1995): find that banking crises preceded 18 of 26 currency crises ("twin crises"); leading indicators show deviation from fundamentals (R² ≈ 0.25) and momentum (R² ≈ 0.20) are both significant predictors of cross-border transmission -- calibrating the 60/40 weight split.
- Relevance to This Investor: The composite signal `0.60 x deviation + 0.40 x price_return` implements the Kaminsky-Reinhart dual-channel transmission mechanism.

**Portfolio Rebalancing and Common Creditor Channel**:
- Theory / Study: Common Creditor Channel of Contagion
- Citation: Caramazza, F., Ricci, L., & Salgado, R. (2004). International financial contagion in currency crises. *Journal of International Money and Finance*, 23(1), 51-70. https://doi.org/10.1016/j.jimonfin.2003.10.001
- Core Insight: When a large international bank or fund has significant exposure to multiple regional markets, a loss in one market triggers risk-limit constraints that force rebalancing (selling) across all correlated positions -- even in markets with no direct fundamental linkage. This common creditor channel amplifies contagion beyond what fundamental analysis would predict.
- Mathematical Formulation: `cross_border_component = cross_border_sensitivity x price_return`. The `price_return` proxy captures the momentum signal that portfolio rebalancers observe when they see regional prices falling.
- Empirical Evidence: Caramazza et al. (2004) find that common creditor exposure explains 30-40% of cross-border contagion variance after controlling for bilateral trade, consistent with `cross_border_sensitivity = 0.40` (40% of contagion signal from momentum/portfolio channel).
- Relevance to This Investor: The 40% weight on `price_return` in ContagionTrader's signal implements the Caramazza et al. common creditor rebalancing channel.

#### 4.2.3  Design Purpose and Activation Scenarios

Purpose: ContagionTrader spreads and deepens the crisis by responding to both fundamental deterioration and price momentum, amplifying the initial HotMoneyFunder selling wave into a broader contagion cascade.

Activation Scenarios:
- Contagion signal threshold crossed (signal < -0.025): Sells 50% of position; amplifies crisis depth.
- Double signal (both deviation and price_return negative): Strongest selling signal; produces deepest cascade.
- Signal reversal (signal positive): Stops selling; waits for recovery signal before re-entering.

Market Contribution: **Strongly Destabilising** -- amplifies the crisis initiated by HotMoneyFunder. With 4,000-share positions, two instances contribute -$160 per round at full activation.

Interaction with other agents: Activates approximately 2-5 rounds after HotMoneyFunder (its threshold requires both deviation AND return to be negative, so it requires multiple rounds of sustained selling). Pushes deviation toward IMFRescuer and ValueContrarian thresholds.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**

| Signal                           | Type       | Rationale                                                           |
|----------------------------------|------------|---------------------------------------------------------------------|
| `deviation`                      | Continuous | Fundamental stress component (60% weight); primary crisis indicator |
| `price_return` (from prev_price) | Continuous | Momentum component (40% weight); portfolio rebalancing trigger      |

Distinct from HotMoneyFunder: uses a composite weighted signal rather than a pure threshold, implementing the dual-channel contagion mechanism.

**4.2.4.2  Core Behavioral Mechanism**

1. Computes `price_return = (price - prev_price) / prev_price`.
2. Computes composite signal: `contagion_signal = 0.60 x deviation + 0.40 x price_return`.
3. If `contagion_signal < -0.025`: SELL 50% of position.
4. No buy logic -- ContagionTrader only exits during crisis; recovery is passive (holds remaining position).

**4.2.4.3  Mathematical Model**

- Decision variable: Sell quantity Q*(t)
- Trigger function:
  ```
  price_return(t)      = (P(t) - P(t-1)) / P(t-1)
  contagion_signal(t)  = 0.60 x deviation(t) + 0.40 x price_return(t)
  Sell: contagion_signal(t) < -0.025
  ```
- Sizing function:
  ```
  Q*(t) = -sell_ratio x position(t)   [-0.50 x position on sell; no buy logic]
  ```
- State variables: `position`, `cash`, `prev_price` (from Market broadcast)
- Parameter definitions:

| Symbol                          | Meaning                                    | Config Path                   | Source                                                                  |
|---------------------------------|--------------------------------------------|-------------------------------|-------------------------------------------------------------------------|
| contagion_weight = 0.60         | Weight on deviation in composite signal    | players.yml -> ContagionTrader | Kaminsky & Reinhart (1999): fundamental channel R² ≈ 0.25 (primary)     |
| cross_border_sensitivity = 0.40 | Weight on price_return in composite signal | players.yml -> ContagionTrader | Caramazza et al. (2004): portfolio channel 30-40% of contagion variance |
| contagion_threshold = -0.025    | Composite signal threshold for sell        | players.yml -> ContagionTrader | Calibrated to activate 2-5 rounds after HotMoneyFunder                  |
| sell_ratio = 0.50               | Fraction of position sold on signal        | players.yml -> ContagionTrader | Moderate (vs. HotMoneyFunder 0.60): contagion spreads more gradually    |

**4.2.4.4  Behavioral Properties**

- Time horizon: Short-term -- responds to contemporaneous dual-signal; no historical accumulation
- Risk tolerance: High during crisis -- 50% position liquidation on signal; no loss limit
- Information asymmetry: None -- uses only public deviation and price return
- Psychological profile: Panic-driven portfolio rebalancing (Caramazza et al., 2004); pure technical/signal trader during crisis with no fundamental buy-side capacity

#### 4.2.5  Decision Process Walkthrough

```
Given:  deviation = -0.03,  price_return = -0.025,  position = 4,000,  sell_ratio = 0.50

Step 1: Compute contagion signal
        signal = 0.60 x (-0.03) + 0.40 x (-0.025) = -0.018 + (-0.010) = -0.028

Step 2: Compare to threshold
        -0.028 < -0.025 -> sell condition satisfied

Step 3: Compute sell quantity
        Q* = -0.50 x 4,000 = -2,000 shares

Step 4: Send order
        action = sell, quantity = 2,000, bid_price = current_price

Result: Adds -2,000 to net demand; contributes lambda x (-2,000) = -$80 to price decline.
        Two instances contribute -$160; combined with HotMoneyFunder selling,
        crisis deepens rapidly.
```

#### 4.2.6  Worked Numerical Example

```
Market state (round 15):  price = 88.0,  prev_price = 93.0,  fundamental = 100.0
  deviation   = (88.0 - 100.0) / 100.0 = -0.12
  price_return = (88.0 - 93.0) / 93.0 = -0.054
  signal      = 0.60 x (-0.12) + 0.40 x (-0.054) = -0.072 + (-0.022) = -0.094

Check: -0.094 << -0.025 -> deep contagion signal
Q*   = -0.50 x 3,200 (current position) = -1,600 shares

Decision: action = sell, quantity = 1,600, bid_price = 88.0
Rationale: At -12% deviation and -5.4% price return, both channels are strongly negative,
producing a composite signal 3.7x the threshold. ContagionTrader is in deep panic mode,
executing the Kaminsky-Reinhart common creditor rebalancing cascade.
```

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                | Notes                                                                      |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| 1 | Kaminsky, G. L., & Reinhart, C. M. (1999). The twin crises. *AER*, 89(3), 473-500. https://doi.org/10.1257/aer.89.3.473                                 | Core framework; calibrates dual-signal weights and contagion threshold     |
| 2 | Caramazza, F., Ricci, L., & Salgado, R. (2004). International financial contagion. *JIMF*, 23(1), 51-70. https://doi.org/10.1016/j.jimonfin.2003.10.001 | Calibrates cross_border_sensitivity = 0.40 (portfolio rebalancing channel) |
| 3 | Eichengreen, B., Rose, A. K., & Wyplosz, C. (1996). Contagious currency crises. *SJE*, 98(4), 463-484. https://doi.org/10.2307/3440879                  | Empirical documentation of cross-border contagion speed and magnitude      |

---

## Source Docstring Excerpts

### Rule / `ContagionTrader`

```text
Spreads crisis from one market to another through correlated selling across borders.

Theory: simulation-bases.md Section 4.2 -- ContagionTrader
Theoretical Basis: Financial contagion (Kaminsky & Reinhart, 1999)
Market Role: destabilizing

Strategy:
    - Signal = contagion_weight * deviation + cross_border_sensitivity * return
    - When signal < contagion_threshold: sell sell_ratio of position
See simulation-bases.md Section 4.2.4.3 for mathematical model.
```

### LLM / `LLMContagionTrader`

```text
LLM-driven contagion trader -- spreads selling across borders. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMContagionTrader`

```text
RuleLLM contagion trader with explicit signal formula rules. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMContagionTrader`

```text
RAG-augmented contagion trader -- spreads selling across borders. Theory: simulation-bases.md Section 4.2.
```
