# DispositionEffect / Rag Loss Averse

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Rag Loss Averse |
| Canonical class | `RagLossAverse` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rag |

## Definition and Goal

RAG-enhanced extreme loss-averse investor.

## Financial Theory / Theoretical Basis

### Rag / `RagLossAverse`
- Theory: simulation-bases.md Section 4.1 -- DispositionInvestor
- Theoretical basis: Prospect Theory loss aversion; RAG retrieves loss-aversion and disposition-effect studies.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rag: `3` | Rag |
| gain_threshold | Rag: `0.03` | Rag |
| initial_cash | Rag: `10000.0` | Rag |
| initial_position | Rag: `50.0` | Rag |
| initial_purchase_price | Rag: `100.0` | Rag |
| llm | Rag: `{'sys_message': 'examples.DispositionEffect.Rag.prompts:RULELLM_LOSS_AVERSE_SYS', 'user_message': 'examples.DispositionEffect.Rag.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | Rag |
| loss_threshold | Rag: `-0.1` | Rag |
| rag | Rag: `{'persist_dir': 'EXPERIMENT/DispositionEffect/Rag/rag_index/rag_loss_averse', 'docs_dir': 'examples/document-sources/files', 'url_csv': 'examples/document-sources/finance_books.csv', 'urls': ['https://en.wikipedia.org/wiki/Loss_aversion', 'https://en.wikipedia.org/wiki/Prospect_theory'], 'agent_autonomous': False, 'catalog_path': 'examples/document-sources/finance_books.csv', 'llm_suggested': False, 'llm_suggested_n_urls': 5, 'docs_save_dir': 'examples/document-sources/files', 'top_k': 5, 'embed...` | Rag |
| sell_fraction_gain | Rag: `0.5` | Rag |
| sell_fraction_loss | Rag: `0.15` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rag | rag_loss_averse | RAG Loss-Averse Investor | `RagLossAverse` | 2 | `examples/DispositionEffect/Rag/players.py` |

## Source Docstring Excerpts

### Rag / `RagLossAverse`

```text
RAG-enhanced extreme loss-averse investor.

Theory: simulation-bases.md Section 4.1 -- DispositionInvestor
Theoretical basis: Prospect Theory loss aversion; RAG retrieves loss-aversion and disposition-effect studies.
See simulation-bases.md Section 4.1 for mathematical model.
```
