# Retail Coordinator

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Social-media-coordinated retail traders (Reddit/WSB style) |
| Theory Family         | Coordination Games / Retail Investor Attention |
| Behavioral Tendency   | **Amplifying** - coordinates buying pressure on targeted stocks, creating short squeezes and momentum |
| Time Horizon          | short |
| Risk Tolerance        | very high |
| Information Asymmetry | low (public social media signal) |
| Determinism           | stochastic |

## Definition and Goals

This agent models a cohort of retail traders who coordinate via social media platforms (Reddit WallStreetBets, Twitter/X, Discord) to concentrate buying pressure on specific stocks, often those with high short interest. The real-world counterpart is the GameStop/AMC phenomenon documented by Pedersen (2022) and the attention-driven trading behavior described by Barber and Odean (2008). The agent buys aggressively when a coordination signal is active and the target has sufficient short interest.

The decision goal is to participate in coordinated buying when social signals and short-interest conditions align, creating momentum and potential short squeezes. It is not a fundamental investor and it does not use valuation. Non-goals: it must not trade without a coordination signal, and it must not short-sell (retail coordinators are characteristically long-only in squeeze scenarios).

## Theoretical Foundation

**Coordination games and retail attention**:
- Theory / Study: Coordination games; Game stopped? GME short squeeze.
- Citation: Cooper, R. (1999). *Coordination Games: Complementarities and Macroeconomics*. Cambridge University Press. https://doi.org/10.1017/CBO9780511609428
- Citation: Barber, B. M., & Odean, T. (2008). All that glitters: The effect of attention and news on the buying behavior of individual and institutional investors. *Review of Financial Studies*, 21(2), 785-818. https://doi.org/10.1093/rfs/hhm079
- Citation: Pedersen, L. H. (2022). Game stopped? GME short squeeze and market dynamics. *NBER Working Paper*. https://doi.org/10.3386/w28146
- Core Insight: Retail investors face a coordination game: concentrated buying is profitable if enough participants join (strategic complementarity). Social media solves the coordination problem by providing a focal point. Attention-grabbing stocks with high short interest become natural targets.
- Mathematical Formulation: `Q = coordination_weight * cash / price * coordination_intensity` when `coordination_signal > coord_threshold` AND `short_interest > si_threshold`.
- Empirical Evidence: Pedersen documents GME dynamics; Barber & Odean show attention drives retail buying; Cookson et al. (2023) show social media disagreement predicts trading volume.
- Relevance to This Agent: The agent operationalizes coordinated retail buying driven by social signals and short-interest targeting.
- Calibration Source: `coord_threshold` 0.3-0.7, `si_threshold` 0.15-0.40, `coordination_weight` 0.10-0.40.
- Falsification Conditions: If the agent trades without a coordination signal or short-sells, the design is falsified.
- Alternative Theories: Pure noise trading (De Long et al. 1990); momentum without coordination mechanism.

## Design Purpose and Activation Triggers

Purpose: Model the destabilizing effect of retail coordination on targeted stocks, demonstrating how social media can solve coordination problems and generate short squeezes and momentum cascades.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `coordination_signal` available (0-1, social media coordination intensity)
- `short_interest` available (fraction of float sold short)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `coordination_signal > coord_threshold` AND `short_interest > si_threshold` AND `cash > 0`: buy aggressively.
- `coordination_signal < exit_threshold` AND `position > 0`: sell (coordination fading, take profits).
- `<Default>`: hold.

Deactivation Conditions:
- coordination signal fades below exit threshold.
- cash fully deployed.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| strong coordination + high SI | aggressive buying | squeeze potential, strategic complementarity |
| strong coordination + low SI | moderate buying | momentum without squeeze |
| fading coordination | profit-taking sells | coordination breakdown |
| no coordination | holds | no focal point |

Environmental Dependencies: requires social media coordination signal and short interest data.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `coordination_signal` | environment | float [0,1] | yes | social media coordination intensity |
| `short_interest` | environment | float [0,1] | yes | fraction of float short |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity for exit |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity is clamped to available resources.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `coordination_signal` | Continuous | 1 tick | focal point intensity |
| `short_interest` | Continuous | 1 tick | squeeze potential |
| `cash` | State | persistent | buy constraint |
| `position` | State | persistent | exit capacity |

Does NOT use: fundamental valuation, institutional order flow, private information, leverage.

#### Core Behavioral Mechanism

1. Read `price`, `coordination_signal`, `short_interest`, `cash`, and `position`.
2. If `coordination_signal > coord_threshold` and `cash > 0`:
   - `coordination_intensity = (coordination_signal - coord_threshold) / (1 - coord_threshold)`.
   - `si_multiplier = 1 + si_boost * max(0, short_interest - si_threshold)`.
   - `q = coordination_weight * cash / price * coordination_intensity * si_multiplier`.
   - Apply noise: `q = q * (1 + N(0, noise_sigma))`, floor to 0.
   - Buy.
3. If `coordination_signal < exit_threshold` and `position > 0`:
   - `q = exit_fraction * position`. Sell.
4. Otherwise, hold.
5. Emit the decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `coordination_weight * cash / price * intensity * si_multiplier` for buys; `exit_fraction * position` for sells |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | never short-sells; position cannot go negative |
| Resource cap | buy capped by cash / price |
| Exit rule | sell when coordination fades below exit threshold |

#### Mathematical Model

