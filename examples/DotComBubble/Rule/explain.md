# DotComBubble Rule Variant — explain.md

## §1 Overview

The Rule variant implements the DotComBubble design with explicit threshold
rules. Bubble dynamics emerge from narrative demand, IPO profit taking,
momentum, valuation-based selling, constrained short selling, mean reversion,
and exogenous market noise.

| Aspect | Detail |
|---|---|
| Variant | Rule |
| Decision mechanism | Rules over `deviation = (price - fundamental) / fundamental` and one-period momentum |
| Design source | `simulation-bases.md §3`, §4, and §6 |
| Market broadcast | `price`, `fundamental`, `deviation`, `round` |
| Order contract | `type`, `from`, `action`, `bid_price`, `quantity`, `reasoning`, `agent_type`, `strategy` |

## §2 Theory → Implementation Mapping

| Design block | Theory component | Implementation |
|---|---|---|
| `§4.1 NewEconomyEvangelist` | Narrative demand and late capitulation | `NewEconomyEvangelist.decide()` buys above deviation `-0.20` and sells a half-sized order below `-0.30` |
| `§4.2 IPOFlipper` | IPO inventory flipping | `IPOFlipper.decide()` sells above `flip_threshold` and accumulates below fundamental |
| `§4.3 MomentumFollower` | One-period return continuation | `MomentumFollower.decide()` buys/sells when momentum crosses `±momentum_threshold` |
| `§4.4 SkepticalValueInvestor` | Fundamental anchoring | `SkepticalValueInvestor.decide()` buys below `value_buy_threshold` and sells above `value_sell_threshold` |
| `§4.5 ShortSeller` | Limits to arbitrage | `ShortSeller.decide()` sells above `short_threshold` and covers below `cover_threshold` |

The coordinator specified by `simulation-bases.md §3` is implemented by
`Market.perceive()` and `Market.decide()`.

## §3 Market Mechanism

For net demand `D(t)`, the market applies:

```text
P(t+1) = max(P(t) + λD(t) + γ(F - P(t)) + ε(t), 0.01)
ε(t) ~ Normal(0, σ)
```

The Rule configuration follows `simulation-bases.md §6`: `λ = 0.01`,
`γ = 0.005`, `σ = 1.0`, and initial price and fundamental are both `100.0`.
The positive price floor keeps all downstream deviation and affordability
calculations defined.

## §4 Variant-Specific Features

- All required config fields use fail-fast indexed access; missing inputs raise.
- Investor state initialization is shared, but each archetype retains its own
  decision rule and inventory.
- IPO, value, and short-seller starting inventories follow the corresponding
  worked examples in `simulation-bases.md §4.2.6`, §4.4.6, and §4.5.6 so their
  sell branches are reachable.
- Rule decisions are deterministic conditional on observations; the price path
  remains stochastic because the market includes `noise_std`.

## §5 Config Reference

Configuration lives under `configs/DotComBubble/Rule/`:

- `simulation.yml`: round count, output paths, and runtime settings.
- `players.yml`: class paths and all required model parameters, each with a
  `# Source:` pointer.
- `topology.yml`: star routing between the market and investor archetypes.
- `persona.yml`: recording and runtime proxy settings shared by player configs.

Stale, unused parameters from older implementations are intentionally absent.

## §6 Running Instructions

From the repository root:

```bash
python -m examples.DotComBubble.Rule.run_dotcombubble \
  -c configs/DotComBubble/Rule/simulation.yml
python -m examples.DotComBubble.Rule.analysis \
  -c configs/DotComBubble/Rule/simulation.yml
```

The simulation writes records under `EXPERIMENT/DotComBubble/Rule/records`.
Analysis writes `summary.json` and `dotcombubble_rule_dynamics.png` under the
Rule analysis directory.

For a two-round smoke test that does not resume from or write into the full-run
records, use an isolated output root, then point analysis at those records:

```bash
python -m examples.DotComBubble.Rule.run_dotcombubble \
  -c configs/DotComBubble/Rule/simulation.yml \
  --steps 2 \
  --output-root EXPERIMENT/DotComBubble/Rule/smoke
python -m examples.DotComBubble.Rule.analysis \
  -c configs/DotComBubble/Rule/simulation.yml \
  --record-path EXPERIMENT/DotComBubble/Rule/smoke/records \
  -o EXPERIMENT/DotComBubble/Rule/smoke/analysis
```

## §7 Expected Behavior

The validation target is a visible but bounded overvaluation episode, followed
by correction pressure from IPO profit taking, value investors, short sellers,
mean reversion, and momentum reversal. Exact peaks and timing vary with market
noise; use the metric bands in `analysis-bases.md §2` and §6 rather than a
single expected trajectory.

## §8 References

Theory and DOI citations are centralized in `simulation-bases.md §2`.
Parameter provenance is in `simulation-bases.md §6`; analysis definitions and
their sources are in `analysis-bases.md §2`.

## §9 Cross-Variant Role

| Comparison | Purpose |
|---|---|
| Rule vs LLM | Test whether persona-only decisions reproduce the explicit behavioral mechanisms |
| Rule vs RuleLLM | Test how language-model mediation changes decisions under explicit rule guidance |
| RuleLLM vs Rag | Test whether retrieved bubble history changes valuation discipline or trade timing |
