# MentalAccountingSunkCostTrader

## Summary

| Field                        | Content                                                                                                                                                 |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Mental-accounting, house-money, sunk-cost, and opportunity-cost agents                                                                                  |
| Theory Family                | Behavioral Finance (mental accounting, sunk-cost fallacy, escalation of commitment)                                                                     |
| Market Role                  | **Destabilising in losses, mixed in gains** — sticky losers, escalation flow, and asymmetric risk-taking after gains hold prices away from fundamentals |
| Time Horizon                 | medium                                                                                                                                                  |
| Risk Tolerance               | state-dependent (varies with realised P&L sign)                                                                                                         |
| Information Asymmetry        | partial (uses own entry price as private reference)                                                                                                     |
| Determinism                  | deterministic                                                                                                                                           |
| Merged profiles              | 6 (HouseMoneyTrader, MentalAccountant, SunkCostHolder ×2, CommitmentEscalator, OpportunityCostTrader — across two scenarios)                            |
| Source scenarios             | MentalAccounting, SunkCostFallacy                                                                                                                       |
| Canonical sub-archetype enum | `ma_mode ∈ {house_money, mental_accountant, sunk_cost_holder, commitment_escalator, opportunity_cost_trader}`                                           |

## Definition and Goals

This agent models the **mental-accounting / sunk-cost / house-money / commitment-escalation / opportunity-cost trader** in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the family of agents whose decisions are governed by reference-dependent valuation segregated across mental accounts, prior-outcome-conditional risk taking, or escalation-of-commitment to losing positions. The six merged profiles span the house-money trader who scales risk up after gains and down after losses (Thaler-Johnson 1990), the mental accountant who segregates positions into separate per-account books (Thaler 1985, 1999), the sunk-cost holder who refuses to realise losses (Arkes-Blumer 1985; Shefrin-Statman 1985), the commitment escalator who doubles down on losing positions to justify prior choices (Staw 1976), and the opportunity-cost trader who reallocates capital from under-performers to better available uses (Thaler 1980).

**Primary goals:**
1. Reproduce the empirical "house-money" effect of Thaler-Johnson (1990) — increased risk taking after prior gains and decreased risk taking after prior losses.
2. Generate the asymmetric realisation pattern of mental accounting: SELL bias for gains-above-threshold accounts, HOLD bias for loss accounts, in the spirit of Shefrin-Statman (1985) and Odean (1998).
3. Produce the sunk-cost stickiness and escalation flow documented by Arkes-Blumer (1985) and Staw (1976), creating sticky losing inventory that is unwound only on substantial reversal.
4. Permit ablation of single mechanisms (account segregation vs. house-money risk scaling vs. escalation) to isolate which channel matters per scenario.

**Non-goals:**
1. Does NOT solve a forward-looking utility problem; activation is rule-based reference-dependent.
2. Does NOT model utility from the act of selling (no realisation utility beyond reference-point comparison).
3. Does NOT model multi-account hierarchical optimisation; mental accounts are independent.
4. Does NOT capture prospect-theory probability weighting (handled by `LossAversionDispositionInvestor`).

## Theoretical Foundation

### Theory 1 — Thaler & Johnson House-Money Effect

