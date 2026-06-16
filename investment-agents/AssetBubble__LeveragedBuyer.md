# AssetBubble / Leveraged Buyer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AssetBubble |
| Agent type | Leveraged Buyer |
| Canonical class | `LeveragedBuyer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, RuleLLM, Rag |

## Definition and Goal

LeveragedBuyer represents the procyclical, momentum-driven participant who uses 3x leverage to amplify returns in a rising market. This agent models the margin investor who buys aggressively during the bubble's escalation phase, boosting demand and pushing prices higher. The critical feature that makes LeveragedBuyer a crash catalyst rather than merely a bubble driver is the margin call mechanism: when the equity ratio falls below 70% of initial equity, LeveragedBuyer is forced to sell 50% of its long position immediately, with no discretion. This forced selling is synchronised across multiple LeveragedBuyer instances (all face the same equity threshold) and provides the sudden coordinated selling pressure that triggers the Phase 3 crash.

## Financial Theory / Theoretical Basis

### Rule / `LeveragedBuyer`
- Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer
- Theory: Leverage amplifies both gains and losses
- Behavior:
- - Uses leverage to increase position sizes
- - Faces margin calls when prices fall
- - Forced to sell during downturns (procyclical)
- Effect: STRONGLY DESTABILIZING - Amplifies both bubbles and crashes
- Formula:
- -> simulation-bases.md Section 4.5 -- LeveragedBuyer (Rule-Based Behavior)

### RuleLLM / `RuleLLMLeveragedBuyer`
- Hybrid leverage rules with LLM reasoning. Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer.

### Rag / `RagLLMLeveragedBuyer`
- RAG-augmented leverage rules with retrieved knowledge. Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `40.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>RuleLLM: `3`<br>Rag: `3` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | Rag, Rule, RuleLLM |
| initial_equity | Rule: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | Rag, Rule, RuleLLM |
| leverage_ratio | Rule: `2.0`<br>RuleLLM: `3.0`<br>Rag: `3.0` | Rag, Rule, RuleLLM |
| llm | RuleLLM: `{'sys_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_LEVERAGED_SYS', 'user_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_LEVERAGED_SYS', 'user_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | Rag, RuleLLM |
| margin_call_threshold | Rule: `0.3`<br>RuleLLM: `0.7`<br>Rag: `0.7` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | leveraged_buyer | Leveraged Buyer | `LeveragedBuyer` | 3 | `examples/AssetBubble/Rule/players.py` |
| RuleLLM | rulellm_leveraged | RuleLLM Leveraged Buyer | `RuleLLMLeveragedBuyer` | 3 | `examples/AssetBubble/RuleLLM/players.py` |
| Rag | ragllm_leveraged | RAG Leveraged Buyer | `RagLLMLeveragedBuyer` | 3 | `examples/AssetBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 LeveragedBuyer

#### 4.5.1  Summary

LeveragedBuyer represents the procyclical, momentum-driven participant who uses 3x leverage to amplify returns in a rising market. This agent models the margin investor who buys aggressively during the bubble's escalation phase, boosting demand and pushing prices higher. The critical feature that makes LeveragedBuyer a crash catalyst rather than merely a bubble driver is the margin call mechanism: when the equity ratio falls below 70% of initial equity, LeveragedBuyer is forced to sell 50% of its long position immediately, with no discretion. This forced selling is synchronised across multiple LeveragedBuyer instances (all face the same equity threshold) and provides the sudden coordinated selling pressure that triggers the Phase 3 crash.

#### 4.5.2  Theoretical and Empirical Foundation

