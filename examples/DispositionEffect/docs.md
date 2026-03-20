# DispositionEffect Simulation - Prospect Theory Trading

## What is This?

| Item               | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| **Phenomenon**     | **Disposition Effect** - Sell winners too early, hold losers too long |
| **Model**          | Reference-point tracking with prospect theory valuation               |
| **Key Feature**    | Purchase price acts as psychological anchor (reference point)         |
| **Academic Value** | Tests Kahneman-Tversky Prospect Theory in market setting              |

## Financial Background

| Theory                   | Application                                        | Reference                                      |
|--------------------------|----------------------------------------------------|------------------------------------------------|
| **Prospect Theory**      | Loss aversion λ ≈ 2.25, S-shaped value function    | Kahneman & Tversky (1979). *Econometrica*      |
| **Disposition Effect**   | Sell winners, hold losers                          | Shefrin & Statman (1985). *Journal of Finance* |
| **Reference Dependence** | Utility relative to reference point, not absolute  | Thaler (1980). *Journal of Economic Behavior*  |
| **Mental Accounting**    | Segregate gains/losses in separate mental accounts | Thaler (1985). *Marketing Science*             |
| **PGR/PLR Methodology**  | Empirical measurement of disposition asymmetry     | Odean (1998). *Journal of Finance*             |

## Key Concepts

### Notations

| Symbol                   | Meaning                                                        |
|--------------------------|----------------------------------------------------------------|
| $P(t)$                   | Market price at round $t$                                      |
| $P_{\text{ref}}$         | Reference price (purchase price / average cost basis)          |
| $g(t)$                   | Gain-loss ratio: $[P(t)-P_{\text{ref}}]/P_{\text{ref}}$        |
| $V(x)$                   | Prospect-theory value function                                 |
| $\alpha,\beta$           | Value-function curvature parameters (both 0.88)                |
| $\lambda$                | Loss-aversion coefficient (2.25)                               |
| $D(t)$                   | Net aggregate demand                                           |
| $\lambda_{\text{price}}$ | Price-impact coefficient (0.06)                                |
| $\gamma$                 | Mean-reversion speed (0.015)                                   |
| $F$                      | Fundamental value (100)                                        |
| $N(t)$                   | Investor's current share position                              |
| $\mathrm{PGR}$           | Proportion of Gains Realised                                   |
| $\mathrm{PLR}$           | Proportion of Losses Realised                                  |
| $\mathrm{DC}$            | Disposition Coefficient $=\mathrm{PGR}-\mathrm{PLR}$           |
| $N(t)$                   | News shock $\sim\mathrm{Uniform}(-5,+5)$ with probability 0.15 |
| $\varepsilon(t)$         | Microstructure noise $\sim\mathcal{N}(0,\,0.4^2)$              |

### Prospect Theory Value Function

$$V(x) = \begin{cases} x^{0.88} & x\ge 0 \quad (\text{gains: concave, risk-averse}) \\ -\lambda\,|x|^{0.88} & x<0 \quad (\text{losses: convex, risk-seeking}) \end{cases}, \qquad \lambda=2.25$$

Key implications:
- **Gains (concave)**: $V'(x)=0.88\,x^{-0.12}$ decreasing $\Rightarrow$ diminishing marginal utility $\Rightarrow$ sell early
- **Losses (convex)**: risk-seeking in losses $\Rightarrow$ hold losers hoping for recovery
- **Loss aversion**: $V(-10)/V(+10)=17.1/7.59=2.25$

### Reference Point

$$g(t) = \frac{P(t) - P_{\text{ref}}}{P_{\text{ref}}}$$

Investor evaluates: "Am I up or down from where I bought?"

## Why These 5 Investor Types?

| Investor                  | Role                | Behavior                                                 |
|---------------------------|---------------------|----------------------------------------------------------|
| **DispositionInvestor**   | ⭐ Behavioral        | Sells winners, holds losers. Prospect theory driven.     |
| **RationalInvestor**      | Benchmark           | Expected utility maximizer. No disposition bias.         |
| **TaxAwareInvestor**      | Tax-Loss Harvesting | Sells losers for tax benefits. Opposite of disposition!  |
| **IndexHolder**           | Passive             | Buy-and-hold. No trading bias.                           |
| **InstitutionalInvestor** | Professional        | Less prone to disposition (career concerns, discipline). |

