# SorosPound LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Mechanism | Persona-driven currency speculation and peg defense |
| Market | Same price/fundamental market as Rule |
| Agents | LLM macro fund, peg defender, convergence trader, opportunistic trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 LLM Macro Hedge Fund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Persona prompt frames aggressive speculative attack |
| Runtime path | LLM emits canonical trading decision from market context |

### §2.2 LLM Peg Defender

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Persona prompt frames reserve-constrained stabilization |
| Runtime path | LLM chooses support or cap actions |

### §2.3 LLM Convergence Trader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Persona prompt expresses belief that peg holds |
| Runtime path | LLM may provide stabilizing convergence demand |

### §2.4 LLM Opportunistic Trader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Persona prompt follows visible attack momentum |
| Runtime path | LLM amplifies directional pressure |

### §2.5 LLM Noise Trader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Persona prompt supplies random baseline liquidity |
| Runtime path | LLM still emits canonical order schema |

## §3 Market Mechanism Implementation

Market mechanics match Rule. LLM changes the decision generator from explicit
Python rules to persona reasoning.

## §4 Variant-Specific Features

LLM tests whether macro-attack, defense, and convergence narratives emerge from
persona prompts without changing market clearing.

## §5 Architecture Diagram

```text
Market state -> persona prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/SorosPound/LLM/players.yml`.

## §7 Running Instructions

```bash
python examples/SorosPound/LLM/run_sorospound_llm.py \
  -c configs/SorosPound/LLM/simulation.yml
```

## §8 Expected Behavior Patterns

Speculative LLM agents should increase peg pressure while defense and
convergence personas resist until credibility deteriorates.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.

