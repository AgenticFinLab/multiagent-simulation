# LUNACollapse / Stablecoin Holder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LUNACollapse |
| Agent type | Stablecoin Holder |
| Canonical class | `StablecoinHolder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A holder who redeems stablecoin exposure when confidence breaks.

## Financial Theory / Theoretical Basis

### Rule / `StablecoinHolder`
- Theory: simulation-bases.md Section 4.1 -- StablecoinHolder
- Theoretical Basis: Algorithmic stablecoin redemption mechanics

### LLM / `LLMStablecoinHolder`
- LLM-driven stablecoin redeemer. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMStablecoinHolder`
- RuleLLM stablecoin redeemer. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMStablecoinHolder`
- RAG stablecoin redeemer. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `1000`<br>LLM: `1000`<br>RuleLLM: `1000`<br>Rag: `1000` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LUNACollapse.LLM.prompts:LLM_STABLECOINHOLDER_PROMPT', 'user_message': 'examples.LUNACollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_STABLECOINHOLDER_PROMPT', 'user_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LUNACollapse.Rag.prompts:RAG_STABLECOINHOLDER_PROMPT', 'user_message': 'examples.LUNACollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| redemption_threshold | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | stablecoinholder | StablecoinHolder | `StablecoinHolder` | 3 | `examples/LUNACollapse/Rule/players.py` |
| LLM | stablecoinholder | StablecoinHolder | `LLMStablecoinHolder` | 3 | `examples/LUNACollapse/LLM/players.py` |
| RuleLLM | stablecoinholder | StablecoinHolder | `RuleLLMStablecoinHolder` | 3 | `examples/LUNACollapse/RuleLLM/players.py` |
| Rag | stablecoinholder | StablecoinHolder | `RagLLMStablecoinHolder` | 3 | `examples/LUNACollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 StablecoinHolder

**Summary**: A holder who redeems stablecoin exposure when confidence breaks.

**Theoretical and Empirical Basis**: Algorithmic stablecoin redemption pressure
observed during Terra/LUNA and described in algorithmic stablecoin risk models.

**Design Purpose**: Represent panic redemption flow that turns peg stress into
base-token selling pressure.

**Behavioral Framework**: Monitors deviation from fundamental value. When the
deviation breaches the redemption threshold, sells a fraction of current
position.

**Decision Process**: If `deviation < -redemption_threshold`, sell up to
50% of position; otherwise hold.

**Worked Numerical Example**: With `redemption_threshold = 0.05`,
`deviation = -0.06`, and `position = 100000`, the holder sells 50000 units.

**Academic References**: Klages-Mundt et al. (2020); Levy (2022).

## Source Docstring Excerpts

### Rule / `StablecoinHolder`

```text
Redeems stablecoin for base token when confidence drops.

Theory: simulation-bases.md Section 4.1 -- StablecoinHolder
Theoretical Basis: Algorithmic stablecoin redemption mechanics
Market Role: destabilizing -- redemptions amplify LUNA supply collapse
```

### LLM / `LLMStablecoinHolder`

```text
LLM-driven stablecoin redeemer. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMStablecoinHolder`

```text
RuleLLM stablecoin redeemer. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMStablecoinHolder`

```text
RAG stablecoin redeemer. Theory: simulation-bases.md Section 4.1.
```
