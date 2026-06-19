# RepresentativenessBias / Bayesian Updater

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | RepresentativenessBias |
| Agent type | Bayesian Updater |
| Canonical class | `BayesianUpdater` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A stabilizing benchmark that combines prior/base-rate information with observed evidence. It corrects overreaction when price deviates materially from fundamental value.

## Financial Theory / Theoretical Basis

### Rule / `BayesianUpdater`
- Theory: simulation-bases.md Section 4.3 -- BayesianUpdater
- Theoretical basis: Bayesian rationality as a stabilizing benchmark.

### LLM / `LLMBayesianUpdater`
- LLM-driven Bayesian updater -- base-rate disciplined benchmark. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMBayesianUpdater`
- RuleLLM Bayesian updater -- rule-guided base-rate benchmark. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMBayesianUpdater`
- RagLLM Bayesian updater -- base-rate benchmark with retrieval. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`, `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_rate_weight | Rule: `0.7`<br>LLM: `0.7`<br>RuleLLM: `0.7`<br>Rag: `0.7` | LLM, Rag, Rule, RuleLLM |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| evidence_weight | Rule: `0.4` | Rule |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.RepresentativenessBias.LLM.prompts:LLM_BAYESIAN_UPDATER_PROMPT', 'user_message': 'examples.RepresentativenessBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.RepresentativenessBias.RuleLLM.prompts:RULELLM_BAYESIAN_UPDATER_SYS', 'user_message': 'examples.RepresentativenessBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.RepresentativenessBias.Rag.prompts:RULELLM_BAYESIAN_UPDATER_SYS', 'user_message': 'examples.RepresentativenessBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | bayesianupdater | BayesianUpdater | `BayesianUpdater` | 1 | `examples/RepresentativenessBias/Rule/players.py` |
| LLM | bayesianupdater | BayesianUpdater | `LLMBayesianUpdater` | 1 | `examples/RepresentativenessBias/LLM/players.py` |
| RuleLLM | bayesianupdater | BayesianUpdater | `RuleLLMBayesianUpdater` | 1 | `examples/RepresentativenessBias/RuleLLM/players.py` |
| Rag | bayesianupdater | BayesianUpdater | `RagLLMBayesianUpdater` | 1 | `examples/RepresentativenessBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 BayesianUpdater

**Summary**: A stabilizing benchmark that combines prior/base-rate information
with observed evidence. It corrects overreaction when price deviates materially
from fundamental value.

**Theoretical and Empirical Foundation**: Based on Grether (1980,
doi:10.2307/1885092) and Bayesian decision theory.

**Design Purpose and Activation Scenarios**: Activates when
`abs(deviation) > 0.05`; buys undervaluation and sells overvaluation.

**Behavioral Framework**: `base_rate_weight` and `evidence_weight` define how
strongly the agent disciplines new signals with priors. Quantity is
`min(500, int(abs(deviation) * 3000))`.

**Decision Process Walkthrough**: Compute deviation, compare it to the 5%
evidence threshold, trade toward fundamental when the signal is strong enough.

**Worked Numerical Example**: Price 94 and fundamental 100 gives deviation
-0.06. Quantity is `min(500, int(0.06 * 3000)) = 180`; the agent buys.

**Academic References**: Grether (1980).

## Source Docstring Excerpts

### Rule / `BayesianUpdater`

```text
Correctly updates beliefs using base rates and new evidence.

Theory: simulation-bases.md Section 4.3 -- BayesianUpdater
Theoretical basis: Bayesian rationality as a stabilizing benchmark.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMBayesianUpdater`

```text
LLM-driven Bayesian updater -- base-rate disciplined benchmark. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMBayesianUpdater`

```text
RuleLLM Bayesian updater -- rule-guided base-rate benchmark. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMBayesianUpdater`

```text
RagLLM Bayesian updater -- base-rate benchmark with retrieval. Theory: simulation-bases.md Section 4.3.
```
