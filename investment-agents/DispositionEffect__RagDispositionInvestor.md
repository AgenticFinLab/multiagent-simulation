# DispositionEffect / Rag Disposition Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Rag Disposition Investor |
| Canonical class | `RagDispositionInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rag |

## Definition and Goal

RAG-enhanced disposition-prone investor.

## Financial Theory / Theoretical Basis

### Rag / `RagDispositionInvestor`
- Has access to Prospect Theory and behavioral finance literature
- through RAG, but still exhibits disposition effect tendencies
- Theory: simulation-bases.md Section 4.1 -- DispositionInvestor
- Theoretical basis: Kahneman & Tversky (1979) Prospect Theory; RAG retrieves disposition effect studies.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| buy_fraction | Rag: `0.15` | Rag |
| custom_state_hot_limit | Rag: `3` | Rag |
| gain_threshold | Rag: `0.03` | Rag |
| initial_cash | Rag: `10000.0` | Rag |
| initial_position | Rag: `50.0` | Rag |
| initial_purchase_price | Rag: `100.0` | Rag |
| llm | Rag: `{'sys_message': 'examples.DispositionEffect.Rag.prompts:RULELLM_DISPOSITION_BIASED_SYS', 'user_message': 'examples.DispositionEffect.Rag.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | Rag |
| loss_threshold | Rag: `-0.1` | Rag |
| max_position | Rag: `200.0` | Rag |
| rag | Rag: `{'persist_dir': 'EXPERIMENT/DispositionEffect/Rag/rag_index/rag_disposition', 'docs_dir': 'examples/document-sources/files', 'url_csv': 'examples/document-sources/finance_books.csv', 'urls': ['https://en.wikipedia.org/wiki/Disposition_effect', 'https://en.wikipedia.org/wiki/Prospect_theory', 'https://www.investopedia.com/terms/d/disposition-effect.asp'], 'agent_autonomous': False, 'catalog_path': 'examples/document-sources/finance_books.csv', 'llm_suggested': False, 'llm_suggested_n_urls': 5, 'd...` | Rag |
| sell_fraction_gain | Rag: `0.5` | Rag |
| sell_fraction_loss | Rag: `0.15` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rag | rag_disposition | RAG Disposition Investor | `RagDispositionInvestor` | 3 | `examples/DispositionEffect/Rag/players.py` |

## Source Docstring Excerpts

### Rag / `RagDispositionInvestor`

```text
RAG-enhanced disposition-prone investor.

Has access to Prospect Theory and behavioral finance literature
through RAG, but still exhibits disposition effect tendencies
in decision-making.

Theory: simulation-bases.md Section 4.1 -- DispositionInvestor
Theoretical basis: Kahneman & Tversky (1979) Prospect Theory; RAG retrieves disposition effect studies.
See simulation-bases.md Section 4.1 for mathematical model.
```
