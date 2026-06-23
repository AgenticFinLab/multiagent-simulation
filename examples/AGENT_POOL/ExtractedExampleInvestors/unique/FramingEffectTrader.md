# Framing-Effect Investors and Framing Arbitrageurs

## Summary

| Field              | Content                                                                                                                                                                                 |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype          | Framing-Effect Investors and Framing Arbitrageurs                                                                                                                                       |
| Sub-archetype enum | `frame_mode ∈ {gain_frame_follower, loss_frame_reactor, frame_arbitrageur}`                                                                                                             |
| Market Role        | Behavioural-bias amplifier — buys positive deviations and sells negative ones, reinforcing trends; arbitrageur mode supplies counter-pressure by exploiting framing-driven mispricings. |
| Merged profiles    | 2 (with arbitrageur mode added for completeness)                                                                                                                                        |
| Scenarios          | FramingEffect                                                                                                                                                                           |
| Observed names     | Gain Frame Follower, Loss Frame Reactor                                                                                                                                                 |
| Decision target    | Buy / sell quantity proportional to fundamental-price deviation, with a frame-dependent intensity coefficient.                                                                          |
| Time horizon       | Short to medium (single-tick deviation response with multi-tick persistence).                                                                                                           |
| Information access | Last price, fundamental proxy, own cash / position, frame label (gain vs. loss); no order-book depth, no peer identity.                                                                 |
| Risk profile       | Trend-reinforcing in both rising and falling regimes; bounded by share-cap and cash.                                                                                                    |

## Definition and Goals

This archetype models investors whose decisions depend not only on the magnitude of price-vs-fundamental deviation, but on whether that deviation is framed as a "gain" (P_t > V_t) or a "loss" (P_t < V_t). Following Tversky & Kahneman (1981), individuals are risk-averse over gains and risk-seeking over losses, generating asymmetric buy / sell intensities. In aggregate, both gain-frame and loss-frame followers buy positive deviations and sell negative ones, jointly amplifying trends.

**Goals.**
1. Translate framing-induced asymmetries into trading flow.
2. Reproduce the empirical fact that retail flows are sensitive to gain / loss frame labelling on the same numerical content.
3. Provide an arbitrageur counter-mode that fades framing-driven over-reactions.

**Non-goals.**
- Acting on real fundamentals beyond V_t.
- Two-sided market making.
- Persistent inventory-management.

## Theoretical Foundation

### Theory 1 — Prospect Theory and Framing (Tversky & Kahneman 1981)

| Field                    | Content                                                                                                                                                                        |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | The Framing of Decisions (Tversky & Kahneman 1981)                                                                                                                             |
| Citation                 | Tversky, A., & Kahneman, D. (1981). The framing of decisions and the psychology of choice. *Science*, 211(4481), 453–458.                                                      |
| DOI                      | 10.1126/science.7455683                                                                                                                                                        |
| Core Insight             | Identical outcomes elicit different choices depending on whether they are framed as gains or losses; risk aversion in gains, risk seeking in losses (S-shaped value function). |
| Mathematical Formulation | Value function `v(x) = x^α` for x > 0, `v(x) = −λ·(−x)^β` for x < 0, with `λ > 1`, `α, β ∈ (0, 1)`.                                                                            |
| Empirical Evidence       | Asian-disease problem; >70% reversal between gain / loss frames on identical lotteries.                                                                                        |
| Relevance to This Agent  | Justifies frame-dependent intensity coefficients in the decision rule.                                                                                                         |
| Calibration Source       | Tversky & Kahneman (1992) — α=β=0.88, λ=2.25.                                                                                                                                  |
| Falsification Conditions | If decisions are invariant to gain/loss frame on identical numerical content, the theory fails.                                                                                |
| Alternative Theories     | Expected utility (von Neumann-Morgenstern) — predicts frame-invariance; rejected.                                                                                              |

### Theory 2 — Reference Dependence and Loss Aversion (Kahneman & Tversky 1979)

