# RepresentativenessBias / Category Overgeneralizer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | RepresentativenessBias |
| Agent type | Category Overgeneralizer |
| Canonical class | `CategoryOvergeneralizer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A destabilizing investor that maps a small sample of recent price movement into a dramatic category such as "growth star" or "falling knife".

## Financial Theory / Theoretical Basis

### Rule / `CategoryOvergeneralizer`
- Theory: simulation-bases.md Section 4.2 -- CategoryOvergeneralizer
- Theoretical basis: base-rate neglect and small-sample extrapolation.

### LLM / `LLMCategoryOvergeneralizer`
- LLM-driven category generalizer -- small-sample extrapolation. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMCategoryOvergeneralizer`
- RuleLLM category generalizer -- rule-guided extrapolation. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMCategoryOvergeneralizer`
- RagLLM category generalizer -- small-sample extrapolation with retrieval. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`, `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| category_weight | Rule: `1.2` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.RepresentativenessBias.LLM.prompts:LLM_CATEGORY_OVERGENERALIZER_PROMPT', 'user_message': 'examples.RepresentativenessBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.RepresentativenessBias.RuleLLM.prompts:RULELLM_CATEGORY_OVERGENERALIZER_SYS', 'user_message': 'examples.RepresentativenessBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.RepresentativenessBias.Rag.prompts:RULELLM_CATEGORY_OVERGENERALIZER_SYS', 'user_message': 'examples.RepresentativenessBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sample_bias | Rule: `0.7` | Rule |
| sample_size | Rule: `2`<br>LLM: `2`<br>RuleLLM: `2`<br>Rag: `2` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | categoryovergeneralizer | CategoryOvergeneralizer | `CategoryOvergeneralizer` | 2 | `examples/RepresentativenessBias/Rule/players.py` |
| LLM | categoryovergeneralizer | CategoryOvergeneralizer | `LLMCategoryOvergeneralizer` | 2 | `examples/RepresentativenessBias/LLM/players.py` |
| RuleLLM | categoryovergeneralizer | CategoryOvergeneralizer | `RuleLLMCategoryOvergeneralizer` | 2 | `examples/RepresentativenessBias/RuleLLM/players.py` |
| Rag | categoryovergeneralizer | CategoryOvergeneralizer | `RagLLMCategoryOvergeneralizer` | 2 | `examples/RepresentativenessBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 CategoryOvergeneralizer

**Summary**: A destabilizing investor that maps a small sample of recent price
movement into a dramatic category such as "growth star" or "falling knife".

**Theoretical and Empirical Foundation**: Based on representativeness and
insensitivity to sample size in Tversky and Kahneman (1974) plus investor
sentiment regime switching in Barberis et al. (1998, doi:10.1016/S0304-405X(98)00027-0).

**Design Purpose and Activation Scenarios**: Activates on deviations above 2%
and reinforces the assigned category, generating overreaction from thin
evidence.

**Behavioral Framework**: `category_weight` controls category strength and
`sample_bias` controls overgeneralization from small samples. Quantity matches
the PatternMatcher formula to isolate the category narrative channel.

**Decision Process Walkthrough**: Read deviation, assign a positive or negative
category, trade in the category direction, and cap by cash or holdings.

**Worked Numerical Example**: A -3% deviation is classified as a falling-knife
category; quantity is `min(800, int(0.03 * 5000)) = 150`; the agent sells up to
150 shares.

**Academic References**: Tversky and Kahneman (1974); Barberis et al. (1998).

## Source Docstring Excerpts

### Rule / `CategoryOvergeneralizer`

```text
Overgeneralizes from small samples into dramatic stock categories.

Theory: simulation-bases.md Section 4.2 -- CategoryOvergeneralizer
Theoretical basis: base-rate neglect and small-sample extrapolation.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMCategoryOvergeneralizer`

```text
LLM-driven category generalizer -- small-sample extrapolation. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMCategoryOvergeneralizer`

```text
RuleLLM category generalizer -- rule-guided extrapolation. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMCategoryOvergeneralizer`

```text
RagLLM category generalizer -- small-sample extrapolation with retrieval. Theory: simulation-bases.md Section 4.2.
```
