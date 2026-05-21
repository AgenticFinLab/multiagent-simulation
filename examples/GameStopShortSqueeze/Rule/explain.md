# GameStopShortSqueeze — Rule Variant

## §1 Overview

The Rule variant implements the GameStop Short Squeeze simulation using deterministic threshold-based rules. The short squeeze emerges from three coordinated mechanics: retail coordinated buying (§4.1), short-seller forced covering (§4.2), and gamma hedging by market makers (§4.3), opposed by institutional value selling (§4.4) and weakly amplified by momentum retail (§4.5). All agents use rules derived directly from `Rule/players.py`.

| Aspect             | Detail                                                             |
|--------------------|--------------------------------------------------------------------|
| Variant            | Rule                                                               |
| Simulation         | GameStopShortSqueeze                                               |
| Decision Mechanism | Threshold rules on deviation δ(t); initial short position for §4.2 |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                    |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                       |
| Price Model        | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t)                   |

---

## §2 Theory → Implementation Mapping

### §2.1 RetailCoordinated (`simulation-bases.md §4.1`)

| Theory Component                          | Implementation                                                                             |
|-------------------------------------------|--------------------------------------------------------------------------------------------|
| Social coordination (Barber et al., 2022) | `if cash > price * 50 and price > 0: buy_qty = min(int(cash * buy_pressure / price), 500)` |
| Buy-pressure parameter                    | `buy_pressure = 0.12` controls fraction of cash deployed per round                         |
| Cash threshold gate                       | `cash > price * 50` — requires minimum cash to trade; prevents exhausted buyers            |
| Max 500 shares                            | Position cap; social-media retail investor buying constraint                               |

### §2.2 ShortSellerHF (`simulation-bases.md §4.2`)

| Theory Component                                    | Implementation                                                                                              |
|-----------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| Short sale constraints (Diamond & Verrecchia, 1987) | `initial_position = -1000` — starts fully short                                                             |
| Forced covering on squeeze                          | `if position < 0 and deviation > cover_threshold: cover_qty = min(abs(position), int(abs(position) * 0.5))` |
| Partial covering                                    | Covers 50% of remaining short position per round when deviation > `cover_threshold = 0.05`                  |
| Squeeze mechanics                                   | Covering creates buying pressure, amplifying price rise, forcing more covering                              |

### §2.3 MarketMakerGamma (`simulation-bases.md §4.3`)

| Theory Component                  | Implementation                                                                                     |
|-----------------------------------|----------------------------------------------------------------------------------------------------|
| Gamma squeeze (Jarrow & Li, 2021) | `hedge_qty = int(abs(deviation) * gamma_exposure * 5000)`                                          |
| Delta hedging buy                 | `if deviation > 0 and hedge_qty > 0: buy_qty = min(hedge_qty, int(cash / price))`                  |
| Gamma exposure parameter          | `gamma_exposure = 0.3` scales hedging response to deviation                                       |
| Mechanical hedging                | Market maker must hedge delta exposure as options go in-the-money; creates systematic buy pressure |

### §2.4 InstitutionalValue (`simulation-bases.md §4.4`)

| Theory Component          | Implementation                                                                                             |
|---------------------------|------------------------------------------------------------------------------------------------------------|
| Fundamental value selling | `initial_position = 2000` — starts long at pre-squeeze price                                               |
| Sell on overvaluation     | `if deviation > sell_threshold: sell_qty = min(1000, max(position, 0))`; `sell_threshold = 0.30`            |
| IEP trigger               | Sells entire long position when deviation > `sell_threshold`; tracks first round of full exit (IEP metric) |
| Countervailing force      | §4.4 provides selling pressure opposing the squeeze forces of §4.1, §4.2, §4.3                             |

### §2.5 MomentumRetail (`simulation-bases.md §4.5`)

| Theory Component                    | Implementation                                                                  |
|-------------------------------------|---------------------------------------------------------------------------------|
| FOMO momentum (Lyocsa et al., 2022) | `if deviation > fomo_threshold: buy_qty = min(50, int(cash / price))`; `fomo_threshold = 0.05` |
| Small position cap                  | 50 shares max — small retail investor; low individual impact but many instances |
| FOMO activation                     | Only buys on positive deviation > `fomo_threshold`; does not short or sell      |

---

## §3 Rule-Specific Notes

- **Squeeze cascade**: §4.1 buys → price rises → deviation increases → §4.2 forced to cover → more buying → §4.3 gamma hedges → more buying → reinforcing squeeze.
- **Three-phase dynamics**: Pre-squeeze (deviation < cover_threshold), squeeze (§4.2 covering, §4.3 hedging), exhaustion (§4.4 sells out, §4.1 runs out of cash).
- **IEP as key diagnostic**: First round where §4.4 position = 0 marks the exhaustion of institutional supply — squeeze enters unconstrained phase.
- **Market broadcast**: Standard `price`, `fundamental`, `deviation`, `round`; all agents use `deviation` directly.

---

## §4 Expected Ranges (Rule Variant)

| Metric                               | Rule Expected Range                      | Interpretation                                                |
|--------------------------------------|------------------------------------------|---------------------------------------------------------------|
| SQI (Squeeze Intensity Index)        | 1.0–5.0                                  | Peak deviation; GME analog ≈24; simulation with 5 agents ≈1–5 |
| PAR (Price-Area Ratio)               | 0.2–1.0                                  | Mean positive deviation over full simulation                  |
| ACC (Agent Coalition)                | §4.1: 40–60%, §4.2: 20–40%, §4.3: 10–30% | Coalition volume shares during squeeze phase                  |
| SCD (Squeeze Collapse Duration)      | 2–8 rounds                               | Rounds from peak deviation to 80% collapse                    |
| IEP (Institutional Exhaustion Point) | Rounds 3–10                              | First round §4.4 exits fully; marks squeeze peak              |
| WTI (Wealth Transfer Index)          | 0.10–0.40                                | Fraction of short-seller wealth transferred to retail/MM      |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity,
squeeze-phase patterns, and agent-level contribution patterns before accepting a
sample.

## §6 Running Instructions

```bash
python examples/GameStopShortSqueeze/Rule/run_gamestopshortsqueeze_rule.py \
  -c configs/GameStopShortSqueeze/Rule/simulation.yml
```

## §7 Expected Behavior

The Rule variant should produce a deterministic short-squeeze arc: coordinated
retail buying lifts price above fundamental, short sellers cover, gamma hedgers
add mechanical demand, and institutional value sellers eventually provide the
main countervailing supply.

## §8 Cross-Variant Role

Rule is the baseline used to evaluate whether LLM, RuleLLM, and RAG variants
preserve the GameStop squeeze mechanism while changing decision timing,
quantity selection, or knowledge use.

## §9 Implementation Traceability

Investor classes in `players.py` map directly to `simulation-bases.md §4.1-§4.5`.
Analysis functions in `analysis.py` should fail fast when market records are
missing rather than fabricating zero-valued metrics.
