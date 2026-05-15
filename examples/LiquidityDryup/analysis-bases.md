# LiquidityDryup Simulation — Analysis Bases

## §1 Analysis Objectives

The LiquidityDryup simulation analysis quantifies the onset, severity, and duration of liquidity dry-up episodes, the role of each agent type in triggering or ameliorating the cascade, and the welfare costs of illiquidity (wealth penalties, price dislocation). The primary goal is to replicate key stylised facts from Brunnermeier & Pedersen (2009) and calibrate the simulation against historical dry-up episodes.

Primary objectives:
1. Measure the severity of the liquidity spiral (how far liquidity falls and how quickly).
2. Identify which agent behaviours (momentum, market maker withdrawal) trigger cascades.
3. Quantify price dislocation relative to fundamental during dry-up episodes.
4. Assess cross-variant differences in cascade onset and recovery speed.
5. Validate simulation against historical Amihud illiquidity ratios and TED-spread analogues.

---

## §2 Core Metrics

### §2.1 Liquidity Ratio Index (LRI)

**Category**: Market Liquidity

**Definition**: Tracks the ratio of actual market liquidity to base liquidity across rounds. Values below 0.5 indicate a dry-up episode; below 0.2 indicates severe dry-up.

**Formula**:

```
LRI(t) = total_liquidity(t) / (base_liquidity × n_market_makers)
```

Where `total_liquidity(t)` is computed from Market agent state.

**Python function**: `liquidity_ratio_index(liquidity_history, base_liquidity, n_market_makers)`

**Inputs**: `liquidity_history` (list of total liquidity per round), `base_liquidity` (config), `n_market_makers` (count)

**Interpretation**:

| LRI Value | Interpretation                                    |
|-----------|---------------------------------------------------|
| > 0.8     | Normal liquidity — all market makers active       |
| 0.5–0.8   | Partial withdrawal — some market makers withdrawn |
| 0.2–0.5   | Dry-up episode — most market makers withdrawn     |
| < 0.2     | Severe dry-up — minimal liquidity remaining       |

**Academic Basis**: Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098). LRI conceptually maps to Brunnermeier–Pedersen's market liquidity measure.

**Normal Range**: 0.6–1.0 (normal); 0.1–0.4 (during dry-up)

**Red Flag Threshold**: LRI < 0.1 (floor hit — market stability at risk) or LRI never falls below 0.5 (no dry-up observed — check `volatility_threshold`)

**Relationships**: Inversely related to PAD (price dislocation); inversely related to MPI (market price impact). LRI drives all cascade dynamics.

**Implementation Notes**: Compute from `liquidity_history` in Market agent state. Plot as time series to identify dry-up onset and recovery rounds.

---

### §2.2 Market Maker Withdrawal Fraction (MWF)

**Category**: Agent Behaviour

**Definition**: The fraction of market makers who have withdrawn in a given round. Key binary indicator of spiral onset — once MWF exceeds 0.5, a full cascade is likely.

**Formula**:

```
MWF(t) = (n_market_makers_withdrawn(t)) / (n_market_makers_total)
```

**Python function**: `market_maker_withdrawal_fraction(agent_states, round_num)`

**Inputs**: `agent_states` per round, filtered for `MarketMaker` class; `provides_liquidity = 0` indicates withdrawal

**Interpretation**:

| MWF Value | Interpretation                       |
|-----------|--------------------------------------|
| 0         | All market makers active — no stress |
| 0–0.5     | Partial stress — recovery possible   |
| > 0.5     | Majority withdrawn — cascade likely  |
| 1.0       | Full withdrawal — dry-up confirmed   |

**Academic Basis**: Grossman, S. J., & Miller, M. H. (1988). doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x). Empirical validation: during Black Monday, NYSE specialists failed to provide bids on ~30% of S&P 500 stocks.

**Normal Range**: 0 (normal); 0.5–1.0 (during dry-up)

**Red Flag Threshold**: MWF = 1.0 for > 20 consecutive rounds (simulation may be stuck in dry-up state)

**Relationships**: Driven by `|return| > volatility_threshold`. Directly determines LRI. Correlated with MPD.

**Implementation Notes**: Track `provides_liquidity` field in each round's agent output. MWF = 0 is expected for most of a calibrated simulation.