**Procyclical Leverage and Forced Deleveraging**:
- Theory / Study: Procyclical Leverage and the Leverage Cycle
- Citation: Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418-437. https://doi.org/10.1016/j.jfi.2008.12.002
- Core Insight: Financial intermediaries manage their balance sheets procyclically: when asset prices rise, mark-to-market equity increases, loosening leverage constraints and enabling additional borrowing and buying. When prices fall, equity declines, tightening leverage constraints and forcing asset sales. This procyclical feedback between asset prices and leverage creates an amplification mechanism where leverage builds during booms and collapses during downturns.
- Mathematical Formulation:
  ```
  equity_ratio(t) = portfolio_value(t) / initial_equity
  where portfolio_value(t) = cash(t) + position(t) x P(t)

  Margin call trigger: equity_ratio(t) < margin_call_threshold (0.70)
  Forced sell: Q_forced = -0.5 x position(t)   (sell half of long)
  ```
- Empirical Evidence: Adrian & Shin (2010) document that the leverage of US broker-dealers follows an AR(1) with positive coefficient ≈ 0.8 against lagged asset price returns (pro-cyclicality); during the 2008 crisis, broker-dealer leverage contracted from ~30x to ~15x through forced deleveraging, consistent with the Abreu-Brunnermeier crash trigger mechanism.
- Relevance to This Investor: LeveragedBuyer's `leverage_ratio = 3.0` and `margin_call_threshold = 0.70` implement the Adrian-Shin procyclicality: it buys on momentum (amplifying the bubble) and is forced to sell when equity falls (triggering the crash).

**Leverage Amplification in Bubble Crashes**:
- Theory / Study: Bubbles and Crashes: Leverage as Crash Catalyst
- Citation: Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173-204. https://doi.org/10.1111/1468-0262.00393
- Core Insight: Forced deleveraging by margin-called investors is the synchronisation mechanism that provides the coordinated exit that triggers a crash. Rational arbitrageurs cannot coordinate their exit timing, but margin calls arrive simultaneously across leveraged participants when prices fall through a threshold -- providing the exogenous synchronisation that Abreu & Brunnermeier's model requires for a crash.
- Mathematical Formulation: Crash triggered when a sufficient fraction of leveraged agents simultaneously hit their margin floor, producing a demand shock large enough to overcome stabilising forces.
- Empirical Evidence: The 2000 NASDAQ crash and 2008 housing collapse both coincided with simultaneous margin call waves; Abreu & Brunnermeier (2003, pp. 190-195) show that with N leveraged agents all facing threshold theta, a price decline of δ = 1 - theta in one round triggers all N agents simultaneously.
- Relevance to This Investor: Multiple `LeveragedBuyer` instances in the simulation will all hit margin_call_threshold = 0.70 within a few rounds of each other during a price decline, producing synchronised forced selling -- the crash catalyst.

#### 4.5.3  Design Purpose and Activation Scenarios

Purpose: LeveragedBuyer serves a dual role: (1) amplifying bubble formation through leveraged demand during the rising phase, and (2) catalysing the crash through synchronised forced selling when margin thresholds are breached.

Activation Scenarios:
- Rising market (price_return > 0.005): Buys aggressively with 3x leverage; amplifies positive feedback loop.
- Falling market (price_return < -0.01): Sells proportionally; begins exiting before margin call is triggered.
- Margin call (equity_ratio < 0.70): Overrides all other logic; forced sells 50% of long; this is the crash catalyst event.

Market Contribution: **Strongly Destabilising** -- amplifies both bubble formation (through leveraged buying) and crash onset (through synchronised forced selling). The leverage multiplier means LeveragedBuyer contributes 3x the market impact per unit of equity compared to unleveraged agents.

Interaction with other agents: During bubble: buys alongside MomentumSpeculator, amplifying demand. During crash: forced selling by LeveragedBuyer reduces prices, which simultaneously (a) triggers more MomentumSpeculator panic selling, (b) triggers additional LeveragedBuyer margin calls in later rounds -- creating a cascade.

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**

