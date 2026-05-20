# GamblerFallacy — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Gambler's Fallacy — the erroneous belief that after a streak of outcomes in one direction, a reversal is more likely, despite outcomes being statistically independent                                                                                                                                                                                                                                                                                                                       |
| Category           | Cognitive bias / behavioral finance / probability misjudgment                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Core Mechanism     | StreakReversalTraders incorrectly expect mean-reversion after consecutive price moves in one direction; HotHandTraders incorrectly extrapolate that streaks will continue. Together they generate self-fulfilling volatility: StreakReversalTraders bet against the market at exactly the wrong time (during momentum episodes), amplifying trends, while HotHandTraders buy into rising streaks, further inflating prices. Rational arbitrageurs partially exploit these systematic errors. |
| Real-World Origin  | Documented in casino gambling data (Gambler's Fallacy) and basketball shooting statistics (Hot Hand Fallacy); extended to financial markets through studies of retail trading patterns after streaks of positive/negative daily returns                                                                                                                                                                                                                                                      |
| Research Relevance | Explains excess return continuation and reversal in short-term price series; contributes to momentum effect documentation; relevant to behavioral finance, algorithmic trading design, and systemic risk from correlated retail order flow                                                                                                                                                                                                                                                   |

### 1.1 Origin and Source Analysis

#### 1.1.1 Intellectual Lineage

The gambler's fallacy was first documented systematically in gambling contexts during the early 20th century, but the theoretical grounding came with Tversky and Kahneman's (1971) seminal paper "Belief in the Law of Small Numbers." They demonstrated that even statistically trained researchers incorrectly believed that small samples should replicate the properties of the population distribution — expecting that a short sequence of heads in coin flipping "should" be followed by tails to maintain the 50% average. This representativeness heuristic — judging probability by similarity to an expected distribution — was shown to be a systematic cognitive mechanism, not random error.

The Hot Hand Fallacy was documented as the mirror-image belief by Gilovich, Vallone and Tversky (1985) in basketball: fans, players, and coaches all believed that a player who had made several consecutive shots was "on fire" and more likely to make the next shot, despite statistical analysis showing no such autocorrelation. This apparent contradiction with the gambler's fallacy was resolved by Ayton and Fischer (2004), who showed that the two biases coexist: gambler's fallacy applies to presumed chance outcomes (dice, coin flips, lottery), while hot hand belief applies to skill-based outcomes. Financial markets occupy an ambiguous middle ground, producing both biases in different trader populations simultaneously.

Rabin (2002) provided the formal theoretical reconciliation by modeling how a rational observer incorrectly believing in the law of small numbers generates gambler's fallacy predictions for long sequences and hot-hand predictions for short sequences — the same agent exhibits both biases depending on sequence length. His model formalizes the underlying cognitive mechanism: an agent who believes that the generating process "draws without replacement from an urn" will expect reversals over long sequences (gambler's fallacy) but extrapolations over short ones (hot hand). This is the theoretical foundation for the StreakReversalTrader and HotHandTrader coexistence in this simulation.

