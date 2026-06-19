# ArchegosCollapse / Prime Broker 2

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ArchegosCollapse |
| Agent type | Prime Broker 2 |
| Canonical class | `PrimeBroker2` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`PrimeBroker2` represents the second-acting prime broker -- the counterparty who acted later and received worse prices. In the Archegos event, Credit Suisse and Nomura delayed action (March 29), incurring losses of $5.5B and $2.9B respectively versus Morgan Stanley's ~$1B. PrimeBroker2 models the cost of second-mover disadvantage in a creditor cascade: it has a higher threshold (-0.15) reflecting greater loss tolerance or slower risk management processes, but this conservatism backfires -- by the time it acts, prices have already been depressed by ConcentratedFund and PrimeBroker1, and its sell orders occur at substantially worse prices.

## Financial Theory / Theoretical Basis

### Rule / `PrimeBroker2`
- Theory: simulation-bases.md Section 4.3 -- PrimeBroker2
- Theoretical basis: Creditor Run / Liquidation Race (Gorton & Metrick, 2012).

### LLM / `LLMPrimeBroker2`
- LLM-driven prime broker 2 -- delayed liquidator at worse prices. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMPrimeBroker2`
- RuleLLM prime broker 2 -- delayed liquidator at worse prices. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMPrimeBroker2`
- RAG-augmented prime broker 2 -- delayed liquidator at worse prices. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| initial_cash | Rule: `200000.0`<br>LLM: `200000.0`<br>RuleLLM: `200000.0`<br>Rag: `200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `3500.0`<br>LLM: `3500.0`<br>RuleLLM: `3500.0`<br>Rag: `3500.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| liquidation_sell_ratio | Rule: `0.35` | Rule |
| liquidation_threshold | Rule: `-0.15` | Rule |
| llm | LLM: `{'sys_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_PRIME_BROKER2_SYS', 'user_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_PRIME_BROKER2_SYS', 'user_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_PRIME_BROKER2_SYS', 'user_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| price_penalty | Rule: `0.97` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | prime_broker2 | Prime Broker 2 | `PrimeBroker2` | 1 | `examples/ArchegosCollapse/Rule/players.py` |
| LLM | prime_broker2 | Prime Broker 2 | `LLMPrimeBroker2` | 1 | `examples/ArchegosCollapse/LLM/players.py` |
| RuleLLM | prime_broker2 | Prime Broker 2 | `RuleLLMPrimeBroker2` | 1 | `examples/ArchegosCollapse/RuleLLM/players.py` |
| Rag | ragllm_prime_broker2 | RAG Prime Broker 2 | `RagLLMPrimeBroker2` | 1 | `examples/ArchegosCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 PrimeBroker2

#### 4.3.1 Summary

`PrimeBroker2` represents the second-acting prime broker -- the counterparty who acted later and received worse prices. In the Archegos event, Credit Suisse and Nomura delayed action (March 29), incurring losses of $5.5B and $2.9B respectively versus Morgan Stanley's ~$1B. PrimeBroker2 models the cost of second-mover disadvantage in a creditor cascade: it has a higher threshold (-0.15) reflecting greater loss tolerance or slower risk management processes, but this conservatism backfires -- by the time it acts, prices have already been depressed by ConcentratedFund and PrimeBroker1, and its sell orders occur at substantially worse prices.

#### 4.3.2 Theoretical and Empirical Foundation

**Theory/Study 1: Second-Mover Disadvantage in Creditor Runs**