## Disposition Effect Mechanism

**Scenario A: WINNER** ($P > P_{\text{ref}}$)

Current Price $= \$110$, Purchase $= \$100$ → GAIN of $\$10$.

Value function (concave for gains): $V(+10) = 10^{0.88} = 7.59$ utils.

Marginal utility declining → "I've made enough" → **SELL EARLY** (realize gains) — "Bird in hand" mentality.

**Scenario B: LOSER** ($P < P_{\text{ref}}$)

Current Price $= \$90$, Purchase $= \$100$ → LOSS of $\$10$.

Value function (convex for losses): $V(-10) = -2.25\times 10^{0.88} = -17.1$ utils.

Risk-seeking in losses → "It might come back" → **HOLD LOSER** (refuse to cut) — Hope for recovery.

## Market Model

$$P(t+1) = P(t) + \lambda_{\text{price}}\cdot D(t) + \gamma\cdot[F - P(t)] + N(t) + \varepsilon(t)$$

where $N(t)\sim\mathrm{Uniform}(-5,+5)$ with probability $p_{\text{news}}=0.15$ per round, else $N(t)=0$; $\varepsilon(t)\sim\mathcal{N}(0,\,0.4^2)$.

This creates random gain/loss situations relative to each investor's reference price, testing disposition effect dynamics.

| Parameter        | Value | Financial Meaning                     |
|------------------|-------|---------------------------------------|
| Price Impact     | 0.06  | Demand sensitivity                    |
| Mean Reversion   | 0.015 | Speed to fundamental                  |
| Noise Std        | 0.40  | Per-round price noise                 |
| News Probability | 15%   | Chance of random news each period     |
| News Impact      | ±5    | Magnitude of news shock               |
| Initial Position | 30    | Start with shares (creates reference) |

## Investor Strategy Logic

### DispositionInvestor (⭐ Behavioral Bias)

Four decision branches based on $g(t)=[P(t)-P_{\text{ref}}]/P_{\text{ref}}$ (*Implementation*: `examples/DispositionEffect/players.py`, `DispositionInvestor.decide()`):

| Branch      | Condition                           | Action                                          | Quantity                                            |
|-------------|-------------------------------------|-------------------------------------------------|-----------------------------------------------------|
| SELL_WINNER | $g\ge 0.05$                         | Concave $V$ — realise gain                      | $-0.4\cdot N$                                       |
| SELL_LOSER  | $g\le -0.30$                        | Extreme loss exceeds convex-$V$ benefit         | $-0.2\cdot N$                                       |
| BUY         | $-0.01\le g<0.01$, $N<N_{\max}$     | Near ref-point: status quo comfort (within ±1%) | $+\min(0.2\cdot(N_{\max}-N),\,0.15\,\text{Cash}/P)$ |
| HOLD        | $-0.30<g<-0.01$ or $0.01\le g<0.05$ | Ride hope (loss) or sit on unrealised gain      | $0$                                                 |

### RationalInvestor (No Bias — Benchmark)

*Implementation*: `RationalInvestor.decide()`. Rebalances to 50 % equity target, ignoring purchase price.

### TaxAwareInvestor (Opposite Pattern)

*Implementation*: `TaxAwareInvestor.decide()`. Sells losers at $g\le -0.05$ for tax benefit; holds winners for deferral until $g\ge 0.20$.

## Strategy Comparison

| Strategy                | Gain Response      | Loss Response      | Reference? |
|-------------------------|--------------------|--------------------|------------|
| **DispositionInvestor** | ⭐ Sell at 5%       | ⭐ Hold until -30%  | Yes (bias) |
| RationalInvestor        | Rebalance by alloc | Rebalance by alloc | No         |
| TaxAwareInvestor        | Hold (tax defer)   | Sell at -5% (tax)  | Yes (tax)  |
| IndexHolder             | Hold               | Hold               | No         |
| InstitutionalInvestor   | Sell at 25%        | Cut at -15%        | Partial    |

## Disposition Metric: PGR vs PLR (Odean 1998 Methodology)

For each round, for each investor, let $u = [P(t)-P_{\text{ref}}]/P_{\text{ref}}$, $q_{\text{sell}}$ = shares sold, $q_{\text{hold}} = \max(0, N - q_{\text{sell}})$:

