# AsianFinancialCrisis / Hot Money Funder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AsianFinancialCrisis |
| Agent type | Hot Money Funder |
| Canonical class | `HotMoneyFunder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

HotMoneyFunder represents the archetypal short-term foreign capital investor who provides liquidity and return-chasing flows during benign periods but reverses rapidly and aggressively at the first sign of currency stress. This agent models the foreign institutional investors -- primarily hedge funds and money market funds -- who provided the capital inflows that fuelled Asian growth in 1994-1997, then executed sudden, large-scale reversals in 1997. HotMoneyFunder is the primary crisis initiator: its 60% position liquidation at the -2% threshold creates the initial selling wave that triggers the contagion cascade.

## Financial Theory / Theoretical Basis

### Rule / `HotMoneyFunder`
- Theory: simulation-bases.md Section 4.1 -- HotMoneyFunder
- Theoretical Basis: Hot money reversal (Radelet & Sachs, 1998)

### LLM / `LLMHotMoneyFunder`
- LLM-driven hot money funder -- rapidly reverses at first crisis signal. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMHotMoneyFunder`
- RuleLLM hot money funder with explicit reversal threshold rules. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMHotMoneyFunder`
- RAG-augmented hot money funder -- rapidly reverses at first crisis signal. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| buy_ratio | Rule: `0.3` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `3000.0`<br>LLM: `3000.0`<br>RuleLLM: `3000.0`<br>Rag: `3000.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_HOT_MONEY_FUNDER_SYS', 'user_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_HOT_MONEY_FUNDER_SYS', 'user_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_HOT_MONEY_FUNDER_SYS', 'user_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| reversal_threshold | Rule: `0.02` | Rule |
| sell_ratio | Rule: `0.6` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | hot_money_funder | Hot Money Funder | `HotMoneyFunder` | 2 | `examples/AsianFinancialCrisis/Rule/players.py` |
| LLM | hot_money_funder | Hot Money Funder | `LLMHotMoneyFunder` | 2 | `examples/AsianFinancialCrisis/LLM/players.py` |
| RuleLLM | hot_money_funder | Hot Money Funder | `RuleLLMHotMoneyFunder` | 2 | `examples/AsianFinancialCrisis/RuleLLM/players.py` |
| Rag | ragllm_hot_money_funder | RAG Hot Money Funder | `RagLLMHotMoneyFunder` | 2 | `examples/AsianFinancialCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 HotMoneyFunder

#### 4.1.1  Summary

HotMoneyFunder represents the archetypal short-term foreign capital investor who provides liquidity and return-chasing flows during benign periods but reverses rapidly and aggressively at the first sign of currency stress. This agent models the foreign institutional investors -- primarily hedge funds and money market funds -- who provided the capital inflows that fuelled Asian growth in 1994-1997, then executed sudden, large-scale reversals in 1997. HotMoneyFunder is the primary crisis initiator: its 60% position liquidation at the -2% threshold creates the initial selling wave that triggers the contagion cascade.

#### 4.1.2  Theoretical and Empirical Foundation

**Sudden Stop Theory**:
- Theory / Study: Hot Money and Sudden Stop Dynamics
- Citation: Radelet, S., & Sachs, J. (1998). The East Asian financial crisis. *Brookings Papers on Economic Activity*, 1998(1), 1-90. https://doi.org/10.1353/eca.1998.0009
- Core Insight: Short-term capital inflows are highly sensitive to risk sentiment and reverse suddenly. A threshold-crossing event (currency deviation, reserve depletion, political shock) triggers rapid, large-scale capital exit. The exit is procyclical and self-reinforcing: exit -> depreciation -> more exit.
- Mathematical Formulation: `Sell when deviation(t) < -0.02; Q_sell = 0.60 x position`. The `0.60` sell ratio reflects the empirical observation that hot money typically exits 50-80% of its position rapidly on reversal signals.
- Empirical Evidence: Radelet & Sachs (1998): Thailand's short-term foreign debt ($45B) vs. FX reserves ($38B) created structural sudden-stop vulnerability. Crisis was triggered by relatively small forward market deviations (~2-3%), not fundamental deterioration. This directly calibrates `reversal_threshold = 0.02`.
- Relevance to This Investor: HotMoneyFunder's rapid 60% liquidation at -2% deviation directly models the Radelet-Sachs sudden stop mechanism.

**Capital Flow Reversal and Balance-of-Payments Crisis**:
- Theory / Study: Exchange Rate Crises and Capital Account Openness
- Citation: Calvo, G. A. (1998). Capital flows and capital-market crises: The simple economics of sudden stops. *Journal of Applied Economics*, 1(1), 35-54.
- Core Insight: When international capital markets are integrated, a sudden stop creates an immediate balance-of-payments crisis even if fiscal fundamentals are sound. The required current account adjustment is abrupt and contractionary. The size of the position that needs to be liquidated determines the depth of the crisis.
- Mathematical Formulation: Crisis depth is proportional to: `total_liquidation_volume x price_impact = (sell_ratio x initial_position x lambda)`. With `sell_ratio = 0.60`, `initial_position = 3,000`, `lambda = 0.04`: each HotMoneyFunder exit contributes -$7.20 to price per instance.
- Empirical Evidence: Calvo (1998) estimates that sudden stops in Latin American and Asian emerging markets produced GDP contractions of 5-10% within 12 months; the magnitude is directly proportional to the pre-crisis current account deficit and short-term debt overhang.
- Relevance to This Investor: Two HotMoneyFunder instances with 3,000 shares each represent the concentrated foreign capital that fuelled pre-crisis inflows; their simultaneous reversal creates the crisis-initiating demand shock.

#### 4.1.3  Design Purpose and Activation Scenarios

Purpose: HotMoneyFunder initiates the crisis by providing the first large-scale selling wave. Without HotMoneyFunder, the system would not spontaneously generate a crisis -- it requires the sudden reversal of concentrated short-term capital.

Activation Scenarios:
- Pre-crisis (deviation > 0): Buys when deviation > 0.02; accumulates position on positive deviation.
- Crisis trigger (deviation < -0.02): Sells 60% of position immediately; the primary crisis-initiating event.
- Recovery phase (deviation rising back toward 0): Cautiously re-enters when deviation > +0.02.

Market Contribution: **Strongly Destabilising** -- initiates the crisis and provides the largest single selling shock. At lambda = 0.04, two instances with 3,000-share positions contribute up to -$144 per round at full liquidation.

Interaction with other agents: HotMoneyFunder's selling drives deviation below ContagionTrader's threshold (-0.025), triggering contagion; the combined selling by both pushes deviation toward IMFRescuer's threshold (-0.05).

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**

| Signal      | Type       | Rationale                                                                                  |
|-------------|------------|--------------------------------------------------------------------------------------------|
| `deviation` | Continuous | Primary trigger; `deviation < -0.02` triggers sell; hot money reversal is deviation-driven |
| `position`  | State      | Required for sell quantity calculation (60% of position)                                   |
| `cash`      | State      | Required for buy quantity calculation (30% deployment)                                     |

Does NOT use: `price_return`, `contagion_signal`, `volume`. HotMoneyFunder's decision is purely threshold-based on deviation -- consistent with the Radelet-Sachs "simple threshold" model of hot money reversal.

**4.1.4.2  Core Behavioral Mechanism**

1. Each round: checks `deviation` against thresholds.
2. If `deviation < -reversal_threshold (-0.02)`: SELL crisis mode -- liquidate 60% of current position.
3. If `deviation > +reversal_threshold (+0.02)`: BUY re-entry -- deploy 30% of cash at current price.
4. Otherwise: HOLD.

**4.1.4.3  Mathematical Model**

- Decision variable: Buy/sell quantity Q*(t)
- Trigger function:
  ```
  Sell:  deviation(t) < -0.02
  Buy:   deviation(t) > +0.02
  Hold:  |deviation(t)| <= 0.02
  ```
- Sizing function:
  ```
  Q*(t) = -sell_ratio x position(t)            [sell: -0.60 x position]
  Q*(t) = +buy_ratio x cash / price(t)          [buy: +0.30 x cash / price]
  ```
- State variables: `position`, `cash` -- updated each round
- Parameter definitions:

| Symbol                    | Meaning                                       | Config Path                  | Source                                                          |
|---------------------------|-----------------------------------------------|------------------------------|-----------------------------------------------------------------|
| reversal_threshold = 0.02 | Deviation before hot money reverses           | players.yml -> HotMoneyFunder | Radelet & Sachs (1998): 2-3% threshold observed in Asian crisis |
| sell_ratio = 0.60         | Fraction of position liquidated on reversal   | players.yml -> HotMoneyFunder | Calvo (1998): 50-80% exit typical in sudden stop episodes       |
| buy_ratio = 0.30          | Fraction of cash deployed on re-entry         | players.yml -> HotMoneyFunder | Conservative re-entry after crisis resolution                   |
| initial_position = 3,000  | Pre-crisis accumulated long position (shares) | players.yml -> HotMoneyFunder | Calibrated to produce 30-60% crisis depth                       |
| initial_cash = $800,000   | Starting cash reserves                        | players.yml -> HotMoneyFunder | Scaled to position size                                         |

**4.1.4.4  Behavioral Properties**

- Time horizon: Very short-term -- threshold-triggered; no memory or accumulation logic
- Risk tolerance: Asymmetric -- extremely aggressive on reversal (60% liquidation); cautious on re-entry (30% deployment)
- Information asymmetry: None -- uses only public deviation signal; no private information
- Psychological profile: Pure panic selling on downside; consistent with the "sudden stop" psychology documented by Calvo (1998); no fundamental analysis -- the 2% deviation threshold is the sole decision criterion

#### 4.1.5  Decision Process Walkthrough

```
Given:  deviation = -0.025,  position = 3,000,  sell_ratio = 0.60