- **Theory/Study**: Thaler, R. H. and Johnson, E. J. (1990). Gambling with the house money and trying to break even: The effects of prior outcomes on risky choice. *Management Science*, 36(6), 643–660.
- **Citation+DOI**: https://doi.org/10.1287/mnsc.36.6.643
- **Core Insight**: After a gain, individuals are more willing to accept additional risk ("playing with the house's money"); after a loss, individuals either become more risk-averse or take a long-shot bet to break even. The result is path-dependent risk taking that is inconsistent with stable utility functions.
- **Mathematical Formulation**: Risk multiplier `m_t = m_gain` if `pnl_{t−1} > 0` else `m_loss`; trade size `Q* = m_t · base_size · |signal_t|`.
- **Empirical Evidence**: Thaler-Johnson (1990) Tables I–III lab experiments; Massa-Simonov (2005, AFA) confirm in field data; Coval-Shumway (2005, JF DOI 10.1111/j.1540-6261.2005.00723.x) for traders.
- **Relevance to This Agent**: Anchors the `house_money` mode and provides the `gain_risk_multiplier`, `loss_risk_multiplier` parameter calibration.
- **Calibration Source**: Thaler-Johnson (1990) experimental coefficients; Coval-Shumway (2005) trader-level estimates.
- **Falsification Conditions**: If `gain_risk_multiplier = loss_risk_multiplier`, mode collapses to base-size active trader. Test: shuffle prior P&L sign; agent flow should be unaffected.
- **Alternative Theories**: Barberis-Huang-Santos (2001, QJE DOI 10.1162/003355301556310) — prospect-theory + narrow framing alternative; Coval-Shumway (2005) — loss-chasing; Kahneman-Tversky (1979, Econometrica) — prospect theory direct.

### Theory 2 — Thaler Mental Accounting

- **Theory/Study**: Thaler, R. H. (1985). Mental accounting and consumer choice. *Marketing Science*, 4(3), 199–214. Thaler, R. H. (1999). Mental accounting matters. *Journal of Behavioral Decision Making*, 12(3), 183–206.
- **Citation+DOI**: https://doi.org/10.1287/mksc.4.3.199 ; https://doi.org/10.1002/(SICI)1099-0771(199909)12:3%3C183::AID-BDM318%3E3.0.CO;2-F
- **Core Insight**: Investors segregate holdings into separate "mental accounts" with reference-dependent local utility. Decisions on each account are made relative to that account's reference point, leading to globally sub-optimal portfolio behaviour such as concurrent borrowing and saving.
- **Mathematical Formulation**: For each account `j`, `pnl_j = (P_t − B_j) / B_j`; sell rule: `sell_j = ρ_g · qty_j` if `pnl_j > θ_g`; `sell_j = ρ_l · qty_j` if `pnl_j < −θ_l` (the small reluctant capitulation).
- **Empirical Evidence**: Thaler (1999) survey of 200+ studies; Kumar-Lim (2008, JF DOI 10.1111/j.1540-6261.2008.01386.x) document narrow-framing in retail trades; Frydman-Barberis-Camerer-Bossaerts-Rangel (2014, JF) brain-imaging confirmation.
- **Relevance to This Agent**: Anchors the `mental_accountant` mode; provides the `num_accounts` parameter for sub-portfolio segregation.
- **Calibration Source**: Thaler (1999); Kumar-Lim (2008) cross-section.
- **Falsification Conditions**: If `num_accounts = 1`, mental-accountant collapses to a standard reference-dependent trader. Test: per-account flow patterns should disappear.
- **Alternative Theories**: Barberis-Huang (2001, JF DOI 10.1111/0022-1082.00367) — narrow framing model; Kőszegi-Rabin (2006, QJE) — endogenous reference-point preferences; Read-Loewenstein-Rabin (1999, JRiU) — choice bracketing.

### Theory 3 — Arkes & Blumer Sunk-Cost Fallacy