**SELL round** ($q < 0$):
- If $u \ge 0$: $\text{realized\_gains} \mathrel{+}= q_{\text{sell}}\cdot u$; $\text{paper\_gains} \mathrel{+}= q_{\text{hold}}\cdot u$
- If $u < 0$: $\text{realized\_losses} \mathrel{+}= q_{\text{sell}}\cdot|u|$; $\text{paper\_losses} \mathrel{+}= q_{\text{hold}}\cdot|u|$

**HOLD round** ($q = 0$):
- If $u > 0$: $\text{paper\_gains} \mathrel{+}= N\cdot u$
- If $u < 0$: $\text{paper\_losses} \mathrel{+}= N\cdot|u|$

**BUY round** ($q > 0$): only update average cost basis — not a sell-opportunity observation.

$$\mathrm{PGR} = \frac{\text{realized\_gains}}{\text{realized\_gains}+\text{paper\_gains}}, \qquad \mathrm{PLR} = \frac{\text{realized\_losses}}{\text{realized\_losses}+\text{paper\_losses}}$$

Disposition Effect confirmed when $\mathrm{PGR} > \mathrm{PLR}$. Disposition Coefficient:

$$\mathrm{DC} = \mathrm{PGR} - \mathrm{PLR} \qquad (\mathrm{DC}>0.15\Rightarrow\text{strong effect};\ \mathrm{DC}>0.10\Rightarrow\text{moderate};\ \mathrm{DC}>0.05\Rightarrow\text{weak})$$

**Key design principle — BUY rounds excluded from paper gain/loss:**
Odean's framework measures the asymmetry in *sell decisions*. A buy is not a choice
between realizing and holding — it does not create a "sell opportunity" observation.
Including paper gain on buy rounds would inflate the denominators and systematically
bias PGR and PLR downward, destroying the signal.

## Mathematical Foundations

### 1. Market Model — Price Dynamics with News Shocks

(*Implementation*: `examples/DispositionEffect/players.py`, `Market.clear()`)

> **Source**: Kyle (1985) [price impact structure]; Grossman & Miller (1988) [1 — demand clearing]; simulation parameters from Shefrin & Statman (1985) [2]. *Implementation*: `examples/DispositionEffect/players.py`, `Market.clear()`.

$$P(t+1) = P(t) + \lambda_{\text{price}}\cdot D(t) + \gamma\cdot[F-P(t)] + N(t) + \varepsilon(t)$$

> **What it does**: Updates the market price each round as the sum of four forces. (1) $\lambda_{\text{price}}\cdot D(t)$ — **demand pressure**: net buying/selling by all agents moves price proportionally (Kyle-style linear impact). (2) $\gamma\cdot[F-P(t)]$ — **mean reversion**: gentle gravitational pull back to fundamental value $F=100$, preventing indefinite drift. (3) $N(t)\sim\mathrm{Uniform}(-5,+5)$ with probability 0.15 — **news shocks**: rare but large jumps that force investors above or below their reference points, triggering disposition decisions. (4) $\varepsilon(t)\sim\mathcal{N}(0,0.4^2)$ — **microstructure noise**: continuous small fluctuations. **Simulates**: the stochastic price environment in which each investor's purchase price becomes either a paper gain or paper loss, directly driving the disposition effect. **Effect**: without the news shocks, investors rarely cross their reference thresholds; with 15% news probability the simulation generates realistic distributions of winner and loser positions.

with $\lambda_{\text{price}}=0.06$, $\gamma=0.015$, $F=100$; news shock $N(t)\sim\mathrm{Uniform}(-5,+5)$ with $p_{\text{news}}=0.15$.

Expected return (at $P\approx F$, $D\approx 0$): $\mathbb{E}[r(t)]\approx 0$.

Return variance per round:

> **Source**: Derived analytically from the price equation above — variance of $\varepsilon$ plus the contribution of intermittent news shocks. *Implementation*: `Market.clear()` calibration.

$$\mathrm{Var}(r(t)) \approx \left(\frac{0.4}{100}\right)^2 + 0.15\cdot\frac{5^2/3}{100^2} \approx 0.00014 \quad\Longrightarrow\quad \sigma_r\approx 1.2\%$$

> **What it does**: Decomposes per-round return variance into two additive components: $(0.4/100)^2$ from continuous microstructure noise and $0.15\times(5^2/3)/100^2$ from the intermittent uniform news shock (variance of $\mathrm{Uniform}(-5,+5)$ scaled by price and weighted by 15% probability). The result $\sigma_r\approx 1.2\%$ per round is deliberately moderate — enough to push investors across their gain/loss thresholds over a 200-round simulation while keeping the price dynamics realistic.

