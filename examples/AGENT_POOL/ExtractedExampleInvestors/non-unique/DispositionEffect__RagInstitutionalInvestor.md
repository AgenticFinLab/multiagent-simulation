# DispositionEffect / Rag Institutional Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Rag Institutional Investor |
| Canonical class | `RagInstitutionalInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rag |

## Definition and Goal

RAG-enhanced institutional investor.

## Financial Theory / Theoretical Basis

### Rag / `RagInstitutionalInvestor`
- Theory: simulation-bases.md Section 4.5 -- InstitutionalInvestor
- Theoretical basis: Shapira & Venezia (2001) professional discipline; RAG retrieves institutional risk-control evidence.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rag: `3` | Rag |
| gain_threshold | Rag: `0.25` | Rag |
| initial_cash | Rag: `10000.0` | Rag |
| initial_position | Rag: `50.0` | Rag |
| initial_purchase_price | Rag: `100.0` | Rag |
| llm | Rag: `{'sys_message': 'examples.DispositionEffect.Rag.prompts:RULELLM_INSTITUTIONAL_SYS', 'user_message': 'examples.DispositionEffect.Rag.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | Rag |
| loss_threshold | Rag: `-0.15` | Rag |
| rag | Rag: `{'persist_dir': 'EXPERIMENT/DispositionEffect/Rag/rag_index/rag_institutional', 'docs_dir': 'examples/document-sources/files', 'url_csv': 'examples/document-sources/finance_books.csv', 'urls': ['https://en.wikipedia.org/wiki/Institutional_investor', 'https://en.wikipedia.org/wiki/Risk_management'], 'agent_autonomous': False, 'catalog_path': 'examples/document-sources/finance_books.csv', 'llm_suggested': False, 'llm_suggested_n_urls': 5, 'docs_save_dir': 'examples/document-sources/files', 'top_k'...` | Rag |
| sell_fraction | Rag: `0.4` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rag | rag_institutional | RAG Institutional Investor | `RagInstitutionalInvestor` | 2 | `examples/DispositionEffect/Rag/players.py` |

## Source Docstring Excerpts

### Rag / `RagInstitutionalInvestor`

```text
RAG-enhanced institutional investor.

Theory: simulation-bases.md Section 4.5 -- InstitutionalInvestor
Theoretical basis: Shapira & Venezia (2001) professional discipline; RAG retrieves institutional risk-control evidence.
See simulation-bases.md Section 4.5 for mathematical model.
```