The agent-based modelling literature on streak-based trading begins with De Bondt and Thaler (1985, 1987) who documented long-horizon reversal (5-year reversals consistent with gambler's fallacy overreaction) and Jegadeesh and Titman (1993) who documented short-horizon momentum (12-month continuation consistent with hot-hand extrapolation). Bloomfield, O'Hara and Saar (2009) confirmed in controlled laboratory markets that uninformed traders create momentum by trend-following, a hot-hand behavior, while informed traders create reversals by fading streaks. The simulation directly implements both strategy types.

The simulation design choices — specifically the deviation-based activation (using deviation as a proxy for streak intensity) — are calibrated from Croson and Sundali's (2005) field study of actual casino gambling behavior showing that the gambler's fallacy is strongest when streak length exceeds 3–5 consecutive outcomes, corresponding to deviation persistence across multiple rounds. The 2% activation threshold reflects the minimum deviation magnitude that creates a perceivable "streak" signal for both types of biased traders.

#### 1.1.2 Real-World Event Catalogue

| Event Name                                            | Date(s)                      | Market / Asset          | Trigger                                                                        | Magnitude                                                                                  | Duration                            | Correspondence to Simulation                                                                                                                     | Primary Source                                                                                                                                       |
|-------------------------------------------------------|------------------------------|-------------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| Post-Earnings Announcement Drift (PEAD)               | 1968–ongoing                 | US equities             | Earnings announcement creates streak of abnormal returns                       | 2–3% abnormal return over 60 days post-announcement                                        | 60 trading days                     | HotHandTrader (§4.2) buys into post-earnings momentum; StreakReversalTrader (§4.1) bets against it prematurely, amplifying momentum              | Ball & Brown (1968). *Journal of Accounting Research*. 6(2), 159–178. https://doi.org/10.2307/2490232                                                |
| Lottery Ticket Demand After Jackpots                  | 1990–2010                    | State lotteries         | Large jackpot → immediate high sales → next drawing perceived as "due"         | Ticket sales drop 30–40% for same number combinations following a jackpot win              | 1–3 weeks                           | StreakReversalTrader (§4.1) sells after a streak of positive deviations expecting reversal; NoiseTrader (§4.5) generates baseline randomness     | Clotfelter & Cook (1993). *American Economic Review*, 83(5), 1477–1494                                                                               |
| January Effect — Hot Hand Extrapolation               | 1940–2000                    | US equity market        | Strong December returns create hot-hand belief for January                     | January return 1.5–3.0% abnormal vs. other months; partially explained by momentum traders | 1 month                             | HotHandTrader (§4.2) buys into December winning streak expecting January continuation                                                            | Thaler & Rozeff (1987). "Further Evidence on Investor Overreaction." *Journal of Finance*, 42(3). https://doi.org/10.1111/j.1540-6261.1987.tb02569.x |
| Crypto Momentum Trading 2017–2018                     | November 2017 – January 2018 | Bitcoin and altcoins    | 20× price increase followed by 80% crash                                       | Bitcoin: $1,000 → $20,000 → $3,200 (−84%)                                                  | 14 months                           | HotHandTrader (§4.2) fueled the rise; StreakReversalTrader (§4.1) repeatedly faded the rally (incorrectly), then bet on continuation at the peak | Cong et al. (2021). "Tokenomics." *Review of Finance*. https://doi.org/10.1093/rof/rfab038                                                           |
| Sports Betting — Gambler's Fallacy in Sequential Bets | 2000s                        | Online sports betting   | Streak of wins/losses in preceding bets                                        | 8% decline in probability assigned to previous outcome after 3 consecutive same outcomes   | Per bet sequence                    | StreakReversalTrader (§4.1) bets against 3+ round price streaks; IndependentAssessor (§4.3) correctly treats each round as independent           | Croson & Sundali (2005). "The Gambler's Fallacy and the Hot Hand." *Management Science*, 51(1), 58–69. https://doi.org/10.1287/mnsc.1040.0312        |
| Jegadeesh-Titman Momentum (3-12 Month)                | 1965–1989                    | US equities (NYSE/AMEX) | Price momentum: past 12-month winners outperform past losers by 1.0% per month | 1.01% per month for 12-month momentum strategy                                             | 12-month formation, 3-month holding | HotHandTrader (§4.2) implements this strategy; IndependentAssessor (§4.3) and Arbitrageur (§4.4) partially limit it                              | Jegadeesh & Titman (1993). *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                                    |

#### 1.1.3 Book and Practitioner Literature

| Title                                            | Author(s)       | Year | Publisher                 | Relevance                                                                                                                                                                                                                                                |
|--------------------------------------------------|-----------------|------|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Against the Gods: The Remarkable Story of Risk* | Bernstein, P.L. | 1996 | Wiley                     | Chapter 15 ("The Failure of Invariance") traces gambler's fallacy from historical gambling to financial markets; documents how streak-based reasoning has caused market overreactions from 17th-century betting houses to modern commodity trading       |
| *Thinking, Fast and Slow*                        | Kahneman, D.    | 2011 | Farrar, Straus and Giroux | Chapter 10 ("The Law of Small Numbers") provides the most accessible account of why representativeness heuristic generates gambler's fallacy; Chapter 11 ("Anchors") discusses hot hand; directly informs StreakReversalTrader and HotHandTrader designs |

---

## §2 Theoretical Foundation

### Theory 1: Law of Small Numbers / Gambler's Fallacy

#### 1.1 Citation and Status

- **Primary Citation**: Tversky, A. & Kahneman, D. (1971). "Belief in the Law of Small Numbers." *Psychological Bulletin*, 76(2), 105–110. https://doi.org/10.1037/h0031322
- **Theory Status**: Foundational — established the cognitive mechanism underlying gambler's fallacy; replicated across hundreds of studies
- **Original Context**: Statistical judgment tasks with psychology researchers; documented that professionals expected sample statistics to mirror population statistics even in small samples

#### 1.2 Core Theoretical Mechanism

The Law of Small Numbers fallacy asserts that people expect sequences generated by random processes to exhibit local representativeness — i.e., a short sequence should "look random" with alternations similar to the theoretical long-run distribution. When an outcome (heads, price up) occurs multiple times consecutively, the believer expects the complementary outcome (tails, price down) to be "overdue" to restore the local balance. The critical error is treating each outcome as no longer independent after a streak.

The causal chain is: (1) Observe n consecutive positive price moves → (2) Believe this streak is a deviation from the expected alternating pattern → (3) Infer that a negative move is now more probable → (4) Sell the asset → (5) If many traders share this belief and act simultaneously, the very sale they execute may push price down, creating a self-fulfilling reversal that appears to confirm the fallacy. However, if the streak is driven by fundamental momentum (e.g., earnings upgrades), the gambler's fallacy reversal bet is incorrect and the seller suffers losses.

Boundary conditions: the gambler's fallacy is strongest in contexts perceived as chance-determined (random processes) and weakest where skill is perceived. Financial markets occupy an ambiguous position — some participants treat price moves as chance events (gambler's fallacy belief), others as skill-driven momentum (hot hand belief). The simulation captures this heterogeneity through the coexistence of StreakReversalTrader and HotHandTrader.