---

### 2. Prospect Theory Value Function — Kahneman-Tversky (1979) [1]

> **Source**: Kahneman, D. & Tversky, A. (1979) [1] — *Prospect Theory: An Analysis of Decision under Risk*. Econometrica, 47(2), 263–291. The S-shaped value function with $\alpha=\beta=0.88$ and $\lambda=2.25$ are the empirically fitted parameters from their original paper. *Implementation*: `examples/DispositionEffect/players.py`, `DispositionInvestor.decide()`.

$$V(x) = \begin{cases} x^{\alpha} & x\ge 0 \\ -\lambda\,|x|^{\beta} & x<0 \end{cases}, \qquad \alpha=\beta=0.88, \quad \lambda=2.25$$

> **What it does**: Defines how investors **feel** about gains and losses relative to their reference point (purchase price), not in absolute dollar terms. The function is intentionally **asymmetric**: (1) For gains ($x\ge 0$): $V(x)=x^{0.88}$ is **concave** — each extra dollar of gain produces less additional satisfaction (diminishing marginal utility). This makes investors eager to lock in gains before they shrink. (2) For losses ($x<0$): $V(x)=-2.25|x|^{0.88}$ is **convex** — each extra dollar of loss hurts slightly less at the margin, making investors willing to gamble on recovery rather than cut losses. The $\lambda=2.25$ coefficient makes losses hurt 2.25× more than equivalent gains feel good. **Simulates**: the psychological mechanism that generates the disposition effect — the concavity in gains drives early selling (PGR $\uparrow$), the convexity in losses drives holding (PLR $\downarrow$). **Effect**: $\mathrm{PGR}>\mathrm{PLR}$ and $\mathrm{DC}=\mathrm{PGR}-\mathrm{PLR}>0$.

Gain domain (concave $V$): marginal utility decreasing

> **Source**: Kahneman & Tversky (1979) [1] — derivative of the value function showing diminishing sensitivity. *Implementation*: shapes the SELL_WINNER threshold in `DispositionInvestor.decide()`.

$$V'(x) = 0.88\,x^{-0.12} \qquad (\text{decreasing in }x)$$

> **What it does**: The marginal value of gains decreases as gains grow — at $x=1$, $V'=0.88$; at $x=100$, $V'\approx 0.65$. This declining marginal utility is precisely why investors are impatient to sell winners: early gains feel proportionally more valuable than later ones, so realizing them early dominates waiting. **Simulates**: the "bird in hand" psychology documented in retail brokerage data.

Example:

> **Source**: Numerical illustration of Kahneman & Tversky (1979) [1] parameters, confirming sub-additivity of gains. *Implementation*: calibration of `gain_threshold = 0.05` in `configs/DispositionEffect/players.yml`.

$$V(+10) = 10^{0.88} = 7.59 \quad;\quad V(+20) = 20^{0.88} = 14.0 < 2\times V(+10)$$

> **What it does**: Demonstrates the concavity: doubling the gain from $+10$ to $+20$ yields only 84% extra utility (14.0 vs $2\times7.59=15.18$), not double. **Effect in simulation**: investors who have already gained 10% feel diminishing urgency to wait for 20% — they sell at the 5% threshold (SELL_WINNER), consistent with Odean's (1998) [3] empirical finding that retail gains are realized at 3–5%.

Loss domain (convex $V$): additional losses hurt less marginally $\Rightarrow$ risk-seeking:

> **Source**: Kahneman & Tversky (1979) [1] — loss aversion coefficient $\lambda=2.25$, convex loss domain. *Implementation*: shapes the HOLD behavior and SELL_LOSER threshold (`loss_threshold = -0.30`) in `DispositionInvestor.decide()`.

$$V(-10) = -2.25\times 10^{0.88} = -17.1 \quad;\quad \frac{V(-10)}{V(+10)} = 2.25$$

> **What it does**: A loss of 10 produces $-17.1$ utils vs a gain of 10 producing $+7.59$ utils — losses hurt 2.25× more than equivalent gains feel good. The convex (risk-seeking) shape in the loss domain means an investor would rather gamble on recovery than accept a certain loss. **Simulates**: why DispositionInvestors hold losers far too long (until $-30\%$) — the pain of cutting a loss is psychologically overwhelming. **Effect**: PLR stays low while PGR is high, generating $\mathrm{DC}>0$.

