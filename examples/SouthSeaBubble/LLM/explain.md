# SouthSeaBubble LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Mechanism | Persona-driven narrative bubble and correction behavior |
| Market | Same price/fundamental market as Rule |
| Agents | LLM insider, narrative believer, skeptical analyst, arbitrageur, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| LLMInsiderAdvantaged | `simulation-bases.md §4.1` | Persona prompt models privileged timing |
| LLMNarrativeBeliever | `simulation-bases.md §4.2` | Persona prompt models promotional-story demand |
| LLMSkepticalAnalyst | `simulation-bases.md §4.3` | Persona prompt models cash-flow skepticism |
| LLMArbitrageur | `simulation-bases.md §4.4` | Persona prompt models mispricing correction |
| LLMNoiseTrader | `simulation-bases.md §4.5` | Persona prompt supplies baseline liquidity |

## §3 Market Mechanism Implementation

Market mechanics match Rule. LLM changes only the decision generator from
explicit rules to persona reasoning and canonical JSON output.

## §4 Variant-Specific Features

LLM tests whether narrative overpricing and skepticism emerge from investor
personas without changing the clearing mechanism.

## §5 Architecture Diagram

```text
Market state -> persona prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/SouthSeaBubble/LLM/players.yml`.

## §7 Running Instructions

```bash
python examples/SouthSeaBubble/LLM/run_southseabubble_llm.py \
  -c configs/SouthSeaBubble/LLM/simulation.yml
```

## §8 Expected Behavior Patterns

Narrative and insider personas may amplify bubble demand; skeptical and
arbitrage personas should resist overvaluation.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.