- **Theory/Study**: Arkes, H. R. and Blumer, C. (1985). The psychology of sunk cost. *Organizational Behavior and Human Decision Processes*, 35(1), 124–140.
- **Citation+DOI**: https://doi.org/10.1016/0749-5978(85)90049-4
- **Core Insight**: Decision makers continue committing resources to a course of action whenever they have made a prior investment of time, money, or effort, even when prospective costs and benefits suggest abandonment. The bias persists in financial decisions and reduces ex-post realisation rates of losses.
- **Mathematical Formulation**: Effective sell threshold `θ_g_eff = θ_g · (1 + sunk_cost_weight)` where `sunk_cost_weight ≈ 0.5–1.0`; the agent will only realise gains beyond the inflated threshold and never realises pure losses.
- **Empirical Evidence**: Arkes-Blumer (1985) experimental Tables I–IV; Strough-Mehta-McFall-Schuller (2008) age-related effects; Soman (2001) cumulative cost effects.
- **Relevance to This Agent**: Anchors the `sunk_cost_holder` mode; produces sticky losing inventory.
- **Calibration Source**: Arkes-Blumer (1985); Strough et al. (2008).
- **Falsification Conditions**: If `sunk_cost_weight = 0`, mode collapses to base mental-accountant; the lag-of-realisation pattern should disappear.
- **Alternative Theories**: Shefrin-Statman (1985, JF DOI 10.1111/j.1540-6261.1985.tb05002.x) — disposition effect as alternative; Kahneman-Tversky (1979) — prospect-theory loss aversion; Heath (1995, OBHDP) — distinguishing sunk costs from "completion" effects.

### Theory 4 — Staw Escalation of Commitment

- **Theory/Study**: Staw, B. M. (1976). Knee-deep in the big muddy: A study of escalating commitment to a chosen course of action. *Organizational Behavior and Human Performance*, 16(1), 27–44.
- **Citation+DOI**: https://doi.org/10.1016/0030-5073(76)90005-2
- **Core Insight**: When confronted with negative outcomes from a prior decision, decision-makers often invest additional resources to justify their initial choice ("self-justification" and "responsibility-bias"). The pattern is robust across business decisions, foreign-policy actions, and personal investment.
- **Mathematical Formulation**: Escalation rule: if `pnl_t < −θ_esc` and `position_t > 0` (still long), buy additional `escalation_size · |pnl_t|` shares. Escalation cap: `position_t ≤ position_0 · (1 + max_escalation_factor)`.
- **Empirical Evidence**: Staw (1976) experimental data; Brockner (1992, AcadMgmtRev) review; Sleesman et al. (2012, JAP DOI 10.1037/a0026954) meta-analysis effect size 0.4.
- **Relevance to This Agent**: Anchors the `commitment_escalator` mode; produces destabilising buy-side flow into losing positions.
- **Calibration Source**: Staw (1976) Tables I–II; Sleesman et al. (2012) meta-analysis.
- **Falsification Conditions**: If `max_escalation_factor = 0`, escalation is disabled; mode collapses to sunk-cost holder.
- **Alternative Theories**: Festinger (1957) — cognitive dissonance theory; Brockner (1992) — entrapment frameworks; Whyte (1986, AcadMgmtRev) — group escalation.

### Theory 5 — Thaler Opportunity-Cost Salience

- **Theory/Study**: Thaler, R. H. (1980). Toward a positive theory of consumer choice. *Journal of Economic Behavior and Organization*, 1(1), 39–60.
- **Citation+DOI**: https://doi.org/10.1016/0167-2681(80)90051-7
- **Core Insight**: Opportunity costs are systematically under-weighted relative to out-of-pocket costs in decision-making. Conversely, when opportunity costs are made salient (e.g., via comparison with a benchmark), agents reallocate from under-performers to better available uses.
- **Mathematical Formulation**: Comparison signal `c_t = (r_alt_t − r_self_t)`; if `c_t > θ_opp` for `T_persist` consecutive ticks, sell the under-performer and reallocate to alternative.
- **Empirical Evidence**: Thaler (1980) survey of consumer studies; Frederick et al. (2009, JCR) experimental confirmation; Spiller (2011, JCR DOI 10.1086/660045) opportunity-cost neglect across financial decisions.
- **Relevance to This Agent**: Anchors the `opportunity_cost_trader` mode; provides the comparison-benchmark mechanism that opposes sunk-cost stickiness.
- **Calibration Source**: Spiller (2011); Frederick et al. (2009) experimental treatments.
- **Falsification Conditions**: If alternative-benchmark return `r_alt_t` unavailable or constant, agent reverts to no-action; cross-section of asset rotation should disappear.
- **Alternative Theories**: Camerer-Loewenstein-Prelec (2005, JEL) — neuroeconomics; Hsee-Loewenstein-Blount-Bazerman (1999, PsychBulletin) — joint vs. separate evaluation.

