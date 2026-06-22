# ArchegosCollapse / Concentrated Fund

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ArchegosCollapse |
| Agent type | Concentrated Fund |
| Canonical class | `ConcentratedFund` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `ConcentratedFund` represents a highly leveraged family office holding large synthetic equity exposure through Total Return Swaps -- modeled directly on Archegos Capital Management's operational structure. This investor is the primary cascade initiator: its forced selling, when triggered by a maintenance margin breach, provides the initial large negative demand shock that drives prices below the prime brokers' liquidation thresholds. Without this agent, no cascade occurs -- it is the single necessary precondition for the entire phenomenon. Its distinguishing feature compared to other investors is the combination of (1) extreme position size (the largest holder in the market), (2) leverage-forced selling (no discretion once triggered), and (3) sudden, large-block liquidation that no other agent type exhibits.

## Financial Theory / Theoretical Basis

### Rule / `ConcentratedFund`
- Theory: simulation-bases.md Section 4.1 -- ConcentratedFund
- Theoretical basis: Total Return Swap Leverage (Becketti, 2021); Hidden Leverage
- (SEC, 2021 Archegos Report).

### LLM / `LLMConcentratedFund`
- LLM-driven concentrated fund -- TRS-leveraged, slow to react to margin calls. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMConcentratedFund`
- RuleLLM concentrated fund -- TRS-leveraged, margin call driven. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMConcentratedFund`
- RAG-augmented concentrated fund -- TRS-leveraged, margin call driven. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `5000.0`<br>LLM: `5000.0`<br>RuleLLM: `5000.0`<br>Rag: `5000.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_CONCENTRATED_FUND_SYS', 'user_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_CONCENTRATED_FUND_SYS', 'user_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_CONCENTRATED_FUND_SYS', 'user_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| margin_threshold | Rule: `-0.15` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trs_sell_ratio | Rule: `0.5` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | concentrated_fund | Concentrated Fund | `ConcentratedFund` | 2 | `examples/ArchegosCollapse/Rule/players.py` |
| LLM | concentrated_fund | Concentrated Fund | `LLMConcentratedFund` | 2 | `examples/ArchegosCollapse/LLM/players.py` |
| RuleLLM | concentrated_fund | Concentrated Fund | `RuleLLMConcentratedFund` | 2 | `examples/ArchegosCollapse/RuleLLM/players.py` |
| Rag | ragllm_concentrated_fund | RAG Concentrated Fund | `RagLLMConcentratedFund` | 2 | `examples/ArchegosCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 ConcentratedFund

#### 4.1.1 Summary

The `ConcentratedFund` represents a highly leveraged family office holding large synthetic equity exposure through Total Return Swaps -- modeled directly on Archegos Capital Management's operational structure. This investor is the primary cascade initiator: its forced selling, when triggered by a maintenance margin breach, provides the initial large negative demand shock that drives prices below the prime brokers' liquidation thresholds. Without this agent, no cascade occurs -- it is the single necessary precondition for the entire phenomenon. Its distinguishing feature compared to other investors is the combination of (1) extreme position size (the largest holder in the market), (2) leverage-forced selling (no discretion once triggered), and (3) sudden, large-block liquidation that no other agent type exhibits.

#### 4.1.2 Theoretical and Empirical Foundation

**Theory/Study 1: TRS Leverage and Hidden Systemic Concentration**

- Citation: Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, Federal Reserve Bank of Kansas City, 2021-Q3, 1-12. https://doi.org/10.18651/ER/v106n3Becketti
- Core Insight: TRS-structured leverage makes extreme concentration invisible to counterparties until the margin breach. The forced close-out mechanism is binary -- below the maintenance margin, no partial adjustment is possible; the entire margined position must be wound down rapidly.
- Mathematical Formulation:
  ```
  equity(t) = initial_equity + (P(t) - P(0)) x position
  margin_breach: equity(t) / (P(t) x position) < maintenance_margin_rate
  ```
