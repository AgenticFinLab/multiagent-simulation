# EchoChamber / Critical Thinker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EchoChamber |
| Agent type | Critical Thinker |
| Canonical class | `CriticalThinker` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Evidence-oriented agent that resists group pressure. **Theoretical and Empirical Basis**: Persuasive-arguments theory and independent evidence evaluation. **Design Purpose**: Provide stabilizing pressure when polarization becomes high. **Behavioral Framework**: Treats high polarization as evidence that views should move toward the center. **Decision Process**: Compute `evidence_signal = -my_opinion * evidence_sensitivity * polarization`, update slowly using `critical_weight`, and emit `depolarize` when `polarization > 0.3`. **Worked Numerical Example**: Opinion `0.6`, polarization `0.7`, and evidence_sensitivity `0.6` create a negative signal that pulls the agent toward the center. **Academic References**: Group-polarization and persuasive-arguments research.

## Financial Theory / Theoretical Basis

### Rule / `CriticalThinker`
- Theory: simulation-bases.md Section 4.3 -- CriticalThinker
- Theoretical basis: Isenberg (1986) persuasive arguments vs social comparison;

### LLM / `LLMCriticalThinker`
- LLM-driven critical thinker -- evaluates evidence independently, resists social proof. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMCriticalThinker`
- RuleLLM critical thinker -- Isenberg depolarization formula + LLM evidence evaluation. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMCriticalThinker`
- RAG-augmented critical thinker -- evidence evaluation with persuasive-arguments literature. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| critical_eagerness | Rule: `0.7`<br>RuleLLM: `0.7`<br>Rag: `0.7` | Rag, Rule, RuleLLM |
| critical_weight | Rule: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| evidence_sensitivity | Rule: `0.6`<br>RuleLLM: `0.6`<br>Rag: `0.6` | Rag, Rule, RuleLLM |
| initial_opinion | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| knowledge | Rag: `{'backend': 'local', 'global_uri': 'examples/document-sources', 'resource_csv': ['examples/document-sources/books.csv', 'examples/document-sources/source'], 'preprocessing': {'parser': 'mineru', 'timeout_per_page': 30, 'max_pages': 250, 'output_position': 'MinerU_processed'}, 'rag': {'output_position': 'rag_index', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size...` | Rag |
| llm | LLM: `{'sys_message': 'examples.EchoChamber.LLM.prompts:LLM_CRITICAL_SYS', 'user_message': 'examples.EchoChamber.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_CRITICAL_SYS', 'user_message': 'examples.EchoChamber.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.EchoChamber.Rag.prompts:RAG_CRITICAL_SYS', 'user_message': 'examples.EchoChamber.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | critical_thinker | Critical Thinker | `CriticalThinker` | 3 | `examples/EchoChamber/Rule/players.py` |
| LLM | llm_critical_thinker | LLM Critical Thinker | `LLMCriticalThinker` | 3 | `examples/EchoChamber/LLM/players.py` |
| RuleLLM | rulellm_critical_thinker | RuleLLM Critical Thinker | `RuleLLMCriticalThinker` | 3 | `examples/EchoChamber/RuleLLM/players.py` |
| Rag | ragllm_critical_thinker | RAG-LLM Critical Thinker | `RagLLMCriticalThinker` | 3 | `examples/EchoChamber/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 CriticalThinker

**Summary**: Evidence-oriented agent that resists group pressure.
**Theoretical and Empirical Basis**: Persuasive-arguments theory and
independent evidence evaluation.
**Design Purpose**: Provide stabilizing pressure when polarization becomes high.
**Behavioral Framework**: Treats high polarization as evidence that views should
move toward the center.
**Decision Process**: Compute `evidence_signal = -my_opinion *
evidence_sensitivity * polarization`, update slowly using `critical_weight`, and
emit `depolarize` when `polarization > 0.3`.
**Worked Numerical Example**: Opinion `0.6`, polarization `0.7`, and
evidence_sensitivity `0.6` create a negative signal that pulls the agent toward
the center.
**Academic References**: Group-polarization and persuasive-arguments research.

## Source Docstring Excerpts

### Rule / `CriticalThinker`

```text
Critical thinker who evaluates evidence and resists group pressure.

Theory: simulation-bases.md Section 4.3 -- CriticalThinker
Theoretical basis: Isenberg (1986) persuasive arguments vs social comparison;
critical thinkers resist social proof and move opinion slowly on merit alone.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMCriticalThinker`

```text
LLM-driven critical thinker -- evaluates evidence independently, resists social proof. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMCriticalThinker`

```text
RuleLLM critical thinker -- Isenberg depolarization formula + LLM evidence evaluation. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMCriticalThinker`

```text
RAG-augmented critical thinker -- evidence evaluation with persuasive-arguments literature. Theory: simulation-bases.md Section 4.3.
```