---

### 3. DispositionInvestor Decision Rule — Formal Thresholds

Shefrin & Statman (1985) [2] formalized the disposition effect: investors are predisposed to sell winners and hold losers due to prospect theory, mental accounting, and seeking pride while avoiding regret. Let $g(t)=[P(t)-P_{\text{ref}}]/P_{\text{ref}}$ (*Implementation*: `DispositionInvestor.decide()`).

> **Source**: Shefrin, H. & Statman, M. (1985) [2] — *The Disposition to Sell Winners Too Early and Ride Losers Too Long*. Journal of Finance, 40(3), 777–790. Threshold values calibrated to Odean (1998) [3] brokerage data (gain realization at 3–5%; loss realization requiring much deeper drawdowns). *Implementation*: `examples/DispositionEffect/players.py`, `DispositionInvestor.decide()`.

$$q(t) = \begin{cases} -0.4\cdot N(t) & g\ge 0.05 \quad (\text{SELL\_WINNER}) \\ -0.2\cdot N(t) & g\le -0.30 \quad (\text{SELL\_LOSER}) \\ +\min\bigl(0.2\cdot(N_{\max}-N),\,0.15\,\text{Cash}/P\bigr) & -0.01\le g<0.01 \quad (\text{BUY}) \\ 0 & \text{otherwise} \quad (\text{HOLD}) \end{cases}$$

> **What it does**: Translates prospect theory psychology into concrete trading rules via the gain-loss ratio $g(t)$. **SELL_WINNER** ($g\ge+5\%$): sells 40% of position — concave value function makes early realization attractive; the 40% fraction is partial to allow repeated gain-realization cycles without depleting the position. **SELL_LOSER** ($g\le-30\%$): sells only 20% of position at extreme loss — convex loss domain means the investor has waited an extraordinarily long time; the 20% fraction reflects extreme reluctance. **BUY** (within $\pm 1\%$ of reference): modest replenishment when price is near the mental anchor — status-quo comfort per Thaler (1980) [4] mental accounting. **HOLD** (everything in between): the vast middle ground — investors neither sell modest gains nor cut manageable losses. **Simulates**: the behavioral asymmetry that Shefrin & Statman (1985) [2] predicted and Odean (1998) [3] confirmed empirically. **Effect**: SELL_WINNER fires frequently (low threshold), SELL_LOSER fires rarely (high threshold) $\Rightarrow$ PGR $\gg$ PLR.

Threshold asymmetry captures loss aversion:

> **Source**: Kahneman & Tversky (1979) [1] loss aversion $\lambda=2.25$; Odean (1998) [3] empirical calibration of actual retail investor threshold ratios. *Implementation*: `gain_threshold` and `loss_threshold` in `configs/DispositionEffect/players.yml`.

$$\frac{|\text{loss\_threshold}|}{\text{gain\_threshold}} = \frac{0.30}{0.05} = 6.0$$

> **What it does**: Quantifies the behavioral asymmetry in a single number. An investor who sells at a 5% gain requires a 30% loss before selling — a 6:1 ratio. This is consistent with loss aversion: the psychological cost of booking a loss is 2.25× larger than the pleasure of a gain per unit, and compounded over the convex loss domain the effective threshold gap widens dramatically. **Simulates**: the irrational "holding on" behavior that causes investors to ride stocks down far past any rational stopping point. **Effect**: directly explains the large observed PGR/PLR gap in the simulation.

BUY band is narrow ($\pm 1\%$) reflecting status quo comfort: investors add shares only when price is nearly exactly at their reference point, consistent with Odean (1998) [3] observations.

---

### 4. PGR/PLR — Odean (1998) [3] Methodology

For each sell-opportunity (SELL or HOLD round) of investor $i$ — Odean (1998) [3] empirically confirmed PGR > PLR in actual brokerage data, with gains realized 50% more frequently than losses (*Implementation*: `examples/DispositionEffect/analysis.py`, `calculate_pgr_plr()`):

Let $u=[P(t)-P_{\text{ref}}]/P_{\text{ref}}$, $q_{\text{sell}}$ = shares sold, $q_{\text{hold}}=\max(0,N-q_{\text{sell}})$.