| Signal                  | Type           | Rationale                                                                                          |
|-------------------------|----------------|----------------------------------------------------------------------------------------------------|
| `return` (price_return) | Continuous     | Momentum signal for normal (non-margin-call) trading                                               |
| `portfolio_value`       | State variable | Required for equity_ratio calculation; the margin call check is the highest-priority decision rule |
| `position`              | State variable | Required for forced sell quantity calculation (50% of position)                                    |
| `cash`                  | State variable | Internal; ensures buy orders respect liquidity                                                     |

Does NOT use: `fundamental`, `bubble_ratio`. LeveragedBuyer is a pure momentum/leverage play -- it ignores whether the asset is fundamentally overvalued.

**4.5.4.2  Core Behavioral Mechanism**

1. **Priority override -- check margin call first**: If `equity_ratio = portfolio_value / initial_equity < 0.70` AND `position > 0`: forced sell 50% of long position, regardless of price direction. This rule has absolute priority over all other logic.
2. Normal regime (no margin call):
   - If `price_return > 0.005` (price rising): buy aggressively using leverage; `Q = price_return x base_size x leverage_ratio`.
   - If `price_return < -0.01` (price falling): sell proportionally to reduce exposure; `Q = price_return x base_size`.
   - Otherwise: hold.
3. Position bounds: buy capped at +60; sell floored at -40.

**4.5.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger functions:
  ```
  PRIORITY: equity_ratio(t) = portfolio_value(t) / initial_equity < 0.70  -> FORCED SELL
  Buy:  price_return(t) > 0.005   -> leveraged buy
  Sell: price_return(t) < -0.01   -> proportional sell
  ```
- Sizing function:
  ```
  Forced sell:  Q*(t) = -0.5 x position(t)   [no discretion]
  Normal buy:   Q*(t) = price_return x base_size x leverage_ratio   [capped at +60]
  Normal sell:  Q*(t) = price_return x base_size   [floored at -40]
  ```
- State variables: `portfolio_value` (marked to market each round), `position` (share count), `cash`
- Parameter definitions:

| Symbol                       | Meaning                      | Config Path                  | Source                                                                        |
|------------------------------|------------------------------|------------------------------|-------------------------------------------------------------------------------|
| leverage_ratio = 3.0         | Leverage on buy orders       | players.yml -> LeveragedBuyer | Adrian & Shin (2010): typical broker-dealer leverage 3-5x during bull markets |
| margin_call_threshold = 0.70 | Equity floor for forced sell | players.yml -> LeveragedBuyer | Industry standard: 70% maintenance margin (30% loss triggers call)            |
| initial_equity = 10,000.0    | Equity denominator           | players.yml -> LeveragedBuyer | Standardised starting portfolio value                                         |

**4.5.4.4  Behavioral Properties**

- Time horizon: Short-term -- responds each round to momentum; margin call can interrupt at any time
- Risk tolerance: Extreme -- 3x leverage; no stop-loss until margin call fires
- Information asymmetry: No -- uses only public price return and own portfolio state
- Psychological profile: Euphoric during bubble (leverage amplifies gains); panic-transformed at margin call (no discretion -- forced seller); embodies the leverage cycle psychology documented by Adrian & Shin (2010): "when things are good, borrow more; when things are bad, you're forced to sell"

#### 4.5.5  Decision Process Walkthrough

```
Given:  price_return = +0.03,  base_size = 20.0,  leverage_ratio = 3.0
        portfolio_value = 11,500,  initial_equity = 10,000  -> equity_ratio = 1.15 (no margin call)

Step 1: Check margin call
        1.15 > 0.70 -> no margin call; proceed to normal logic

Step 2: Check price_return
        0.03 > 0.005 -> buy condition satisfied

Step 3: Compute quantity
        Q_raw = 0.03 x 20.0 x 3.0 = 1.8 -> round to 1 share (within +60 cap)

Step 4: Send order
        action = buy, quantity = 1, bid_price = current_price

Result: Modest leveraged buy during moderate uptrend; contributes +lambda x 1 = +$0.15 to price
```