| Field                    | Content                                                                                                                  |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Prospect Theory                                                                                                          |
| Citation                 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. |
| DOI                      | 10.2307/1914185                                                                                                          |
| Core Insight             | Outcomes are evaluated relative to a reference point (here, V_t); losses loom larger than gains by factor λ ≈ 2.         |
| Mathematical Formulation | `Q* = θ_frame · sign(P_t − V_t) ·                                                                                        |
| Empirical Evidence       | Endowment effect, equity premium puzzle, disposition effect — all hinge on reference-dependent loss aversion.            |
| Relevance to This Agent  | Defines V_t as the reference point and asymmetric gradient via λ.                                                        |
| Calibration Source       | Tversky & Kahneman (1992); Booij, van Praag, & van de Kuilen (2010).                                                     |
| Falsification Conditions | If sell intensity is symmetric to buy intensity in absolute deviation, λ = 1 and theory rejected.                        |
| Alternative Theories     | Symmetric utility (mean-variance) — predicts no asymmetry.                                                               |

### Theory 3 — Attribute Framing and Choice (Levin, Schneider, Gaeth 1998)

| Field                    | Content                                                                                                                                                                                                               |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Typology of Framing Effects                                                                                                                                                                                           |
| Citation                 | Levin, I. P., Schneider, S. L., & Gaeth, G. J. (1998). All frames are not created equal: A typology and critical analysis of framing effects. *Organizational Behavior and Human Decision Processes*, 76(2), 149–188. |
| DOI                      | 10.1006/obhd.1998.2804                                                                                                                                                                                                |
| Core Insight             | Three distinct framing types: risky-choice, attribute, goal; each produces measurable preference reversals on identical content.                                                                                      |
| Mathematical Formulation | Frame multiplier `m_frame ∈ {m_gain, m_loss}` applied to baseline demand.                                                                                                                                             |
| Empirical Evidence       | Meta-analysis of 100+ framing experiments; effect-size d ≈ 0.5–1.0.                                                                                                                                                   |
| Relevance to This Agent  | Justifies the discrete-frame switch in `frame_mode`.                                                                                                                                                                  |
| Calibration Source       | Levin et al. (1998) meta-effects.                                                                                                                                                                                     |
| Falsification Conditions | If frame label has no measurable effect on demand at identical V_t / P_t, the theory fails.                                                                                                                           |
| Alternative Theories     | Pure rational decoding — predicts d ≈ 0; rejected by 30 years of evidence.                                                                                                                                            |

### Theory 4 — Limits to Framing Arbitrage (Barberis & Thaler 2003)

| Field                    | Content                                                                                                                           |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | A Survey of Behavioral Finance                                                                                                    |
| Citation                 | Barberis, N., & Thaler, R. (2003). A survey of behavioral finance. *Handbook of the Economics of Finance*, 1, 1053–1128.          |
| DOI                      | 10.1016/S1574-0102(03)01027-6                                                                                                     |
| Core Insight             | Framing-induced mispricings persist because rational arbitrageurs face limits to arbitrage (capital, horizon, noise-trader risk). |
| Mathematical Formulation | Mispricing magnitude `μ_t =                                                                                                       |
| Empirical Evidence       | Closed-end fund discounts, twin-stock spreads, IPO under-pricing.                                                                 |
| Relevance to This Agent  | Justifies the `frame_arbitrageur` mode and its bounded capacity.                                                                  |
| Calibration Source       | Barberis & Thaler (2003).                                                                                                         |
| Falsification Conditions | If arbitrageurs eliminate framing mispricings instantly, theory fails.                                                            |
| Alternative Theories     | Frictionless arbitrage — rejected empirically.                                                                                    |

### Theory 5 — Trend Amplification by Behavioural Traders (DeLong, Shleifer, Summers, Waldmann 1990)

| Field                    | Content                                                                                                                                                                                       |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Theory/Study             | Positive-Feedback Trading and Destabilising Speculation                                                                                                                                       |
| Citation                 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379–395. |
| DOI                      | 10.1111/j.1540-6261.1990.tb03695.x                                                                                                                                                            |
| Core Insight             | Even rational traders can find it profitable to ride positive-feedback flows from behavioural traders rather than fade them.                                                                  |
| Mathematical Formulation | Demand impulse from frame followers: `D_t = c · (P_t − V_t)`; price drift accelerated when c > 0.                                                                                             |
| Empirical Evidence       | Momentum effect (Jegadeesh & Titman 1993).                                                                                                                                                    |
| Relevance to This Agent  | Provides the macro-level mechanism for trend amplification.                                                                                                                                   |
| Calibration Source       | DSSW (1990); Jegadeesh & Titman (1993).                                                                                                                                                       |
| Falsification Conditions | If price reverts immediately to V_t after a deviation, no positive-feedback channel exists.                                                                                                   |
| Alternative Theories     | Frictionless reversion — rejected by momentum evidence.                                                                                                                                       |

