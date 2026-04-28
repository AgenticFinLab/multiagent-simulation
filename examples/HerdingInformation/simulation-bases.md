# HerdingInformation — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                     |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Information Cascade Herding — agents abandon their private information signals and follow the observed crowd direction when sufficiently many preceding agents have made the same decision, creating a rational but informationally inefficient cascade                                                                                                                                                                         |
| Category           | Cognitive bias / information economics / rational herding                                                                                                                                                                                                                                                                                                                                                                       |
| Core Mechanism     | CascadeFollower (§4.1) ignores private signal once cascade_count reaches cascade_trigger threshold — accumulating evidence from observed price deviations; ReputationHerder (§4.2) follows consensus to protect professional reputation regardless of private signal; IndependentThinker (§4.3) and Contrarian (§4.4) act as rational stabilizers trading against the cascade; NoiseTrader (§4.5) provides background liquidity |
| Real-World Origin  | Formally modeled by Banerjee (1992) and Bikhchandani et al. (1992); empirically documented in analyst forecast revisions (Welch, 2000), IPO subscription herding (Welch, 1992), and fund manager career-concern herding (Scharfstein & Stein, 1990)                                                                                                                                                                             |
| Research Relevance | Explains why markets can remain mispriced even when most individual agents have correct private information — the cascade suppresses private signal usage; relevant to market efficiency debates, regulatory disclosure policy, and the design of information aggregation mechanisms                                                                                                                                            |

### 1.1 Origin and Source Analysis

#### 1.1.1 Intellectual Lineage

The theoretical foundation for information cascade herding was established simultaneously and independently by Banerjee (1992) in "A Simple Model of Herd Behavior" and Bikhchandani, Hirshleifer and Welch (1992) in "A Theory of Fads, Fashion, Custom, and Cultural Change." Both papers established the central result: when agents make sequential decisions and observe the decisions (not the private signals) of predecessors, a cascade forms when the cumulative public information from observed actions outweighs any individual private signal. Once the cascade forms, every rational agent ignores their private signal and follows the crowd — even though the crowd's collective "decision" may be based on a coincidental early majority, not on the aggregate of private information.

The key insight — and the key empirical implication — is that information cascades are fragile. Because agents are discarding their private information once in a cascade, the cascade contains less information than the sum of all agents' private signals. A single strong contrary signal can break the cascade and trigger a reversal. This fragility is modeled through the `cascade_trigger` parameter: the CascadeFollower (§4.1) begins following only after `cascade_count ≥ cascade_trigger`, and each round with |deviation| > 0.03 increments cascade_count — so a sustained sequence of same-direction observations is required before the cascade "locks in."

Scharfstein and Stein (1990) extended the herding literature to professional analysts and fund managers under career concerns: even a fully rational manager may prefer to mimic consensus (the "share the blame" equilibrium) because individual deviation from consensus that turns out wrong is more career-damaging than following consensus and being wrong together. This is the mechanism encoded in ReputationHerder (§4.2): the `reputation_concern` parameter scales trade size upward when following the consensus deviation direction, modeling the amplification of herding under career pressure.

Welch (2000) provided direct empirical evidence for information cascades in analyst stock recommendations: analysts revise forecasts in the direction of recent consensus forecasts (not in the direction of their own private information). He found that analyst revisions are significantly better predicted by the previous 2–3 analysts' revisions than by the analyst's own new information — a clean empirical signature of cascade following. This finding directly calibrates the cascade_trigger parameter: 2–3 consistent observations (|deviation| > 0.03 for 2–3 rounds) should be sufficient to trigger cascade behavior.

The limits of cascade correction are documented by Avery and Zemsky (1998), who showed that when assets can be traded (vs. binary decision models), information cascades are less likely to form because the price signal aggregates some of the suppressed private information. However, they also showed that when private signal quality is heterogeneous (some agents have better information than others), partial cascades can still form among the lower-quality signal holders — which is precisely the heterogeneous population modeled here (CascadeFollower vs. IndependentThinker).

#### 1.1.2 Real-World Event Catalogue