- Empirical Evidence: FSB (2022) documented Archegos held $35-40B notional exposure with 5-8x leverage. The maintenance margin was approximately 10-15% of notional, implying a margin call is triggered by a price decline of roughly 10-20% from the initial position price. Liquidation fractions of 50-70% in the first round of margin calls are documented in prime broker operational reports.
- Relevance to This Investor: The trigger threshold `leverage_trigger = 0.15` corresponds to a 15% decline from fundamental (approximating the 10-20% empirical range after adjusting for the leverage ratio). The `liquidation_fraction = 0.50` reflects the 50% first-round liquidation documented in post-event analysis.
- Parameter Calibration: leverage_trigger ∈ [0.10, 0.20]; chosen 0.15 as midpoint of empirical range.

**Theory/Study 2: Overconfidence and Concentration Risk**

- Citation: Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261-292. https://doi.org/10.1162/003355301556400
- Core Insight: Overconfident investors hold more concentrated positions and trade more frequently than optimal. They systematically underestimate risk from their own concentration, believing their information edge justifies the risk -- until a forced liquidation event reveals the full extent of their exposure.
- Mathematical Formulation: Overconfident position sizing: `Q_overconf = Q_optimal x (1 + overconf_multiplier)`, where `overconf_multiplier ∝ perceived information advantage`.
- Empirical Evidence: Barber & Odean (2001) document that high-confidence traders earn 3.5% lower annual returns net of trading costs, with higher concentration and larger drawdowns. This is consistent with Archegos's known operating style (concentrated bets, high leverage, information-advantage belief).
- Relevance to This Investor: Models the psychological basis for the ConcentratedFund's extreme position size and reluctance to de-risk earlier. The high initial_position reflects overconfident position sizing.

#### 4.1.3 Design Purpose and Activation Scenarios

**Purpose**: Generate the initial large negative demand shock that triggers the cascade. ConcentratedFund is the necessary first-mover in the cascade chain.

| Market Condition                            | ConcentratedFund Response             | Economic Effect                                                                                             | Theory                                               |
|---------------------------------------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| deviation >= -0.15 (normal/moderate decline) | Hold position; no action              | No cascade initiation                                                                                       | Section 4.1.2 Theory 1: below maintenance margin trigger    |
| deviation < -0.15 (margin breach)           | Forced sell: `position x 0.50` shares | Large negative demand shock (-500-1500 shares); price declines further; deviation crosses broker thresholds | Section 4.1.2 Theory 1: maintenance margin forced close-out |

**Market Contribution**: Strongly Destabilizing. A single forced sell of 50% of position (typically 1000-2000 shares at position_size 2000-4000) generates net demand of -1000 to -2000, producing a price change of `lambda x (-1500) = 0.03 x (-1500) = -$4.50` -- approximately a 4.5% price decline in one round.

**Interaction Effects**: Must sell BEFORE PrimeBroker1's threshold (-0.10) is crossed, or the cascade ordering does not replicate the Archegos timing. ConcentratedFund's selling is the sole driver of the first threshold crossing; PrimeBroker1 and PrimeBroker2 only act after ConcentratedFund has moved prices into cascade territory.

#### 4.1.4 Behavioral Framework

##### 4.1.4.1 Decision Information Set

| Signal        | Usedtheta    | Rationale                                                                                                         |
|---------------|----------|-------------------------------------------------------------------------------------------------------------------|
| `deviation`   | Yes      | The primary trigger signal; directly measures the equity loss relative to fundamental, proxying for margin status |
| `price`       | Yes      | Used for portfolio valuation and order pricing                                                                    |
| `fundamental` | Implicit | Used only through `deviation`; ConcentratedFund does not independently compute fundamental analysis               |
| `prev_price`  | No       | Trigger is level-based (deviation threshold), not change-based                                                    |
| `round`       | No       | No frequency control; triggers immediately when margin breached                                                   |

**Information asymmetry note**: ConcentratedFund knows its leverage ratio but is modeled as NOT knowing when other prime brokers will liquidate. This asymmetry -- not knowing competitors' thresholds -- is historically accurate: Archegos held TRS positions with multiple prime brokers simultaneously, and no single broker had full visibility into the others' exposure.

##### 4.1.4.2 Core Behavioral Mechanism

ConcentratedFund starts the simulation with a very large long equity position funded through TRS leverage. In normal rounds (deviation above -0.15), it holds passively -- the leveraged fund has no incentive to trade; it is waiting for the position to appreciate.

