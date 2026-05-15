# HerdEffect Rag — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                                         |
|--------------------|--------------------------------------------------------------------------------|
| Variant            | Rag                                                                            |
| Simulation         | HerdEffect                                                                     |
| Decision Mechanism | RAG-augmented LLM with rule formulas + retrieved document context              |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                |
| Market Broadcast   | `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, `round` |
| Price Model        | Same order-book clearing as Rule — Market agent unchanged                      |

The Rag variant is the most capable: it combines rule formula grounding (as in RuleLLM) with document retrieval from a corpus of academic momentum literature, bubble case studies, and historical crash data. Retrieved context shapes agent conviction and exit timing.

## §2 Theory → Implementation Mapping

### §2.1 RagMomentumInvestor (simulation-bases.md §4.1)

| Theory Component                 | Implementation                                                                           |
|----------------------------------|------------------------------------------------------------------------------------------|
| Shiller (1984) positive feedback | Rule formula in system prompt: `bid_price = price × (1 + lambda_price × ret)`            |
| RAG retrieval                    | Retrieves Jegadeesh & Titman (1993) momentum evidence; historical momentum return series |
| Document-grounded conviction     | Retrieved momentum returns may strengthen buy conviction in uptrends                     |

### §2.2 RagContrarianInvestor (simulation-bases.md §4.2)

| Theory Component                        | Implementation                                                                                |
|-----------------------------------------|-----------------------------------------------------------------------------------------------|
| De Bondt & Thaler (1985) mean reversion | Rule formula in system prompt; fundamental from `extras`                                      |
| RAG retrieval                           | Retrieves De Bondt & Thaler (1985) reversal evidence; historical value investing case studies |
| Timing improvement                      | Retrieved valuation benchmarks may improve contrarian entry timing → higher REI               |

### §2.3 RagRiskAverseInvestor (simulation-bases.md §4.3)

| Theory Component               | Implementation                                                                          |
|--------------------------------|-----------------------------------------------------------------------------------------|
| Markowitz (1952) mean-variance | Rule variance formula in system prompt                                                  |
| RAG retrieval                  | Retrieves volatility regime studies; Black Monday/dot-com crash histories               |
| Earlier exit                   | Historical crash awareness may trigger position reduction earlier than Rule → lower MDD |

### §2.4 RagNoiseTrader (simulation-bases.md §4.4)

| Theory Component                    | Implementation                                                    |
|-------------------------------------|-------------------------------------------------------------------|
| De Long et al. (1990) noise trading | Rule random bid/quantity in system prompt                         |
| RAG retrieval                       | Retrieves market microstructure noise studies; liquidity research |
| Modulated noise                     | Retrieved liquidity studies may anchor bid price variance         |

### §2.5 RagAggressiveInvestor (simulation-bases.md §4.5)

| Theory Component                  | Implementation                                                             |
|-----------------------------------|----------------------------------------------------------------------------|
| Leveraged momentum + acceleration | Rule formula in system prompt: `kappa × ret + accel_bonus × acceleration`  |
| RAG retrieval                     | Retrieves leveraged trading case studies; dot-com bubble acceleration data |
| Bounded by rule                   | Rule ±80 cap preserved even with document-reinforced conviction            |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3*

```
P(t+1) = P(t) + α × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Identical to Rule variant. RAG context modifies agent bid values and quantities through the LLM layer, not through market mechanics.

## §4 Variant Architecture

| Component      | Detail                                                                        |
|----------------|-------------------------------------------------------------------------------|
| Base class     | `BaseInvestor` (Rag subclass)                                                 |
| Primary engine | `calculate_bid()` rule formulas + LLM                                         |
| RAG component  | `ResourceManager.resolve_agent_knowledge()` retrieves docs per agent          |
| Vector store   | Shared RAG index of momentum/crash literature; agent-specific local knowledge |
| Inference      | `LangChainAPIInference` with retrieved context prepended                      |
| Output         | Same `{bid_price, quantity, strategy, cash, position}` as Rule                |

## §5 Config Reference

Config file: `configs/HerdEffect/Rag/simulation.yml`

Key extras:
- All Rule parameters (lambda_price, beta, kappa, accel_bonus, etc.)
- `lm_name`: LLM model identifier
- `knowledge`: RAG knowledge config (backend, global_uri, rag settings)
- `private_knowledge`: agent-specific document sources
- `record_path`: RAG index path

## §6 Running Instructions

```bash
python -m examples.HerdEffect.Rag.run_herd_effect \
    -c configs/HerdEffect/Rag/simulation.yml
```

Or via Streamlit UI: select "HerdEffect" → "Rag" variant.

## §7 Expected Behavior

- **Document-grounded momentum**: MomentumInvestor conviction anchored to retrieved Jegadeesh-Titman evidence
- **Earlier crash awareness**: RagRiskAverseInvestor exits earlier than Rule due to retrieved crash histories → slightly lower MDD
- **Higher REI**: Retrieved De Bondt & Thaler reversal evidence improves ContrarianInvestor timing
- **Bounded amplification**: AggressiveInvestor still ±80 cap despite document-reinforced conviction
- **Most interpretable**: Agent reasoning cites specific retrieved documents for every decision

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Shiller (1984) `doi:10.2307/2534436` — RagMomentumInvestor corpus anchor
- Jegadeesh & Titman (1993) `doi:10.1111/j.1540-6261.1993.tb04702.x` — retrieved momentum evidence
- De Bondt & Thaler (1985) `doi:10.1111/j.1540-6261.1985.tb05004.x` — RagContrarianInvestor corpus
- Markowitz (1952) `doi:10.1111/j.1540-6261.1952.tb01525.x` — RagRiskAverseInvestor corpus

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