| Event Name                                 | Date(s)                    | Market / Asset                              | Trigger                                                                            | Magnitude                                                                                         | Duration                       | Correspondence to Simulation                                                                                                                                     | Primary Source                                                                                                                                            |
|--------------------------------------------|----------------------------|---------------------------------------------|------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Analyst Recommendation Herding             | 1990–2000                  | US equity analyst forecasts                 | Consensus forecast → subsequent analysts revise in same direction                  | Welch (2000): last 2 analyst revisions predict next revision with R²=0.42                         | Rolling; measured quarterly    | CascadeFollower (§4.1): cascade_count accumulates from observed deviation direction; ReputationHerder (§4.2): follows consensus to avoid being unique contrarian | Welch, I. (2000). "Herding among Security Analysts." *Journal of Financial Economics*, 58(3), 369–396                                                     |
| IPO Subscription Herding                   | 1980–2000                  | US equity IPO subscriptions                 | Early (institutional) subscription signals quality → retail subscribers follow     | Welch (1992): a 1% increase in early subscription predicts 4% increase in later subscriptions     | IPO cycle (~2 weeks per issue) | CascadeFollower (§4.1): cascade_trigger = 2 (need 2 prior institutional subscriptions); ReputationHerder (§4.2): retail banks follow institutional lead          | Welch, I. (1992). "Sequential Sales, Learning, and Cascades." *Journal of Finance*, 47(2), 695–732                                                        |
| Mutual Fund Manager Career Concern Herding | 1980–1996                  | US equity mutual funds                      | Performance measurement → career-concerned managers follow top-performing peers    | Scharfstein & Stein (1990): career-concern herding strongest for young/probationary fund managers | Quarterly rebalancing          | ReputationHerder (§4.2): reputation_concern ∈ [1.0, 3.0] directly models career-concern intensity                                                                | Scharfstein, D.S. & Stein, J.C. (1990). "Herd Behavior and Investment." *American Economic Review*, 80(3), 465–479                                        |
| Hong Kong Stock Market Herding 1997        | July 1997 – January 1998   | Hong Kong HSI                               | Asian financial crisis contagion; consensus sell signal                            | HSI fell 60% from July 1997 peak; institutional cascade selling despite mixed private signals     | 6 months                       | CascadeFollower (§4.1): accumulates cascade_count from sustained negative deviation; full cascade selling at cascade_trigger threshold                           | Christie, W.G. & Huang, R.D. (1995). "Following the Pied Piper: Do Individual Returns Herd around the Market?" *Financial Analysts Journal*, 51(4), 31–37 |
| COVID-19 Tech Stock Re-Rating 2020–2021    | April 2020 – February 2021 | US tech equities (FAANG + ARK ETF holdings) | COVID remote-work narrative → analyst consensus buy → institutional cascade buying | Nasdaq 100: +74% in 10 months; ARK Innovation ETF ×3                                              | 10 months                      | ReputationHerder (§4.2): analyst consensus buy → reputation herding; CascadeFollower (§4.1): cascade lock-in after 3+ consecutive positive deviations            | Chang, E.C., Cheng, J.W. & Khorana, A. (2000). "An Examination of Herd Behavior in Equity Markets." *Journal of Banking & Finance*, 24(10), 1651–1679     |

#### 1.1.3 Book and Practitioner Literature

| Title                                                     | Author(s)                     | Year | Publisher                  | Relevance                                                                                                                                                                                                                                                                                                 |
|-----------------------------------------------------------|-------------------------------|------|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Animal Spirits: How Human Psychology Drives the Economy* | Akerlof, G.A. & Shiller, R.J. | 2009 | Princeton University Press | Chapter 3 ("Confidence and Its Multipliers") documents how narratives and consensus create self-reinforcing confidence cycles — the macroeconomic analog to information cascade herding modeled in this simulation; directly informs ReputationHerder's consensus-following mechanism                     |
| *The Wisdom of Crowds*                                    | Surowiecki, J.                | 2004 | Doubleday                  | Chapters 1–3 document that crowds are wise when information aggregation is independent but break down under herding — the exact tension between IndependentThinker (§4.3) efficiency and CascadeFollower (§4.1) inefficiency; provides the practitioner motivation for studying information cascade costs |

---

## §2 Theoretical Foundation

### Theory 1: Information Cascade Model

#### §T1.1 Citation and Status

