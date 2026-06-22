# DispositionEffect / Institutional Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Institutional Investor |
| Canonical class | `InstitutionalInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM |

## Definition and Goal

`InstitutionalInvestor` is the professional active manager. It still tracks position outcomes, but uses symmetric sell discipline rather than asymmetric retail loss aversion.

## Financial Theory / Theoretical Basis

### Rule / `InstitutionalInvestor`
- Professional money managers show weaker disposition effect
- Theory: simulation-bases.md Section 4.5 -- InstitutionalInvestor
- Theoretical basis: Shapira & Venezia (2001) professional discipline; symmetric thresholds reduce disposition bias.

### LLM / `LLMInstitutionalInvestor`
- LLM-driven institutional investor -- professional symmetric thresholds, weak disposition. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMInstitutionalInvestor`
- Hybrid rule+LLM institutional investor -- symmetric gain/loss rules embedded. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `_hold_order`, `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3` | LLM, Rule, RuleLLM |
| gain_threshold | Rule: `0.25`<br>RuleLLM: `0.25` | Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0` | LLM, Rule, RuleLLM |
| initial_position | Rule: `30.0`<br>LLM: `0.0`<br>RuleLLM: `50.0` | LLM, Rule, RuleLLM |
| initial_purchase_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0` | LLM, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.DispositionEffect.LLM.prompts:LLM_INSTITUTIONAL_SYS', 'user_message': 'examples.DispositionEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_INSTITUTIONAL_SYS', 'user_message': 'examples.DispositionEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM, RuleLLM |
| loss_threshold | Rule: `-0.15`<br>RuleLLM: `-0.15` | Rule, RuleLLM |
| sell_fraction | Rule: `0.4`<br>RuleLLM: `0.4` | Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | institutional_investor | Institutional Investor | `InstitutionalInvestor` | 1 | `examples/DispositionEffect/Rule/players.py` |
| LLM | llm_institutional | LLM Institutional Investor | `LLMInstitutionalInvestor` | 2 | `examples/DispositionEffect/LLM/players.py` |
| RuleLLM | rulellm_institutional | RuleLLM Institutional Investor | `RuleLLMInstitutionalInvestor` | 2 | `examples/DispositionEffect/RuleLLM/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 InstitutionalInvestor

#### Section 4.5.1 Summary

`InstitutionalInvestor` is the professional active manager. It still tracks position outcomes, but uses symmetric sell discipline rather than asymmetric retail loss aversion.

#### Section 4.5.2 Theoretical and Empirical Foundation

The design follows Shapira and Venezia (2001), who show that professional investors exhibit weaker disposition effects than individual retail investors because of process discipline and oversight.

#### Section 4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `gain_loss >= gain_threshold` | sell | disciplined profit taking | Professional risk management |
| `gain_loss <= loss_threshold` | sell | symmetric loss cutting | Fiduciary discipline |
| otherwise | hold | no threshold breach | Trading discipline |

#### Section 4.5.4 Behavioral Framework

```python
if gain_loss >= gain_threshold:
    quantity = -position * sell_fraction
elif gain_loss <= loss_threshold:
    quantity = -position * sell_fraction
else:
    quantity = 0
```

#### Section 4.5.5 Decision Process Walkthrough

Unlike the retail disposition investor, the institutional investor sells the same fraction after a large gain or a large loss. This weakens PGR/PLR asymmetry.

#### Section 4.5.6 Worked Numerical Example

With `position = 30`, `sell_fraction = 0.4`, and `gain_loss = 25%`, the sell order is `-12` shares. At `gain_loss = -15%`, the sell order is also `-12` shares.

#### Section 4.5.7 Academic References

Shapira & Venezia (2001); institutional discipline literature.

---

## Source Docstring Excerpts

### Rule / `InstitutionalInvestor`

```text
Institutional Investor.

Professional money managers show weaker disposition effect
due to training, oversight, and fiduciary duty.

Parameters from config extras:
    - gain_threshold, loss_threshold, sell_fraction

Theory: simulation-bases.md Section 4.5 -- InstitutionalInvestor
Theoretical basis: Shapira & Venezia (2001) professional discipline; symmetric thresholds reduce disposition bias.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMInstitutionalInvestor`

```text
LLM-driven institutional investor -- professional symmetric thresholds, weak disposition. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMInstitutionalInvestor`

```text
Hybrid rule+LLM institutional investor -- symmetric gain/loss rules embedded. Theory: simulation-bases.md Section 4.5.
```