---

### §2.3 Market Price Impact (MPI)

**Category**: Market Impact

**Definition**: The effective Kyle lambda per round, computed as the ratio of price change to net order flow. Higher MPI during dry-up confirms the endogenous amplification mechanism.

**Formula**:

```
MPI(t) = |ΔP(t)| / |NetDemand(t)| if NetDemand(t) ≠ 0
```

**Python function**: `market_price_impact(price_history, trade_history)`

**Inputs**: `price_history` (round-by-round prices), `trade_history` (quantities by agent)

**Interpretation**:

| MPI Value             | Interpretation                          |
|-----------------------|-----------------------------------------|
| ≈ base `price_impact` | Normal liquidity — no amplification     |
| 2–5× base             | Moderate amplification                  |
| > 5× base             | Severe amplification — dry-up confirmed |

**Academic Basis**: Kyle, A. S. (1985). doi:[10.2307/1913210](https://doi.org/10.2307/1913210). Amihud, Y. (2002). doi:[10.1016/S1386-4181(01)00024-6](https://doi.org/10.1016/S1386-4181(01)00024-6).

**Normal Range**: 1–3× base `price_impact`; > 5× during dry-up

**Red Flag Threshold**: MPI remains at baseline throughout (no amplification — check `base_liquidity` vs. `price_impact` calibration)

**Relationships**: Directly inversely proportional to LRI (via `liquidity_factor`). Drives PAD and WPI.

**Implementation Notes**: Exclude rounds with `NetDemand = 0` from mean computation. Report as ratio to baseline (round-1 MPI).

---

### §2.4 Price-Amplitude Dislocation (PAD)

**Category**: Price Discovery

**Definition**: Maximum sustained deviation from fundamental value during a dry-up episode, normalised to fundamental. Measures how far prices can diverge when liquidity is absent.

**Formula**:

```
PAD = max(|P(t) − F| / F) over the dry-up episode (rounds where LRI < 0.5)
```

**Python function**: `price_amplitude_dislocation(price_history, fundamental, lri_history, threshold=0.5)`

**Inputs**: `price_history`, `fundamental` value, `lri_history`, `threshold` for dry-up definition

**Interpretation**:

| PAD Value | Interpretation                                           |
|-----------|----------------------------------------------------------|
| < 0.05    | Minimal dislocation — liquidity restored quickly         |
| 0.05–0.15 | Moderate dislocation                                     |
| 0.15–0.30 | Severe dislocation (calibration target for major crises) |
| > 0.30    | Extreme dislocation — may indicate model instability     |

**Academic Basis**: Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098). GFC corporate bond prices deviated 20–50% from model values during peak illiquidity.

**Normal Range**: 0.08–0.25 (calibrated to historical crises)

**Red Flag Threshold**: PAD < 0.03 (dry-up has no price effect) or PAD > 0.50 (extreme divergence — check `mean_reversion`)

**Relationships**: Driven by MPI and MWF. Inversely related to LRI. Creates trading opportunities for ValueTrader.

**Implementation Notes**: Compute only during dry-up rounds (LRI < threshold). If no dry-up occurs in a simulation run, PAD = 0.

---

### §2.5 Liquidity Persistence Duration (LPD)

**Category**: Cascade Dynamics

**Definition**: The number of consecutive rounds in which LRI remains below 0.5, measuring how long the dry-up persists. Long LPD indicates the spiral is self-sustaining; short LPD indicates rapid recovery.

**Formula**:

```
LPD = max consecutive rounds with LRI(t) < 0.5
```

**Python function**: `liquidity_persistence_duration(lri_history, threshold=0.5)`

**Inputs**: `lri_history` (list of LRI per round)

**Interpretation**:

| LPD Value    | Interpretation                   |
|--------------|----------------------------------|
| 0–5 rounds   | Transient shock — rapid recovery |
| 5–15 rounds  | Moderate dry-up episode          |
| 15–30 rounds | Sustained crisis                 |
| > 30 rounds  | Extended dry-up — structural     |