## Design Purpose and Activation Triggers

| Trigger condition                        | Activated mode            | Effect                                            |
|------------------------------------------|---------------------------|---------------------------------------------------|
| `pnl_{t−1} > 0` AND `                    | signal_t                  | > θ_act`                                          |
| `pnl_{t−1} ≤ 0` AND `                    | signal_t                  | > θ_act`                                          |
| Account `pnl_j > θ_g`                    | `mental_accountant`       | SELL `ρ_g · qty_j` of account `j`                 |
| Account `pnl_j < −θ_l`                   | `mental_accountant`       | SELL `ρ_l · qty_j` (small reluctant capitulation) |
| `pnl < 0` AND `                          | pnl                       | > θ_esc` AND `position > 0`                       |
| `pnl < 0` AND `                          | pnl                       | < θ_g_eff` (sticky region)                        |
| `r_alt − r_self > θ_opp` for `T_persist` | `opportunity_cost_trader` | SELL self, reallocate                             |
| `<Default>`                              | any mode                  | HOLD (no order)                                   |

**Prerequisite Signals:** price `P_t`, fundamental or signal proxy (for `house_money` direction), prior-period realised P&L `pnl_{t−1}`, per-lot or per-account cost basis `B_j`, alternative-asset return `r_alt_t` (for opportunity-cost mode).

**Missing-Signal Policy:** If `B_j` missing, fall back to weighted-average cost. If `r_alt` missing, deactivate `opportunity_cost_trader`. If `pnl_{t−1}` unobservable, treat `house_money` as risk-neutral (`m_gain = m_loss = 1`).

**Deactivation Conditions:** Cooldown `T_cool = 50` ticks after capitulation. Permanent deactivation if `cum_drawdown < dd_kill = −0.40`.

Market Contribution by Regime:

| Regime         | Contribution         | Mechanism                                                                                               |
|----------------|----------------------|---------------------------------------------------------------------------------------------------------|
| Calm           | Mildly destabilising | Mental-accountant realises small gains; modest reflexive flow                                           |
| Trending boom  | Destabilising        | House-money trader scales up directional flow; mental-accountant sells gains (mild dampening)           |
| Trending crash | Destabilising        | Sunk-cost holders refuse to sell; commitment-escalators add to losers; both prolong the down-move       |
| Stress / Panic | Destabilising        | Escalation peaks; sunk-cost stickiness reduces sell-side liquidity below baseline                       |
| Reversal phase | Mixed-to-stabilising | Sticky losers eventually capitulate as `θ_g_eff` is finally reached; opportunity-cost rotation kicks in |

Interaction with other agents: opposes `LossAversionDispositionInvestor`'s gains-realisation in the gain region but reinforces it in the loss region; complementary to `OverconfidenceAndRepresentativenessTrader` after gains (both amplify directional flow); absorbed by `MarketMakerLiquidityAgent` and `Arbitrageur` who profit from the resulting persistence.

## Behavioural Framework

#### 3.6.1 State Variables

- `position`: integer share count
- `cash`: float
- `lots` (per `mental_accountant`): list of `{cost_basis, qty, account_id}` entries
- `entry_price`: float per-position reference for sunk-cost
- `pnl_{t−1}`: float, prior-tick realised P&L
- `cum_drawdown`: float
- `position_0`: integer, initial position level (for escalation cap)
- `cooldown_ticks`: integer
- `escalation_count_t`: integer, number of escalation buys this episode

#### 3.6.2 Decision Rule