## Design Purpose and Activation Triggers

This agent fulfils three roles:
1. **Trend amplifier** — `gain_frame_follower` and `loss_frame_reactor` both buy positive deviations and sell negative ones.
2. **Asymmetric reaction generator** — different intensity coefficients for gain vs. loss frames produce skewed price impact.
3. **Counter-arbitrage option** — `frame_arbitrageur` mode fades extreme framing mispricings.

**Activation triggers (per mode):**
- `gain_frame_follower`: |P_t − V_t| > θ_frame on positive deviation → buy at intensity `m_gain`; on negative deviation → sell at intensity `m_gain · ρ_g`.
- `loss_frame_reactor`: same trigger; intensity `m_loss` (with `m_loss > m_gain` per λ).
- `frame_arbitrageur`: |P_t − V_t| > θ_arb (large mispricing) → fade with intensity `m_arb`.

**Deactivation conditions:** |P_t − V_t| ≤ θ_frame, share-cap reached, cash exhausted.

### Market Contribution by Regime

| Regime         | Contribution                                                               |
|----------------|----------------------------------------------------------------------------|
| Calm           | No activation; deviations small.                                           |
| Trending boom  | Buy demand on positive deviation amplifies trend; destabilising.           |
| Trending crash | Sell pressure on negative deviation amplifies decline; destabilising.      |
| Reversal       | Both modes flip direction; partial stabilisation when V_t crosses P_t.     |
| Stress         | Intense flow on both sides; arbitrageur mode contributes counter-pressure. |

**Interaction with other agents:** Frame followers act as positive-feedback partners to MomentumTrendTraders; framing arbitrageurs counterparty value-investors to relieve mispricings.

## Behavioural Framework

### 3.6.1 State Variables

| Symbol       | Type        | Description                                                            |
|--------------|-------------|------------------------------------------------------------------------|
| `frame_mode` | Categorical | One of `{gain_frame_follower, loss_frame_reactor, frame_arbitrageur}`. |
| `position`   | Integer     | Shares held.                                                           |
| `cash`       | Float       | Cash balance.                                                          |
| `V_t`        | Float       | Fundamental proxy.                                                     |
| `m_frame`    | Float       | Frame intensity coefficient (m_gain or m_loss).                        |
| `share_cap`  | Integer     | Per-trade share cap.                                                   |
| `θ_frame`    | Float       | Activation deviation threshold.                                        |
| `γ`          | Float       | Curvature of intensity function.                                       |
| `last_dev`   | Float       | Most recent (P_t − V_t).                                               |

### 3.6.2 Decision Rule

```
observe P_t, V_t
dev = P_t − V_t

if frame_mode == gain_frame_follower:
    if dev > θ_frame:
        Q* = + min(share_cap, m_gain · dev^γ · cash / P_t)        # risk-averse buy: scale by gain-frame coeff
    elif dev < −θ_frame:
        Q* = − min(position, m_gain · ρ_g · |dev|^γ)              # protect gain
    else:
        Q* = 0

elif frame_mode == loss_frame_reactor:
    if dev > θ_frame:
        Q* = + min(share_cap, m_loss · dev^γ · cash / P_t)
    elif dev < −θ_frame:
        Q* = − min(position, m_loss · |dev|^γ)                    # risk-seeking sell, larger λ
    else:
        Q* = 0

elif frame_mode == frame_arbitrageur:
    if |dev| > θ_arb:
        Q* = − sign(dev) · min(arb_cap, m_arb · |dev|^γ · cash / P_t)   # fade extreme framing
    else:
        Q* = 0
```

### 3.6.3 Mode-specific update rules

- `gain_frame_follower`: ρ_g (sell-side scaling) reflects risk aversion: ρ_g < 1, agent reluctant to fully unwind on negative dev.
- `loss_frame_reactor`: full λ-asymmetry; sell intensity > buy intensity.
- `frame_arbitrageur`: fades only above θ_arb (large mispricings); bounded by `arb_cap`.

### 3.6.4 Determinism Contract and State Update

- Deterministic given (`P_t`, `V_t`, `cash`, `position`, `frame_mode`, parameters, share-cap state).
- After each tick: `cash −= Q* · P_t` (positive Q* = buy); `position += Q*`; `last_dev = dev`.