**Academic Basis**: Amihud, Y. (2002). doi:[10.1016/S1386-4181(01)00024-6](https://doi.org/10.1016/S1386-4181(01)00024-6). Historical episodes: Black Monday ~1 day (short); GFC ~6 months (long).

**Normal Range**: 5–20 rounds for a well-calibrated 100-round simulation

**Red Flag Threshold**: LPD = 0 (no dry-up — check `volatility_threshold`) or LPD > 60 (permanent dry-up — check `value_multiplier`)

**Relationships**: Determined by balance between cascade acceleration (MWF, MPI) and recovery force (ValueTrader capacity). Rag variant should show shorter LPD.

**Implementation Notes**: Report both onset round and LPD. If multiple dry-up episodes occur, report the longest.

---

### §2.6 Wealth Distribution Index (WDI)

**Category**: Welfare

**Definition**: Gini coefficient of terminal wealth across all agents. Higher WDI indicates more concentrated wealth — a dry-up redistributes wealth from LiquiditySeeker (hurt by constrained execution) to MarketMaker (who earns spread in normal times) and ValueTrader (who buys the dip).

**Formula**:

```
WDI = Gini(terminal_wealth_i for all agents i)
```

**Python function**: `wealth_distribution_index(agent_states, final_price)`

**Inputs**: `agent_states` (final cash and positions), `final_price`

**Interpretation**:

| WDI Value | Interpretation                                     |
|-----------|----------------------------------------------------|
| 0.0–0.15  | Near-equal wealth — minimal redistribution         |
| 0.15–0.30 | Moderate redistribution                            |
| 0.30–0.50 | Significant wealth concentration                   |
| > 0.50    | Extreme inequality — crisis beneficiaries dominant |

**Academic Basis**: Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098). Redistribution from liquidity-constrained to patient capital is a key feature of liquidity dry-ups.

**Normal Range**: 0.15–0.40

**Red Flag Threshold**: WDI < 0.05 (all agents roughly equal — dry-up had no distributional effect)

**Relationships**: Positively correlated with PAD and LPD; higher dislocation → more redistribution. ValueTrader WPI highest; LiquiditySeeker WPI lowest.

**Implementation Notes**: Compute at end of simulation. For a 7-agent simulation, a Gini > 0.30 is significant.

---

### §2.7 Liquidity Provider Index (LPI)

**Category**: Agent Contribution

**Definition**: Measures the share of total liquidity provided by each agent class, distinguishing systematic (MarketMaker), crisis-time (ValueTrader), and absent (others) contributors.

**Formula**:

```
LPI_class = Σ(provides_liquidity from class) / Σ(total_provides_liquidity across all rounds)
```

**Python function**: `liquidity_provider_index(trade_history)`

**Inputs**: `trade_history` with `provides_liquidity` field per agent per round

**Interpretation**: LPI_MarketMaker should be ~0.8 in normal markets, falling to ~0.2 during dry-up. LPI_ValueTrader rises during dry-up. Used to assess whether the crisis is supply-driven (market maker withdrawal) or demand-driven (excess sell orders).

**Academic Basis**: Grossman & Miller (1988); Brunnermeier & Pedersen (2009).

**Normal Range**: LPI_MarketMaker 0.6–0.9; LPI_ValueTrader 0.05–0.3

**Red Flag Threshold**: LPI_MarketMaker < 0.3 throughout (market makers never dominant — model miscalibrated)

**Implementation Notes**: Report per-agent-class LPI for full transparency. Stacked bar chart per round visualises the liquidity transition.

---

## §3 Metric Relationships

```
MWF → LRI (withdrawal fraction drives total liquidity)
LRI → MPI (lower liquidity → higher price impact, via liquidity_factor)
MPI → PAD (higher impact → larger deviations from fundamental)
PAD → LPD (large deviations persist when ValueTrader capacity is limited)
PAD + LPD → WDI (long, large dislocation redistributes more wealth)
MWF ← MomentumTrader (momentum amplifies volatility, triggering more withdrawal)
LRI → LiquiditySeeker execution (constrained orders → "missing demand")
```

---

## §4 Data Collection Requirements

| Metric | Required Data                          | Collection Frequency |
|--------|----------------------------------------|----------------------|
| LRI    | Market `liquidity_history`             | Every round          |
| MWF    | Agent `provides_liquidity` field       | Every round          |
| MPI    | Price returns + net demand per round   | Every round          |
| PAD    | Price history + fundamental + LRI      | Post-run             |
| LPD    | LRI time series                        | Post-run             |
| WDI    | Final agent states + final price       | Post-run             |
| LPI    | Per-agent `provides_liquidity` history | Every round          |