> **Source**: Odean, T. (1998) [3] — *Are Investors Reluctant to Realize Their Losses?* Journal of Finance, 53(5), 1775–1798. Odean developed this accounting framework to measure disposition effect in 10,000 brokerage accounts; he found PGR $\approx 0.148$, PLR $\approx 0.099$ in actual data. *Implementation*: `examples/DispositionEffect/analysis.py`, `calculate_pgr_plr()`.

$$\text{If }u\ge 0:\quad \text{realized\_gains}\mathrel{+}=q_{\text{sell}}\cdot u; \quad \text{paper\_gains}\mathrel{+}=q_{\text{hold}}\cdot u$$

$$\text{If }u<0:\quad \text{realized\_losses}\mathrel{+}=q_{\text{sell}}\cdot|u|; \quad \text{paper\_losses}\mathrel{+}=q_{\text{hold}}\cdot|u|$$

> **What it does**: These two accounting rules classify every share's outcome at every sell-or-hold decision point. For a gain ($u\ge 0$): shares actually sold contribute to **realized gains** (the investor acted on the gain), while shares kept despite the gain contribute to **paper gains** (the investor had the opportunity to sell but chose not to). For a loss ($u<0$): shares sold become **realized losses** (investor cut the loss), shares held become **paper losses** (investor refused to sell despite the loss). Critically, BUY rounds are excluded — an investor cannot "realize" a gain or loss by buying more shares, so buy rounds do not generate sell-opportunity observations. **Simulates**: the decision-tree that every investor faces at each moment: when you have a winner, do you sell it? When you have a loser, do you sell it? The ratio of yes-sells to total opportunities is exactly PGR (for winners) and PLR (for losers).

> **Source**: Odean (1998) [3] — PGR and PLR ratios, the primary empirical test statistics. *Implementation*: `calculate_pgr_plr()` in `examples/DispositionEffect/analysis.py`.

$$\mathrm{PGR} = \frac{\text{realized\_gains}}{\text{realized\_gains}+\text{paper\_gains}}, \qquad \mathrm{PLR} = \frac{\text{realized\_losses}}{\text{realized\_losses}+\text{paper\_losses}}$$

> **What it does**: PGR is the fraction of "sell opportunities for winners" that were actually taken — how often the investor realizes a gain when they could. PLR is the same for losers. A rational investor with no bias would have PGR $\approx$ PLR (no systematic preference). A disposition-biased investor has PGR $>$ PLR: they realize gains much more frequently than they cut losses. Odean (1998) [3] found PGR/PLR $\approx 1.5$ in real data; the simulation targets a similar ratio. **Simulates**: the aggregate statistical signature of the disposition effect across all trading rounds — the single most important output metric of this simulation.

Disposition Coefficient:

> **Source**: Derived from Odean (1998) [3] — DC is the standard scalar summary of disposition bias magnitude. *Implementation*: `calculate_pgr_plr()` returns DC as the primary scoring variable.

$$\mathrm{DC} = \mathrm{PGR} - \mathrm{PLR} \qquad (\text{expected for DispositionInvestor: DC}\approx 0.15\text{--}0.40)$$

> **What it does**: A single number summarizing the intensity of disposition bias. DC $= 0$ means no bias (PGR $=$ PLR, rational behavior). DC $> 0$ means the investor sells winners more readily than losers. DC $= 0.15$ (the strong-effect threshold) means the investor has a 15 percentage-point higher probability of realizing a gain than a loss in any given round. DC $= 0.40$ (expected upper range) reflects extreme behavioral bias — consistent with less-sophisticated retail investors in Odean's data. **Effect**: DispositionInvestor targets DC $\approx 0.15$–$0.40$; RationalInvestor targets DC $\approx 0$; TaxAwareInvestor targets DC $< 0$ (negative — actively realizes losses for tax purposes).

---

### 5. Disposition Effect — Market Impact (Frazzini 2006) [5]

Aggregate disposition bias creates price underreaction to news — Frazzini (2006) [5] shows that when many investors hold paper gains on a stock, subsequent price reaction to good news is dampened (*Implementation*: `DispositionEffect/analysis.py`):

> **Source**: Frazzini, A. (2006) [5] — *The Disposition Effect and Underreaction to News*. Journal of Finance, 61(4), 2017–2046. Frazzini documented that stocks with many investors sitting on paper gains have systematically muted initial price reactions to positive news events, followed by a post-announcement drift. *Implementation*: `DispositionEffect/analysis.py`, aggregate price dynamics.