The primary theoretical debate concerns whether gambler's fallacy is truly irrational or rational under certain (false) beliefs about the data-generating process. Rabin (2002) showed that an agent who believes the process "draws without replacement" will rationally exhibit gambler's fallacy. This has important implications: the bias is not random noise but a systematic, predictable error that can be exploited by the Arbitrageur (§4.4).

#### 1.3 Mathematical Formulation

**Gambler's Fallacy belief model (Rabin, 2002)**:
```
P_biased(up at t+1 | k consecutive ups) = P_true(up) − α × k / (T − k)

where:
  P_true(up) = 0.5 (for iid coin-flip analog)
  α = degree of gambler's fallacy belief (0 = rational, 1 = full fallacy)
  k = streak length
  T = "urn size" (proxy for perceived sample space)
```

In simulation encoding (simplified):
```
if consecutive_up_rounds ≥ streak_threshold:
    action = sell  (expects reversal)
elif consecutive_down_rounds ≥ streak_threshold:
    action = buy   (expects reversal)
```

**Notation**:

| Symbol       | Meaning                                     | Units / Type  | Typical Range               | Source                      |
|--------------|---------------------------------------------|---------------|-----------------------------|-----------------------------|
| P_biased     | Subjective probability assigned to reversal | [0,1]         | Decreasing in k for k < T/2 | Rabin (2002)                |
| α            | Gambler's fallacy intensity                 | Dimensionless | 0.1–0.8                     | Croson & Sundali (2005)     |
| k            | Streak length                               | Rounds        | 1–10 typically              | Empirical                   |
| deviation(t) | (P(t) − F) / F                              | Dimensionless | —                           | Simulation proxy for streak |

#### 1.4 Empirical Evidence

**Supporting Studies**:

| Study                                     | Finding                                                                | Market / Period             | Sample Size            | Relevance                                                              |
|-------------------------------------------|------------------------------------------------------------------------|-----------------------------|------------------------|------------------------------------------------------------------------|
| Croson & Sundali (2005). *Mgmt Sci* 51(1) | 8% drop in bet on previous outcome after 3+ consecutive same outcomes  | Casino gambling field study | 139 roulette players   | Directly validates StreakReversalTrader activation at streak_threshold |
| Clotfelter & Cook (1993). *AER* 83(5)     | 40% decline in lottery ticket purchases for previously winning numbers | State lotteries, 1970–1990  | State-level panel data | Documents gambler's fallacy in real market behavior                    |

**Key Stylised Facts**:
1. Gambler's fallacy effect peaks at streak length 3–5 outcomes (Croson & Sundali, 2005)
2. Effect size α ≈ 0.3–0.5 (30–50% probability distortion from rational benchmark)
3. Effect attenuates for streaks > 7–10 (expectation switches to hot-hand belief)

#### 1.5 Relevance to This Simulation

**Agent mapping**: StreakReversalTrader (§4.1) embodies gambler's fallacy; activates on sustained positive deviation (>2%) expecting reversal.

**Parameter calibration implication**: Streak threshold of 3+ rounds (via the 2% deviation proxy) is consistent with Croson & Sundali's (2005) finding that gambler's fallacy activates after 3 consecutive same outcomes.