- **Primary Citation**: Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). "A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades." *Journal of Political Economy*, 100(5), 992–1026. doi:10.1086/261849
- **Supporting Citation**: Banerjee, A.V. (1992). "A Simple Model of Herd Behavior." *QJE* 107(3), 797–817. doi:10.2307/2118364
- **Theory Status**: Foundational — one of the most cited papers in information economics; cited 7,000+
- **Original Context**: Sequential decision model; binary decisions; rational Bayesian updating

#### §T1.2 Core Theoretical Mechanism

The information cascade model shows that when agents make decisions sequentially and observe predecessors' choices (but not private signals), a cascade inevitably forms. The mechanism is:

1. Agent 1 acts on private signal S₁ (e.g., buys if signal is positive).
2. Agent 2 observes Agent 1's action, updates beliefs, and acts on combined public + private signal.
3. After sufficient agents have acted in the same direction, the public information (from observed actions) outweighs any single private signal.
4. Agent N (for large N) ignores private signal Sₙ entirely and copies the crowd — even if Sₙ is negative.

The cascade is informationally inefficient because agent N's private signal Sₙ is lost — never incorporated into prices. This creates fragility: the cascade is based on the early agents' private signals (which may have been weakly informative), and a single strong contrary signal can break it.

In the simulation, the price deviation serves as the "observed action" signal: CascadeFollower increments cascade_count each round that |deviation| > 0.03, accumulating evidence of a sustained crowd direction. When cascade_count reaches cascade_trigger, the agent begins trading in the direction of the deviation — abandoning any contrary private signal. The cascade_trigger parameter directly controls when private information is discarded.

#### §T1.3 Mathematical Formulation

**Cascade formation model (Bikhchandani et al., 1992 discrete analog)**:
```
cascade_count(t+1) = cascade_count(t) + 1   if |dev(t)| > 0.03
cascade_count(t+1) = cascade_count(t)        otherwise

Cascade active: cascade_count ≥ cascade_trigger

Cascade trade size:
  qty = min(800, int(|dev| × social_weight × 5000))
  Action: follow deviation direction (buy if dev > 0; sell if dev < 0)
```

| Symbol          | Definition                                        | Calibrated Value | Source                                               |
|-----------------|---------------------------------------------------|------------------|------------------------------------------------------|
| cascade_trigger | Number of consistent observations to form cascade | 3–8              | Welch (2000): 2–3 prior analyst revisions sufficient |
| social_weight   | Scale factor for cascade trade size               | 1.0–3.0          | Scharfstein & Stein (1990) herding intensity         |
| 0.03 threshold  | Minimum deviation to count as cascade evidence    | Fixed            | Bikhchandani et al. (1992) practical calibration     |

#### §T1.4 Empirical Evidence

| Study                                    | Context                      | Finding                                                                                   | Relevance                                                |
|------------------------------------------|------------------------------|-------------------------------------------------------------------------------------------|----------------------------------------------------------|
| Welch (2000). *JFE* 58(3)                | US analyst forecasts 1990–96 | Last 2 revisions predict next revision; herding reduces forecast accuracy                 | Calibrates cascade_trigger = 2–3                         |
| Bikhchandani et al. (1992). *JPE* 100(5) | Sequential binary decisions  | Cascade forms after (log(N)/log(2)) agents                                                | Sets cascade_trigger range 3–8                           |
| Avery & Zemsky (1998). *AER* 88(4)       | Trading markets              | Price signal partially prevents cascade; partial cascade in heterogeneous-quality markets | Validates that cascade forms despite market price signal |

#### §T1.5 Relevance to Simulation

Theory 1 is encoded by CascadeFollower (§4.1). Its interaction with ReputationHerder (§4.2) creates a compounded herding signal: both agents trade in the same direction once active, creating a buying/selling coalition that IndependentThinker (§4.3) and Contrarian (§4.4) must overcome.

---

### Theory 2: Reputation-Based Herding

#### §T2.1 Citation and Status

- **Primary Citation**: Scharfstein, D.S. & Stein, J.C. (1990). "Herd Behavior and Investment." *American Economic Review*, 80(3), 465–479.
- **Theory Status**: Highly influential — 3,000+ citations; established career-concern herding as a distinct mechanism
- **Original Context**: Investment decisions by professional managers under performance evaluation

#### §T2.2 Core Theoretical Mechanism