**Does NOT use:** order-book depth, traded volume, peer-trader identity, news sentiment, social-media flow, options-implied volatility, dividend events. Uses only own cash / position state plus market price and fundamental proxy V_t.

### 3.6.5 Action Space

| Property             | Specification                                                                    |
|----------------------|----------------------------------------------------------------------------------|
| Order types allowed  | MARKET (default); LIMIT at `P_t · (1 ± ε_offset)` permitted in arbitrageur mode. |
| Price level rule     | MARKET at best bid/ask; LIMIT slightly inside spread for arbitrageur.            |
| Order quantity rule  | `Q* = m_frame ·                                                                  |
| Order lifetime       | MARKET: immediate; LIMIT: 5 ticks.                                               |
| Cancellation policy  | Cancel pending LIMIT on `dev` sign-flip.                                         |
| Inventory constraint | `position ∈ [−short_cap, +long_cap]`; `cash ≥ 0`.                                |
| Wealth-leverage cap  | No leverage in follower modes; arbitrageur leverage ≤ 2.0.                       |
| Stop-loss-kill rule  | Force flat if `                                                                  |

## Parameters

| Symbol      | Name                   | Default | Range          | Units    | Source           | Sensitivity | Notes                    |
|-------------|------------------------|---------|----------------|----------|------------------|-------------|--------------------------|
| `m_gain`    | Gain-frame intensity   | 1.0     | [0.5, 2.0]     | unitless | TK (1992) α=0.88 | High        | Buy slope                |
| `m_loss`    | Loss-frame intensity   | 2.25    | [1.5, 3.0]     | unitless | TK (1992) λ=2.25 | High        | Sell slope               |
| `ρ_g`       | Gain-frame sell ratio  | 0.5     | [0.2, 1.0]     | fraction | Calibrated       | Medium      | Risk-averse sell scaling |
| `m_arb`     | Arbitrageur intensity  | 0.8     | [0.3, 1.5]     | unitless | Calibrated       | Medium      | Fade size                |
| `γ`         | Curvature exponent     | 0.88    | [0.5, 1.2]     | unitless | TK (1992)        | High        | S-shape                  |
| `θ_frame`   | Activation threshold   | 0.005   | [0.001, 0.02]  | fraction | Calibrated       | High        | Min                      |
| `θ_arb`     | Arbitrageur threshold  | 0.05    | [0.02, 0.20]   | fraction | Calibrated       | Medium      | Large mispricing         |
| `share_cap` | Max order size         | 800     | [100, 5000]    | shares   | Per scenario     | Low         | Hard clamp               |
| `arb_cap`   | Arbitrageur cap        | 2000    | [500, 10000]   | shares   | Risk policy      | Medium      | Capital constraint       |
| `long_cap`  | Max long position      | 10000   | [1000, 100000] | shares   | Risk policy      | Low         | Inventory cap            |
| `short_cap` | Max short position     | 0       | [0, 10000]     | shares   | Mode-dependent   | Low         | Followers cannot short   |
| `ε_offset`  | LIMIT price offset     | 0.001   | [0, 0.01]      | fraction | Manual           | Low         | Inside-spread            |
| `k`         | Mean-revert exit ticks | 3       | [1, 10]        | ticks    | Manual           | Low         | Flatten gate             |

## Population and Heterogeneity

Categorical mixture in the population:
- FramingEffect scenario default: `gain_frame_follower` 0.45, `loss_frame_reactor` 0.45, `frame_arbitrageur` 0.10.
- High-arbitrage variant: `frame_arbitrageur` 0.30, gain/loss followers 0.35 each.

Heterogeneity per agent:
- `m_gain` ~ Normal(1.0, 0.2), truncated [0.5, 1.5].
- `m_loss` ~ Normal(2.25, 0.4), truncated [1.5, 3.0].
- `θ_frame` ~ LogNormal(μ=ln(0.005), σ=0.4), truncated [0.001, 0.02].
- `share_cap` ~ DiscreteUniform({400, 600, 800, 1000, 1200}).

## Worked Numerical Examples

**Example 1 — Gain-frame buy on positive deviation.**
P_t=105, V_t=100 → dev=+0.05; m_gain=1.0, γ=0.88; cash=$10,000.
Q* = min(800, 1.0 · 0.05^0.88 · 10000 / 105) ≈ min(800, 6.3) ≈ +6 buy at 105.