```
on tick t:
    if cooldown_ticks > 0: cooldown_ticks -= 1; emit nothing; return
    pnl_pct = (P_t − entry_price) / entry_price
    signal = (P_t − F_t) / F_t   if F_t available else 0

    if ma_mode == house_money:
        m = m_gain if pnl_{t−1} > 0 else m_loss
        if |signal| > θ_act:
            Q* = sign(-signal) · m · base_size · |signal|
            emit MARKET; return

    if ma_mode == mental_accountant:
        for each account j in lots:
            pnl_j = (P_t − B_j) / B_j
            if pnl_j > θ_g:
                emit MARKET sell ρ_g · qty_j
            elif pnl_j < −θ_l:
                emit MARKET sell ρ_l · qty_j   # small capitulation
        return

    if ma_mode == sunk_cost_holder:
        θ_g_eff = θ_g · (1 + sunk_cost_weight)
        if pnl_pct > θ_g_eff:
            emit MARKET sell ρ_g_sc · position
        # never sell at a loss
        return

    if ma_mode == commitment_escalator:
        if pnl_pct < −θ_esc and position > 0 and escalation_count_t < max_escalations:
            Q* = escalation_size · |pnl_pct| · cash / P_t
            Q* = min(Q*, position_0 · max_escalation_factor − position)
            emit MARKET buy Q*; escalation_count_t += 1
        return

    if ma_mode == opportunity_cost_trader:
        if r_alt_t − r_self_t > θ_opp:
            persist_counter += 1
            if persist_counter ≥ T_persist:
                emit MARKET sell · rotation_fraction · position
                persist_counter ← 0
        else:
            persist_counter ← max(0, persist_counter − 1)
        return
```

#### 3.6.3 Reference-Point Update

```
on entry (new position): entry_price ← fill_price
on partial sell:        entry_price unchanged (FIFO depletion of qty)
on full close:          entry_price ← None; escalation_count_t ← 0
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, F_t, entry_price, lots, position_t, cash_t, pnl_{t−1}, r_alt_t, cum_drawdown_t, ma_mode, RNG_seed)` the output `(action, Q*)` is a pure function. Heterogeneity comes from instantiation-time draws on `m_gain, m_loss, sunk_cost_weight, escalation_size, θ_g, θ_l, θ_esc, num_accounts`.

Does NOT use: `bid_ask_spread`, full order-book depth, traded volume, peer counter-party identity, news content, sentiment, options chain, social-graph signals, or own factor exposures. The decision is taken from `(P_t, F_t, entry_price/lots, pnl, r_alt)` alone.

**State variables:**
- Pre-decide observables: `P_t`, `F_t`, `r_alt_t`, `pnl_{t−1}`, account-level `B_j`.
- Internal: `position`, `cash`, `lots`, `entry_price`, `position_0`, `escalation_count_t`, `persist_counter`, `cum_drawdown`, `cooldown_ticks`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty`; `cash_{t+1} = cash_t − filled_qty · fill_price`.
2. If buy: append lot `(fill_price, filled_qty, j)` to `lots[j]` per account. If sell: FIFO-deplete oldest lots; realised P&L credited to `pnl_t`.
3. `equity_{t+1} = cash_{t+1} + position_{t+1} · P_{t+1}`; `peak_equity_{t+1} = max(...)`; `cum_drawdown` rolling.
4. If `position_{t+1} = 0`: reset `entry_price ← None`, `escalation_count_t ← 0`.
5. If sell triggered: `cooldown_ticks ← T_cool`.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                       |
|----------------------|------------------------------------------------------------|
| Order types allowed  | MARKET only (reference-dependent decisions are fast)       |
| Price level rule     | Cross the spread; no limit price                           |
| Order quantity rule  | Per-mode: see 3.6.2 (capped by cash, position, escalation) |
| Order lifetime       | One tick (immediate-or-cancel marketable)                  |
| Cancellation policy  | Cancel-on-fill or end-of-tick                              |
| Inventory constraint | `                                                          |
| Wealth/leverage cap  | No leverage; `cash ≥ 0`                                    |
| Stop-loss/kill rule  | `cum_drawdown < dd_kill = −0.40` ⇒ permanent deactivation  |

