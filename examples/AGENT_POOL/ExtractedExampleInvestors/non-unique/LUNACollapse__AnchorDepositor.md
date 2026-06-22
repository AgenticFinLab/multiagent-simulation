# LUNACollapse / Anchor Depositor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LUNACollapse |
| Agent type | Anchor Depositor |
| Canonical class | `AnchorDepositor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A yield depositor who exits when confidence in the yield ecosystem falls.

## Financial Theory / Theoretical Basis

### Rule / `AnchorDepositor`
- Theory: simulation-bases.md Section 4.4 -- AnchorDepositor
- Theoretical Basis: Bank run dynamics in DeFi yield protocols

### LLM / `LLMAnchorDepositor`
- LLM-driven yield depositor exit agent. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMAnchorDepositor`
- RuleLLM yield depositor exit agent. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMAnchorDepositor`
- RAG yield depositor exit agent. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LUNACollapse.LLM.prompts:LLM_ANCHORDEPOSITOR_PROMPT', 'user_message': 'examples.LUNACollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_ANCHORDEPOSITOR_PROMPT', 'user_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LUNACollapse.Rag.prompts:RAG_ANCHORDEPOSITOR_PROMPT', 'user_message': 'examples.LUNACollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| yield_threshold | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | anchordepositor | AnchorDepositor | `AnchorDepositor` | 2 | `examples/LUNACollapse/Rule/players.py` |
| LLM | anchordepositor | AnchorDepositor | `LLMAnchorDepositor` | 2 | `examples/LUNACollapse/LLM/players.py` |
| RuleLLM | anchordepositor | AnchorDepositor | `RuleLLMAnchorDepositor` | 2 | `examples/LUNACollapse/RuleLLM/players.py` |
| Rag | anchordepositor | AnchorDepositor | `RagLLMAnchorDepositor` | 2 | `examples/LUNACollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 AnchorDepositor

**Summary**: A yield depositor who exits when confidence in the yield ecosystem
falls.

**Theoretical and Empirical Basis**: Anchor Protocol withdrawals were central to
the Terra confidence collapse.

**Design Purpose**: Represent slower but large deposit flight from yield
strategies.

**Behavioral Framework**: Uses `yield_threshold` and market deviation as a
confidence proxy.

**Decision Process**: Withdraw/sell when confidence falls below the configured
threshold; otherwise hold.

**Worked Numerical Example**: If confidence-implied stress exceeds 5%, the
depositor exits part of the position.

**Academic References**: Terra/Anchor event analyses; DeFi run literature.

## Source Docstring Excerpts

### Rule / `AnchorDepositor`

```text
Withdraws from high-yield protocol when ecosystem confidence drops.

Theory: simulation-bases.md Section 4.4 -- AnchorDepositor
Theoretical Basis: Bank run dynamics in DeFi yield protocols
Market Role: destabilizing -- rapid withdrawals collapse TVL
```

### LLM / `LLMAnchorDepositor`

```text
LLM-driven yield depositor exit agent. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMAnchorDepositor`

```text
RuleLLM yield depositor exit agent. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMAnchorDepositor`

```text
RAG yield depositor exit agent. Theory: simulation-bases.md Section 4.4.
```