When price decline brings deviation below the leverage_trigger threshold (-0.15), this signals a maintenance margin breach. At this point, the fund loses discretion: it must sell to meet margin calls from its prime brokers. The forced close-out is large and abrupt -- the fund does not sell gradually; it liquidates a fixed fraction of its position immediately in the triggered round.

The sizing reflects TRS margin call mechanics: the fund does not sell the entire position (which would close out all synthetic exposure), but a substantial fraction sufficient to restore the equity ratio above maintenance margin. In practice, 40-60% of position is sold in the initial margin call response.

ConcentratedFund has no persistent state beyond its current position size. Once it has sold in response to a margin call, it cannot re-enter (no cash available; position reduced). If deviation recovers, the fund simply holds the reduced position.

##### 4.1.4.3 Mathematical Model

**Decision Variable**: Q_sell = forced sell quantity (shares)

**Trigger Function**:
```
Trigger when: δ(t) < -theta_leverage
where δ(t) = (P(t) - F) / F   [deviation from fundamental]
      theta_leverage = leverage_trigger = 0.15  [maintenance margin approximation]
```

**Sizing Function**:
```
Q_sell(t) = position(t) x φ_liquidation
where φ_liquidation = liquidation_fraction = 0.50
Constraint: Q_sell <= position(t)   [cannot sell more than held]
Result: action = "sell", quantity = Q_sell
```

**State Variables**:
| Variable | Type  | Initial Value | Update Rule                         | Economic Meaning                          |
|----------|-------|---------------|-------------------------------------|-------------------------------------------|
| position | int   | 2000 shares   | position -= Q_sell each sell round  | Remaining synthetic long exposure         |
| cash     | float | 10000.0       | cash += Q_sell x price when selling | Available cash (small; fund is leveraged) |

**Parameter Definitions**:
| Symbol        | Plain-Language Meaning                     | Config Path                 | Value | Source                                     |
|---------------|--------------------------------------------|-----------------------------|-------|--------------------------------------------|
| theta_leverage    | Deviation threshold triggering margin call | extras.leverage_trigger     | 0.15  | Becketti (2021); FSB (2022)                |
| φ_liquidation | Fraction of position sold at margin call   | extras.liquidation_fraction | 0.50  | Archegos post-mortem; prime broker reports |

**Model Limitations**: The model uses a single static threshold for the margin call, whereas real TRS agreements use dynamic margin schedules (margin increases as losses deepen). This simplification is consistent with agent-based modeling conventions (LeBaron, 2006; *Handbook of Computational Economics*, Vol. 2).

##### 4.1.4.4 Behavioral Properties

| Property               | Value                                                                                                | Rationale                                                                             |
|------------------------|------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| Time Horizon           | Position trader (months), forced to liquidate instantly                                              | TRS positions are designed for medium-term holding; forced close-out is instantaneous |
| Risk Tolerance         | Extreme (leverage ratio 5-8x)                                                                        | Empirically documented in FSB (2022); Archegos operational profile                    |
| Decision Frequency     | Condition-triggered only (not every round)                                                           | Only acts when leverage_trigger is crossed; holds in all other rounds                 |
| Information Processing | Partially rational (holds based on information edge belief); forced action ignores market conditions | Barber & Odean (2001) overconfidence model                                            |
| Psychological Profile  | Overconfident in position; denial-resistant to early signs of loss; abrupt capitulation at threshold | Archegos post-mortem accounts; Barber & Odean (2001)                                  |

#### 4.1.5 Decision Process Walkthrough

**Example Market State**:
- Round: 12
- Price: 84.5 -- declining from initial 100.0
- Fundamental: 100.0
- Deviation: (84.5 - 100.0) / 100.0 = -0.155 -- BELOW the -0.15 trigger
- Position: 2000 shares
- Cash: 10,000

**Decision Trace**:

Step 1 -- Perception:
  ConcentratedFund observes deviation = -0.155.
  This is below the leverage_trigger threshold of -0.15.
  In real terms: the TRS mark-to-market loss on 2000 shares x ($100 - $84.50) = $31,000 has depleted the margin account.

Step 2 -- Trigger Check:
  Check: -0.155 < -0.15theta -> YES
  Margin call triggered. The prime broker demands immediate collateral posting or position close-out.