---

## §5 Cross-Scenario Predictions

| Variant | LRI(min)  | MWF(max) | PAD       | LPD   | WDI       | LPI(MM)  |
|---------|-----------|----------|-----------|-------|-----------|----------|
| Rule    | 0.05–0.20 | 0.7–1.0  | 0.10–0.25 | 10–25 | 0.25–0.45 | 0.3–0.6  |
| LLM     | 0.05–0.30 | 0.5–1.0  | 0.08–0.20 | 8–20  | 0.20–0.40 | 0.3–0.7  |
| RuleLLM | 0.05–0.25 | 0.6–1.0  | 0.09–0.22 | 9–22  | 0.22–0.42 | 0.3–0.65 |
| Rag     | 0.10–0.30 | 0.4–0.8  | 0.07–0.18 | 6–15  | 0.18–0.35 | 0.4–0.75 |

---

## §6 Validation Framework

### §6.1 Stylised Facts

1. Liquidity dry-up is self-reinforcing: once MWF > 0.5, LRI should continue to fall for at least 3 more rounds without intervention.
2. Price impact during dry-up is 3–10× the normal level (MPI multiplier).
3. `ValueTrader` wealth should exceed `LiquiditySeeker` wealth at the end of dry-up episodes.
4. Momentum traders amplify the initial shock — removing them should reduce PAD by ≥ 30%.
5. Recovery begins only when `|deviation| > trade_threshold` activates `ValueTrader` as liquidity provider.

### §6.2 Calibration Targets

| Parameter                    | Empirical Target                 | Source                           |
|------------------------------|----------------------------------|----------------------------------|
| LRI minimum during dry-up    | 0.05–0.20                        | Amihud (2002) ILLIQ spikes       |
| MPI during crisis            | 5–10× normal                     | Kyle (1985); GFC data            |
| PAD during GFC-like scenario | 0.15–0.30                        | Credit spread data, 2008         |
| LPD for major crisis         | 15–30 rounds (for 100-round sim) | Black Monday 1 day; GFC 6 months |

### §6.3 Cross-Variant Predictions

- Rule variant: most mechanical cascade; highest MWF; LRI lowest minimum.
- LLM variant: emergent coordination — MMs may observe "others withdrawing" and follow; cascade may be faster or slower depending on prompt.
- RuleLLM: rule-anchored cascade; LLM may adjust timing but spiral still occurs above threshold.
- Rag variant: lowest LPD — KB retrieves historical recovery data; MMs may re-enter sooner.

### §6.4 Validation Failure Signs

| Symptom                      | Likely Cause                    | Fix                                                          |
|------------------------------|---------------------------------|--------------------------------------------------------------|
| No dry-up (LRI always > 0.7) | `volatility_threshold` too high | Reduce `volatility_threshold` to 0.02                        |
| Permanent dry-up (LRI → 0)   | ValueTrader capacity too small  | Increase `base_liquidity_provision` or `value_multiplier`    |
| PAD < 0.03                   | `price_impact` too small        | Increase `price_impact`                                      |
| MWF = 0 always               | `volatility_threshold` too high | Reduce threshold                                             |
| WDI ≈ 0                      | All agents earn similar returns | Check that LiquiditySeeker execution is properly constrained |

---

## §7 Visualization Recommendations

1. **LRI time series**: Line chart of LRI per round; shade regions where LRI < 0.5 as "dry-up episodes".
2. **Stacked liquidity chart**: Per-round stacked bar of `provides_liquidity` by agent class (shows transition from MM-dominated to VT-only).
3. **Price deviation chart**: `(P − F) / F` per round; overlay with LRI on secondary axis.
4. **MPI evolution**: Effective price impact per round; mark dry-up onset with vertical line.
5. **Wealth trajectory**: Line chart of cumulative wealth for each agent class; identify redistribution timing.
6. **Cross-variant LRI comparison**: 4-panel chart with LRI for Rule/LLM/RuleLLM/Rag; compare minimum LRI and recovery speed.
