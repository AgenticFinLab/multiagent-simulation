# DispositionEffect / Rag Rational Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Rag Rational Investor |
| Canonical class | `RagRationalInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rag |

## Definition and Goal

RAG-enhanced rational investor.

## Financial Theory / Theoretical Basis

### Rag / `RagRationalInvestor`
- Theory: simulation-bases.md Section 4.2 -- RationalInvestor
- Theoretical basis: Expected Utility Theory; RAG retrieves rational portfolio management research.

## Behavior and Decision Logic

- Key implementation methods: No public methods were parsed.
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rag: `3` | Rag |
| initial_cash | Rag: `10000.0` | Rag |
| initial_position | Rag: `50.0` | Rag |
| initial_purchase_price | Rag: `100.0` | Rag |
| llm | Rag: `{'sys_message': 'examples.DispositionEffect.Rag.prompts:RULELLM_RATIONAL_SYS', 'user_message': 'examples.DispositionEffect.Rag.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}` | Rag |
| rag | Rag: `{'persist_dir': 'EXPERIMENT/DispositionEffect/Rag/rag_index/rag_rational', 'docs_dir': 'examples/document-sources/files', 'url_csv': 'examples/document-sources/finance_books.csv', 'urls': ['https://en.wikipedia.org/wiki/Rational_choice_theory', 'https://en.wikipedia.org/wiki/Expected_utility_hypothesis', 'https://www.investopedia.com/terms/r/rationalbehavior.asp'], 'agent_autonomous': False, 'catalog_path': 'examples/document-sources/finance_books.csv', 'llm_suggested': False, 'llm_suggested_n_u...` | Rag |
| rebalance_threshold | Rag: `0.1` | Rag |
| target_allocation | Rag: `0.5` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rag | rag_rational | RAG Rational Investor | `RagRationalInvestor` | 2 | `examples/DispositionEffect/Rag/players.py` |

## Source Docstring Excerpts

### Rag / `RagRationalInvestor`

```text
RAG-enhanced rational investor.

Uses academic research to make informed decisions,
potentially overcoming disposition biases.

Theory: simulation-bases.md Section 4.2 -- RationalInvestor
Theoretical basis: Expected Utility Theory; RAG retrieves rational portfolio management research.
See simulation-bases.md Section 4.2 for mathematical model.
```