## Parameters

| Symbol                  | Name                        | Default | Range          | Units    | Source                 | Sensitivity | Notes                           |
|-------------------------|-----------------------------|---------|----------------|----------|------------------------|-------------|---------------------------------|
| `m_gain`                | Gain risk multiplier        | 2.0     | [1.0, 4.0]     | none     | Thaler-Johnson (1990)  | High        | House-money risk scale          |
| `m_loss`                | Loss risk multiplier        | 0.5     | [0.0, 1.0]     | none     | Thaler-Johnson (1990)  | High        | Risk reduction post-loss        |
| `θ_act`                 | Activation threshold        | 0.01    | [0.005, 0.05]  | return   | Odean (1998)           | Med         | House-money signal cutoff       |
| `θ_g`                   | Gain-realisation threshold  | 0.05    | [0.02, 0.20]   | return   | Shefrin-Statman (1985) | High        | Disposition cousin              |
| `θ_l`                   | Loss-capitulation threshold | 0.20    | [0.10, 0.40]   | return   | Odean (1998)           | Med         | Reluctant capitulation          |
| `ρ_g`                   | Gain sell fraction          | 0.70    | [0.10, 1.0]    | fraction | Odean (1998) Table II  | Med         | Per-account gain realisation    |
| `ρ_l`                   | Loss sell fraction          | 0.20    | [0.05, 0.50]   | fraction | Odean (1998)           | Med         | Reluctant per-account           |
| `num_accounts`          | Mental accounts             | 3       | [1, 10]        | count    | Kumar-Lim (2008)       | Med         | Segregation count               |
| `sunk_cost_weight`      | Sunk-cost inflation         | 0.6     | [0.0, 1.5]     | none     | Arkes-Blumer (1985)    | High        | Multiplies `θ_g_eff`            |
| `θ_esc`                 | Escalation trigger          | 0.10    | [0.05, 0.30]   | return   | Staw (1976)            | High        | Loss size for escalation        |
| `escalation_size`       | Escalation flow scale       | 0.20    | [0.05, 0.50]   | none     | Sleesman et al. (2012) | High        | Fraction of cash per escalation |
| `max_escalation_factor` | Max position cap            | 1.0     | [0.0, 3.0]     | none     | implementation choice  | Med         | Multiplier on initial position  |
| `max_escalations`       | Max escalation events       | 3       | [0, 10]        | count    | implementation choice  | Low         | Episode cap                     |
| `θ_opp`                 | Opportunity-cost trigger    | 0.05    | [0.02, 0.20]   | return   | Spiller (2011)         | Med         | Alt-vs-self spread              |
| `T_persist`             | Persistence required        | 5       | [1, 30]        | ticks    | Spiller (2011)         | Low         | Ticks of consistent advantage   |
| `rotation_fraction`     | Rotation trade size         | 0.50    | [0.10, 1.0]    | fraction | implementation choice  | Med         | Fraction sold on rotation       |
| `base_size`             | Base trade size             | 400     | [100, 1000]    | shares   | retail avg             | Low         | Default scale                   |
| `T_cool`                | Cooldown horizon            | 50      | [10, 200]      | ticks    | implementation choice  | Low         | Post-trade pause                |
| `dd_kill`               | Drawdown deactivation       | −0.40   | [−0.60, −0.15] | return   | risk cap               | Low         | Permanent deactivation          |

## Population and Heterogeneity

```yaml
ma_mode_mixture:
  house_money: 0.20
  mental_accountant: 0.30        # largest by Thaler (1999) survey
  sunk_cost_holder: 0.20
  commitment_escalator: 0.15
  opportunity_cost_trader: 0.15
heterogeneity:
  m_gain: Lognormal(ln 2.0, 0.30)
  m_loss: Beta(2, 5)
  sunk_cost_weight: Lognormal(ln 0.6, 0.40)
  theta_esc: Lognormal(ln 0.10, 0.50)
  escalation_size: Beta(2, 8)
  num_accounts: DiscreteUniform[1, 10]
```