`q_buy = min(cash/price, coordination_weight * (cash/price) * I * M * (1+epsilon))` if `coordination_signal > theta_coord` and `short_interest > theta_si`; `q_sell = min(position, exit_fraction * position)` if `coordination_signal < theta_exit`; otherwise `q = 0`. Where `I = (coord_signal - theta_coord)/(1 - theta_coord)`, `M = 1 + si_boost * max(0, short_interest - theta_si)`, `epsilon ~ N(0, noise_sigma)`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_coord` | coordination threshold | 0.50 | Cooper (1999) |
| `theta_si` | short interest threshold | 0.20 | Pedersen (2022) |
| `theta_exit` | exit/profit-taking threshold | 0.25 | calibration |
| `coordination_weight` | fraction of cash to deploy | 0.20 | calibration |
| `si_boost` | short-interest multiplier scaling | 2.0 | Pedersen (2022) |
| `exit_fraction` | fraction of position to sell on exit | 0.40 | calibration |
| `noise_sigma` | stochastic noise | 0.10 | calibration (high for retail heterogeneity) |

#### Behavioral Properties

- Time horizon: short, because coordination is ephemeral and profit-taking is quick.
- Risk tolerance: very high, because participants accept potential total loss for squeeze upside.
- Information asymmetry: low, all use the same public social signal.
- Psychological profile: FOMO-driven, community-reinforced, high conviction during coordination phase.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `coord_threshold` | float | 0.50 | [0.30, 0.70] | high | coordination signal level to trigger buying | Higher -> fewer coordination events | Cooper (1999) |
| `si_threshold` | float | 0.20 | [0.15, 0.40] | medium | minimum short interest for squeeze targeting | Higher -> fewer targets | Pedersen (2022) |
| `coordination_weight` | float | 0.20 | [0.10, 0.40] | high | fraction of cash deployed per tick | Higher -> more concentrated buying | calibration |
| `si_boost` | float | 2.0 | [1.0, 4.0] | medium | multiplier for high short interest | Higher -> more aggressive on high-SI targets | Pedersen (2022) |
| `exit_threshold` | float | 0.25 | [0.10, 0.40] | medium | coordination fade level for profit-taking | Lower -> later exit | calibration |
| `exit_fraction` | float | 0.40 | [0.20, 0.80] | medium | fraction of position sold on exit | Higher -> faster position unwinding | calibration |
| `noise_sigma` | float | 0.10 | [0.0, 0.20] | low | stochastic sizing noise | Higher -> more heterogeneity | calibration |

## Worked Numerical Examples

### Case 1 - Coordinated Squeeze Buy

System state: price 50.0, coordination_signal 0.80, short_interest 0.35, cash 10000, position 50.
Calculation: `I = (0.80 - 0.50)/(1-0.50) = 0.60`. `M = 1 + 2.0*(0.35-0.20) = 1.30`. `q = 0.20 * (10000/50) * 0.60 * 1.30 = 0.20 * 200 * 0.78 = 31.2 -> 31`.
Decision: buy 31.
State update: cash decreases by 1550, position increases by 31.

### Case 2 - Coordination Fade Exit

System state: price 80.0, coordination_signal 0.15, short_interest 0.30, cash 2000, position 200.
Calculation: `0.15 < 0.25` exit threshold. `q = 0.40 * 200 = 80`.
Decision: sell 80.
State update: position decreases by 80, cash increases by 6400.

### Case 3 - No Coordination

System state: price 50.0, coordination_signal 0.30, short_interest 0.40, cash 10000, position 100.
Calculation: `0.30 < 0.50` coordination threshold not met; `0.30 > 0.25` exit not triggered.
Decision: hold.
State update: unchanged.

### Edge Case - Coordination Active but Low Short Interest

System state: price 50.0, coordination_signal 0.70, short_interest 0.10, cash 10000, position 0.
Calculation: `coordination_signal > 0.50` but `short_interest 0.10 < 0.20` threshold. Reduced mode: `si_multiplier = 1 + 2.0*max(0, 0.10-0.20) = 1.0`. Still buys but without SI boost: `I = 0.40`. `q = 0.20 * 200 * 0.40 * 1.0 = 16`.
Decision: buy 16.
State update: cash decreases by 800, position increases by 16.

## Behavioral Verification and Calibration

- Given `coordination_signal > coord_threshold` and `cash > 0`, agent must buy.
- Given `coordination_signal < exit_threshold` and `position > 0`, agent must sell.
- Agent must never short-sell.
- Agent must never trade without coordination signal present.
- Higher `short_interest` must produce larger order sizes (ceteris paribus).

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-si-boost | `si_boost = 0` | short interest targeting amplifies squeezes | decrease | max price spike |
| low-coord-threshold | `coord_threshold = 0.30` | lower barrier -> more frequent coordination | increase | coordination event frequency |
| no-exit | `exit_threshold = 0` | exit selling limits duration | increase | position holding duration |
| no-noise | `noise_sigma = 0` | heterogeneity reduces synchronization | increase | order time clustering |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Cooper, R. (1999). Coordination Games. https://doi.org/10.1017/CBO9780511609428 | Strategic complementarity theory |
| 2 | Barber, B. M., & Odean, T. (2008). All that glitters. https://doi.org/10.1093/rfs/hhm079 | Attention-driven retail trading |
| 3 | Pedersen, L. H. (2022). Game stopped? https://doi.org/10.3386/w28146 | GME short squeeze analysis |
| 4 | Cookson, J. A., Engelberg, J., & Mullins, W. (2023). Echo chambers. https://doi.org/10.1093/rfs/hhad031 | Social media and trading |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-retail-coordinator.png) |
| Status | draft |
