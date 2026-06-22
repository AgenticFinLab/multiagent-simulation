# HerdingInformation / Independent Thinker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HerdingInformation |
| Agent type | Independent Thinker |
| Canonical class | `IndependentThinker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements rational Bayesian updating with correct private signal processing. Contrarian -- buys when cascade overvalues, sells when undervalues. Represents the arbitrage force against cascade inefficiency.

## Financial Theory / Theoretical Basis

### Rule / `IndependentThinker`
- Theory: simulation-bases.md Section 4.3 -- IndependentThinker
- Theoretical basis: Independent private signal processing (Banerjee, 1992 baseline).

### LLM / `LLMIndependentThinker`
- LLM-driven rational independent thinker. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMIndependentThinker`
- RuleLLM-driven rational independent thinker. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMIndependentThinker`
- RagLLM-driven rational independent thinker. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HerdingInformation.LLM.prompts:LLM_INDEPENDENT_THINKER_SYS', 'user_message': 'examples.HerdingInformation.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.HerdingInformation.RuleLLM.prompts:RULELLM_INDEPENDENT_THINKER_SYS', 'user_message': 'examples.HerdingInformation.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.HerdingInformation.Rag.prompts:RAGLLM_INDEPENDENT_THINKER_SYS', 'user_message': 'examples.HerdingInformation.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| signal_precision | Rule: `0.9`<br>LLM: `0.9`<br>RuleLLM: `0.9`<br>Rag: `0.9` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | independentthinker | IndependentThinker | `IndependentThinker` | 2 | `examples/HerdingInformation/Rule/players.py` |
| LLM | independentthinker | IndependentThinker | `LLMIndependentThinker` | 2 | `examples/HerdingInformation/LLM/players.py` |
| RuleLLM | independentthinker | IndependentThinker | `RuleLLMIndependentThinker` | 2 | `examples/HerdingInformation/RuleLLM/players.py` |
| Rag | independentthinker | IndependentThinker | `RagLLMIndependentThinker` | 2 | `examples/HerdingInformation/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 IndependentThinker

**Summary**: Implements rational Bayesian updating with correct private signal processing. Contrarian -- buys when cascade overvalues, sells when undervalues. Represents the arbitrage force against cascade inefficiency.

**Foundation**: Bikhchandani et al. (1992) rational benchmark; Avery & Zemsky (1998) trading cascade limits. `doi:10.1086/261849`

**Design Purpose**: Model the rational counter-force to information cascades. Uses private signal quality (signal_precision) to trade against cascade mispricings. Subject to capacity limits that prevent full correction (Theory 3).

**Behavioral Framework**:

| Decision Variable    | Logic                                             | Formula                        |
|----------------------|---------------------------------------------------|--------------------------------|
| Activation threshold | Detects cascade misvaluation                      | `abs(deviation) > 0.03` |
| Trade size           | Precision-scaled contrarian                       | `min(500, int(abs(dev) x signal_precision x 3000))` |
| Direction            | Contrarian: buys when dev < 0; sells when dev > 0 | Against cascade direction      |
| signal_precision     | Private signal quality                            | 0.5 (low) -> 2.0 (high quality) |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. If `|deviation| > 0.03`: trade contrariantly
3. `qty = min(500, int(|dev| x signal_precision x 3000))`; direction = -sign(deviation)

**Worked Example** (signal_precision=0.9, deviation=+0.07 -- cascade is buying):
- `|0.07| > 0.03` -> activates
- qty = min(500, int(0.07 x 0.9 x 3000)) = min(500, 189) = 189
- Action: sell 210 shares -- correcting overvaluation

**References**: simulation-bases.md Section 2 Theory 3; `doi:10.1086/261849`

---

## Source Docstring Excerpts

### Rule / `IndependentThinker`

```text
Theory: simulation-bases.md Section 4.3 -- IndependentThinker

Theoretical basis: Independent private signal processing (Banerjee, 1992 baseline).
Independent thinker: processes private signals correctly without social bias.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMIndependentThinker`

```text
LLM-driven rational independent thinker. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMIndependentThinker`

```text
RuleLLM-driven rational independent thinker. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMIndependentThinker`

```text
RagLLM-driven rational independent thinker. Theory: simulation-bases.md Section 4.3.
```