The mixture reflects the population fractions implied by Kumar-Lim (2008) for narrow-framing investors and Sleesman et al. (2012) escalation prevalence in business decisions.

## Worked Numerical Examples

**Case 1 — House-money after a gain (`ma_mode = house_money`)**: `pnl_{t−1} = +1000, signal = −0.02, m_gain = 2.0, base_size = 400`.
- Multiplier `m = 2.0`; `Q* = sign(-(-0.02)) · 2.0 · 400 · 0.02 = 16` shares.
- Above `θ_act`; emit MARKET buy 16 shares.
- Action: BUY 16 shares (scaled up vs. base 8).

**Case 2 — Mental-accountant gain realisation (`ma_mode = mental_accountant`)**: account `j`: `B_j = 100, qty_j = 200, P_t = 108`. `pnl_j = +0.08 > θ_g = 0.05`.
- `sell qty = ρ_g · qty_j = 0.70 · 200 = 140` shares.
- Action: MARKET sell 140 of account `j`.

**Case 3 — Sunk-cost stickiness (`ma_mode = sunk_cost_holder`)**: `entry_price = 100, P_t = 92, sunk_cost_weight = 0.6, θ_g = 0.05`.
- `θ_g_eff = 0.05 · 1.6 = 0.08`. `pnl_pct = −0.08`; below threshold and negative.
- Action: HOLD; no sell at any loss.

**Case 4 — Commitment escalation (`ma_mode = commitment_escalator`)**: `entry_price = 100, P_t = 88, position = 500, cash = 50,000, escalation_size = 0.20, max_escalation_factor = 1.0, escalation_count_t = 1, max_escalations = 3`.
- `pnl_pct = −0.12 < −θ_esc = −0.10`; escalation triggered.
- `Q* = 0.20 · 0.12 · 50000 / 88 ≈ 13.6` → round to 14 shares.
- Cap by `position_0 · max_escalation_factor − position = 500 · 1.0 − 500 = 0`. Stop-cap binds.
- Action: HOLD (cap binds); next tick if cap allows, escalate.

**Edge case — Escalation cap binding**: As Case 4 shows, when `position ≥ position_0 · (1 + max_escalation_factor)`, escalation halts even with deepening losses. Variant `commitment_escalator` then reverts to `sunk_cost_holder` behaviour.

## Validation and Calibration

- **V1 — House-money asymmetry (Theory 1)**: Conditional on `pnl_{t−1} > 0`, agent flow magnitude is `m_gain / m_loss ≈ 4×` larger than after losses. Ablation: set `m_gain = m_loss`.
- **V2 — Per-account gain realisation (Theory 2)**: Within a `mental_accountant` agent, sell-on-gain rate is `ρ_g / ρ_l ≈ 3.5×` higher than sell-on-loss rate. Ablation: set `num_accounts = 1`.
- **V3 — Sunk-cost stickiness (Theory 3)**: Hazard ratio of selling at a loss vs. selling at a gain is < 0.10 in `sunk_cost_holder` mode. Ablation: set `sunk_cost_weight = 0`.
- **V4 — Escalation flow (Theory 4)**: After a 10%+ loss, `commitment_escalator` agent's average buy flow is 2-3× pre-loss baseline; positive autocorrelation in losses → buy flow. Ablation: set `max_escalation_factor = 0`.
- **V5 — Opportunity-cost rotation (Theory 5)**: When alternative outperforms by `>θ_opp` for `T_persist` ticks, rotation flow rises 50%+ above baseline. Ablation: set `r_alt_t = r_self_t`.
- **V6 — Drawdown deactivation**: Across the full population, fraction permanently deactivated by `dd_kill` matches the Coval-Shumway (2005) trader-attrition estimate (~5-10% per year).

