# DispositionEffect / Tax Aware Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Tax Aware Investor |
| Canonical class | `TaxAwareInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM |

## Definition and Goal

`TaxAwareInvestor` deliberately reverses the disposition effect by realizing losses for tax benefits and deferring gains.

## Financial Theory / Theoretical Basis

### Rule / `TaxAwareInvestor`
- Opposite of disposition effect for tax optimization:
- - Sells losers to harvest tax losses
- - Holds winners to defer capital gains tax
- Theory: simulation-bases.md Section 4.3 -- TaxAwareInvestor
- Theoretical basis: Constantinides (1983) tax-loss harvesting; anti-disposition via economic incentive.

### LLM / `LLMTaxAwareInvestor`
- LLM-driven tax-aware investor -- harvests losses, defers gains for tax optimization. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMTaxAwareInvestor`
- Hybrid rule+LLM tax-aware investor -- tax-loss harvesting rules embedded. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `_hold_order`, `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| capital_gains_hold | Rule: `0.2`<br>RuleLLM: `0.2` | Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3` | LLM, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0` | LLM, Rule, RuleLLM |
| initial_position | Rule: `30.0`<br>LLM: `0.0`<br>RuleLLM: `50.0` | LLM, Rule, RuleLLM |
| initial_purchase_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0` | LLM, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DispositionEffect.LLM.prompts:LLM_TAX_AWARE_SYS', 'user_message': 'examples.DispositionEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_TAX_AWARE_SYS', 'user_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM, RuleLLM |
| tax_harvest_fraction | Rule: `0.5`<br>RuleLLM: `0.5` | Rule, RuleLLM |
| tax_loss_threshold | Rule: `-0.05`<br>RuleLLM: `-0.05` | Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | tax_aware_investor | Tax Aware Investor | `TaxAwareInvestor` | 2 | `examples/DispositionEffect/Rule/players.py` |
| LLM | llm_tax_aware | LLM Tax-Aware Investor | `LLMTaxAwareInvestor` | 2 | `examples/DispositionEffect/LLM/players.py` |
| RuleLLM | rulellm_tax_aware | RuleLLM Tax Aware Investor | `RuleLLMTaxAwareInvestor` | 2 | `examples/DispositionEffect/RuleLLM/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 TaxAwareInvestor

#### Section 4.3.1 Summary

`TaxAwareInvestor` deliberately reverses the disposition effect by realizing losses for tax benefits and deferring gains.

#### Section 4.3.2 Theoretical and Empirical Foundation

The design follows Constantinides (1983) on optimal tax-loss trading and Odean's observation that loss realization rises in December when tax motives dominate psychology.

#### Section 4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `gain_loss <= tax_loss_threshold` | sell loser | harvests tax loss and increases PLR | Tax-loss harvesting |
| `gain_loss >= capital_gains_hold` | hold winner | defers capital gains tax | Tax optimization |
| otherwise | hold | no tax trigger | Transaction discipline |

#### Section 4.3.4 Behavioral Framework

```python
if gain_loss <= tax_loss_threshold:
    quantity = -position * tax_harvest_fraction
elif gain_loss >= capital_gains_hold:
    quantity = 0
else:
    quantity = 0
```

#### Section 4.3.5 Decision Process Walkthrough

At a 5% loss, the investor sells part of the position to realize a tax loss. At a 15% gain, it avoids selling to defer taxes.

#### Section 4.3.6 Worked Numerical Example

With `position = 30`, `price = 95`, `purchase_price = 100`, and `tax_harvest_fraction = 0.5`, the tax-aware sell order is `-15` shares.

#### Section 4.3.7 Academic References

Constantinides (1983); Odean (1998).

---

## Source Docstring Excerpts

### Rule / `TaxAwareInvestor`

```text
Tax-Aware Investor.

Opposite of disposition effect for tax optimization:
- Sells losers to harvest tax losses
- Holds winners to defer capital gains tax

Parameters from config extras:
    - tax_loss_threshold, capital_gains_hold, tax_harvest_fraction

Theory: simulation-bases.md Section 4.3 -- TaxAwareInvestor
Theoretical basis: Constantinides (1983) tax-loss harvesting; anti-disposition via economic incentive.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMTaxAwareInvestor`

```text
LLM-driven tax-aware investor -- harvests losses, defers gains for tax optimization. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMTaxAwareInvestor`

```text
Hybrid rule+LLM tax-aware investor -- tax-loss harvesting rules embedded. Theory: simulation-bases.md Section 4.3.
```