**Example 2 — Loss-frame sell on negative deviation.**
P_t=95, V_t=100 → dev=−0.05; m_loss=2.25; position=200.
Q* = − min(200, 2.25 · 0.05^0.88 · 200) = − min(200, 14.2) ≈ −14 sell at 95.
Compare to gain-frame at same deviation: Q*≈−7 (smaller in magnitude due to ρ_g=0.5) — illustrating asymmetry.

**Example 3 — Frame arbitrageur fading large mispricing.**
P_t=120, V_t=100 → dev=+0.20 > θ_arb=0.05; m_arb=0.8, γ=0.88; cash=$50,000.
Q* = − min(2000, 0.8 · 0.20^0.88 · 50000 / 120) = − min(2000, 81) ≈ −81 sell (short or unwind long) at 120.

**Example 4 — Below threshold (no activation).**
P_t=100.3, V_t=100 → dev=+0.003 < θ_frame=0.005 → Q* = 0.

**Example 5 — Edge case: cash exhausted on extended trend.**
After 10 buying rounds in `gain_frame_follower`, cash=$0; even if dev > θ_frame, Q* clamped to 0.

## Validation and Calibration

**Validation targets:**
- Frame asymmetry: aggregate sell-on-loss intensity / buy-on-gain intensity ≈ λ ≈ 2.25 (TK 1992).
- Trend amplification: deviation half-life increases by ≥ 30% when both follower modes active vs. ablation off.
- Arbitrageur capacity: with arbitrageur fraction ≥ 0.30, max |dev| capped at ≤ 1.5 · θ_arb.

**Ablation Hooks:**
- Set `m_loss = m_gain` → no asymmetry; tests prospect-theory channel.
- Disable arbitrageur mode → unbounded deviation drift; tests B&T (2003) limits.
- Set `γ = 1` → linear response; tests S-shape contribution.

**Calibration sources:**
- Tversky & Kahneman (1992): α=β=0.88, λ=2.25.
- Booij, van Praag, & van de Kuilen (2010): population-level prospect-theory parameters.

## Academic References

1. Tversky, A., & Kahneman, D. (1981). The framing of decisions and the psychology of choice. *Science*, 211(4481), 453–458. DOI: 10.1126/science.7455683
2. Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. DOI: 10.2307/1914185
3. Tversky, A., & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323. DOI: 10.1007/BF00122574
4. Levin, I. P., Schneider, S. L., & Gaeth, G. J. (1998). All frames are not created equal: A typology and critical analysis of framing effects. *OBHDP*, 76(2), 149–188. DOI: 10.1006/obhd.1998.2804
5. Barberis, N., & Thaler, R. (2003). A survey of behavioral finance. *Handbook of the Economics of Finance*, 1, 1053–1128. DOI: 10.1016/S1574-0102(03)01027-6
6. De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *JF*, 45(2), 379–395. DOI: 10.1111/j.1540-6261.1990.tb03695.x
7. Booij, A. S., van Praag, B. M. S., & van de Kuilen, G. (2010). A parametric analysis of prospect theory's functionals for the general population. *Theory and Decision*, 68(1-2), 115–148. DOI: 10.1007/s11238-009-9144-4
8. Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *JF*, 48(1), 65–91. DOI: 10.1111/j.1540-6261.1993.tb04702.x
9. Barberis, N. (2013). Thirty years of prospect theory in economics. *Journal of Economic Perspectives*, 27(1), 173–196. DOI: 10.1257/jep.27.1.173

## Design Provenance and Versioning

- **Version:** 1.0 (pilot pass, 2026-Q2)
- **Source skeleton:** examples/AGENT_POOL/ExtractedExampleInvestors/unique/FramingEffectTrader.md (skeleton, 40 lines)
- **Merged scenarios:** FramingEffect (×2 sub-roles) + arbitrageur extension.
- **Sub-archetype synthesis:** two original profiles (Gain Frame Follower, Loss Frame Reactor) plus an arbitrageur mode → 3-level `frame_mode` enum sharing one S-shape decision core.
- **Authoring rubric:** agent-design-skill.md (12-section pilot depth) + agent-design-finance.md addendum.
- **Audit fields:** Market Role, Market Contribution by Regime, 8-row Action Space, observation `Does NOT use:` declaration, ablation hooks — all present.
- **Open issues:** V_t treated as exogenous reference; future versions may incorporate adaptive reference-point updating (Kőszegi-Rabin 2006).