**Ablation Hooks**:
- `m_gain = m_loss = 1.0` → disables house-money (Theory 1).
- `num_accounts = 1` → disables mental segregation (Theory 2).
- `sunk_cost_weight = 0` → disables sunk-cost stickiness (Theory 3).
- `max_escalation_factor = 0` → disables escalation (Theory 4).
- `θ_opp = ∞` → disables opportunity-cost rotation (Theory 5).

## Academic References

1. Thaler, R. H. and Johnson, E. J. (1990). Gambling with the house money and trying to break even: The effects of prior outcomes on risky choice. *Management Science*, 36(6), 643–660. https://doi.org/10.1287/mnsc.36.6.643
2. Coval, J. D. and Shumway, T. (2005). Do behavioral biases affect prices? *Journal of Finance*, 60(1), 1–34. https://doi.org/10.1111/j.1540-6261.2005.00723.x
3. Thaler, R. H. (1985). Mental accounting and consumer choice. *Marketing Science*, 4(3), 199–214. https://doi.org/10.1287/mksc.4.3.199
4. Thaler, R. H. (1999). Mental accounting matters. *Journal of Behavioral Decision Making*, 12(3), 183–206. https://doi.org/10.1002/(SICI)1099-0771(199909)12:3%3C183::AID-BDM318%3E3.0.CO;2-F
5. Barberis, N. and Huang, M. (2001). Mental accounting, loss aversion, and individual stock returns. *Journal of Finance*, 56(4), 1247–1292. https://doi.org/10.1111/0022-1082.00367
6. Kumar, A. and Lim, S. S. (2008). How do decision frames influence the stock investment choices of individual investors? *Management Science*, 54(6), 1052–1064. https://doi.org/10.1287/mnsc.1070.0845
7. Shefrin, H. and Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777–790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
8. Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775–1798. https://doi.org/10.1111/0022-1082.00072
9. Arkes, H. R. and Blumer, C. (1985). The psychology of sunk cost. *Organizational Behavior and Human Decision Processes*, 35(1), 124–140. https://doi.org/10.1016/0749-5978(85)90049-4
10. Staw, B. M. (1976). Knee-deep in the big muddy: A study of escalating commitment to a chosen course of action. *Organizational Behavior and Human Performance*, 16(1), 27–44. https://doi.org/10.1016/0030-5073(76)90005-2
11. Sleesman, D. J., Conlon, D. E., McNamara, G. and Miles, J. E. (2012). Cleaning up the big muddy: A meta-analytic review of the determinants of escalation of commitment. *Journal of Applied Psychology*, 97(3), 541–562. https://doi.org/10.1037/a0026954
12. Brockner, J. (1992). The escalation of commitment to a failing course of action: Toward theoretical progress. *Academy of Management Review*, 17(1), 39–61. https://doi.org/10.5465/amr.1992.4279568
13. Thaler, R. H. (1980). Toward a positive theory of consumer choice. *Journal of Economic Behavior and Organization*, 1(1), 39–60. https://doi.org/10.1016/0167-2681(80)90051-7
14. Spiller, S. A. (2011). Opportunity cost consideration. *Journal of Consumer Research*, 38(4), 595–610. https://doi.org/10.1086/660045
15. Kőszegi, B. and Rabin, M. (2006). A model of reference-dependent preferences. *Quarterly Journal of Economics*, 121(4), 1133–1165. https://doi.org/10.1162/qjec.121.4.1133
16. Frydman, C., Barberis, N., Camerer, C., Bossaerts, P. and Rangel, A. (2014). Using neural data to test a theory of investor behavior: An application to realization utility. *Journal of Finance*, 69(2), 907–946. https://doi.org/10.1111/jofi.12126

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/MentalAccountingSunkCostTrader.md` (legacy); six merged scenario profiles from `MentalAccounting`, `SunkCostFallacy`.
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 4.2 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
