# CreditCycle / Minsky Borrower

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CreditCycle |
| Agent type | Minsky Borrower |
| Canonical class | `MinskyBorrower` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**4.2.1 Economic Role**: Speculative-to-Ponzi borrower who increases leverage during periods of stability.

## Financial Theory / Theoretical Basis

### Rule / `MinskyBorrower`
- Theory: simulation-bases.md Section 4.2 -- MinskyBorrower
- Theoretical basis: Minsky (1986) financial instability hypothesis; periods of

### LLM / `LLMMinskyBorrower`
- LLM-driven Minsky borrower -- accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMMinskyBorrower`
- RuleLLM-driven Minsky borrower -- accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMMinskyBorrower`
- RAG-augmented Minsky borrower -- accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| crisis_threshold | Rule: `-0.05` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| hedge_rounds | Rule: `20`<br>LLM: `20`<br>RuleLLM: `20`<br>Rag: `20` | LLM, Rag, Rule, RuleLLM |
| hedge_size | Rule: `100`<br>LLM: `100`<br>RuleLLM: `100`<br>Rag: `100` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_leverage | Rule: `1.0` | Rule |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CreditCycle.LLM.prompts:LLM_MINSKY_BORROWER_SYS', 'user_message': 'examples.CreditCycle.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CreditCycle.RuleLLM.prompts:RULELLM_MINSKY_BORROWER_SYS', 'user_message': 'examples.CreditCycle.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CreditCycle.Rag.prompts:RAG_MINSKY_BORROWER_SYS', 'user_message': 'examples.CreditCycle.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_leverage | Rule: `5.0` | Rule |
| order_size | Rule: `500` | Rule |
| ponzi_rounds | Rule: `80`<br>LLM: `80`<br>RuleLLM: `80`<br>Rag: `80` | LLM, Rag, Rule, RuleLLM |
| ponzi_size | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| speculative_rounds | Rule: `40`<br>LLM: `40`<br>RuleLLM: `40`<br>Rag: `40` | LLM, Rag, Rule, RuleLLM |
| speculative_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | minskyborrower | MinskyBorrower | `MinskyBorrower` | 2 | `examples/CreditCycle/Rule/players.py` |
| LLM | minskyborrower | MinskyBorrower | `LLMMinskyBorrower` | 2 | `examples/CreditCycle/LLM/players.py` |
| RuleLLM | minskyborrower | MinskyBorrower | `RuleLLMMinskyBorrower` | 2 | `examples/CreditCycle/RuleLLM/players.py` |
| Rag | minskyborrower | MinskyBorrower | `RagLLMMinskyBorrower` | 2 | `examples/CreditCycle/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 MinskyBorrower

**4.2.1 Economic Role**: Speculative-to-Ponzi borrower who increases leverage during periods of stability.

**4.2.2 Destabilizing/Stabilizing**: Destabilizing -- ratchets leverage upward during calm, creates fragility that magnifies any price decline into forced deleveraging.

**4.2.3 Mathematical Model**:

```
stable_rounds(t) = stable_rounds(t-1) + 1   if |δ(t)| < 0.02
stable_rounds(t) = 0                          otherwise

qty(t) = order_size x 2    if δ(t) < crisis_threshold  [forced sell]
qty(t) = order_size        if stable_rounds > 3          [levered buy]
qty(t) = 0                 otherwise
```

Parameters: `crisis_threshold` = -0.05, `order_size` = 500.

**4.2.4 Calibration Targets**: Buys in >=3 consecutive low-volatility rounds; forced sell volume ≈ 1,000 units during crisis.

**4.2.5 Historical Analogue**: Minsky (1986) Ponzi-finance phase; hedge fund leverage accumulation pre-LTCM; household mortgage leverage 2004-2007.

**4.2.6 Interaction Pattern**: Synchronizes buying with ProCyclicalLender during stable phase; mass sell during crisis coincides with ProCyclicalLender withdrawal.

**4.2.7 Diversity Contribution**: Models the endogenous fragility mechanism -- calm-period leverage accumulation that seeds the bust.

---

## Source Docstring Excerpts

### Rule / `MinskyBorrower`

```text
Increases leverage during stability, creating fragility that leads to crisis.

Theory: simulation-bases.md Section 4.2 -- MinskyBorrower
Theoretical basis: Minsky (1986) financial instability hypothesis; periods of
stability breed instability as agents accumulate debt through hedge->speculative->Ponzi.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMMinskyBorrower`

```text
LLM-driven Minsky borrower -- accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMMinskyBorrower`

```text
RuleLLM-driven Minsky borrower -- accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMMinskyBorrower`

```text
RAG-augmented Minsky borrower -- accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md Section 4.2.
```
