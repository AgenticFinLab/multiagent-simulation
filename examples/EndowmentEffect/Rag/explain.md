# EndowmentEffect Rag — Implementation Guide

## 1. Overview

The Rag variant combines the RuleLLM personas and decision rules with retrieved
document context. `RagLLMInvestor` retrieves before inference, validates the
model response, applies configured size and portfolio constraints, and sends a
canonical order to the shared Rule `Market`.

## 2. Theory → Implementation Mapping

| Design block | Rag class | Prompt/retrieval implementation |
|---|---|---|
| `simulation-bases.md §4.1` EndowedHolder | `RagLLMEndowedHolder` | ownership persona and premium rule; market-state retrieval query |
| `simulation-bases.md §4.2` StatusQuoSeller | `RagLLMStatusQuoSeller` | inertia persona and high-action threshold; market-state retrieval query |
| `simulation-bases.md §4.3` RationalArbitrageur | `RagLLMRationalArbitrageur` | symmetric fundamental rule; market-state retrieval query |
| `simulation-bases.md §4.4` NewBuyer | `RagLLMNewBuyer` | no-ownership persona and entry rule; market-state retrieval query |
| `simulation-bases.md §4.5` NoiseTrader | `RagLLMNoiseTrader` | intermittent-trading persona and rule; market-state retrieval query |

The inherited prompts retain literal `== PERSONA ==` and
`== DECISION RULES ==` sections. Retrieved passages are evidence for applying
those rules; they do not replace them.

## 3. Environment and Round Flow

`Market` is imported from `Rule/players.py` and implements the price update in
`simulation-bases.md §3.1`. Each round broadcasts `price`, `fundamental`, and
`deviation`. Investors retrieve context, request one decision, enforce cash and
inventory constraints, and send an `order` payload back to the market.

## 4. Rag Architecture and I/O Contract

`ResourceManager` resolves shared and agent-local paths. `KnowledgeStore`
loads a local index, copies a shared index, or builds from processed documents.
A file lock prevents concurrent actors from racing while publishing the shared
index. Missing required documents or configuration fails fast.

The model decision must contain exactly `action`, `bid_price`, `quantity`, and
`reasoning`, with private reasoning parsed from `<analysis>`. Runtime payloads
add `analysis`, `strategy`, `rag_context`, and `outbound_messages`.
`_RAG_FALLBACK` is the stable context sentinel consumed by analysis.

## 5. Configuration

`configs/EndowmentEffect/Rag/players.yml` supplies market parameters, initial
portfolios, RuleLLM parameters, model settings, retry limits, and per-agent RAG
settings. Required values are read directly. The simulator injects the top-level
`knowledge` block into player extras before setup.

## 6. Running Instructions

From the repository root:

```bash
python -m examples.EndowmentEffect.Rag.run_endowmenteffect_rag \
  -c configs/EndowmentEffect/Rag/simulation.yml
```

The embedding and inference backends require the environment variables named
in the YAML templates. Index construction may dominate startup time; round
execution starts after actor and knowledge-store setup.

## 7. Expected Behavior

The behavioral signature should remain comparable to RuleLLM: biased holders
resist selling, fundamental agents counter mispricing, and noise trading adds
background liquidity. Retrieval can moderate or reinforce those decisions, so
directional claims require matched repeated runs rather than a single trace.

## 8. Verification and Failure Modes

Syntax/import tests do not call external services. The Rag smoke test injects a
fake knowledge store and fake model response to exercise prompt construction,
decision validation, state serialization, action creation, and retrieval
coverage. Full startup additionally requires processed documents or a valid
shared index, embedding credentials, and inference credentials.

## 9. References and Variant Comparison

Theory and DOI citations live in `simulation-bases.md §2`; parameter sources
live in §6; metric definitions and calibration targets live in
`analysis-bases.md §§2 and 6`; the four-variant comparison is in
`simulation-bases.md §9`.