Step 3 -- Sizing:
  Q_sell = position x liquidation_fraction = 2000 x 0.50 = 1000 shares
  Constraint: Q_sell = 1000 <= position = 2000 ✓

Step 4 -- Action:
  Decision: action = "sell", quantity = 1000, bid_price = 84.5 (market order at current price)

Step 5 -- Market Impact:
  This order contributes -1000 to net demand D(t).
  Price effect: DeltaP ≈ lambda x (-1000) = 0.03 x (-1000) = -$30.00
  New price (before mean reversion and noise): P ≈ 84.5 - 30 = ~54.5
  New deviation: (54.5 - 100) / 100 = -0.455 -> well below PrimeBroker1 threshold (-0.10)

#### 4.1.6 Worked Numerical Example

**Inputs**:
| Variable                 | Value       |
|--------------------------|-------------|
| P(t)                     | 84.5        |
| F                        | 100.0       |
| δ(t) = (84.5-100)/100    | -0.155      |
| position                 | 2000 shares |
| cash                     | $10,000     |
| leverage_trigger (theta)     | 0.15        |
| liquidation_fraction (φ) | 0.50        |

**Calculation**:
```
Step 1: Check trigger: δ = -0.155 < -theta = -0.15 -> True
Step 2: Q_sell = 2000 x 0.50 = 1000 shares
Step 3: Constraint: 1000 <= 2000 ✓
Step 4: Submit order: sell 1000 shares at $84.50
```

**Expected Market Impact** (assuming no other orders this round):
```
D(t) = 0 - 1000 = -1000 (only this order)
DeltaP_demand = lambda x D = 0.03 x (-1000) = -$30.00
DeltaP_mean_rev = gamma x (F - P) = 0.01 x (100 - 84.5) = +$0.155
DeltaP_noise ≈ 0 (expected value)
P(t+1) ≈ 84.5 - 30.0 + 0.155 = $54.66
New deviation ≈ (54.66 - 100) / 100 = -0.453
```
This -45.3% deviation far exceeds both PrimeBroker thresholds (-0.10, -0.15), triggering the cascade in the following rounds.

#### 4.1.7 Academic References

| # | Full Citation                                                                                                                                                                                                      | Contribution                                                             |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 1 | Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, Federal Reserve Bank of Kansas City, 2021-Q3, 1-12. https://doi.org/10.18651/ER/v106n3Becketti                                | TRS leverage mechanics; margin call thresholds; liquidation fractions    |
| 2 | Financial Stability Board. (2022). *Non-bank Financial Intermediation: Global Monitoring Report 2022*, pp. 47-54. https://www.fsb.org/2022/12/global-monitoring-report-on-non-bank-financial-intermediation-2022/  | Empirical leverage ratios and concentration data for Archegos-type funds |
| 3 | Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261-292. https://doi.org/10.1162/003355301556400              | Overconfidence as basis for extreme position sizing and concentration    |
| 4 | LeBaron, B. (2006). Agent-based computational finance. In L. Tesfatsion & K. L. Judd (Eds.), *Handbook of Computational Economics*, Vol. 2, pp. 1187-1233. Elsevier. https://doi.org/10.1016/S1574-0021(05)02024-1 | Justification for single-threshold margin call simplification            |

---

## Source Docstring Excerpts

### Rule / `ConcentratedFund`

```text
TRS-leveraged concentrated fund (Archegos-style).

Theory: simulation-bases.md Section 4.1 -- ConcentratedFund
Theoretical basis: Total Return Swap Leverage (Becketti, 2021); Hidden Leverage
(SEC, 2021 Archegos Report).
Forced to sell when price drops below margin threshold.
Sells trs_sell_ratio * position when margin call triggered.
See simulation-bases.md Section 4.1.4.3 for mathematical model.
```

### LLM / `LLMConcentratedFund`

```text
LLM-driven concentrated fund -- TRS-leveraged, slow to react to margin calls. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMConcentratedFund`

```text
RuleLLM concentrated fund -- TRS-leveraged, margin call driven. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMConcentratedFund`

```text
RAG-augmented concentrated fund -- TRS-leveraged, margin call driven. Theory: simulation-bases.md Section 4.1.
```
