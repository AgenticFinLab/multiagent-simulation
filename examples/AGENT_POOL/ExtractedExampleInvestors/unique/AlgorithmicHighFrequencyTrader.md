# Algorithmic, high-frequency, and program-trading agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Algorithmic, high-frequency, and program-trading agents |
| Merged profiles | 3 |
| Scenarios | BlackMonday1987, FlashCrash |
| Observed names | Algorithmic Trader, High Frequency Trader, Program Trader |

## Consolidated Definition and Goals

- **BlackMonday1987 / Program Trader**: The ProgramTrader is an institutional investor running automated execution algorithms that trigger large block orders when price thresholds are breached. Unlike the PortfolioInsurer (who sells proportionally to deviation), the ProgramTrader sells with convex amplification: larger deviations trigger disproportionately larger sells. This models the discrete tier-based program sell orders documented in the Brady Commission report, where each successive price threshold activated a new wave of automated selling at even greater volume. The ProgramTrader is the simulation's dominant per-round force during cascade escalation -- generating the heaviest selling waves at the worst price levels.
- **FlashCrash / Algorithmic Trader**: **Role:** Trend-following algorithm; mid-speed amplifier.
- **FlashCrash / High Frequency Trader**: **Role:** Ultra-fast momentum trader; primary crash trigger.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.3 -- ProgramTrader
- Theoretical basis: Brady Commission (1988) program trading feedback loops;
- LLM-driven program trader -- automated feedback amplifier. Theory: simulation-bases.md Section 4.3.
- RuleLLM-driven program trader -- automated feedback amplifier. Theory: simulation-bases.md Section 4.3.
- RAG-augmented program trader -- automated feedback amplifier. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.3 -- AlgorithmicTrader
- Theoretical basis: Trend-following algorithm as positive-feedback mechanism;
- LLM-driven algorithmic trader -- trend-following momentum via LLM systematic reasoning. Theory: simulation-bases.md Section 4.3.
- Hybrid: Trend-following algorithm rules + LLM systematic reasoning. Theory: simulation-bases.md Section 4.3.
- RAG-augmented algorithmic trader -- trend-following rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.1 -- HighFrequencyTrader
- Theoretical basis: Kirilenko et al. (2017) HFT flash crash role; momentum
- LLM-driven high-frequency trader -- momentum detection and rapid bets via LLM reasoning. Theory: simulation-bases.md Section 4.1.
- Hybrid: HFT momentum rules + LLM rapid reasoning. Theory: simulation-bases.md Section 4.1.
- RAG-augmented HFT -- momentum rules + LLM rapid reasoning + retrieved knowledge. Theory: simulation-bases.md Section 4.1.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| BlackMonday1987 | Program Trader | [BlackMonday1987__ProgramTrader.md](../BlackMonday1987__ProgramTrader.md) |
| FlashCrash | Algorithmic Trader | [FlashCrash__AlgorithmicTrader.md](../FlashCrash__AlgorithmicTrader.md) |
| FlashCrash | High Frequency Trader | [FlashCrash__HighFrequencyTrader.md](../FlashCrash__HighFrequencyTrader.md) |