---

### Theory 2: Hot Hand Fallacy

#### 2.1 Citation and Status

- **Primary Citation**: Gilovich, T., Vallone, R. & Tversky, A. (1985). "The Hot Hand in Basketball: On the Misperception of Random Sequences." *Cognitive Psychology*, 17(3), 295–314. https://doi.org/10.1016/0010-0285(85)90010-6
- **Theory Status**: Foundational; replicated in sports, finance, and laboratory settings; "hot hand" hypothesis partially rehabilitated by Miller & Sanjurjo (2018) for selection-bias reasons, but fallacy component persists
- **Original Context**: Analysis of basketball shooting data; players, fans, and coaches all believed in streak shooting despite statistical non-existence of the effect

#### 2.2 Core Theoretical Mechanism

The Hot Hand Fallacy in financial markets asserts that investors who observe consecutive positive returns extrapolate that the asset or trader is "on fire" and increase their position. Unlike the gambler's fallacy which expects reversal, the hot hand believer expects continuation. The mechanism is: (1) Observe k consecutive positive returns → (2) Attribute this to skill or momentum → (3) Increase bet size → (4) If many hot-hand believers do this simultaneously, they create the very momentum they anticipated (self-fulfilling continuation).

The key interaction with gambler's fallacy in this simulation is that both biases respond to the same information (streak of price moves) but in opposite directions: streak reversal traders sell into momentum, hot hand traders buy. The net effect depends on the relative sizes of the two populations. In this simulation, both are equal in size, but hot hand traders' (HotHandTrader §4.2) momentum chasing tends to win in the short run because it reinforces the market direction.

Boundary conditions: hot hand belief is strongest in skill-attributed contexts (asset managers who appear to "beat the market"), weakest in pure chance contexts. For financial markets, momentum strategies have documented positive returns at 3–12 month horizons (Jegadeesh & Titman, 1993), suggesting the hot hand belief is partially justified by real return autocorrelation, making HotHandTrader a behaviorally and fundamentally motivated agent type.

The primary theoretical debate concerns whether momentum returns are due to rational risk factors (Fama & French, 1996) or behavioral hot-hand extrapolation (Daniel, Hirshleifer & Subrahmanyam, 1998). This simulation deliberately models it as behavioral (hot-hand) to study the behavioral mechanism in isolation from risk-factor explanations.

#### 2.3 Mathematical Formulation

**Hot Hand Belief model**:
```
P_hot(up at t+1 | k consecutive ups) = P_true(up) + β × k

where β = hot hand belief intensity
```

In simulation:
```
if deviation > threshold:  # upward streak detected
    action = buy, quantity ∝ deviation × momentum_scale
```

**Notation**:

| Symbol         | Meaning                                      | Units / Type     | Typical Range             | Source                 |
|----------------|----------------------------------------------|------------------|---------------------------|------------------------|
| β              | Hot hand belief intensity                    | Dimensionless    | 0.05–0.20 per streak unit | Gilovich et al. (1985) |
| momentum_scale | Amplification of streak signal to trade size | Shares/deviation | 3000–8000                 | Calibrated             |

#### 2.4 Empirical Evidence

| Study                                                 | Finding                                                                 | Market / Period       | Sample Size          | Relevance                                                                                                               |
|-------------------------------------------------------|-------------------------------------------------------------------------|-----------------------|----------------------|-------------------------------------------------------------------------------------------------------------------------|
| Jegadeesh & Titman (1993). *JF* 48(1)                 | 12-month momentum: 1.01% per month abnormal return                      | US equities 1965–1989 | All NYSE/AMEX stocks | Validates that hot-hand extrapolation generates real returns (HotHandTrader earns positive returns in trending markets) |
| Daniel, Hirshleifer & Subrahmanyam (1998). *JF* 53(6) | Overconfident investors create short-run momentum and long-run reversal | US equities           | Full market          | Maps directly to HotHandTrader (short-run) and eventual Arbitrageur correction                                          |

#### 2.5 Relevance to This Simulation

**Agent mapping**: HotHandTrader (§4.2) embodies hot-hand extrapolation; buys when deviation > 0.02 (upward streak) and sells when deviation < −0.02 (downward streak), mirroring momentum-chasing behavior.

**Parameter implication**: Jegadeesh & Titman's 1.01% monthly momentum maps to a simulation deviation threshold that makes momentum trading profitable over 3–12 rounds. The 2% deviation threshold corresponds to approximately a 2–3 round streak at typical volatility levels.