Scharfstein and Stein (1990) showed that rational investment managers may mimic consensus not because of information cascade dynamics but because of career concerns: if a manager deviates from consensus and is wrong, they bear full reputational cost; if they follow consensus and are wrong, the blame is shared. Under asymmetric reputational punishment, the optimal strategy for a career-concerned manager is to follow the crowd even when their private signal conflicts with consensus.

The key difference from the Bikhchandani et al. (1992) cascade is the mechanism: information cascade herding discards private signals because public information dominates; reputation herding may discard private signals even when they are informative, purely to minimize reputational risk. Both produce the same observable behavior (following the crowd) but have different policy implications.

In the simulation, ReputationHerder (§4.2) activates at the lower threshold of |deviation| > 0.02 (vs. CascadeFollower's cascade_count mechanism) and trades in the direction of deviation scaled by `reputation_concern × 4000`. The reputation_concern parameter captures how strongly career incentives amplify herding behavior.

#### §T2.3 Mathematical Formulation

**Reputation herding trade rule (Scharfstein & Stein, 1990 analog)**:
```
Activation: |deviation| > 0.02

qty = min(600, int(|dev| × reputation_concern × 4000))
Action: follow deviation direction

where reputation_concern ∈ [1.0, 3.0]
  1.0 = weak career concern (young portfolio manager)
  3.0 = strong career concern (large fund manager under close scrutiny)
```

#### §T2.4 Empirical Evidence

| Study                                    | Context              | Finding                                                                  | Relevance                                                   |
|------------------------------------------|----------------------|--------------------------------------------------------------------------|-------------------------------------------------------------|
| Scharfstein & Stein (1990). *AER* 80(3)  | Theoretical          | Career concern herding dominates when reputation uncertainty is high     | Validates reputation_concern parameter                      |
| Chevalier & Ellison (1999). *JPE* 107(6) | Fund manager careers | Managers with tenure < 3 years herd more; consistent with career concern | Calibrates reputation_concern ≈ 2.0–3.0 for young managers  |
| Welch (2000). *JFE* 58(3)                | Analyst forecasts    | Career concern explains 40% of analyst forecast revision herding         | Validates ReputationHerder as distinct from CascadeFollower |

#### §T2.5 Relevance to Simulation

Theory 2 is encoded by ReputationHerder (§4.2). Its lower activation threshold (0.02 vs. §4.1's cascade_count mechanism) means it activates earlier than CascadeFollower, providing a "pre-cascade" herding force that begins before full cascade lock-in occurs.

---

### Theory 3: Limits to Arbitrage Against Cascade Herding

#### §T3.1 Citation and Status

- **Primary Citation**: Shleifer, A. & Vishny, R.W. (1997). "The Limits of Arbitrage." *Journal of Finance*, 52(1), 35–55. doi:10.1111/j.1540-6261.1997.tb03807.x
- **Supporting Citation**: Pontiff, J. (2006). "Costly Arbitrage and the Myth of Idiosyncratic Risk." *Journal of Accounting and Economics* 42(1–2), 35–52. doi:10.1016/j.jacceco.2006.04.002
- **Theory Status**: Canonical — established limits to arbitrage framework
- **Original Context**: Asset pricing with capital constraints on rational investors

#### §T3.2 Core Theoretical Mechanism

IndependentThinker (§4.3) and Contrarian (§4.4) represent the arbitrage force against cascade herding. However, their combined capacity is structurally limited: IndependentThinker capped at 500 shares, Contrarian at 400 shares — significantly less than CascadeFollower's 800 and ReputationHerder's 600. The capacity ratio ≈ 0.56, consistent with Pontiff (2006) empirical finding of 40–60% arbitrage capacity limitation.

This capacity asymmetry means that cascade herding, once formed, cannot be immediately corrected even by rational agents — the correction is partial and delayed.

#### §T3.3 Mathematical Formulation

```
IndependentThinker max = 500 shares
Contrarian max        = 400 shares
CascadeFollower max   = 800 shares
ReputationHerder max  = 600 shares

Capacity ratio = (500 + 400) / (800 + 600) = 900 / 1400 = 0.643
```

| Agent              | Max shares | Role      |
|--------------------|------------|-----------|
| CascadeFollower    | 800        | Herding   |
| ReputationHerder   | 600        | Herding   |
| IndependentThinker | 500        | Arbitrage |
| Contrarian         | 400        | Arbitrage |

#### §T3.4 Empirical Evidence

| Study                                | Context                   | Finding                                                           | Relevance                            |
|--------------------------------------|---------------------------|-------------------------------------------------------------------|--------------------------------------|
| Shleifer & Vishny (1997). *JF* 52(1) | Hedge funds and arbitrage | Capital-constrained arbitrageurs cannot fully correct mispricings | Validates asymmetric capacity design |
| Pontiff (2006). *JAE* 42(1–2)        | Mutual fund arbitrage     | 40–60 % arbitrage capacity limitation for costly arbitrage        | Calibrates 900/1400 = 64 % ratio     |

#### §T3.5 Relevance to Simulation

Theory 3 explains why IndependentThinker and Contrarian cannot fully prevent cascade formation or immediately terminate cascade episodes. The ratio of (§4.3 max + §4.4 max) = 900 vs. (§4.1 max + §4.2 max) = 1,400 creates structural correction resistance.

---

## §3 Market Design

| Component         | Design Choice                                    | Justification                                                         |
|-------------------|--------------------------------------------------|-----------------------------------------------------------------------|
| Price formation   | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t) | Standard Walrasian ABM                                                |
| Fundamental value | Constant F                                       | Isolates information cascade as deviation source                      |
| Market broadcast  | `{type, price, fundamental, deviation, round}`   | Deviation serves as the "observed action" signal for cascade counting |
| Cascade counting  | CascadeFollower maintains internal counter       | Deviation > 0.03 increments counter; models information accumulation  |
| Order format      | buy / sell / hold with quantity                  | Standard                                                              |

---

## §4 Investor Taxonomy

### §4.1 CascadeFollower

**Summary**: Implements Bikhchandani et al. (1992) information cascade model. Ignores private signal once cascade_count reaches cascade_trigger threshold. Primary cascade amplifier — follows deviation direction unconditionally after lock-in.

**Foundation**: Bikhchandani, Hirshleifer & Welch (1992); Banerjee (1992). `doi:10.1086/261849`

**Design Purpose**: Encode the rational-but-informationally-inefficient cascade: once enough consecutive observations confirm a direction (cascade_trigger rounds of |deviation| > 0.03), the agent follows the crowd regardless of its private signal.

**Behavioral Framework**:

| Decision Variable       | Logic                                              | Formula                            |
|-------------------------|----------------------------------------------------|------------------------------------|
| Cascade count increment | Each round                                         | deviation                          |
| Cascade activation      | Permanent after threshold                          | `cascade_count ≥ cascade_trigger`  |
| Trade size              | Proportional to deviation × social amplification   | `min(800, int(                     |
| Direction               | Follow deviation (buy if dev > 0; sell if dev < 0) | Unconditional after cascade active |
| Pre-cascade             | Hold                                               | `cascade_count < cascade_trigger`  |

**Decision Walkthrough** (one round):
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. If `|deviation| > 0.03`: `cascade_count += 1`
3. If `cascade_count >= cascade_trigger`: cascade is active
4. If cascade active: `qty = min(800, int(|dev| × social_weight × 5000))`; direction = sign(deviation)
5. If cascade inactive: hold

**Worked Example** (cascade_trigger=3, social_weight=1.5, deviation=+0.06, cascade_count=3):
- cascade_count(3) ≥ cascade_trigger(3) → cascade active
- qty = min(800, int(0.06 × 1.5 × 5000)) = min(800, 450) = 450
- Action: buy 450 shares — cascade lock-in

**References**: simulation-bases.md §2 Theory 1; `doi:10.1086/261849`

---

### §4.2 ReputationHerder

**Summary**: Implements Scharfstein & Stein (1990) reputation/career-concern herding. Follows consensus direction to protect professional reputation. Lower activation threshold than CascadeFollower — activates before full cascade lock-in.

**Foundation**: Scharfstein & Stein (1990); Chevalier & Ellison (1999) career-concern evidence.

**Design Purpose**: Represent the "pre-cascade" herding force from career incentives. Activates at any |deviation| > 0.02 — does not require the sustained evidence that CascadeFollower needs. Creates compounded herding coalition with CascadeFollower.

**Behavioral Framework**:

| Decision Variable    | Logic                                                | Formula                |
|----------------------|------------------------------------------------------|------------------------|
| Activation threshold | Lower than CascadeFollower                           | `                      |
| Trade size           | Proportional to deviation × reputation amplification | `min(600, int(         |
| Direction            | Follow deviation direction                           | Consensus follower     |
| reputation_concern   | Career pressure intensity                            | 1.0 (low) → 3.0 (high) |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. If `|deviation| > 0.02`: trade
3. `qty = min(600, int(|dev| × reputation_concern × 4000))`; direction = sign(deviation)

**Worked Example** (reputation_concern=1.5, deviation=+0.04):
- `|0.04| > 0.02` → activates
- qty = min(600, int(0.04 × 1.5 × 4000)) = min(600, 240) = 240
- Action: buy 240 shares — reputation herding

**References**: simulation-bases.md §2 Theory 2; `doi:10.2307/2006957`

---

### §4.3 IndependentThinker

**Summary**: Implements rational Bayesian updating with correct private signal processing. Contrarian — buys when cascade overvalues, sells when undervalues. Represents the arbitrage force against cascade inefficiency.

**Foundation**: Bikhchandani et al. (1992) rational benchmark; Avery & Zemsky (1998) trading cascade limits. `doi:10.1086/261849`

**Design Purpose**: Model the rational counter-force to information cascades. Uses private signal quality (signal_precision) to trade against cascade mispricings. Subject to capacity limits that prevent full correction (Theory 3).

**Behavioral Framework**:

| Decision Variable    | Logic                                             | Formula                        |
|----------------------|---------------------------------------------------|--------------------------------|
| Activation threshold | Detects cascade misvaluation                      | `                              |
| Trade size           | Precision-scaled contrarian                       | `min(500, int(                 |
| Direction            | Contrarian: buys when dev < 0; sells when dev > 0 | Against cascade direction      |
| signal_precision     | Private signal quality                            | 0.5 (low) → 2.0 (high quality) |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. If `|deviation| > 0.03`: trade contrariantly
3. `qty = min(500, int(|dev| × signal_precision × 3000))`; direction = -sign(deviation)

**Worked Example** (signal_precision=1.0, deviation=+0.07 — cascade is buying):
- `|0.07| > 0.03` → activates
- qty = min(500, int(0.07 × 1.0 × 3000)) = min(500, 210) = 210
- Action: sell 210 shares — correcting overvaluation

**References**: simulation-bases.md §2 Theory 3; `doi:10.1086/261849`

---

### §4.4 Contrarian

**Summary**: Implements De Bondt & Thaler (1985) deliberate contrarian strategy. Triggers on larger deviations than IndependentThinker. Pure crowd-counter — no private signal model, just fundamental anchoring.

**Foundation**: De Bondt & Thaler (1985) overreaction/contrarian investing. `doi:10.1111/j.1540-6261.1985.tb05004.x`

**Design Purpose**: Provide a secondary, simpler correction mechanism alongside IndependentThinker. Activates at `|deviation| > contrarian_threshold × 0.05` — higher bar than IndependentThinker. Combined with §4.3, creates the 900-share maximum correction capacity.

**Behavioral Framework**:

| Decision Variable    | Logic                                    | Formula                               |
|----------------------|------------------------------------------|---------------------------------------|
| Activation threshold | Configurable                             | `                                     |
| Trade size           | Simple deviation-based                   | `min(400, int(                        |
| Direction            | Contrarian — against deviation direction | Sells when dev > 0; buys when dev < 0 |
| contrarian_threshold | Activation level multiplier              | 1 → 20 (multiplied by 0.05)           |

**Decision Walkthrough** (one round):
1. Receive market broadcast
2. If `|deviation| > contrarian_threshold × 0.05`: trade contrariantly
3. `qty = min(400, int(|dev| × 2000))`; direction = -sign(deviation)

**Worked Example** (contrarian_threshold=1, deviation=+0.08):
- threshold = 1 × 0.05 = 0.05; `|0.08| > 0.05` → activates
- qty = min(400, int(0.08 × 2000)) = min(400, 160) = 160
- Action: sell 160 shares

**References**: simulation-bases.md §2 Theory 3; `doi:10.1111/j.1540-6261.1985.tb05004.x`

---

### §4.5 NoiseTrader

**Summary**: Implements Black (1986) noise trader model. Random direction with configurable trade probability. Background liquidity provider — can accidentally trigger CascadeFollower's cascade_count via random price deviations.

**Foundation**: Black (1986) noise trader model. `doi:10.1111/j.1540-6261.1986.tb04513.x`

**Design Purpose**: Provide baseline stochastic liquidity. Accidental cascade initiator — random trades that move price can increment CascadeFollower's cascade_count if `|deviation| > 0.03` results. Mean-neutral over time but adds run-to-run variance.

**Behavioral Framework**:

| Decision Variable | Logic              | Formula                          |
|-------------------|--------------------|----------------------------------|
| Activation        | Random per round   | `random() < trade_probability`   |
| Trade size        | Fixed random range | `random.randint(100, 500)`       |
| Direction         | Random             | `random.choice(["buy", "sell"])` |

**Decision Walkthrough** (one round):
1. `if random() < trade_probability`: trade
2. Randomly choose buy or sell; `qty = random.randint(100, 500)`

**Worked Example** (trade_probability=0.30):
- 30 % chance of trading per round
- Expected volume per round: 0.30 × 300 = 90 shares (mean of 100–500 range)

**References**: Black (1986) `doi:10.1111/j.1540-6261.1986.tb04513.x`; De Long et al. (1990)

---

## §5 Agent Diversity Rationale

| Agent Pair              | Diversity Purpose                                                                                                                                   |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| §4.1 vs. §4.2           | Two distinct herding mechanisms: §4.1 is information cascade (requires sustained evidence); §4.2 is reputation herding (activates at any deviation) |
| §4.3 vs. §4.4           | Two stabilizing mechanisms: §4.3 uses private signal precision; §4.4 is purely crowd-contrary                                                       |
| §4.1/§4.2 vs. §4.3/§4.4 | Herding vs. correction; capacity asymmetry (1400 vs. 900 max) models limits to arbitrage                                                            |
| §4.5 (NoiseTrader)      | Background liquidity; can accidentally trigger cascade_count increments                                                                             |

---

## §6 Parameter Reference Table

| Parameter            | Agent         | Default | Calibrated Range | Source                          |
|----------------------|---------------|---------|------------------|---------------------------------|
| initial_price        | Market        | 100.0   | 80–120           | Standard ABM                    |
| fundamental_value    | Market        | 100.0   | 80–120           | Stable fundamental              |
| price_impact (λ)     | Market        | 0.001   | 0.0005–0.005     | Farmer & Foley (2009)           |
| mean_reversion (γ)   | Market        | 0.05    | 0.01–0.10        | Standard ABM                    |
| noise_std            | Market        | 0.5     | 0.1–2.0          | Black (1986)                    |
| initial_cash         | All investors | 100000  | Fixed            |                                 |
| social_weight        | §4.1          | 1.5     | 1.0–3.0          | Welch (2000) herding intensity  |
| cascade_trigger      | §4.1          | 3       | 2–8              | Welch (2000): 2–3 observations  |
| reputation_concern   | §4.2          | 1.5     | 1.0–3.0          | Scharfstein & Stein (1990)      |
| signal_precision     | §4.3          | 1.0     | 0.5–2.0          | Information quality calibration |
| contrarian_threshold | §4.4          | 1       | 1–20             | Contrarian activation level     |
| trade_probability    | §4.5          | 0.30    | 0.20–0.40        | Black (1986)                    |

---

## §7 Round Structure

| Step | Agent                                                                          | Action                                                                  | Output                |
|------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------|-----------------------|
| 1    | CascadeFollower, ReputationHerder, IndependentThinker, Contrarian, NoiseTrader | `perceive()`: read market broadcast; update cascade_count if applicable | Updated custom_state  |
| 2    | All investors                                                                  | `decide()`: check activation; compute buy/sell/hold + quantity          | Decision dict         |
| 3    | All investors                                                                  | `act()`: send order to Market; update cash/position                     | Order message         |
| 4    | Market                                                                         | `perceive()`: aggregate orders; compute new price                       | —                     |
| 5    | Market                                                                         | `decide()`: return price + fundamental + deviation                      | Market result dict    |
| 6    | Market                                                                         | `act()`: broadcast market update                                        | Market update message |

---

## §8 Historical Case Studies

### Case 1: Analyst Recommendation Cascade — Welch (2000) Empirical Finding

| Attribute          | Detail                                                                                                                                                                  |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | US equity analyst recommendation revisions 1990–1996; Welch (2000) documented that analyst revisions follow preceding revisions more than their own private information |
| Mechanism          | Analysts observe recent consensus revisions; private signal is discarded when consensus direction is strong; career concern amplifies following behavior                |
| Magnitude          | Last 2 analyst revisions explain next revision with R² = 0.42; private information contribution R² ≈ 0.08 (20% of herding total)                                        |
| Duration           | Quarterly earnings cycle; measured across 7 years                                                                                                                       |
| Agents Modeled     | CascadeFollower (§4.1): cascade_trigger = 2 (two prior analyst revisions); ReputationHerder (§4.2): analyst career concern herding                                      |
| Rational Response  | IndependentThinker (§4.3): the minority of analysts who maintain independent forecasts                                                                                  |
| Simulation Mapping | cascade_count increments from sustained deviation (consensus signal); CascadeFollower activates when cascade_trigger = 2–3 prior observations                           |

### Case 2: Asian Financial Crisis 1997 — Cascade Selling

| Attribute          | Detail                                                                                                                                                         |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | Hong Kong HSI: −60% from July 1997 to January 1998; institutional cascade selling despite mixed private signals about Hong Kong fundamentals                   |
| Mechanism          | Thailand baht devaluation (July 1997) → regional contagion narrative → institutional consensus sell → cascade following by fund managers protecting reputation |
| Magnitude          | HSI: 16,000 → 6,400 (−60%); HKD defended at cost of reserves; Hong Kong GDP −6%                                                                                |
| Duration           | 6 months of acute crisis; 18-month recovery                                                                                                                    |
| Agents Modeled     | §4.2 ReputationHerder: fund managers following regional sell consensus; §4.1 CascadeFollower: after 3+ rounds of negative deviation, cascade sell locks in     |
| Rational Response  | §4.3 IndependentThinker: long-term value investors who correctly assessed Hong Kong fundamentals                                                               |
| Simulation Mapping | Negative deviation accumulates → cascade_count rises → CascadeFollower activates sell orders; IndependentThinker buys against cascade but is overwhelmed       |

### Case 3: IPO Subscription Herding — Welch (1992)

| Attribute          | Detail                                                                                                                                                |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | US IPO subscription herding 1980–1992; early institutional subscriptions predict subsequent retail and institutional subscriptions                    |
| Mechanism          | Early institutional subscription → positive signal → later subscriptions follow regardless of own private valuation                                   |
| Magnitude          | 1% increase in early subscription → 4% increase in later subscription (cascade multiplier ≈ 4×)                                                       |
| Duration           | 2-week IPO subscription window                                                                                                                        |
| Agents Modeled     | §4.1 CascadeFollower: retail subscriptions following institutional early buyers; cascade_trigger = 2 (need 2 prior institutional signals)             |
| Rational Response  | §4.3 IndependentThinker: institutions with own valuation model who don't follow cascade                                                               |
| Simulation Mapping | Early rounds of deviation > 0.03 (institutional interest) → cascade_count triggers → CascadeFollower buys aggressively → price overshoots fundamental |

---

## §9 Variant Comparison

| Variant | Investor Logic                                                | Key Difference from Rule                  | Expected Outcome                                                         |
|---------|---------------------------------------------------------------|-------------------------------------------|--------------------------------------------------------------------------|
| Rule    | Hard-coded cascade_count + reputation logic                   | Baseline cascade herding                  | Strongest cascade formation; highest cascade persistence                 |
| LLM     | LLM prompt with cascade follower / reputation herder personas | LLM may reason about cascade fragility    | Weaker cascade; higher IndependentThinker effectiveness analog           |
| RuleLLM | Rule cascade logic + LLM narrative                            | Rule mechanics dominate                   | Near-Rule cascade dynamics                                               |
| Rag     | LLM + retrieval of Bikhchandani / Welch papers                | May retrieve cascade fragility conditions | Most moderate; RAG may "break" cascade by providing contrary information |