- Citation: Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016
- Core Insight: In a creditor run, later-moving creditors face a coordination disadvantage: earlier liquidators have already depressed collateral prices, reducing the recovery value of later liquidations. The second mover's payoff is `Q x P(t₂) = Q x [P(t₁) - lambda x Q₁]`, which is strictly less than the first mover's payoff for any positive first-mover sell volume Q₁.
- Mathematical Formulation: `PnL_loss(second mover) = Q₂ x lambda x Q₁` -- the loss from late action is proportional to first mover's volume times price impact.
- Empirical Evidence: Credit Suisse's $5.5B loss vs. Morgan Stanley's ~$1B loss in the Archegos event is consistent with a 3-5x penalty for delayed action when $35B in positions were being simultaneously unwound (Financial Times, April 6, 2021).
- Relevance to This Investor: PrimeBroker2's higher threshold (-0.15) vs PrimeBroker1 (-0.10) models the delayed reaction. The price at which PrimeBroker2 sells is already depressed by both ConcentratedFund's and PrimeBroker1's selling, replicating the empirical payoff differential.
- Parameter Calibration: liquidation_threshold = 0.15 (vs PrimeBroker1's 0.10); the 0.05 differential represents a 5% additional loss tolerance before action.

**Theory/Study 2: Institutional Inertia and Slow Risk Management Response**

- Citation: Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777-790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Core Insight: The disposition effect -- the tendency to hold losers too long -- is documented in both individual and institutional investors. Risk managers at slower-acting institutions may exhibit disposition-like reluctance to crystallize losses, delaying forced selling beyond the risk-optimal threshold.
- Mathematical Formulation: Disposition-adjusted threshold: `theta₂_effective = theta₂_optimal x (1 + d)`, where `d > 0` is the disposition effect delay factor.
- Empirical Evidence: Shefrin & Statman (1985) document the disposition effect across multiple asset classes; institutional manifestations include delayed margin call enforcement documented in post-crisis analyses.
- Relevance to This Investor: The higher threshold (-0.15 vs PrimeBroker1's -0.10) models institutional hesitation and slower response, even at greater financial cost.

#### 4.3.3 Design Purpose and Activation Scenarios

**Purpose**: Deepen the cascade trough by selling at worse prices than PrimeBroker1, completing the wave of prime broker liquidations and driving prices to their minimum before recovery.

| Market Condition  | PrimeBroker2 Response                            | Economic Effect                                                                    | Theory                                     |
|-------------------|--------------------------------------------------|------------------------------------------------------------------------------------|--------------------------------------------|
| deviation >= -0.15 | Hold (monitors situation)                        | Cascade not yet reached PrimeBroker2's trigger                                     | Second-mover waiting strategy              |
| deviation < -0.15 | Sell: `position x 0.35` (accepting worse prices) | Third large sell order at deeply discounted prices; pushes price to cascade trough | Section 4.3.2 Theory 1: second-mover disadvantage |

**Market Contribution**: Strongly Destabilizing. Deepens the cascade trough. Sells at prices 30-50% below initial levels (after ConcentratedFund and PrimeBroker1 have already sold), realizing the worst outcomes of the three liquidating agents.

#### 4.3.4 Behavioral Framework

##### 4.3.4.1 Mathematical Model

**Trigger Function**:
```
Trigger when: δ(t) < -theta₂  where theta₂ = 0.15
```

**Sizing Function**:
```
Q_sell = position(t) x φ₂  where φ₂ = 0.35 (slightly smaller than PrimeBroker1's 0.40 -- accepts partial liquidation)
Constraint: Q_sell <= position(t)
```

PrimeBroker2 accepts a price penalty representing the worse execution prices from delayed action. In the model, this is captured naturally through the price dynamics -- by the time PrimeBroker2 triggers, prices are already significantly lower.

#### 4.3.5 Decision Process Walkthrough

After PrimeBroker1's selling:
- Price: ~43.2 (from worked example above)
- Deviation: -0.568 -- far below both thresholds
- PrimeBroker2 triggers immediately in the same or next round

Q_sell = position x 0.35 = 1000 x 0.35 = 350 shares at ~$43.20
Market impact: DeltaP ≈ 0.03 x (-350) = -$10.50; P drops to ~$32.70
This represents a 67% decline from initial $100 -- consistent with Archegos-scale events (ViacomCBS fell 60%).

#### 4.3.6 Worked Numerical Example

```
P(t) = 43.15, δ = -0.569, position = 1000, theta₂ = 0.15, φ₂ = 0.35
Step 1: -0.569 < -0.15 -> True (triggered immediately after PrimeBroker1)
Step 2: Q_sell = 1000 x 0.35 = 350 shares
Step 3: Sell 350 @ $43.15
Market impact: DeltaP ≈ 0.03 x (-350) = -$10.50
P(t+1) ≈ 43.15 - 10.50 + 0.01x(100-43.15) = 43.15 - 10.50 + 0.569 = $33.22
δ(t+1) ≈ -0.668  -> minimum cascade point; triggers BlockTradeBuyer
```

#### 4.3.7 Academic References

| # | Full Citation                                                                                                                                                                                   | Contribution                                              |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| 1 | Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016                     | Second-mover payoff disadvantage; cascade amplification   |
| 2 | Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777-790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x | Institutional hesitation and delayed loss crystallization |

---

## Source Docstring Excerpts

### Rule / `PrimeBroker2`

```text
Delayed second-mover prime broker.

Theory: simulation-bases.md Section 4.3 -- PrimeBroker2
Theoretical basis: Creditor Run / Liquidation Race (Gorton & Metrick, 2012).
Higher threshold required before acting (waits longer than PrimeBroker1).
Faces worse prices due to first-mover's cascade selling pressure.
Effective price = market_price * price_penalty.
See simulation-bases.md Section 4.3.4.3 for mathematical model.
```

### LLM / `LLMPrimeBroker2`

```text
LLM-driven prime broker 2 -- delayed liquidator at worse prices. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMPrimeBroker2`

```text
RuleLLM prime broker 2 -- delayed liquidator at worse prices. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMPrimeBroker2`

```text
RAG-augmented prime broker 2 -- delayed liquidator at worse prices. Theory: simulation-bases.md Section 4.3.
```
