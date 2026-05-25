# RepresentativenessBias RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Simulation | RepresentativenessBias |
| Decision Mechanism | LLM reasoning constrained by explicit decision rules |
| Theory Reference | `simulation-bases.md §2` and `§4` |
| Market Broadcast | Same Market implementation as Rule |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMPatternMatcher (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Prototype matching | `RULELLM_PATTERN_MATCHER_SYS` includes pattern trigger rules |
| Quantity formula | Prompt states `min(800, int(abs(deviation) * 5000))` |
| Runtime path | `RuleLLMInvestor.decide()` validates `action`, `bid_price`, `quantity`, and `reasoning` |

### §2.2 RuleLLMCategoryOvergeneralizer (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Category extrapolation | Prompt labels positive deviation as growth category and negative deviation as falling-knife category |
| Small sample bias | Rule text preserves threshold-based overgeneralization |
| Runtime path | Quantity is capped by available cash or position |

### §2.3 RuleLLMBayesianUpdater (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Bayesian discipline | Prompt activates only outside the 5% base-rate band |
| Fundamental correction | Buys undervaluation and sells overvaluation |
| Runtime path | Failed parse after three attempts raises an error |

### §2.4 RuleLLMContrarianStatistical (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Arbitrage against biased pressure | Prompt identifies large deviations as representativeness-driven mispricing |
| Correction threshold | 5% threshold matches the Rule stabilizer |
| Runtime path | Orders include canonical fields for post-run audit |

### §2.5 RuleLLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Random liquidity | Prompt states 30% random trade probability |
| Neutral role | Persona is liquidity-oriented, not biased |
| Runtime path | LLM output remains bounded by state constraints |

## §3 Market Mechanism

Market mechanics are unchanged from Rule. RuleLLM changes only the investor
decision generator.

## §4 Variant Architecture

```text
Market state -> == PERSONA == + == DECISION RULES == prompt -> LLM -> validated order
```

## §5 Config Reference

Primary config: `configs/RepresentativenessBias/RuleLLM/players.yml`.
LLM settings live under `extras.llm`.

## §6 Running Instructions

```bash
python examples/RepresentativenessBias/RuleLLM/run_representativenessbias_rulellm.py \
  -c configs/RepresentativenessBias/RuleLLM/simulation.yml
```

## §7 Expected Behavior

RuleLLM should keep the Rule sign and threshold structure while allowing
language reasoning to explain or modestly modulate decisions.

## §8 References

See `simulation-bases.md §2` for full citations.

## §9 Variant Comparison

See `simulation-bases.md §9`.
