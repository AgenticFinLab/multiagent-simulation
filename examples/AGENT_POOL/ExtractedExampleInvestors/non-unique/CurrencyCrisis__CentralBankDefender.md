# CurrencyCrisis / Central Bank Defender

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CurrencyCrisis |
| Agent type | Central Bank Defender |
| Canonical class | `CentralBankDefender` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**4.3.1 Economic Role**: Government/central bank defending the currency peg by purchasing domestic currency.

## Financial Theory / Theoretical Basis

### Rule / `CentralBankDefender`
- Theory: simulation-bases.md Section 4.3 -- CentralBankDefender
- Theoretical basis: Central bank defense mechanisms (Obstfeld, 1996); intervenes

### LLM / `LLMCentralBankDefender`
- LLM-driven central bank defender -- buys domestic currency to defend peg. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMCentralBankDefender`
- RuleLLM-driven central bank defender -- buys domestic currency to defend peg. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMCentralBankDefender`
- RAG-augmented central bank defender -- buys domestic currency to defend peg. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| defense_size | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| defense_threshold | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `5000000.0`<br>LLM: `5000000.0`<br>RuleLLM: `5000000.0`<br>Rag: `5000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `3000`<br>LLM: `3000`<br>RuleLLM: `3000`<br>Rag: `3000` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_CENTRAL_BANK_DEFENDER_SYS', 'user_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_CENTRAL_BANK_DEFENDER_SYS', 'user_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_CENTRAL_BANK_DEFENDER_SYS', 'user_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `500` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | centralbankdefender | CentralBankDefender | `CentralBankDefender` | 1 | `examples/CurrencyCrisis/Rule/players.py` |
| LLM | centralbankdefender | CentralBankDefender | `LLMCentralBankDefender` | 1 | `examples/CurrencyCrisis/LLM/players.py` |
| RuleLLM | centralbankdefender | CentralBankDefender | `RuleLLMCentralBankDefender` | 1 | `examples/CurrencyCrisis/RuleLLM/players.py` |
| Rag | centralbankdefender | CentralBankDefender | `RagLLMCentralBankDefender` | 1 | `examples/CurrencyCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 CentralBankDefender

**4.3.1 Economic Role**: Government/central bank defending the currency peg by purchasing domestic currency.

**4.3.2 Destabilizing/Stabilizing**: Stabilizing -- provides counter-buying when currency weakens; limited by reserve capacity.

**4.3.3 Mathematical Model**:

```
qty(t) = order_size   if deviation < -defense_threshold  [buy/defend]
qty(t) = order_size   if deviation > +defense_threshold  [sell reserves]
qty(t) = 0            otherwise
```

Parameters: `defense_threshold` = 0.05, `order_size` = 500, `initial_cash` = 5,000,000, `initial_position` = 3000.

**4.3.4 Calibration Targets**: Defense activates once the peg is under material pressure; the central bank can provide up to 500 units of stabilizing buy pressure per round.

**4.3.5 Historical Analogue**: Bank of England defending sterling (1992, pre-Black Wednesday); Bank of Thailand defending baht (1997).

**4.3.6 Interaction Pattern**: Direct counterparty to SpeculativeAttacker; provides price floor; limited by initial_cash reserves.

**4.3.7 Diversity Contribution**: Models the government's asymmetric role -- can stabilize but eventually runs out of reserves.

---

## Source Docstring Excerpts

### Rule / `CentralBankDefender`

```text
Defends currency peg using foreign reserves and interest rate adjustments.

Theory: simulation-bases.md Section 4.3 -- CentralBankDefender
Theoretical basis: Central bank defense mechanisms (Obstfeld, 1996); intervenes
by buying domestic currency; limited by reserve capacity.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMCentralBankDefender`

```text
LLM-driven central bank defender -- buys domestic currency to defend peg. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMCentralBankDefender`

```text
RuleLLM-driven central bank defender -- buys domestic currency to defend peg. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMCentralBankDefender`

```text
RAG-augmented central bank defender -- buys domestic currency to defend peg. Theory: simulation-bases.md Section 4.3.
```