$$\mathbb{E}[\Delta P \mid \text{news, many paper gains}] < \mathbb{E}[\Delta P \mid \text{news, no paper gains}]$$

> **What it does**: Describes a **market-level** consequence of the disposition effect at the aggregate level, beyond individual investor psychology. When a positive news shock arrives (e.g., $N(t)=+4$ in the simulation), price should jump to immediately reflect the new fundamental. But if many DispositionInvestors are sitting on paper gains just above their reference price, they **immediately sell into the news rally** (SELL_WINNER fires). This selling pressure partially offsets the news-driven demand, causing the initial price reaction to be **smaller** than it would be without disposition-biased investors. The remaining price adjustment then occurs gradually over subsequent rounds — appearing as a **post-news drift** in prices. **Simulates**: the empirical anomaly that stocks with high "overhang" (many investors above their reference price) underreact to positive news initially and continue drifting upward afterward. **Effect**: the presence of DispositionInvestors in the simulation dampens news-driven price spikes and creates autocorrelation in returns following news events — a testable market-microstructure prediction consistent with Frazzini (2006) [5].

Drift magnitude $\propto$ fraction of investors with reference point below current price.

---

## Scoring (validate_disposition_effect)

Defined in `masim/evaluation/finance/validation.py` (line 2472):

$\text{comparison\_score} = 1.0$ if $\mathrm{PGR} > \mathrm{PLR}$, else $0.2$.

$$\text{dc\_score} = \begin{cases} 1.0 & \mathrm{DC} > 0.15 \\ 0.7 + (\mathrm{DC}-0.10)\times 6 & \mathrm{DC} > 0.10 \\ 0.4 + (\mathrm{DC}-0.05)\times 6 & \mathrm{DC} > 0.05 \\ \mathrm{DC}\times 8 & \mathrm{DC} > 0 \\ 0 & \mathrm{DC}\le 0 \end{cases}$$

$$\text{overall\_score} = \text{comparison\_score}\times 0.4 + \text{dc\_score}\times 0.6$$

$\text{valid} = (\text{overall\_score} > 0.5)$ AND $(\mathrm{PGR} > \mathrm{PLR})$.

Target for a well-functioning simulation: `overall_score > 0.5` (DC > ~0.08 with PGR > PLR).

## Configuration Parameters (DispositionInvestor)

| Parameter            | Value | Theoretical Basis                                                                       |
|----------------------|-------|-----------------------------------------------------------------------------------------|
| `gain_threshold`     | 0.05  | Odean (1998): retail gain realization ~3-5%; concave value function triggers early sell |
| `loss_threshold`     | -0.30 | Odean: strong loss aversion, must reach large loss before selling; convex loss domain   |
| `sell_fraction_gain` | 0.4   | Partial sell preserves position for repeated gain-realization cycles                    |
| `sell_fraction_loss` | 0.2   | Minimal sell at loss; reflects extreme reluctance (loss aversion asymmetry)             |
| `max_position`       | 30.0  | = initial_position; no speculative buildup beyond original stake                        |
| `buy_fraction`       | 0.2   | Modest replenishment near reference point; 20% of deficit per round                     |
| `loss_aversion` λ    | 2.25  | Kahneman-Tversky canonical estimate                                                     |

## Known Issues Fixed

### Issue 1: Trade Loader Loading Zero Trades
**File**: `examples/DispositionEffect/analysis.py`, `load_simulation_data()`  
**Bug**: Checked `if "strategy" in turn_data` on the outer block dict (keys are `turn_r000001_...`), not the inner payload.  
**Fix**: Now iterates `turn_block -> turn_key -> step_results[0] -> decision_payload`, extracting `{round, quantity, bid_price, strategy}` per trade.

### Issue 2: PGR/PLR Double-Counting on BUY Rounds
**File**: `examples/DispositionEffect/analysis.py`, `calculate_pgr_plr()`  
**Bug**: The BUY branch added `position × unit_gain` to paper gains before updating the reference price — inflating the paper gains denominator for the same shares already counted on HOLD rounds.  
**Fix**: BUY branch only updates average cost basis. Paper gain/loss is counted exclusively on SELL and HOLD rounds (Odean 1998 methodology).

