# MentalAccounting / Mental Accountant

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MentalAccounting |
| Agent type | Mental Accountant |
| Canonical class | `MentalAccountant` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

1. **Summary**: Segregates current holdings into separate mental accounts and evaluates each account relative to entry price. This creates local realization behavior that can diverge from total-portfolio optimization. 2. **Theoretical and Empirical Foundation**: Thaler (1999) explains account coding; Odean (1998) and Shefrin & Statman (1985) document account-level realization patterns. 3. **Design Purpose and Activation Scenarios**: Activates when account-level P&L crosses gain or loss thresholds. 4. **Behavioral Framework**: Uses `num_accounts`, `loss_aversion_per_account`, current `position`, and `entry_price`. 5. **Decision Process Walkthrough**: Compute account P&L; sell 70% of one account after gains above 5%; reluctantly sell 20% of one account after loss threshold; otherwise hold. 6. **Worked Numerical Example**: With `position=600`, `num_accounts=3`, and `pnl=+8%`, per-account position is 200 and sell quantity is 140. 7. **Academic References**: Thaler (1985, 1999); Odean (1998); Shefrin & Statman (1985).

## Financial Theory / Theoretical Basis

### Rule / `MentalAccountant`
- Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant

### LLM / `LLMMentalAccountant`
- Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant.

### RuleLLM / `RuleLLMMentalAccountant`
- Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant.

### Rag / `RagLLMMentalAccountant`
- Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MentalAccounting.LLM.prompts:LLM_MENTAL_ACCOUNTANT_PROMPT', 'user_message': 'examples.MentalAccounting.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_MENTAL_ACCOUNTANT_SYS', 'user_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.MentalAccounting.Rag.prompts:RULELLM_MENTAL_ACCOUNTANT_SYS', 'user_message': 'examples.MentalAccounting.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| loss_aversion_per_account | Rule: `2.25`<br>LLM: `2.25`<br>RuleLLM: `2.25`<br>Rag: `2.25` | LLM, Rag, Rule, RuleLLM |
| num_accounts | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | mentalaccountant | MentalAccountant | `MentalAccountant` | 2 | `examples/MentalAccounting/Rule/players.py` |
| LLM | mentalaccountant | MentalAccountant | `LLMMentalAccountant` | 2 | `examples/MentalAccounting/LLM/players.py` |
| RuleLLM | mentalaccountant | MentalAccountant | `RuleLLMMentalAccountant` | 2 | `examples/MentalAccounting/RuleLLM/players.py` |
| Rag | mentalaccountant | MentalAccountant | `RagLLMMentalAccountant` | 2 | `examples/MentalAccounting/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 MentalAccountant

1. **Summary**: Segregates current holdings into separate mental accounts and evaluates each account relative to entry price. This creates local realization behavior that can diverge from total-portfolio optimization.
2. **Theoretical and Empirical Foundation**: Thaler (1999) explains account coding; Odean (1998) and Shefrin & Statman (1985) document account-level realization patterns.
3. **Design Purpose and Activation Scenarios**: Activates when account-level P&L crosses gain or loss thresholds.
4. **Behavioral Framework**: Uses `num_accounts`, `loss_aversion_per_account`, current `position`, and `entry_price`.
5. **Decision Process Walkthrough**: Compute account P&L; sell 70% of one account after gains above 5%; reluctantly sell 20% of one account after loss threshold; otherwise hold.
6. **Worked Numerical Example**: With `position=600`, `num_accounts=3`, and `pnl=+8%`, per-account position is 200 and sell quantity is 140.
7. **Academic References**: Thaler (1985, 1999); Odean (1998); Shefrin & Statman (1985).

## Source Docstring Excerpts

### Rule / `MentalAccountant`

```text
Segregates portfolio into separate accounts, doesn't net gains/losses.

Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant
Strategy specification: simulation-bases.md Section 4.1.4 -- Behavioral Framework
Parameters: simulation-bases.md Section 6

Parameters from config extras:
    - num_accounts, loss_aversion_per_account
```

### LLM / `LLMMentalAccountant`

```text
LLM-driven MentalAccountant.

Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant.
Strategy specification: simulation-bases.md Section 4.1.4.
```

### RuleLLM / `RuleLLMMentalAccountant`

```text
Hybrid: MentalAccountant rules + LLM reasoning.

Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant.
Strategy specification: simulation-bases.md Section 4.1.4.
```

### Rag / `RagLLMMentalAccountant`

```text
RAG-augmented: MentalAccountant rules + LLM + retrieved knowledge.

Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant.
Strategy specification: simulation-bases.md Section 4.1.4.
```
