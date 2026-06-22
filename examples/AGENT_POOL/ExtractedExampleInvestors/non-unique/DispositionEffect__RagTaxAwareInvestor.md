# DispositionEffect / Rag Tax Aware Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Rag Tax Aware Investor |
| Canonical class | `RagTaxAwareInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rag |

## Definition and Goal

RAG-enhanced tax-aware investor.

## Financial Theory / Theoretical Basis

### Rag / `RagTaxAwareInvestor`
- Theory: simulation-bases.md Section 4.3 -- TaxAwareInvestor
- Theoretical basis: Constantinides (1983) tax-loss harvesting; RAG retrieves tax strategy literature.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| capital_gains_hold | Rag: `0.2` | Rag |
| custom_state_hot_limit | Rag: `3` | Rag |
| initial_cash | Rag: `10000.0` | Rag |
| initial_position | Rag: `50.0` | Rag |
| initial_purchase_price | Rag: `100.0` | Rag |
| llm | Rag: `{'sys_message': 'examples.DispositionEffect.Rag.prompts:RULELLM_TAX_AWARE_SYS', 'user_message': 'examples.DispositionEffect.Rag.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | Rag |
| rag | Rag: `{'persist_dir': 'EXPERIMENT/DispositionEffect/Rag/rag_index/rag_tax_aware', 'docs_dir': 'examples/document-sources/files', 'url_csv': 'examples/document-sources/finance_books.csv', 'urls': ['https://en.wikipedia.org/wiki/Tax_loss_harvesting', 'https://en.wikipedia.org/wiki/Capital_gains_tax'], 'agent_autonomous': False, 'catalog_path': 'examples/document-sources/finance_books.csv', 'llm_suggested': False, 'llm_suggested_n_urls': 5, 'docs_save_dir': 'examples/document-sources/files', 'top_k': 5, ...` | Rag |
| tax_harvest_fraction | Rag: `0.5` | Rag |
| tax_loss_threshold | Rag: `-0.05` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rag | rag_tax_aware | RAG Tax Aware Investor | `RagTaxAwareInvestor` | 2 | `examples/DispositionEffect/Rag/players.py` |

## Source Docstring Excerpts

### Rag / `RagTaxAwareInvestor`

```text
RAG-enhanced tax-aware investor.

Has access to tax-loss harvesting strategies and
related academic literature.

Theory: simulation-bases.md Section 4.3 -- TaxAwareInvestor
Theoretical basis: Constantinides (1983) tax-loss harvesting; RAG retrieves tax strategy literature.
See simulation-bases.md Section 4.3 for mathematical model.
```
