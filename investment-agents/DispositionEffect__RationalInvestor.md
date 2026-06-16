# DispositionEffect / Rational Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Rational Investor |
| Canonical class | `RationalInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM |

## Definition and Goal

`RationalInvestor` is the expected-utility benchmark. It ignores purchase-price anchoring and rebalances toward a target equity allocation.

## Financial Theory / Theoretical Basis

### Rule / `RationalInvestor`
- NOT affected by sunk costs or reference points.
- Theory: simulation-bases.md Section 4.2 -- RationalInvestor
- Theoretical basis: Expected Utility Theory (von Neumann & Morgenstern, 1944); ignores purchase price.

### LLM / `LLMRationalInvestor`
- LLM-driven rational investor -- trades on fundamentals, ignores reference point. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMRationalInvestor`
- Hybrid rule+LLM rational investor -- rebalancing rules embedded, no reference point. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `_hold_order`, `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3` | LLM, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0` | LLM, Rule, RuleLLM |
| initial_position | Rule: `30.0`<br>LLM: `0.0`<br>RuleLLM: `50.0` | LLM, Rule, RuleLLM |
| initial_purchase_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0` | LLM, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DispositionEffect.LLM.prompts:LLM_RATIONAL_SYS', 'user_message': 'examples.DispositionEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_RATIONAL_SYS', 'user_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM, RuleLLM |
| rebalance_threshold | Rule: `0.1`<br>RuleLLM: `0.1` | Rule, RuleLLM |
| target_allocation | Rule: `0.5`<br>RuleLLM: `0.5` | Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | rational_investor | Rational Investor | `RationalInvestor` | 2 | `examples/DispositionEffect/Rule/players.py` |
| LLM | llm_rational | LLM Rational Investor | `LLMRationalInvestor` | 2 | `examples/DispositionEffect/LLM/players.py` |
| RuleLLM | rulellm_rational | RuleLLM Rational Investor | `RuleLLMRationalInvestor` | 2 | `examples/DispositionEffect/RuleLLM/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 RationalInvestor

#### Section 4.2.1 Summary

`RationalInvestor` is the expected-utility benchmark. It ignores purchase-price anchoring and rebalances toward a target equity allocation.

#### Section 4.2.2 Theoretical and Empirical Foundation

The agent represents von Neumann-Morgenstern expected utility and standard portfolio rebalancing. It provides the non-behavioral comparison required to measure disposition-effect performance drag.

#### Section 4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| allocation above target band | sell | trims overweight exposure | Expected utility |
| allocation below target band | buy | restores target exposure | Portfolio rebalancing |
| allocation within band | hold | avoids unnecessary trading | Transaction discipline |

#### Section 4.2.4 Behavioral Framework

```python
equity_value = position * price
total_value = cash + equity_value
current_alloc = equity_value / total_value
if abs(current_alloc - target_allocation) > rebalance_threshold:
    quantity = (target_position - position) * 0.5
else:
    quantity = 0
```

#### Section 4.2.5 Decision Process Walkthrough

If the stock position rises above the 50% target by more than 10 percentage points, the investor sells part of the position. If it falls below the lower band, it buys.

#### Section 4.2.6 Worked Numerical Example

With `cash = 10000`, `position = 30`, and `price = 100`, equity value is 3000 and allocation is 23.1%. The investor buys toward the 50% target.

#### Section 4.2.7 Academic References

Von Neumann & Morgenstern (1944); Markowitz portfolio-selection tradition.

---

## Source Docstring Excerpts

### Rule / `RationalInvestor`

```text
Rational Investor (Baseline).

Makes decisions based on expected future returns,
NOT affected by sunk costs or reference points.

Parameters from config extras:
    - target_allocation, rebalance_threshold

Theory: simulation-bases.md Section 4.2 -- RationalInvestor
Theoretical basis: Expected Utility Theory (von Neumann & Morgenstern, 1944); ignores purchase price.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMRationalInvestor`

```text
LLM-driven rational investor -- trades on fundamentals, ignores reference point. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMRationalInvestor`

```text
Hybrid rule+LLM rational investor -- rebalancing rules embedded, no reference point. Theory: simulation-bases.md Section 4.2.
```