### Issue 3: `remaining` Double-Counting Sold Shares
**File**: `examples/DispositionEffect/analysis.py`, `calculate_pgr_plr()`  
**Bug**: `remaining = position - abs(quantity)` included the sold shares in the paper gain count.  
**Fix**: `remaining = max(0, position - realized_qty)` — excludes sold shares correctly.

### Issue 4: Position Depletion to Near-Zero
**File**: `examples/DispositionEffect/players.py`, `configs/DispositionEffect/players.yml`  
**Bug**: `sell_fraction_gain = 0.6` with `gain_threshold = 0.10` depleted position to ~2 shares after 3-4 sell events. Near-zero position produces near-zero PGR/PLR signal.  
**Fix**: `sell_fraction_gain = 0.4`, `gain_threshold = 0.05` (more frequent triggers, less depletion per trigger).

### Issue 5: Unconditional Replenishment Buy (No Behavioral Basis)
**File**: `examples/DispositionEffect/players.py`  
**Bug**: Buy fired every round when `position < max_position` regardless of price level — not grounded in Prospect Theory. `max_position = 60` doubled the initial stake without justification.  
**Fix**: Buy fires only when `-0.02 <= gain_loss < gain_threshold` (near reference point), reflecting status quo comfort. `max_position = initial_position = 30` prevents speculative buildup.

## Topology

```
                         +-------------------+
                         |      market       | <-- News shocks create +/-
                         +---------+---------+
                                   |
     +-----------+-----------------+-----------------+-----------+
     v           v                 v                 v           v
 disposition   rational        tax_aware        index      institutional
 (⭐ biased)   (benchmark)    (opposite!)     (passive)   (disciplined)
```

## Files

| File                                            | Purpose                     |
|-------------------------------------------------|-----------------------------|
| `examples/DispositionEffect/players.py`         | Market + 5 investor classes |
| `examples/DispositionEffect/analysis.py`        | PGR/PLR calculation + plots |
| `examples/DispositionEffect/run_disposition.py` | Entry point                 |
| `configs/DispositionEffect/simulation.yml`      | Main config                 |
| `configs/DispositionEffect/players.yml`         | Player definitions          |
| `configs/DispositionEffect/topology.yml`        | Star topology               |

## Running

```bash
# Run simulation
python examples/DispositionEffect/run_disposition.py -c configs/DispositionEffect/simulation.yml

# Run analysis on recorded data
python examples/DispositionEffect/analysis.py -c configs/DispositionEffect/simulation.yml
```

## Expected Behavior

| Phase     | Observation                                                   |
|-----------|---------------------------------------------------------------|
| News (+)  | DispositionInvestor sells quickly after price rises above +5% |
| News (-)  | DispositionInvestor holds until -30% loss (rarely sells)      |
| Near ref  | DispositionInvestor modestly buys back (within ±1% of ref)    |
| Over time | PGR >> PLR for disposition investor; PGR ≈ PLR for rational   |
| Score     | DC = PGR - PLR > 0.10 (moderate-strong); overall score > 0.5  |

## Real-World Mapping

| Simulation         | Real-World Example                        |
|--------------------|-------------------------------------------|
| Sell winners early | Retail investors locking in profits       |
| Hold losers        | "Diamond hands" on losing stocks          |
| Tax-loss harvest   | Year-end selling for tax benefits         |
| Institutional      | Mutual funds with disciplined rebalancing |

## References

\[1\] Kahneman, D. & Tversky, A. (1979). *Prospect Theory: An Analysis of Decision under Risk*. Econometrica, 47(2), 263–291.

\[2\] Shefrin, H. & Statman, M. (1985). *The Disposition to Sell Winners Too Early and Ride Losers Too Long: Theory and Evidence*. Journal of Finance, 40(3), 777–790.

\[3\] Odean, T. (1998). *Are Investors Reluctant to Realize Their Losses?* Journal of Finance, 53(5), 1775–1798.

\[4\] Thaler, R.H. (1980). *Toward a Positive Theory of Consumer Choice*. Journal of Economic Behavior & Organization, 1(1), 39–60.

\[5\] Frazzini, A. (2006). *The Disposition Effect and Underreaction to News*. Journal of Finance, 61(4), 2017–2046.

\[6\] Thaler, R.H. (1985). *Mental Accounting and Consumer Choice*. Marketing Science, 4(3), 199–214.