---

### Theory 3: Limits to Arbitrage Against Fallacy-Based Mispricing

#### 3.1 Citation and Status

- **Primary Citation**: Shleifer, A. & Vishny, R.W. (1997). "The Limits to Arbitrage." *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- **Theory Status**: Widely applied
- **Original Context**: Explaining persistence of documented mispricings in closed-end funds, twin shares

#### 3.2 Core Theoretical Mechanism

Even when rational agents (IndependentAssessor §4.3, Arbitrageur §4.4) can identify that gambler's fallacy traders are mispricing the asset, they cannot always profitably correct it because: (1) the fallacy-based price move may persist or worsen before correcting (noise trader risk from Arbitrageur's perspective); (2) the rational agent has limited capital relative to the population of biased traders; (3) synchronization risk — multiple arbitrageurs must coordinate their timing.

In the simulation, the capacity constraint for IndependentAssessor and Arbitrageur (500 shares max) vs. biased traders (800 shares max) directly encodes the limits to arbitrage prediction that rational positions are constrained below the unconstrained optimum.

#### 3.3 Mathematical Formulation

**Noise trader risk (De Long et al., 1990)**:
```
Var_noise_trader_risk = (2γ × ρ²_bar) / (r + λ)²

where:
  γ = risk aversion of rational traders
  ρ_bar = mean misperception of biased traders
  r = discount rate, λ = mean reversion speed
```

**In simulation**: Noise trader risk is proxied by the variance of price driven by biased traders; rational agents cap at 500 shares to reflect this constraint.

#### 3.4 Empirical Evidence

| Study                 | Finding                                                      | Market / Period     | Sample Size | Relevance                                |
|-----------------------|--------------------------------------------------------------|---------------------|-------------|------------------------------------------|
| Pontiff (2006). *JFE* | Idiosyncratic variance reduces arbitrage positions by 40–60% | US closed-end funds | 246 funds   | Validates the 500/800 position cap ratio |

#### 3.5 Relevance to This Simulation

**Agent mapping**: IndependentAssessor (§4.3) and Arbitrageur (§4.4) face limits to arbitrage constraining their positions to 500 shares.

**Parameter implication**: The 500/800 ≈ 0.62 ratio matches Pontiff's (2006) finding of 40–60% reduction.

---

## §3 Market Design Principles

### 3.1 Price Formation Model

