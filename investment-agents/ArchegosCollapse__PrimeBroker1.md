# ArchegosCollapse / Prime Broker 1

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ArchegosCollapse |
| Agent type | Prime Broker 1 |
| Canonical class | `PrimeBroker1` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`PrimeBroker1` represents the first-acting prime broker -- the counterparty that liquidates ahead of competitors, obtaining better prices. In the Archegos event, Morgan Stanley acted earliest (March 25-26) among the major prime brokers. PrimeBroker1 models the financially rational response to a creditor run: first-mover advantage means acting at threshold -0.10 (a less severe decline) rather than waiting for the more conservative threshold. This investor is the second link in the cascade chain: its large sell order, coming at prices still above PrimeBroker2's eventual selling price, amplifies the initial ConcentratedFund shock and pushes prices toward PrimeBroker2's trigger.

## Financial Theory / Theoretical Basis

### Rule / `PrimeBroker1`
- Theory: simulation-bases.md Section 4.2 -- PrimeBroker1
- Theoretical basis: Creditor Run / Liquidation Race (Gorton & Metrick, 2012).

### LLM / `LLMPrimeBroker1`
- LLM-driven prime broker 1 -- first-mover liquidator. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMPrimeBroker1`
- RuleLLM prime broker 1 -- first-mover liquidator. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMPrimeBroker1`
- RAG-augmented prime broker 1 -- first-mover liquidator. Theory: simulation-bases.md Section 4.2.

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
| initial_position | Rule: `4000.0`<br>LLM: `4000.0`<br>RuleLLM: `4000.0`<br>Rag: `4000.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| liquidation_sell_ratio | Rule: `0.4` | Rule |
| liquidation_threshold | Rule: `-0.1` | Rule |
| llm | LLM: `{'sys_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_PRIME_BROKER1_SYS', 'user_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_PRIME_BROKER1_SYS', 'user_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_PRIME_BROKER1_SYS', 'user_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | prime_broker1 | Prime Broker 1 | `PrimeBroker1` | 1 | `examples/ArchegosCollapse/Rule/players.py` |
| LLM | prime_broker1 | Prime Broker 1 | `LLMPrimeBroker1` | 1 | `examples/ArchegosCollapse/LLM/players.py` |
| RuleLLM | prime_broker1 | Prime Broker 1 | `RuleLLMPrimeBroker1` | 1 | `examples/ArchegosCollapse/RuleLLM/players.py` |
| Rag | ragllm_prime_broker1 | RAG Prime Broker 1 | `RagLLMPrimeBroker1` | 1 | `examples/ArchegosCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 PrimeBroker1

#### 4.2.1 Summary

`PrimeBroker1` represents the first-acting prime broker -- the counterparty that liquidates ahead of competitors, obtaining better prices. In the Archegos event, Morgan Stanley acted earliest (March 25-26) among the major prime brokers. PrimeBroker1 models the financially rational response to a creditor run: first-mover advantage means acting at threshold -0.10 (a less severe decline) rather than waiting for the more conservative threshold. This investor is the second link in the cascade chain: its large sell order, coming at prices still above PrimeBroker2's eventual selling price, amplifies the initial ConcentratedFund shock and pushes prices toward PrimeBroker2's trigger.

#### 4.2.2 Theoretical and Empirical Foundation

**Theory/Study 1: Creditor Run and First-Mover Advantage**

- Citation: Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016
- Core Insight: The first creditor to liquidate collateral captures the highest price (before mass liquidation depresses value). This creates a dominant strategy equilibrium: all creditors prefer to liquidate first, producing a coordination failure that amplifies the borrower's distress into a system-wide run.
- Mathematical Formulation: First-mover payoff premium = `Q x [P(t₁) - P(t₂)] = Q x lambda x Q₁ > 0`, where Q₁ is first-mover sell volume and t₂ > t₁. This premium is always positive, making early liquidation dominant regardless of Q₁.
- Empirical Evidence: Gorton & Metrick (2012) document that repo creditors begin running when haircuts rise above 5-10%, well before borrower insolvency. In Archegos, Morgan Stanley's early action allowed it to limit losses to ~$1B versus Credit Suisse's $5.5B (Financial Times, April 2021 analysis).
- Relevance to This Investor: PrimeBroker1's threshold (-0.10) is set lower than PrimeBroker2's (-0.15) to capture the first-mover decision: it accepts acting at moderate distress rather than waiting for confirmed crisis.
- Parameter Calibration: liquidation_threshold = 0.10 reflects the 10% decline that typically prompts prime broker risk committees to initiate forced close-out; liquidation_fraction = 0.40 (slightly less than ConcentratedFund) reflects broker position size constraints.

**Theory/Study 2: Risk-Averse Institutional Decision-Making Under Uncertainty**

- Citation: Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291. https://doi.org/10.2307/1914185
- Core Insight: Loss aversion causes decision-makers to weight potential losses more heavily than equivalent gains. Institutional risk managers exhibit strong loss aversion: a 15% recovery in prices is valued far less than avoiding an additional 15% decline. This asymmetry explains why prime brokers act decisively to cut losses rather than waiting for recovery.
- Mathematical Formulation: Loss aversion utility: `U(x) = x^alpha for x > 0; -lambda x (-x)^β for x < 0`, with lambda ≈ 2.25, alpha = β ≈ 0.88 (Tversky & Kahneman, 1992).
- Empirical Evidence: Loss aversion coefficient lambda ≈ 2.25 is documented across multiple experimental studies (Tversky & Kahneman, 1992, *Journal of Risk and Uncertainty*, 5(4), 297-323). In institutional settings, risk management guidelines typically enforce stop-loss rules at 10-15% loss thresholds.
- Relevance to This Investor: The low threshold (-0.10) reflects institutional risk management stop-loss rules grounded in loss aversion; PrimeBroker1 would rather realize a certain 10% loss than risk a worse outcome by waiting.

#### 4.2.3 Design Purpose and Activation Scenarios

**Purpose**: Amplify the initial ConcentratedFund shock by adding a second large sell order at relatively good prices, driving prices further down toward PrimeBroker2's trigger.

| Market Condition                       | PrimeBroker1 Response   | Economic Effect                                                              | Theory                                           |
|----------------------------------------|-------------------------|------------------------------------------------------------------------------|--------------------------------------------------|
| deviation >= -0.10                      | Hold; monitoring        | No amplification; creditor run has not started                               | Section 4.2.2 below risk threshold                      |
| deviation < -0.10 (first-mover window) | Sell: `position x 0.40` | Second large sell order at moderate price; pushes deviation well below -0.15 | Section 4.2.2 Theory 1: first-mover advantage dominates |

**Market Contribution**: Strongly Destabilizing. PrimeBroker1's 0.40 x position sell order (typically 400-800 shares) adds -400 to -800 net demand. Combined with ConcentratedFund's prior selling, this depresses prices into PrimeBroker2's threshold range.

**Interaction Effects**: PrimeBroker1 acts AFTER ConcentratedFund's selling (which creates the -0.10 deviation crossing) but BEFORE PrimeBroker2 (whose threshold is -0.15). PrimeBroker1 and ConcentratedFund are the key cascade initiators; PrimeBroker2 deepens the trough.

#### 4.2.4 Behavioral Framework

##### 4.2.4.1 Decision Information Set

| Signal        | Usedtheta    | Rationale                                                                                  |
|---------------|----------|--------------------------------------------------------------------------------------------|
| `deviation`   | Yes      | Primary risk signal: monitors loss relative to fundamental as margin quality proxy         |
| `price`       | Yes      | Used for order pricing                                                                     |
| `prev_price`  | No       | Threshold-based decision, not change-based                                                 |
| `fundamental` | Implicit | Via deviation only; PrimeBroker1 monitors counterparty collateral quality, not asset value |

##### 4.2.4.2 Core Behavioral Mechanism

PrimeBroker1 is the institutional risk manager who decided to act early rather than risk a worse outcome from waiting. In normal rounds (deviation above -0.10), it holds its collateral and monitors. Once deviation crosses -0.10, its risk management protocol triggers an automatic liquidation order.

The sell size (40% of position) is chosen to significantly reduce exposure in one action while not creating a catastrophic position mismatch. The prime broker's position is held as collateral against the fund's TRS exposure -- it is not a directional bet, but a risk management tool.

After selling, PrimeBroker1 does not re-enter; its holding represents collateral that has been liquidated to close the TRS contracts.

##### 4.2.4.3 Mathematical Model

**Trigger Function**:
```
Trigger when: δ(t) < -theta₁  where theta₁ = liquidation_threshold = 0.10
```

**Sizing Function**:
```
Q_sell = position(t) x φ₁  where φ₁ = liquidation_fraction = 0.40
Constraint: Q_sell <= position(t)
```

**Parameter Definitions**:
| Symbol | Meaning                              | Config Path                  | Value | Source                                                            |
|--------|--------------------------------------|------------------------------|-------|-------------------------------------------------------------------|
| theta₁     | First-mover liquidation threshold    | extras.liquidation_threshold | 0.10  | Gorton & Metrick (2012); prime broker risk management conventions |
| φ₁     | Fraction of collateral position sold | extras.liquidation_fraction  | 0.40  | Standard prime broker collateral liquidation protocol             |

#### 4.2.5 Decision Process Walkthrough

**Example Market State** (round after ConcentratedFund sells):
- Price: 54.7 (after ConcentratedFund's selling)
- Fundamental: 100.0
- Deviation: (54.7 - 100) / 100 = -0.453 -- well below -0.10 threshold
- Position: 1000 shares (collateral held against ConcentratedFund TRS)

Step 1: Observe δ = -0.453 < -0.10 -> trigger
Step 2: Q_sell = 1000 x 0.40 = 400 shares
Step 3: Submit order: sell 400 shares at $54.70
Step 4: Market impact: DeltaP ≈ 0.03 x (-400) = -$12.00; New P ≈ $42.70; New δ ≈ -0.573

#### 4.2.6 Worked Numerical Example

```
P(t) = 54.7, δ = -0.453, position = 1000, theta₁ = 0.10, φ₁ = 0.40
Step 1: -0.453 < -0.10 -> True
Step 2: Q_sell = 1000 x 0.40 = 400 shares
Step 3: Sell 400 @ $54.70
Market impact: D = -400; DeltaP_demand = 0.03 x (-400) = -$12.00
P(t+1) ≈ 54.7 - 12.0 + 0.01x(100-54.7) = 54.7 - 12.0 + 0.453 = $43.15
δ(t+1) ≈ (43.15 - 100) / 100 = -0.569
```
This deepens deviation well beyond PrimeBroker2's threshold (-0.15), ensuring cascade continuation.

#### 4.2.7 Academic References

| # | Full Citation                                                                                                                                                                                   | Contribution                                            |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| 1 | Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016                     | Creditor run theory; first-mover liquidation advantage  |
| 2 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291. https://doi.org/10.2307/1914185                                        | Loss aversion basis for early risk management threshold |
| 3 | Tversky, A., & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297-323. https://doi.org/10.1007/BF00122574 | Quantitative loss aversion coefficient lambda ≈ 2.25         |

---

## Source Docstring Excerpts

### Rule / `PrimeBroker1`

```text
First-mover prime broker liquidator.

Theory: simulation-bases.md Section 4.2 -- PrimeBroker1
Theoretical basis: Creditor Run / Liquidation Race (Gorton & Metrick, 2012).
Acts when price drops below liquidation_threshold.
Sells liquidation_sell_ratio * position per round at market price.
First-mover advantage: receives full market price (no price_penalty).
See simulation-bases.md Section 4.2.4.3 for mathematical model.
```

### LLM / `LLMPrimeBroker1`

```text
LLM-driven prime broker 1 -- first-mover liquidator. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMPrimeBroker1`

```text
RuleLLM prime broker 1 -- first-mover liquidator. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMPrimeBroker1`

```text
RAG-augmented prime broker 1 -- first-mover liquidator. Theory: simulation-bases.md Section 4.2.
```
