# MarketCrash Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | RuleLLM-style decision making augmented with retrieved crisis knowledge |
| Market | Same rule-based market as Rule/RuleLLM |
| Knowledge Sources | Shared `examples/document-sources` corpus and scenario RAG index |
| Runtime Change | Documentation-only backfill in this commit |

## §2 Theory → Implementation Mapping

### §2.1 Rag Risk-Parity / Volatility Targeting

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | RAG prompt combines market state with retrieved risk-parity/crash context |
| Effect | Retrieved context may strengthen or moderate deleveraging reasoning |

### §2.2 Rag Leveraged Fund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Retrieved leverage-cycle knowledge informs margin spiral reasoning |
| Effect | May change urgency or explanation, not market schema |

### §2.3 Rag Market Maker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Retrieved liquidity-crisis context informs quote withdrawal |
| Effect | Liquidity behavior should remain schema-compatible |

### §2.4 Rag Panic Seller

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Retrieved crisis narratives may amplify panic reasoning |
| Effect | Panic timing/quantity may differ from RuleLLM |

### §2.5 Rag Bottom Fisher

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | Retrieved value/limits-of-arbitrage context informs contrarian buying |
| Effect | Stabilizing response may be earlier or more cautious |

## §3 Market Mechanism Implementation

The market remains rule-based. RAG changes only the context supplied to LLM
investors before structured decisions are parsed.

## §4 Variant-Specific Features

Rag adds retrieval setup, embedding/index configuration, and per-agent
`private_knowledge.rag` settings. If retrieval fails, behavior should be
reviewed as a quality issue.

## §5 Architecture Diagram

```text
Market update -> retrieve context -> LLM prompt -> decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/MarketCrash/Rag/players.yml`, including top-level
`knowledge` and per-agent `private_knowledge.rag`.

## §7 Running Instructions

```bash
python examples/MarketCrash/Rag/run_marketcrash_rag.py \
  -c configs/MarketCrash/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Rag should preserve crash mechanics while retrieved crisis knowledge changes
reasoning, urgency, or stabilization interpretation.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