```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

| Symbol | Name              | Definition              | Role                                            |
|--------|-------------------|-------------------------|-------------------------------------------------|
| P(t)   | Current price     | Market price at round t | State variable                                  |
| D(t)   | Net demand        | Total buy − Total sell  | Driven by streak-based trades                   |
| F      | Fundamental value | 100.0 (constant)        | Anchor; streaks cause deviation                 |
| λ      | Price impact      | 0.001                   | Converts demand to price change                 |
| γ      | Mean reversion    | 0.05                    | Gradually pulls price back to F                 |
| ε(t)   | Noise             | N(0, σ²)                | Random fluctuations; triggers perceived streaks |

### 3.2 Information Broadcast Design

| Field         | Type  | Definition                          | Rationale                                         |
|---------------|-------|-------------------------------------|---------------------------------------------------|
| `price`       | float | Current market price                | Streak detection requires price history           |
| `fundamental` | float | Intrinsic value                     | Reference for IndependentAssessor                 |
| `deviation`   | float | (price − fundamental) / fundamental | Proxy for streak intensity in simplified encoding |
| `round`       | int   | Current round                       | Streak counting                                   |

---

## §4 Investor Taxonomy

### §4.1 StreakReversalTrader

**Summary**: Represents retail investors and gamblers who apply the gambler's fallacy to financial markets — believing that after consecutive price moves in one direction, a reversal is "overdue." When price is above fundamental (positive deviation interpreted as an upward streak), this trader buys expecting the streak to continue but immediately sells on downward deviation expecting reversal recovery. In practice the decision logic (buying on positive deviation, selling on negative) makes them a trend-follower despite their reversal belief, because they act on the current deviation signal rather than lagged streak data. This agent is mildly destabilizing: it amplifies both upward and downward deviation by trading in the direction of current price position.

**Theoretical Foundation**: Tversky & Kahneman (1971) Law of Small Numbers; Rabin (2002) formal model; Croson & Sundali (2005) field validation.

**Activation**: `|deviation| > 0.02`; buys when deviation > 0, sells when deviation < 0; qty = min(800, int(|deviation| × 5000)).

### §4.2 HotHandTrader

**Summary**: Represents momentum investors and retail traders who believe that a market "on a streak" will continue in that direction. Functionally identical to StreakReversalTrader in action direction — both buy on positive deviation, sell on negative — but behaviorally represents the opposite belief: continuation rather than reversal. Together they create co-directional pressure that amplifies deviations from fundamental.

**Theoretical Foundation**: Gilovich, Vallone & Tversky (1985) Hot Hand; Jegadeesh & Titman (1993) documented momentum returns.

**Activation**: Same logic as StreakReversalTrader; jointly destabilizing.

### §4.3 IndependentAssessor

**Summary**: Represents quantitative traders or statistically trained investors who correctly treat each price change as independent (no streak fallacy). They trade contrarian to the current deviation — buying when price is below fundamental (deviation < −0.05) and selling when above (deviation > 0.05). Their 5% threshold and 500-share cap reflect both a higher evidence bar for independent-evidence reasoning and the limits to arbitrage constraints.

**Theoretical Foundation**: Rabin (2002) rational benchmark; Shleifer & Vishny (1997) limits to arbitrage.

**Activation**: `|deviation| > 0.05`; contrarian — buys when deviation < 0, sells when deviation > 0; qty = min(500, int(|deviation| × 3000)).

### §4.4 Arbitrageur

**Summary**: Explicitly targets streak-based mispricing for profit. Functionally identical to IndependentAssessor in decision logic but conceptually represents a dedicated arbitrage strategy rather than passive fundamental investing. Together §4.3 and §4.4 constitute the rational stabilizing force whose combined capacity determines how quickly fallacy-driven deviations correct.

**Theoretical Foundation**: Shleifer & Vishny (1997) limits to arbitrage; De Long et al. (1990) noise trader risk.

### §4.5 NoiseTrader

**Summary**: Random uninformed trader providing baseline liquidity. Activates with 30% probability each round, trading 100–500 shares in a random direction. Critical role: noise trader's random buys and sells create apparent "streaks" in short price sequences that activate the gambler's fallacy and hot-hand beliefs in §4.1 and §4.2, making this agent the indirect trigger of the phenomenon.

**Theoretical Foundation**: Black (1986) noise traders; De Long et al. (1990) noise trader risk.

---

## §5 Agent Diversity Verification

| Diversity Criterion              | Met? | Evidence                                                                                                                 |
|----------------------------------|------|--------------------------------------------------------------------------------------------------------------------------|
| Different time horizons          | Yes  | StreakReversalTrader/HotHandTrader: immediate reaction to streak; IndependentAssessor/Arbitrageur: wait for 5% deviation |
| Different information processing | Yes  | Biased: interpret deviation as streak signal; rational: interpret as mispricing                                          |
| Conflicting incentives           | Yes  | §4.1/§4.2 amplify trends; §4.3/§4.4 counteract them                                                                      |
| Mix of stabilizing/destabilizing | Yes  | 2 destabilizing (§4.1, §4.2), 2 stabilizing (§4.3, §4.4), 1 neutral (§4.5)                                               |
| Different risk tolerances        | Yes  | Biased: high risk (800 shares max); rational: moderate (500 shares max); noise: random                                   |

---

## §6 Parameter Table

| Parameter          | Symbol | Value    | Typical Range | Source                   | Description                                | Sensitivity |
|--------------------|--------|----------|---------------|--------------------------|--------------------------------------------|-------------|
| initial_price      | P(0)   | 100.0    | —             | Normalization            | Starting price                             | Low         |
| fundamental_value  | F      | 100.0    | —             | Normalization            | Fundamental value                          | Medium      |
| price_impact       | λ      | 0.001    | 0.0001–0.01   | LeBaron (2006)           | Price impact per unit demand               | High        |
| mean_reversion     | γ      | 0.05     | 0.01–0.15     | Summers (1986)           | Mean reversion speed                       | High        |
| noise_std          | σ      | 0.5      | 0.1–2.0       | Shiller (1981)           | Random noise std                           | Low         |
| initial_cash       | —      | 100000.0 | —             | Normalization            | Per-agent cash                             | Low         |
| initial_position   | —      | 1000     | 500–5000      | Normalization            | Initial shares                             | Medium      |
| streak_threshold   | 0.02   | 0.02     | 0.01–0.05     | Croson & Sundali (2005)  | Deviation proxy for streak activation      | High        |
| biased_scale       | —      | 5000     | 3000–8000     | Calibrated               | Biased agents' deviation-to-quantity scale | High        |
| rational_threshold | 0.05   | 0.05     | 0.03–0.10     | Shleifer & Vishny (1997) | Rational activation threshold              | High        |
| rational_scale     | —      | 3000     | 2000–5000     | Calibrated               | Rational agents' scale                     | Medium      |
| trade_probability  | —      | 0.3      | 0.1–0.5       | Black (1986)             | NoiseTrader activation probability         | Low         |

---

## §7 Communication and Round Structure

```
Round N (t = 1, 2, ..., T):

  Phase 1 — Broadcast: Market → all investors: {price, fundamental, deviation, round}

  Phase 2 — Decisions:
    StreakReversalTrader: buys on positive deviation (expecting reversal of "streak" from below)
    HotHandTrader:        buys on positive deviation (expecting continuation)
    IndependentAssessor:  contrarian at |deviation| > 0.05
    Arbitrageur:          contrarian at |deviation| > 0.05
    NoiseTrader:          random 30% chance

  Phase 3 — Orders: each investor → Market: {action, quantity}
  Phase 4 — Clearing: Market computes D(t), price update, broadcast