**Margin call scenario**:
```
Given:  portfolio_value = 6,800,  initial_equity = 10,000  -> equity_ratio = 0.68
        position = 60 shares

Step 1: Check margin call
        0.68 < 0.70 -> MARGIN CALL TRIGGERED; override all other logic

Step 2: Compute forced sell
        Q_forced = -0.5 x 60 = -30 shares

Step 3: Send order (no discretion)
        action = sell, quantity = 30, bid_price = current_price

Result: Large forced sell; adds -30 to net demand; contributes lambda x (-30) = -$4.50 to price decline;
        triggers further price decline, potentially triggering other LeveragedBuyer margin calls
```

#### 4.5.6  Worked Numerical Example

```
Market state (crash phase):  price = 92.0 (fell from peak 155.0),  position = 45 shares
                              cash = 3,200,  initial_equity = 10,000
                              portfolio_value = 3,200 + 45 x 92.0 = 3,200 + 4,140 = $7,340
                              equity_ratio = 7,340 / 10,000 = 0.734

This round: price falls further to 86.0
  Updated portfolio_value = 3,200 + 45 x 86.0 = 3,200 + 3,870 = $7,070
  equity_ratio = 7,070 / 10,000 = 0.707  -- STILL ABOVE 0.70 this round

Next round: price falls to 80.0
  portfolio_value = 3,200 + 45 x 80.0 = 3,200 + 3,600 = $6,800
  equity_ratio = 6,800 / 10,000 = 0.68 < 0.70  -> MARGIN CALL

Forced sell: Q = -0.5 x 45 = -22 shares (rounded down from 22.5)
Decision: action = sell, quantity = 22, bid_price = 80.0

Rationale: Three rounds of price decline finally crosses the margin call threshold.
LeveragedBuyer must sell 22 shares regardless of any other analysis, contributing -22 to net
demand and pushing price down further -- the procyclical leverage cascade documented by Adrian & Shin (2010).
```

#### 4.5.7  Academic References

| # | Citation                                                                                                                                                                   | Notes                                                                                                                |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| 1 | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418-437. https://doi.org/10.1016/j.jfi.2008.12.002                 | Core reference for procyclical leverage mechanism; calibrates leverage_ratio and margin dynamics                     |
| 2 | Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173-204. https://doi.org/10.1111/1468-0262.00393                                      | Grounds synchronised margin-call crash trigger; calibrates margin_call_threshold                                     |
| 3 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 | Funding-liquidity spiral: forced selling -> lower prices -> more margin calls; validates LeveragedBuyer cascade effect |

## Source Docstring Excerpts

### Rule / `LeveragedBuyer`

```text
Leveraged buyer using margin to amplify positions.
Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer

Theory: Leverage amplifies both gains and losses
    During bubbles, leveraged buyers amplify upside
    During crashes, forced deleveraging amplifies downside
    -> simulation-bases.md Section 2 (context: synchronization risk and crash dynamics)

Behavior:
    - Uses leverage to increase position sizes
    - Faces margin calls when prices fall
    - Forced to sell during downturns (procyclical)

Effect: STRONGLY DESTABILIZING - Amplifies both bubbles and crashes

Formula:
    equity_ratio = portfolio_value / initial_equity
    If equity_ratio < margin_call_threshold: forced deleverage (sell 50%)
    Else: quantity = price_return x base_position_size x leverage_ratio
    -> simulation-bases.md Section 4.5 -- LeveragedBuyer (Rule-Based Behavior)

Parameters from config extras:
    - leverage_ratio, margin_call_threshold, base_position_size, initial_equity
    -> simulation-bases.md Section 6
```

### RuleLLM / `RuleLLMLeveragedBuyer`

```text
Hybrid leverage rules with LLM reasoning. Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer.
```

### Rag / `RagLLMLeveragedBuyer`

```text
RAG-augmented leverage rules with retrieved knowledge. Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer.
```
