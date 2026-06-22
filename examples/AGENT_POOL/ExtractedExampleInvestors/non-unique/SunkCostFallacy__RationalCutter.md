# SunkCostFallacy / Rational Cutter

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SunkCostFallacy |
| Agent type | Rational Cutter |
| Canonical class | `RationalCutter` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

This investor represents forward-looking agents who ignore past costs and act on valuation.

## Financial Theory / Theoretical Basis

### Rule / `RationalCutter`
- Theory: simulation-bases.md Section 4.3 -- RationalCutter
- Theoretical basis: forward-looking rationality.

### LLM / `LLMRationalCutter`
- LLM rational cutter ignoring sunk costs and cutting losses. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMRationalCutter`
- RuleLLM rational cutter ignoring sunk costs and cutting losses. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMRationalCutter`
- RagLLM rational cutter ignoring sunk costs and cutting losses. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| cut_threshold | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_RATIONAL_CUTTER_SYS', 'user_message': 'examples.SunkCostFallacy.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_RATIONAL_CUTTER_SYS', 'user_message': 'examples.SunkCostFallacy.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SunkCostFallacy.Rag.prompts:RAGLLM_RATIONAL_CUTTER_SYS', 'user_message': 'examples.SunkCostFallacy.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | rationalcutter | RationalCutter | `RationalCutter` | 2 | `examples/SunkCostFallacy/Rule/players.py` |
| LLM | rationalcutter | RationalCutter | `LLMRationalCutter` | 2 | `examples/SunkCostFallacy/LLM/players.py` |
| RuleLLM | rationalcutter | RationalCutter | `RuleLLMRationalCutter` | 2 | `examples/SunkCostFallacy/RuleLLM/players.py` |
| Rag | rationalcutter | RationalCutter | `RagLLMRationalCutter` | 2 | `examples/SunkCostFallacy/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 RationalCutter

#### Section 4.3.1 Summary

This investor represents forward-looking agents who ignore past costs and act
on valuation.

It provides the benchmark that separates economically justified trades from
commitment-driven trades.

#### Section 4.3.2 Theoretical and Empirical Foundation

Portfolio-choice theory implies that irreversible costs are irrelevant to
current allocation. Expected future value, not psychological commitment,
determines trade direction.

#### Section 4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < -cut_threshold` | Buy | Treats undervaluation as opportunity | Section 2.4 |
| `deviation > cut_threshold` | Sell | Reduces overvalued exposure | Section 2.4 |
| Small deviation | Hold | Avoids noise churn | Section 2.4 |

#### Section 4.3.4 Behavioral Framework

The agent uses `cut_threshold` and `position_size`. It is not emotionally
attached to prior entry price.

#### Section 4.3.5 Decision Process Walkthrough

At price 94 and fundamental 100, the agent buys because the asset is
undervalued, regardless of whether the current position is losing relative to
entry.

#### Section 4.3.6 Worked Numerical Example

```text
P=94, F=100, deviation=-0.06, cut_threshold=0.05
Q = position_size * |deviation| / cut_threshold = 350 * 1.2 = 420 shares
```

#### Section 4.3.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Markowitz (1952), https://doi.org/10.1111/j.1540-6261.1952.tb01525.x | Forward-looking allocation benchmark. |
| 2 | Thaler (1980), https://doi.org/10.1016/0167-2681(80)90051-7 | Contrast with mental accounting. |

## Source Docstring Excerpts

### Rule / `RationalCutter`

```text
Cuts losses based on forward-looking assessment, ignores past investment.

Theory: simulation-bases.md Section 4.3 -- RationalCutter
Theoretical basis: forward-looking rationality.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMRationalCutter`

```text
LLM rational cutter ignoring sunk costs and cutting losses. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMRationalCutter`

```text
RuleLLM rational cutter ignoring sunk costs and cutting losses. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMRationalCutter`

```text
RagLLM rational cutter ignoring sunk costs and cutting losses. Theory: simulation-bases.md Section 4.3.
```