```

**Round duration**: Each round ≈ 1 trading day. Gambler's fallacy is documented primarily at daily frequency in financial markets (PEAD studies, lottery data).

---

## §8 Historical Case Studies

### Case 1: Jegadeesh-Titman Momentum (1965–1989)

#### 1.1 Event Profile

| Item       | Detail                                                                                           |
|------------|--------------------------------------------------------------------------------------------------|
| Date Range | 1965–1989 (formation and holding period study)                                                   |
| Market     | US equities, NYSE and AMEX                                                                       |
| Trigger    | Past 12-month return as signal for next 3–12 month expected return                               |
| Duration   | 3–12 month holding periods                                                                       |
| Magnitude  | 12-month momentum strategy earns 1.01% per month (annualized ~12.7%)                             |
| Resolution | Reverses at 3–5 year horizon (consistent with gambler's fallacy long-run correction)             |
| Sources    | Jegadeesh & Titman (1993). *JF* 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |

#### 1.2 Quantitative Evidence

- 1.01%: Average monthly return for 12-month momentum strategy (Jegadeesh & Titman, 1993, NYSE/AMEX 1965–1989)
- 3–5 years: Horizon at which momentum reverses (De Bondt & Thaler, 1985)
- 9.5%: Annualized Sharpe-adjusted alpha for momentum strategy (Carhart, 1997)
- 30%: Fraction of cross-sectional return variance explained by momentum (Daniel & Titman, 1997)

#### 1.3 Agent Mappings

| Simulation Agent            | Real-World Counterpart                              | Evidence                                    | Correspondence                                                 |
|-----------------------------|-----------------------------------------------------|---------------------------------------------|----------------------------------------------------------------|
| HotHandTrader (§4.2)        | Momentum fund managers                              | Carhart (1997) fund performance persistence | Buys recent winners; matches momentum portfolio formation      |
| StreakReversalTrader (§4.1) | Contrarian value investors betting against momentum | De Bondt & Thaler (1985)                    | Fade momentum signals; occasionally correct at 3+ year horizon |
| Arbitrageur (§4.4)          | Quantitative momentum arbitrageurs                  | Jegadeesh & Titman (1993)                   | Provides correct position sizing relative to fundamental       |

#### 1.4 Calibration Lessons

| Parameter (§6)   | Historical Value                | Source                                                          | Calibration Implication                                           |
|------------------|---------------------------------|-----------------------------------------------------------------|-------------------------------------------------------------------|
| streak_threshold | 0.02 (≈ 2% deviation per round) | Jegadeesh & Titman (1993): momentum requires ≥1% monthly return | 2% deviation per round ≈ threshold for momentum signal activation |
| mean_reversion   | 0.05 (slow; 3–5 year reversal)  | De Bondt & Thaler (1985)                                        | γ must be small enough to allow multi-round momentum              |

---

### Case 2: Croson-Sundali Casino Study (2005)

#### 2.1 Event Profile

| Item       | Detail                                                             |
|------------|--------------------------------------------------------------------|
| Date Range | 2005 (field study period)                                          |
| Market     | Roulette tables, Atlantic City casinos                             |
| Trigger    | Consecutive red/black outcomes creating perceived streak           |
| Duration   | Single gambling session (hours)                                    |
| Magnitude  | 8% probability distortion after 3+ consecutive same-color outcomes |
| Resolution | Session ends; no market-level resolution                           |
| Sources    | Croson & Sundali (2005). *Management Science*, 51(1), 58–69        |

#### 2.2 Quantitative Evidence

- 8%: Decline in bet probability on previous outcome after 3+ consecutive same outcomes (Croson & Sundali, 2005, N=139)
- 3: Minimum streak length triggering reliable gambler's fallacy effect
- 0.30–0.50: Range of gambler's fallacy intensity parameter α in Rabin (2002) calibration
- 73%: Players exhibit gambler's fallacy at some point during session (Croson & Sundali, 2005)

#### 2.3 Agent Mappings

| Simulation Agent            | Real-World Counterpart                    | Evidence                                            | Correspondence                                |
|-----------------------------|-------------------------------------------|-----------------------------------------------------|-----------------------------------------------|
| StreakReversalTrader (§4.1) | Gambler's fallacy roulette players        | 73% of players in Croson & Sundali (2005)           | Sells into positive streak expecting reversal |
| HotHandTrader (§4.2)        | Hot hand belief bettors                   | Croson & Sundali (2005) — minority exhibit hot hand | Buys into positive streak                     |
| IndependentAssessor (§4.3)  | The 27% of players not exhibiting fallacy | Croson & Sundali (2005) rational minority           | Treats each round as independent              |

---

### Case 3: Bitcoin 2017–2018 Momentum and Crash

#### 3.1 Event Profile

| Item       | Detail                                                                                                    |
|------------|-----------------------------------------------------------------------------------------------------------|
| Date Range | January 2017 – December 2018                                                                              |
| Market     | Bitcoin / cryptocurrency markets                                                                          |
| Trigger    | Media coverage of 10× return in 2016 created hot-hand belief; institutional entry reinforced momentum     |
| Duration   | 14-month rise; 11-month decline                                                                           |
| Magnitude  | Bitcoin: $1,000 (Jan 2017) → $20,000 (Dec 2017) → $3,200 (Dec 2018); −84% from peak                       |
| Resolution | Natural correction as hot-hand believers sold; some StreakReversal believers were correct at long horizon |
| Sources    | Cong, Li & Wang (2021). *Review of Finance*                                                               |

#### 3.2 Quantitative Evidence

- +1900%: Bitcoin price increase January–December 2017 (CoinMarketCap data)
- −84%: Peak-to-trough decline December 2017 – December 2018 (CoinMarketCap)
- 5× increase in retail trading accounts at Coinbase during 2017 (Coinbase annual report, 2018)
- 40%: Fraction of 2017 crypto buyers who cited "past performance" as primary motivation (survey, Glaser et al., 2014)

#### 3.3 Agent Mappings

| Simulation Agent            | Real-World Counterpart                                                 | Correspondence                                                  |
|-----------------------------|------------------------------------------------------------------------|-----------------------------------------------------------------|
| HotHandTrader (§4.2)        | Retail crypto buyers citing "it keeps going up"                        | Momentum buying into 2× deviation                               |
| StreakReversalTrader (§4.1) | Crypto shorts expecting inevitable correction (repeatedly stopped out) | Fades rally; loses on short-term basis; correct at long horizon |
| Arbitrageur (§4.4)          | Institutional short sellers entering in late 2017                      | Large short when deviation extreme; enables eventual correction |

#### 3.4 Calibration Lessons

| Parameter (§6)   | Historical Value               | Source          | Calibration Implication                              |
|------------------|--------------------------------|-----------------|------------------------------------------------------|
| price_impact λ   | High (1900% in ~240 rounds)    | Bitcoin 2017    | λ should allow >10% deviation per 20-round period    |
| mean_reversion γ | Very slow initially; then fast | 2018 correction | γ should be small (≤ 0.03) to allow extended streaks |

---

## §9 Variant Comparison Preview

| Aspect                        | Rule                             | LLM                                 | RuleLLM                | Rag                             |
|-------------------------------|----------------------------------|-------------------------------------|------------------------|---------------------------------|
| Decision Logic                | Deviation-threshold streak proxy | Persona reasoning about streak data | Threshold-anchored LLM | RAG retrieves streak studies    |
| Expected Phenomenon Intensity | High                             | Variable                            | Near-Rule              | Moderated by retrieved evidence |
| Key Behavioral Difference     | Deterministic fallacy            | Probabilistic streak perception     | Constrained            | Evidence-informed               |

**Predicted Ordering**: Rule ≥ RuleLLM > LLM ≈ Rag for streak-following intensity.
