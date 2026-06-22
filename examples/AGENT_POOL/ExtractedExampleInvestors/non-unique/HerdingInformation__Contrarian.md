# HerdingInformation / Contrarian

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HerdingInformation |
| Agent type | Contrarian |
| Canonical class | `Contrarian` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements De Bondt & Thaler (1985) deliberate contrarian strategy. Triggers on larger deviations than IndependentThinker. Pure crowd-counter -- no private signal model, just fundamental anchoring.

## Financial Theory / Theoretical Basis

### Rule / `Contrarian`
- Theory: simulation-bases.md Section 4.4 -- Contrarian
- Theoretical basis: Anti-herding / contrarian strategy (Froot et al., 1992).

### LLM / `LLMContrarian`
- LLM-driven contrarian investor. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMContrarian`
- RuleLLM-driven contrarian investor. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMContrarian`
- RagLLM-driven contrarian investor. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `250`<br>LLM: `250`<br>RuleLLM: `250`<br>Rag: `250` | LLM, Rag, Rule, RuleLLM |
| contrarian_threshold | Rule: `0.4`<br>LLM: `0.4`<br>RuleLLM: `0.4`<br>Rag: `0.4` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HerdingInformation.LLM.prompts:LLM_CONTRARIAN_SYS', 'user_message': 'examples.HerdingInformation.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.HerdingInformation.RuleLLM.prompts:RULELLM_CONTRARIAN_SYS', 'user_message': 'examples.HerdingInformation.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.HerdingInformation.Rag.prompts:RAGLLM_CONTRARIAN_SYS', 'user_message': 'examples.HerdingInformation.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | contrarian | Contrarian | `Contrarian` | 1 | `examples/HerdingInformation/Rule/players.py` |
| LLM | contrarian | Contrarian | `LLMContrarian` | 1 | `examples/HerdingInformation/LLM/players.py` |
| RuleLLM | contrarian | Contrarian | `RuleLLMContrarian` | 1 | `examples/HerdingInformation/RuleLLM/players.py` |
| Rag | contrarian | Contrarian | `RagLLMContrarian` | 1 | `examples/HerdingInformation/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 Contrarian

**Summary**: Implements De Bondt & Thaler (1985) deliberate contrarian strategy. Triggers on larger deviations than IndependentThinker. Pure crowd-counter -- no private signal model, just fundamental anchoring.

**Foundation**: De Bondt & Thaler (1985) overreaction/contrarian investing. `doi:10.1111/j.1540-6261.1985.tb05004.x`

**Design Purpose**: Provide a secondary, simpler correction mechanism alongside IndependentThinker. Activates at `|deviation| > contrarian_threshold x 0.05` -- higher bar than IndependentThinker. Combined with Section 4.3, creates the 900-share maximum correction capacity.

**Behavioral Framework**:

| Decision Variable    | Logic                                    | Formula                               |
|----------------------|------------------------------------------|---------------------------------------|
| Activation threshold | Configurable                             | `abs(deviation) > contrarian_threshold x 0.05` |
| Trade size           | Simple deviation-based                   | `min(400, int(abs(dev) x 2000))` |
| Direction            | Contrarian -- against deviation direction | Sells when dev > 0; buys when dev < 0 |
| contrarian_threshold | Activation level multiplier              | 1 -> 20 (multiplied by 0.05)           |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. If `|deviation| > contrarian_threshold x 0.05`: trade contrariantly
3. `qty = min(400, int(|dev| x 2000))`; direction = -sign(deviation)

**Worked Example** (contrarian_threshold=0.4, deviation=+0.08):
- threshold = 0.4 x 0.05 = 0.02; `|0.08| > 0.02` -> activates
- qty = min(400, int(0.08 x 2000)) = min(400, 160) = 160
- Action: sell 160 shares

**References**: simulation-bases.md Section 2 Theory 3; `doi:10.1111/j.1540-6261.1985.tb05004.x`

---

## Source Docstring Excerpts

### Rule / `Contrarian`

```text
Theory: simulation-bases.md Section 4.4 -- Contrarian

Theoretical basis: Anti-herding / contrarian strategy (Froot et al., 1992).
Contrarian trader: deliberately goes against the crowd.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMContrarian`

```text
LLM-driven contrarian investor. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMContrarian`

```text
RuleLLM-driven contrarian investor. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMContrarian`

```text
RagLLM-driven contrarian investor. Theory: simulation-bases.md Section 4.4.
```