Step 1: Check deviation threshold
        -0.025 < -0.02 -> sell condition satisfied

Step 2: Compute sell quantity
        Q* = -0.60 x 3,000 = -1,800 shares

Step 3: Send order
        action = sell, quantity = 1,800, bid_price = current_price

Result: Removes 1,800 shares from demand; contributes lambda x (-1,800) = 0.04 x (-1,800) = -$72 to price
        One HotMoneyFunder instance reduces price by $72 in a single round.
        Two instances contribute -$144 simultaneously -> rapid crisis deepening.
```

#### 4.1.6  Worked Numerical Example

```
Market state:  price = 97.0 (deviation = -0.03),  position = 2,400 (reduced from earlier sells)
               cash = $400,000

Check: deviation = -0.03 < -0.02 -> SELL
Q*    = -0.60 x 2,400 = -1,440 shares

Decision: action = sell, quantity = 1,440, bid_price = 97.0
Cash received: 1,440 x 97.0 = $139,680; new cash = $539,680; new position = 960

Rationale: With deviation already at -3%, HotMoneyFunder continues liquidating.
Its 60% sell ratio means it exits a large fraction of remaining position each round,
creating persistent selling pressure throughout the crisis phase -- the self-reinforcing
capital outflow documented by Radelet & Sachs (1998).
```

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                             | Notes                                                                            |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| 1 | Radelet, S., & Sachs, J. (1998). The East Asian financial crisis. *Brookings Papers*, 1998(1), 1-90. https://doi.org/10.1353/eca.1998.0009                           | Core framework; calibrates reversal_threshold and crisis narrative               |
| 2 | Calvo, G. A. (1998). Capital flows and capital-market crises. *Journal of Applied Economics*, 1(1), 35-54.                                                           | Grounds sell_ratio = 0.60 and initial_position in sudden stop theory             |
| 3 | Eichengreen, B., Rose, A. K., & Wyplosz, C. (1996). Contagious currency crises. *Scandinavian Journal of Economics*, 98(4), 463-484. https://doi.org/10.2307/3440879 | Documents symmetric threshold behaviour of hot money in multiple crisis episodes |

---

## Source Docstring Excerpts

### Rule / `HotMoneyFunder`

```text
Provides short-term foreign currency loans that reverse rapidly at first sign of trouble.

Theory: simulation-bases.md Section 4.1 -- HotMoneyFunder
Theoretical Basis: Hot money reversal (Radelet & Sachs, 1998)
Market Role: destabilizing

Strategy:
    - When deviation > reversal_threshold (market rising): deploy buy_ratio of cash
    - When deviation < -reversal_threshold (market falling): sell sell_ratio of position
See simulation-bases.md Section 4.1.4.3 for mathematical model.
```

### LLM / `LLMHotMoneyFunder`

```text
LLM-driven hot money funder -- rapidly reverses at first crisis signal. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMHotMoneyFunder`

```text
RuleLLM hot money funder with explicit reversal threshold rules. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMHotMoneyFunder`

```text
RAG-augmented hot money funder -- rapidly reverses at first crisis signal. Theory: simulation-bases.md Section 4.1.
```
