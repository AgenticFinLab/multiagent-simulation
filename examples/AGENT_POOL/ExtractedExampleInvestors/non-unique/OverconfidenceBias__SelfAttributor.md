# OverconfidenceBias / Self Attributor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | OverconfidenceBias |
| Agent type | Self Attributor |
| Canonical class | `SelfAttributor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

1. **Summary**: SelfAttributor raises confidence after favorable conditions and discounts negative evidence. It creates path-dependent risk taking. 2. **Theoretical and Empirical Foundation**: Biased self-attribution in Daniel et al. (1998) and Gervais and Odean (2001, DOI `10.1093/rfs/14.1.1`) motivates the role. 3. **Design Purpose and Activation Scenarios**: Activates when an existing position and positive deviation make success feel skill-based, or when losses trigger exposure trimming. 4. **Behavioral Framework**: Positive deviation with inventory increases buy size by `confidence_boost`; negative deviation beyond a threshold can trigger a sell. 5. **Decision Process Walkthrough**: Observe current inventory, read deviation, apply confidence boost or loss trim, then cap order by cash/inventory. 6. **Worked Numerical Example**: With `base_size = 400` and `confidence_boost = 0.5`, a positive state can request `600` shares before cash constraints. 7. **Academic References**: Daniel et al. (1998), Gervais and Odean (2001).

## Financial Theory / Theoretical Basis

### Rule / `SelfAttributor`
- Theoretical basis: simulation-bases.md Section 4.2 -- SelfAttributor.

### LLM / `LLMSelfAttributor`
- Theoretical basis: simulation-bases.md Section 4.2 -- SelfAttributor.

### RuleLLM / `RuleLLMSelfAttributor`
- Theoretical basis: simulation-bases.md Section 4.2 -- SelfAttributor.

### Rag / `RagLLMSelfAttributor`
- Theoretical basis: simulation-bases.md Section 4.2 -- SelfAttributor.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| confidence_boost | Rule: `0.5`<br>LLM: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.OverconfidenceBias.LLM.prompts:LLM_SELF_ATTRIBUTOR_PROMPT', 'user_message': 'examples.OverconfidenceBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.OverconfidenceBias.RuleLLM.prompts:RULELLM_SELF_ATTRIBUTOR_SYS', 'user_message': 'examples.OverconfidenceBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.OverconfidenceBias.Rag.prompts:RULELLM_SELF_ATTRIBUTOR_SYS', 'user_message': 'examples.OverconfidenceBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | selfattributor | SelfAttributor | `SelfAttributor` | 2 | `examples/OverconfidenceBias/Rule/players.py` |
| LLM | selfattributor | SelfAttributor | `LLMSelfAttributor` | 2 | `examples/OverconfidenceBias/LLM/players.py` |
| RuleLLM | selfattributor | SelfAttributor | `RuleLLMSelfAttributor` | 2 | `examples/OverconfidenceBias/RuleLLM/players.py` |
| Rag | selfattributor | SelfAttributor | `RagLLMSelfAttributor` | 2 | `examples/OverconfidenceBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 SelfAttributor

1. **Summary**: SelfAttributor raises confidence after favorable conditions and
discounts negative evidence. It creates path-dependent risk taking.
2. **Theoretical and Empirical Foundation**: Biased self-attribution in Daniel
et al. (1998) and Gervais and Odean (2001, DOI `10.1093/rfs/14.1.1`) motivates
the role.
3. **Design Purpose and Activation Scenarios**: Activates when an existing
position and positive deviation make success feel skill-based, or when losses
trigger exposure trimming.
4. **Behavioral Framework**: Positive deviation with inventory increases buy
size by `confidence_boost`; negative deviation beyond a threshold can trigger a
sell.
5. **Decision Process Walkthrough**: Observe current inventory, read deviation,
apply confidence boost or loss trim, then cap order by cash/inventory.
6. **Worked Numerical Example**: With `base_size = 400` and
`confidence_boost = 0.5`, a positive state can request `600` shares before cash
constraints.
7. **Academic References**: Daniel et al. (1998), Gervais and Odean (2001).

## Source Docstring Excerpts

### Rule / `SelfAttributor`

```text
Attributes success to skill, failure to bad luck.

Theoretical basis: simulation-bases.md Section 4.2 -- SelfAttributor.
Strategy specification: simulation-bases.md Section 4.2.4.
```

### LLM / `LLMSelfAttributor`

```text
LLM-driven SelfAttributor.

Theoretical basis: simulation-bases.md Section 4.2 -- SelfAttributor.
Strategy specification: simulation-bases.md Section 4.2.4.
```

### RuleLLM / `RuleLLMSelfAttributor`

```text
Hybrid: SelfAttributor rules + LLM reasoning.

Theoretical basis: simulation-bases.md Section 4.2 -- SelfAttributor.
Strategy specification: simulation-bases.md Section 4.2.4.
```

### Rag / `RagLLMSelfAttributor`

```text
RAG-augmented SelfAttributor.

Theoretical basis: simulation-bases.md Section 4.2 -- SelfAttributor.
Strategy specification: simulation-bases.md Section 4.2.4.
```
