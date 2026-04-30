# AsianFinancialCrisis — Simulation Design Basis

## 1. Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                            |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | **Financial Contagion Crisis (1997 Asian Financial Crisis)** — a self-reinforcing currency and capital-flow collapse in which short-term foreign capital ("hot money") reverses suddenly upon first signs of currency stress, triggering a cascade of contagion selling across regional markets, with IMF intervention providing a delayed and partial floor           |
| Category           | Currency crisis / hot money reversal / cross-border contagion / balance-of-payments crisis                                                                                                                                                                                                                                                                             |
| Core Mechanism     | Hot money reverses suddenly when currency deviation crosses a threshold → exchange rate depreciates → ContagionTrader spreads panic across regional proxies → deeper depreciation triggers more hot money reversal → feedback loop deepens. IMFRescuer and ValueContrarian provide a delayed floor once deviation is severe enough, eventually arresting the spiral.   |
| Real-World Origin  | July 2, 1997: Thai baht depegged; immediate 15–20% depreciation. Crisis spread to Philippines, Malaysia, Indonesia, South Korea within 3 months. Thai baht −55%; Indonesian rupiah −83%; South Korean won −54% vs. USD. IMF rescue packages totalling ~$117 billion.                                                                                                   |
| Research Relevance | The Asian crisis exemplifies how sudden reversals of short-term capital flows, combined with cross-border contagion, can produce self-fulfilling currency collapses that destroy fundamentally sound economies. It tests whether IMF-style interventions with conditionality can arrest feedback loops, and whether contagion is fundamentally driven or panic-driven. |


## 2. Theoretical Foundation

### Theory: Hot Money Reversal and the Sudden Stop Problem

- **Citation**: Radelet, S., & Sachs, J. (1998). The East Asian financial crisis: Diagnosis, remedies, prospects. *Brookings Papers on Economic Activity*, 1998(1), 1–90. https://doi.org/10.1353/eca.1998.0009
- **Core Insight**: Short-term foreign capital ("hot money") inflows are highly sensitive to risk sentiment. During expansion, hot money enters emerging markets rapidly in search of yield. At the first sign of trouble — currency deviation, political uncertainty, regional stress — it reverses rapidly regardless of fundamental economic conditions. This "sudden stop" of capital flows triggers a balance-of-payments crisis: reserves are drained, exchange rates collapse, and the economy enters a self-reinforcing spiral.
- **Mathematical Formulation**:
  ```
  HotMoney sells when: deviation(t) < −reversal_threshold   (downside reversal)
  HotMoney buys when:  deviation(t) > +reversal_threshold   (upside re-entry)
  Sell quantity: sell_ratio × current_position   (60% liquidation on reversal)
  Buy quantity:  buy_ratio × available_cash / price   (30% deployment on re-entry)
  ```
- **Empirical Evidence**: Radelet & Sachs (1998) document that Thailand's short-term foreign debt reached $45B by mid-1997 (compared to FX reserves of $38B), creating a structural vulnerability to sudden stops. In their post-mortem, the trigger was a relatively small deviation in Thai baht forward markets, not a fundamental deterioration — consistent with the `reversal_threshold = 0.02` (2% deviation) parameter.
- **Relevance to This Simulation**: `HotMoneyFunder` holds large pre-crisis positions financed by short-term instruments. When deviation crosses −2%, it rapidly liquidates 60% of its position, creating the first wave of selling pressure that triggers the contagion cascade.
- **Calibration Implication**: `reversal_threshold = 0.02` (Radelet & Sachs: small deviations trigger reversal in hot money flows); `sell_ratio = 0.60` (rapid liquidation consistent with sudden stop dynamics); `initial_position = 3,000` (large pre-crisis accumulated position).

---

### Theory: Financial Contagion and Cross-Border Transmission

- **Citation**: Kaminsky, G. L., & Reinhart, C. M. (1999). The twin crises: The causes of banking and balance-of-payments problems. *American Economic Review*, 89(3), 473–500. https://doi.org/10.1257/aer.89.3.473
- **Core Insight**: Financial stress spreads across borders through three channels: (1) trade linkages (currency depreciation in one country makes regional competitors less competitive, triggering selling), (2) common creditors (foreign banks with exposure to multiple regional markets rebalance all positions simultaneously when one deteriorates), and (3) pure investor panic (herding based on perceived regional correlation). The 1997 crisis exhibited all three channels simultaneously, producing extremely rapid cross-border transmission.
- **Mathematical Formulation**:
  ```
  contagion_signal(t) = contagion_weight × deviation(t) + cross_border_sensitivity × price_return(t)
  Sell when: contagion_signal(t) < −contagion_threshold   (−0.025)
  Sell quantity: sell_ratio × current_position   (50% liquidation)
  ```
- **Empirical Evidence**: Kaminsky & Reinhart (1999) find that banking and currency crises coincide ("twin crises") in 18 of 26 studied episodes; the correlation between regional financial markets rises from near-zero to 0.6–0.8 during contagion episodes. Their analysis of leading indicators shows that deviation from fundamental (30% weight) and momentum (20% weight) are the strongest predictors of contagion spread — consistent with the `contagion_weight = 0.60` and `cross_border_sensitivity = 0.40` parameterisation.
- **Relevance to This Simulation**: `ContagionTrader` implements the dual-channel contagion signal: deviation measures fundamental stress; price_return measures momentum-driven panic. The −0.025 threshold for the composite signal captures the empirical finding that contagion requires both channels to be negative simultaneously.
- **Calibration Implication**: `contagion_weight = 0.60`, `cross_border_sensitivity = 0.40` (Kaminsky & Reinhart: fundamental channel slightly stronger than momentum in twin-crisis episodes); `contagion_threshold = −0.025` (composite signal threshold calibrated to produce contagion onset within 12–25 rounds).

---

### Theory: International Lender of Last Resort and IMF Conditionality

- **Citation**: Corsetti, G., Pesenti, P., & Roubini, N. (1999). Paper tigers? A model of the Asian crisis. *European Economic Review*, 43(7), 1211–1236. https://doi.org/10.1016/S0014-2921(98)00111-0
- **Core Insight**: IMF emergency lending provides a stabilising floor but with two critical features: (1) conditionality requirements (fiscal austerity, interest rate increases) that may worsen near-term economic conditions, and (2) deployment only at severe dislocation levels, meaning the crisis deepens substantially before intervention. The IMF's "lender of last resort" role creates a moral hazard: creditors anticipate eventual rescue, which may have contributed to the initial excessive hot-money lending.
- **Mathematical Formulation**:
  ```
  IMF intervenes when: deviation(t) < −rescue_threshold   (−0.05)
  Rescue quantity: buy_ratio × available_cash / price   (25% of $5M cash reserves per rescue round)
  ```
- **Empirical Evidence**: Corsetti et al. (1999) document that IMF programs were announced for Thailand ($17.2B, August 1997), Indonesia ($43B, November 1997), and South Korea ($58B, December 1997) — all after currencies had already depreciated by 15–30%, consistent with `rescue_threshold = −0.05` (5% before intervention). The IMF's total commitment was ~$117B but actual disbursement was slower, modelled by the `buy_ratio = 0.25` gradual deployment.
- **Relevance to This Simulation**: `IMFRescuer` deploys $5M in cash reserves (disproportionately large, modelling sovereign-scale rescue capacity) but only after `deviation < −0.05`. Its large cash reserve and gradual deployment (25% per rescue round) models the IMF's "deep pockets but slow trigger" pattern.
- **Calibration Implication**: `rescue_threshold = −0.05` (Corsetti et al.: intervention after ~5–15% depreciation); `buy_ratio = 0.25` (gradual programme disbursement); `initial_cash = $5,000,000` (scaled to represent sovereign rescue capacity relative to other agents).

---

### Theory: Contrarian Value Investing in Crisis Markets

- **Citation**: Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch 2007–2008. *Journal of Economic Perspectives*, 23(1), 77–100. https://doi.org/10.1257/jep.23.1.77
- **Core Insight**: In severe crisis periods, assets are priced far below fundamental values due to fire-sale dynamics and forced deleveraging. Fundamental investors who have sufficient liquidity and long time horizons can profit by buying deeply discounted assets. However, value buyers require a significantly larger discount than IMF-style rescuers because they bear private-sector execution risk with no sovereign backing.
- **Mathematical Formulation**:
  ```
  ValueContrarian buys when:  deviation(t) < −oversold_threshold   (−0.08)
  ValueContrarian sells when: deviation(t) > +overbought_threshold  (+0.10)
  Buy/sell quantity: buy_ratio × cash / price   or   sell_ratio × position   (both 0.20)
  ```
- **Empirical Evidence**: During the 1997 crisis, institutional investors with fundamental mandates (e.g., value-oriented hedge funds, long-horizon sovereign wealth funds) began accumulating Thai, Korean, and Indonesian equities when they had fallen 40–60% below pre-crisis valuations — consistent with `oversold_threshold = −0.08` as a first entry point and subsequent accumulation.
- **Relevance to This Simulation**: `ValueContrarian` represents the private-sector value buyer who enters later and deeper than IMFRescuer, providing a second layer of price floor support. The `−0.08` threshold (8% below fundamental) reflects the deeper discount private buyers require vs. IMF's 5%.
- **Calibration Implication**: `oversold_threshold = −0.08` (requires deeper discount than IMF); `overbought_threshold = +0.10` (sells when recovered significantly above fundamental, capturing crisis-recovery premium); `buy_ratio = sell_ratio = 0.20` (conservative capital deployment).


## 3. Market Design Principles

### 3.1 Price Formation Model

**Formula**:
```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

**Variable Definitions**:

| Symbol | Name                          | Definition                                                                                          | Role in Crisis                                                                                 |
|--------|-------------------------------|-----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| P(t)   | Current exchange rate / price | Market price; initialised at 100.0                                                                  | Falls rapidly when hot money exits and contagion spreads                                       |
| D(t)   | Net demand                    | Σ(buy) − Σ(sell) across all agents                                                                  | Strongly negative during crisis phase; determines depreciation speed                           |
| F      | Fundamental value             | Pre-crisis equilibrium = 100.0 (constant)                                                           | Reference for all deviation calculations; represents economic fundamentals pre-crisis          |
| λ      | Price impact                  | 0.04 (HIGH — emerging markets have thin liquidity; even moderate selling creates large price moves) | Critical: higher λ reflects thin EM FX liquidity; consistent with observed baht/won volatility |
| γ      | Mean reversion                | 0.02 (LOW — capital flow crises persist; fundamental gravity is weak during crisis)                 | Slow pull toward F; models the empirical pattern that currency crises are persistent           |
| ε(t)   | Noise                         | ~ N(0, σ²), σ = 0.02                                                                                | Modest noise; FX markets are less noisy than equity markets                                    |

**Economic Design Rationale**:
- High λ (0.04) reflects that emerging market FX markets have substantially lower liquidity than developed equity markets. A given net demand shock produces larger price moves.
- Low γ (0.02) models the empirical persistence of currency crises: Radelet & Sachs (1998) document that once capital flight begins, fundamental gravity is overwhelmed for extended periods.
- The `initial_price = fundamental = 100.0` starts the simulation at equilibrium; the HotMoneyFunder's large position creates the vulnerability that produces the crisis when the first negative shock occurs.

**Sensitivity**:
- Increasing λ from 0.04 to 0.08 approximately doubles crisis depth and speed.
- Increasing γ from 0.02 to 0.10 significantly reduces crisis persistence; IMF rescue becomes less necessary.
- Recommended sensitivity grid: λ ∈ {0.02, 0.04, 0.06, 0.08} × γ ∈ {0.01, 0.02, 0.05}.

### 3.2 Additional Market Mechanisms

**Price Floor**: `max(price, 0.01)` — prevents numerical collapse.

**Position Constraints**: Sell quantity limited to current position (no naked shorts beyond initial position); buy quantity limited by available cash.

**Asymmetric Scale**: IMFRescuer's `initial_cash = $5,000,000` is disproportionately large compared to HotMoneyFunder ($800,000), modelling the asymmetry between sovereign rescue capacity and private capital — but the 5% threshold delay means the crisis deepens before the rescue arrives.

### 3.3 Information Broadcast Design

Each round, the Market broadcasts to all investors:

| Field         | Type  | Rationale                                                                                              |
|---------------|-------|--------------------------------------------------------------------------------------------------------|
| `price`       | float | Current market price; primary signal for all agents                                                    |
| `prev_price`  | float | Required for ContagionTrader's momentum component (`price_return = (price − prev_price) / prev_price`) |
| `fundamental` | float | Fundamental value F; enables deviation calculation                                                     |
| `deviation`   | float | `(price − F) / F`; precomputed; primary trigger variable for HotMoneyFunder and IMFRescuer             |
| `volume`      | float | Total trading volume; indicates crisis activity level                                                  |
| `round`       | int   | Round number; used for phase tracking                                                                  |


## 4. Investor Taxonomy

### Investor: HotMoneyFunder

#### 4.1.1  Summary

HotMoneyFunder represents the archetypal short-term foreign capital investor who provides liquidity and return-chasing flows during benign periods but reverses rapidly and aggressively at the first sign of currency stress. This agent models the foreign institutional investors — primarily hedge funds and money market funds — who provided the capital inflows that fuelled Asian growth in 1994–1997, then executed sudden, large-scale reversals in 1997. HotMoneyFunder is the primary crisis initiator: its 60% position liquidation at the −2% threshold creates the initial selling wave that triggers the contagion cascade.

#### 4.1.2  Theoretical and Empirical Foundation

**Sudden Stop Theory**:
- Theory / Study: Hot Money and Sudden Stop Dynamics
- Citation: Radelet, S., & Sachs, J. (1998). The East Asian financial crisis. *Brookings Papers on Economic Activity*, 1998(1), 1–90. https://doi.org/10.1353/eca.1998.0009
- Core Insight: Short-term capital inflows are highly sensitive to risk sentiment and reverse suddenly. A threshold-crossing event (currency deviation, reserve depletion, political shock) triggers rapid, large-scale capital exit. The exit is procyclical and self-reinforcing: exit → depreciation → more exit.
- Mathematical Formulation: `Sell when deviation(t) < −0.02; Q_sell = 0.60 × position`. The `0.60` sell ratio reflects the empirical observation that hot money typically exits 50–80% of its position rapidly on reversal signals.
- Empirical Evidence: Radelet & Sachs (1998): Thailand's short-term foreign debt ($45B) vs. FX reserves ($38B) created structural sudden-stop vulnerability. Crisis was triggered by relatively small forward market deviations (~2–3%), not fundamental deterioration. This directly calibrates `reversal_threshold = 0.02`.
- Relevance to This Investor: HotMoneyFunder's rapid 60% liquidation at −2% deviation directly models the Radelet-Sachs sudden stop mechanism.

**Capital Flow Reversal and Balance-of-Payments Crisis**:
- Theory / Study: Exchange Rate Crises and Capital Account Openness
- Citation: Calvo, G. A. (1998). Capital flows and capital-market crises: The simple economics of sudden stops. *Journal of Applied Economics*, 1(1), 35–54.
- Core Insight: When international capital markets are integrated, a sudden stop creates an immediate balance-of-payments crisis even if fiscal fundamentals are sound. The required current account adjustment is abrupt and contractionary. The size of the position that needs to be liquidated determines the depth of the crisis.
- Mathematical Formulation: Crisis depth is proportional to: `total_liquidation_volume × price_impact = (sell_ratio × initial_position × λ)`. With `sell_ratio = 0.60`, `initial_position = 3,000`, `λ = 0.04`: each HotMoneyFunder exit contributes −$7.20 to price per instance.
- Empirical Evidence: Calvo (1998) estimates that sudden stops in Latin American and Asian emerging markets produced GDP contractions of 5–10% within 12 months; the magnitude is directly proportional to the pre-crisis current account deficit and short-term debt overhang.
- Relevance to This Investor: Two HotMoneyFunder instances with 3,000 shares each represent the concentrated foreign capital that fuelled pre-crisis inflows; their simultaneous reversal creates the crisis-initiating demand shock.

#### 4.1.3  Design Purpose and Activation Scenarios

Purpose: HotMoneyFunder initiates the crisis by providing the first large-scale selling wave. Without HotMoneyFunder, the system would not spontaneously generate a crisis — it requires the sudden reversal of concentrated short-term capital.

Activation Scenarios:
- Pre-crisis (deviation > 0): Buys when deviation > 0.02; accumulates position on positive deviation.
- Crisis trigger (deviation < −0.02): Sells 60% of position immediately; the primary crisis-initiating event.
- Recovery phase (deviation rising back toward 0): Cautiously re-enters when deviation > +0.02.

Market Contribution: **Strongly Destabilising** — initiates the crisis and provides the largest single selling shock. At λ = 0.04, two instances with 3,000-share positions contribute up to −$144 per round at full liquidation.

Interaction with other agents: HotMoneyFunder's selling drives deviation below ContagionTrader's threshold (−0.025), triggering contagion; the combined selling by both pushes deviation toward IMFRescuer's threshold (−0.05).

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**

| Signal      | Type       | Rationale                                                                                  |
|-------------|------------|--------------------------------------------------------------------------------------------|
| `deviation` | Continuous | Primary trigger; `deviation < −0.02` triggers sell; hot money reversal is deviation-driven |
| `position`  | State      | Required for sell quantity calculation (60% of position)                                   |
| `cash`      | State      | Required for buy quantity calculation (30% deployment)                                     |

Does NOT use: `price_return`, `contagion_signal`, `volume`. HotMoneyFunder's decision is purely threshold-based on deviation — consistent with the Radelet-Sachs "simple threshold" model of hot money reversal.

**4.1.4.2  Core Behavioral Mechanism**

1. Each round: checks `deviation` against thresholds.
2. If `deviation < −reversal_threshold (−0.02)`: SELL crisis mode — liquidate 60% of current position.
3. If `deviation > +reversal_threshold (+0.02)`: BUY re-entry — deploy 30% of cash at current price.
4. Otherwise: HOLD.

**4.1.4.3  Mathematical Model**

- Decision variable: Buy/sell quantity Q*(t)
- Trigger function:
  ```
  Sell:  deviation(t) < −0.02
  Buy:   deviation(t) > +0.02
  Hold:  |deviation(t)| ≤ 0.02
  ```
- Sizing function:
  ```
  Q*(t) = −sell_ratio × position(t)            [sell: −0.60 × position]
  Q*(t) = +buy_ratio × cash / price(t)          [buy: +0.30 × cash / price]
  ```
- State variables: `position`, `cash` — updated each round
- Parameter definitions:

| Symbol                    | Meaning                                       | Config Path                  | Source                                                          |
|---------------------------|-----------------------------------------------|------------------------------|-----------------------------------------------------------------|
| reversal_threshold = 0.02 | Deviation before hot money reverses           | players.yml → HotMoneyFunder | Radelet & Sachs (1998): 2–3% threshold observed in Asian crisis |
| sell_ratio = 0.60         | Fraction of position liquidated on reversal   | players.yml → HotMoneyFunder | Calvo (1998): 50–80% exit typical in sudden stop episodes       |
| buy_ratio = 0.30          | Fraction of cash deployed on re-entry         | players.yml → HotMoneyFunder | Conservative re-entry after crisis resolution                   |
| initial_position = 3,000  | Pre-crisis accumulated long position (shares) | players.yml → HotMoneyFunder | Calibrated to produce 30–60% crisis depth                       |
| initial_cash = $800,000   | Starting cash reserves                        | players.yml → HotMoneyFunder | Scaled to position size                                         |

**4.1.4.4  Behavioral Properties**

- Time horizon: Very short-term — threshold-triggered; no memory or accumulation logic
- Risk tolerance: Asymmetric — extremely aggressive on reversal (60% liquidation); cautious on re-entry (30% deployment)
- Information asymmetry: None — uses only public deviation signal; no private information
- Psychological profile: Pure panic selling on downside; consistent with the "sudden stop" psychology documented by Calvo (1998); no fundamental analysis — the 2% deviation threshold is the sole decision criterion

#### 4.1.5  Decision Process Walkthrough

```
Given:  deviation = −0.025,  position = 3,000,  sell_ratio = 0.60

Step 1: Check deviation threshold
        −0.025 < −0.02 → sell condition satisfied

Step 2: Compute sell quantity
        Q* = −0.60 × 3,000 = −1,800 shares

Step 3: Send order
        action = sell, quantity = 1,800, bid_price = current_price

Result: Removes 1,800 shares from demand; contributes λ × (−1,800) = 0.04 × (−1,800) = −$72 to price
        One HotMoneyFunder instance reduces price by $72 in a single round.
        Two instances contribute −$144 simultaneously → rapid crisis deepening.
```

#### 4.1.6  Worked Numerical Example

```
Market state:  price = 97.0 (deviation = −0.03),  position = 2,400 (reduced from earlier sells)
               cash = $400,000

Check: deviation = −0.03 < −0.02 → SELL
Q*    = −0.60 × 2,400 = −1,440 shares

Decision: action = sell, quantity = 1,440, bid_price = 97.0
Cash received: 1,440 × 97.0 = $139,680; new cash = $539,680; new position = 960

Rationale: With deviation already at −3%, HotMoneyFunder continues liquidating.
Its 60% sell ratio means it exits a large fraction of remaining position each round,
creating persistent selling pressure throughout the crisis phase — the self-reinforcing
capital outflow documented by Radelet & Sachs (1998).
```

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                             | Notes                                                                            |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| 1 | Radelet, S., & Sachs, J. (1998). The East Asian financial crisis. *Brookings Papers*, 1998(1), 1–90. https://doi.org/10.1353/eca.1998.0009                           | Core framework; calibrates reversal_threshold and crisis narrative               |
| 2 | Calvo, G. A. (1998). Capital flows and capital-market crises. *Journal of Applied Economics*, 1(1), 35–54.                                                           | Grounds sell_ratio = 0.60 and initial_position in sudden stop theory             |
| 3 | Eichengreen, B., Rose, A. K., & Wyplosz, C. (1996). Contagious currency crises. *Scandinavian Journal of Economics*, 98(4), 463–484. https://doi.org/10.2307/3440879 | Documents symmetric threshold behaviour of hot money in multiple crisis episodes |

---

### Investor: ContagionTrader

#### 4.2.1  Summary

ContagionTrader represents the cross-border investor who spreads financial stress from one market to related regional markets, modelling the contagion transmission channel documented in Kaminsky & Reinhart (1999). Unlike HotMoneyFunder who responds purely to absolute deviation, ContagionTrader uses a composite signal that combines fundamental stress (deviation) with momentum (price_return). This dual-signal design implements the Kaminsky-Reinhart finding that contagion spreads through both fundamental linkages and investor panic/portfolio rebalancing simultaneously.

#### 4.2.2  Theoretical and Empirical Foundation

**Twin Crises and Contagion Transmission**:
- Theory / Study: Financial Contagion via Common Creditors and Portfolio Rebalancing
- Citation: Kaminsky, G. L., & Reinhart, C. M. (1999). The twin crises. *American Economic Review*, 89(3), 473–500. https://doi.org/10.1257/aer.89.3.473
- Core Insight: Financial contagion spreads through three channels: trade linkages, common creditor rebalancing, and pure panic. The "twin crises" pattern (currency + banking) arises because the same shock triggers simultaneous currency defense and banking sector stress. Contagion requires both a stress signal AND a momentum trigger — neither alone is sufficient for cross-border spread.
- Mathematical Formulation: `contagion_signal = 0.60 × deviation + 0.40 × price_return`. The 60/40 split assigns primary weight to fundamental stress (deviation) and secondary weight to momentum (portfolio rebalancing signal).
- Empirical Evidence: Kaminsky & Reinhart (1999) study 76 currency crises and 26 banking crises (1970–1995): find that banking crises preceded 18 of 26 currency crises ("twin crises"); leading indicators show deviation from fundamentals (R² ≈ 0.25) and momentum (R² ≈ 0.20) are both significant predictors of cross-border transmission — calibrating the 60/40 weight split.
- Relevance to This Investor: The composite signal `0.60 × deviation + 0.40 × price_return` implements the Kaminsky-Reinhart dual-channel transmission mechanism.

**Portfolio Rebalancing and Common Creditor Channel**:
- Theory / Study: Common Creditor Channel of Contagion
- Citation: Caramazza, F., Ricci, L., & Salgado, R. (2004). International financial contagion in currency crises. *Journal of International Money and Finance*, 23(1), 51–70. https://doi.org/10.1016/j.jimonfin.2003.10.001
- Core Insight: When a large international bank or fund has significant exposure to multiple regional markets, a loss in one market triggers risk-limit constraints that force rebalancing (selling) across all correlated positions — even in markets with no direct fundamental linkage. This common creditor channel amplifies contagion beyond what fundamental analysis would predict.
- Mathematical Formulation: `cross_border_component = cross_border_sensitivity × price_return`. The `price_return` proxy captures the momentum signal that portfolio rebalancers observe when they see regional prices falling.
- Empirical Evidence: Caramazza et al. (2004) find that common creditor exposure explains 30–40% of cross-border contagion variance after controlling for bilateral trade, consistent with `cross_border_sensitivity = 0.40` (40% of contagion signal from momentum/portfolio channel).
- Relevance to This Investor: The 40% weight on `price_return` in ContagionTrader's signal implements the Caramazza et al. common creditor rebalancing channel.

#### 4.2.3  Design Purpose and Activation Scenarios

Purpose: ContagionTrader spreads and deepens the crisis by responding to both fundamental deterioration and price momentum, amplifying the initial HotMoneyFunder selling wave into a broader contagion cascade.

Activation Scenarios:
- Contagion signal threshold crossed (signal < −0.025): Sells 50% of position; amplifies crisis depth.
- Double signal (both deviation and price_return negative): Strongest selling signal; produces deepest cascade.
- Signal reversal (signal positive): Stops selling; waits for recovery signal before re-entering.

Market Contribution: **Strongly Destabilising** — amplifies the crisis initiated by HotMoneyFunder. With 4,000-share positions, two instances contribute −$160 per round at full activation.

Interaction with other agents: Activates approximately 2–5 rounds after HotMoneyFunder (its threshold requires both deviation AND return to be negative, so it requires multiple rounds of sustained selling). Pushes deviation toward IMFRescuer and ValueContrarian thresholds.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**

| Signal                           | Type       | Rationale                                                           |
|----------------------------------|------------|---------------------------------------------------------------------|
| `deviation`                      | Continuous | Fundamental stress component (60% weight); primary crisis indicator |
| `price_return` (from prev_price) | Continuous | Momentum component (40% weight); portfolio rebalancing trigger      |

Distinct from HotMoneyFunder: uses a composite weighted signal rather than a pure threshold, implementing the dual-channel contagion mechanism.

**4.2.4.2  Core Behavioral Mechanism**

1. Computes `price_return = (price − prev_price) / prev_price`.
2. Computes composite signal: `contagion_signal = 0.60 × deviation + 0.40 × price_return`.
3. If `contagion_signal < −0.025`: SELL 50% of position.
4. No buy logic — ContagionTrader only exits during crisis; recovery is passive (holds remaining position).

**4.2.4.3  Mathematical Model**

- Decision variable: Sell quantity Q*(t)
- Trigger function:
  ```
  price_return(t)      = (P(t) − P(t−1)) / P(t−1)
  contagion_signal(t)  = 0.60 × deviation(t) + 0.40 × price_return(t)
  Sell: contagion_signal(t) < −0.025
  ```
- Sizing function:
  ```
  Q*(t) = −sell_ratio × position(t)   [−0.50 × position on sell; no buy logic]
  ```
- State variables: `position`, `cash`, `prev_price` (from Market broadcast)
- Parameter definitions:

| Symbol                          | Meaning                                    | Config Path                   | Source                                                                  |
|---------------------------------|--------------------------------------------|-------------------------------|-------------------------------------------------------------------------|
| contagion_weight = 0.60         | Weight on deviation in composite signal    | players.yml → ContagionTrader | Kaminsky & Reinhart (1999): fundamental channel R² ≈ 0.25 (primary)     |
| cross_border_sensitivity = 0.40 | Weight on price_return in composite signal | players.yml → ContagionTrader | Caramazza et al. (2004): portfolio channel 30–40% of contagion variance |
| contagion_threshold = −0.025    | Composite signal threshold for sell        | players.yml → ContagionTrader | Calibrated to activate 2–5 rounds after HotMoneyFunder                  |
| sell_ratio = 0.50               | Fraction of position sold on signal        | players.yml → ContagionTrader | Moderate (vs. HotMoneyFunder 0.60): contagion spreads more gradually    |

**4.2.4.4  Behavioral Properties**

- Time horizon: Short-term — responds to contemporaneous dual-signal; no historical accumulation
- Risk tolerance: High during crisis — 50% position liquidation on signal; no loss limit
- Information asymmetry: None — uses only public deviation and price return
- Psychological profile: Panic-driven portfolio rebalancing (Caramazza et al., 2004); pure technical/signal trader during crisis with no fundamental buy-side capacity

#### 4.2.5  Decision Process Walkthrough

```
Given:  deviation = −0.03,  price_return = −0.025,  position = 4,000,  sell_ratio = 0.50

Step 1: Compute contagion signal
        signal = 0.60 × (−0.03) + 0.40 × (−0.025) = −0.018 + (−0.010) = −0.028

Step 2: Compare to threshold
        −0.028 < −0.025 → sell condition satisfied

Step 3: Compute sell quantity
        Q* = −0.50 × 4,000 = −2,000 shares

Step 4: Send order
        action = sell, quantity = 2,000, bid_price = current_price

Result: Adds −2,000 to net demand; contributes λ × (−2,000) = −$80 to price decline.
        Two instances contribute −$160; combined with HotMoneyFunder selling,
        crisis deepens rapidly.
```

#### 4.2.6  Worked Numerical Example

```
Market state (round 15):  price = 88.0,  prev_price = 93.0,  fundamental = 100.0
  deviation   = (88.0 − 100.0) / 100.0 = −0.12
  price_return = (88.0 − 93.0) / 93.0 = −0.054
  signal      = 0.60 × (−0.12) + 0.40 × (−0.054) = −0.072 + (−0.022) = −0.094

Check: −0.094 << −0.025 → deep contagion signal
Q*   = −0.50 × 3,200 (current position) = −1,600 shares

Decision: action = sell, quantity = 1,600, bid_price = 88.0
Rationale: At −12% deviation and −5.4% price return, both channels are strongly negative,
producing a composite signal 3.7× the threshold. ContagionTrader is in deep panic mode,
executing the Kaminsky-Reinhart common creditor rebalancing cascade.
```

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                | Notes                                                                      |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| 1 | Kaminsky, G. L., & Reinhart, C. M. (1999). The twin crises. *AER*, 89(3), 473–500. https://doi.org/10.1257/aer.89.3.473                                 | Core framework; calibrates dual-signal weights and contagion threshold     |
| 2 | Caramazza, F., Ricci, L., & Salgado, R. (2004). International financial contagion. *JIMF*, 23(1), 51–70. https://doi.org/10.1016/j.jimonfin.2003.10.001 | Calibrates cross_border_sensitivity = 0.40 (portfolio rebalancing channel) |
| 3 | Eichengreen, B., Rose, A. K., & Wyplosz, C. (1996). Contagious currency crises. *SJE*, 98(4), 463–484. https://doi.org/10.2307/3440879                  | Empirical documentation of cross-border contagion speed and magnitude      |

---

### Investor: IMFRescuer

#### 4.3.1  Summary

IMFRescuer represents the international public-sector rescue mechanism — the IMF and associated bilateral lenders — that provides emergency liquidity during severe currency crises. This agent models the two defining features of IMF crisis intervention: (1) very large financial firepower ($5M initial cash, representing the scale of sovereign rescue capacity relative to private investors), and (2) a high activation threshold (−5% deviation), reflecting the IMF's documented reluctance to intervene until the crisis is well-established. The result is a "deep pockets but slow trigger" rescue pattern: prices fall significantly before intervention, but once it begins, the scale of intervention provides meaningful price support.

#### 4.3.2  Theoretical and Empirical Foundation

**IMF Conditionality and Crisis Resolution**:
- Theory / Study: IMF Conditionality and Lender of Last Resort
- Citation: Corsetti, G., Pesenti, P., & Roubini, N. (1999). Paper tigers? A model of the Asian crisis. *European Economic Review*, 43(7), 1211–1236. https://doi.org/10.1016/S0014-2921(98)00111-0
- Core Insight: IMF programs provide emergency liquidity but with conditionality (austerity, interest rate hikes) that may worsen short-term conditions. The program deployment threshold (requiring severe dislocation) creates a moral hazard and a crisis-deepening lag.
- Mathematical Formulation: `Activate when deviation(t) < −0.05; buy with 25% of cash reserves per rescue round`. The gradual deployment (25% per round) models the IMF's tranche-based disbursement structure.
- Empirical Evidence: Corsetti et al. (1999): Thailand IMF program ($17.2B) announced August 14, 1997, after baht had already depreciated ~15%; Indonesia program ($43B) November 1997 after 35% depreciation; Korea program ($58B) December 1997 after 25% won depreciation. Average activation after 15–35% depreciation → calibrates `rescue_threshold = −0.05` as a conservative lower bound.
- Relevance to This Investor: `initial_cash = $5,000,000` and `buy_ratio = 0.25` implement the "deep pockets, gradual deployment" pattern; `rescue_threshold = −0.05` models the delayed activation documented in Corsetti et al.

**Lender of Last Resort Theory**:
- Theory / Study: International Lender of Last Resort
- Citation: Fischer, S. (1999). On the need for an international lender of last resort. *Journal of Economic Perspectives*, 13(4), 85–104. https://doi.org/10.1257/jep.13.4.85
- Core Insight: An international lender of last resort provides conditional liquidity to prevent self-fulfilling panics from destroying fundamentally sound economies. The lender's credibility depends on both its financial capacity and its willingness to deploy capital decisively. Fischer argues the IMF was the closest available institution but operated with insufficient speed and scale in 1997.
- Empirical Evidence: Fischer (1999) documents that the IMF's $17B Thailand package was insufficient to restore confidence; South Korea's $58B package (with additional bilateral commitments) was more effective because of its scale. The key lesson: lender of last resort effectiveness scales with firepower relative to the threatened market.
- Relevance to This Investor: `initial_cash = $5,000,000` (calibrated to be 6.25× larger than HotMoneyFunder's $800K, modelling sovereign vs. private capital asymmetry) provides a meaningful floor even against coordinated selling.

#### 4.3.3  Design Purpose and Activation Scenarios

Purpose: IMFRescuer provides the first floor in the crisis, activating at −5% deviation with large capital reserves. Its presence ensures the simulation has a realistic rescue mechanism that limits but does not prevent crisis depth.

Activation Scenarios:
- Pre-threshold (deviation > −0.05): Holds completely; IMF does not intervene before severe dislocation.
- Threshold crossed (deviation < −0.05): Deploys 25% of remaining cash reserves per round; provides sustained buying support.
- Recovery: Holds remaining position as passive stabiliser.

Market Contribution: **Strongly Stabilising** — once activated, $5M in reserves at 25%/round provides meaningful buying support even against coordinated selling. However, the 5% threshold delay means crisis reaches −10% to −30% before IMF activates in many simulation runs.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**: `deviation` only — threshold-based, consistent with IMF's public program announcement criteria.

**4.3.4.2  Core Behavioral Mechanism**: Hold until `deviation < −0.05`; then buy `buy_ratio × cash / price` each round until cash is exhausted or deviation recovers.

**4.3.4.3  Mathematical Model**

- Trigger: `deviation(t) < −rescue_threshold (−0.05)`
- Sizing: `Q*(t) = buy_ratio × cash / price(t) = 0.25 × cash / price`
- Parameter: `rescue_threshold = −0.05` (Corsetti et al., 1999); `buy_ratio = 0.25` (tranche-based disbursement)

**4.3.4.4  Behavioral Properties**

- Time horizon: Patient — activates only after sustained crisis; deploys gradually
- Risk tolerance: Low — risk is sovereign, not profit-motivated; willing to buy into falling market
- Psychological profile: Rule-based intervention; no fundamental valuation; pure crisis-floor provider

#### 4.3.5  Decision Process Walkthrough

```
Given:  deviation = −0.07,  cash = $5,000,000,  price = 93.0,  buy_ratio = 0.25

Step 1: Check threshold
        −0.07 < −0.05 → rescue activated

Step 2: Compute buy quantity
        Q* = 0.25 × 5,000,000 / 93.0 = 13,440 shares

Step 3: Send order
        action = buy, quantity = 13,440, bid_price = 93.0

Result: Large buying wave; contributes λ × 13,440 = 0.04 × 13,440 = +$537.60 upward price pressure;
        significantly counteracts selling by HotMoneyFunder and ContagionTrader.
```

#### 4.3.6  Worked Numerical Example

```
Market state (round 20, first IMF activation):  price = 92.0,  deviation = −0.08,  cash = $5,000,000

Q* = 0.25 × 5,000,000 / 92.0 = 13,587 shares
Decision: buy 13,587 shares

Round 21: cash now $3,750,000; price 93.5 (IMF buying partially arrested decline)
Q* = 0.25 × 3,750,000 / 93.5 = 10,027 shares → continued support

Rationale: Gradual 25%/round deployment provides sustained multi-round buying pressure,
modelling the IMF's tranche disbursement structure documented by Corsetti et al. (1999).
```

#### 4.3.7  Academic References

| # | Citation                                                                                                                              | Notes                                                             |
|---|---------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| 1 | Corsetti, G., Pesenti, P., & Roubini, N. (1999). Paper tigers? *EER*, 43(7), 1211–1236. https://doi.org/10.1016/S0014-2921(98)00111-0 | Core reference; calibrates rescue_threshold = −0.05 and buy_ratio |
| 2 | Fischer, S. (1999). On the need for an international lender of last resort. *JEP*, 13(4), 85–104. https://doi.org/10.1257/jep.13.4.85 | Grounds IMF firepower asymmetry and speed-of-deployment design    |
| 3 | Radelet, S., & Sachs, J. (1998). The East Asian financial crisis. *Brookings Papers*, 1998(1), 1–90.                                  | Documents actual IMF program timelines and sizes for calibration  |

---

### Investor: ValueContrarian

#### 4.4.1  Summary

ValueContrarian represents the private-sector fundamental investor who seeks to exploit deep crisis-driven discounts to fundamental value. This agent models long-horizon institutional investors — hedge funds, sovereign wealth funds, private equity — who are willing to buy assets during crisis but require a larger discount than the IMF (which has sovereign backing and can tolerate lower expected returns). ValueContrarian provides the second layer of price floor support after IMFRescuer and eventually profits from crisis recovery.

#### 4.4.2  Theoretical and Empirical Foundation

**Crisis Investing and Fundamental Value Recovery**:
- Theory / Study: Contrarian Investing and Mean Reversion
- Citation: Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch 2007–2008. *Journal of Economic Perspectives*, 23(1), 77–100. https://doi.org/10.1257/jep.23.1.77
- Core Insight: In severe liquidity crises, assets trade far below fundamental values due to fire-sale dynamics. Investors with long time horizons and adequate liquidity can earn substantial returns by absorbing forced sales, but they require deep discounts to compensate for execution risk and uncertainty about when prices will recover.
- Mathematical Formulation: `Buy when deviation < −0.08; sell when deviation > +0.10`. The asymmetric thresholds (−8% entry, +10% exit) reflect the recovery premium that contrarian investors require.
- Empirical Evidence: Post-crisis studies of 1997 Asian markets show that investors who entered Thai, Korean, and Indonesian equity markets at 40–60% discounts in Q1 1998 earned returns of 100–200% over the following 3 years (Brunnermeier, 2009; consistent with fundamentals-driven recovery).
- Relevance to This Investor: `oversold_threshold = −0.08` (8% below F) represents the minimum discount ValueContrarian requires before entering; `overbought_threshold = +0.10` (+10% above F) is the exit point capturing the post-crisis recovery premium.

**Limits to Arbitrage and Position Building**:
- Theory / Study: Patient Capital and Crisis Arbitrage
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Fundamental-value investors face capital constraints that prevent them from deploying unlimited capital into deep discounts. ValueContrarian's `buy_ratio = 0.20` reflects this constraint — it deploys cautiously to avoid overcommitting before the crisis floor is established.
- Empirical Evidence: During 1997 Asian crisis, even well-capitalised funds deployed capital gradually across multiple rounds (weeks) rather than in a single decisive entry — consistent with the 20% per-round deployment.
- Relevance to This Investor: Conservative capital deployment (20% per round) ensures ValueContrarian does not exhaust its buying power in the early crisis phase before prices bottom.

#### 4.4.3  Design Purpose and Activation Scenarios

Purpose: ValueContrarian provides the second floor (deeper than IMFRescuer) and eventual recovery-phase selling that normalises prices after the crisis.

Activation Scenarios:
- Deep crisis (deviation < −0.08): Buys; provides incremental buying support deeper in the crisis.
- Recovery overshoot (deviation > +0.10): Sells; prevents post-crisis overvaluation.
- Between thresholds (−0.08 to +0.10): Holds.

Market Contribution: **Stabilising** — deepens the floor below IMFRescuer; provides the second rescue layer. Also provides recovery-phase selling that prevents over-correction.

#### 4.4.4  Behavioral Framework

- Trigger: `deviation < −0.08` (buy) or `deviation > +0.10` (sell)
- Sizing: `0.20 × cash / price` (buy) or `0.20 × position` (sell)
- Parameters: `oversold_threshold = −0.08` (Brunnermeier, 2009: private buyers enter at 8–15% below fundamental); `overbought_threshold = +0.10`

#### 4.4.5  Decision Process Walkthrough

```
Given:  deviation = −0.10,  cash = $1,000,000,  price = 90.0

Check: −0.10 < −0.08 → buy condition
Q* = 0.20 × 1,000,000 / 90.0 = 2,222 shares

Decision: buy 2,222 shares; adds +$88.9 upward price pressure (at λ = 0.04)
```

#### 4.4.6  Worked Numerical Example

```
Recovery phase: deviation = +0.11,  price = 111.0,  position = 3,200 shares
Check: +0.11 > +0.10 → sell condition
Q* = 0.20 × 3,200 = 640 shares

Decision: sell 640 shares; prevents post-crisis overvaluation above fundamental + 10%
```

#### 4.4.7  Academic References

| # | Citation                                                                                                                                              | Notes                                                      |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| 1 | Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch. *JEP*, 23(1), 77–100. https://doi.org/10.1257/jep.23.1.77                    | Grounds deep discount requirement for private value buyers |
| 2 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Grounds 20% per-round capital deployment constraint        |

---

### Investor: NoiseTrader

#### 4.5.1  Summary

NoiseTrader represents uninformed retail FX speculators and random order flow participants who trade on impulse, rumour, and random sentiment rather than any systematic signal. In the AsianFinancialCrisis simulation, NoiseTrader serves a specific design purpose: it prevents crisis-driven mispricings from following overly smooth paths, adds realistic background volatility consistent with emerging-market FX noise, and provides liquidity that allows other agents to execute their strategies. NoiseTrader's random direction means its aggregate effect on mean pricing is near zero, but its activity rate (`trade_probability = 0.30`) is higher than in developed-market scenarios, reflecting the elevated noise in crisis-era EM currency markets.

#### 4.5.2  Theoretical and Empirical Foundation

**Noise Trading and Market Microstructure**:
- Theory / Study: Noise Trading and Its Market Effects
- Citation: Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x
- Core Insight: Noise traders (those who trade on noise rather than information) create liquidity and price volatility. Without noise traders, markets would be too thin — only information-based trades would occur. Noise traders make markets more active but also more volatile; their presence is necessary for market function.
- Mathematical Formulation: `Q_noise ~ Uniform(min_order, max_order)` with random direction (buy/sell each with probability 0.5); `P(trade) = 0.30` per round.
- Empirical Evidence: Black (1986) estimates that uninformed trading accounts for 30–60% of total order flow in liquid markets. In crisis-era EM FX markets, the proportion of noise-driven flow increases as institutional participants withdraw and retail speculators increase activity.
- Relevance to This Investor: `trade_probability = 0.30` (higher than the 0.05 in developed-market simulations) reflects the elevated noise documented in 1997 Asian FX markets; 3 instances produce realistic background volatility.

#### 4.5.3  Design Purpose and Activation Scenarios

Purpose: Add background noise that prevents the simulation from being too mechanistic; provide liquidity; model the realistic presence of uninformed order flow in crisis-era EM FX markets.

Activation Scenarios:
- With probability 0.30 per round: trades (70% chance of holding each round).
- Random direction (buy or sell with equal probability).
- Random quantity drawn from Uniform(min_order, max_order).

Market Contribution: **Neutral** — expected net demand = 0 over many rounds; but provides random demand shocks that add realistic noise to crisis price dynamics.

#### 4.5.4  Behavioral Framework

- Trigger: `random() < trade_probability = 0.30`
- Direction: `random() > 0.5 → buy; else sell`
- Sizing: `Q ~ Uniform(min_order, max_order)`
- Constrained by cash (buy) or position (sell)

#### 4.5.5  Decision Process Walkthrough

```
Round 15 (mid-crisis):
  Step 1: random() = 0.22 < 0.30 → active this round
  Step 2: random() = 0.38 < 0.5 → sell
  Step 3: quantity = Uniform(min_order, max_order) → drawn quantity (constrained by position)
  Action: sell at current price

Round 16:
  Step 1: random() = 0.85 > 0.30 → inactive; hold
```

#### 4.5.6  Worked Numerical Example

```
Market state:  price = 88.0 (deviation = −0.12),  NoiseTrader position = 200 shares

Trade fires (probability 0.30 rolls 0.22):
  direction: random = 0.65 > 0.5 → buy
  quantity:  drawn from Uniform range → 150 shares (constrained by cash)

Decision: action = buy, quantity = 150
Market impact: adds +150 to net demand D(t); contributes λ × 150 = +$6.0 to price
Note: A random buy during a deep crisis slightly slows the cascade — realistic noise that
prevents the crisis path from being a smooth monotonic decline.
```

#### 4.5.7  Academic References

| # | Citation                                                                                                                                     | Notes                                                                           |
|---|----------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| 1 | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                            | Foundational rationale for noise trading; establishes trade_probability concept |
| 2 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices. *JFE*, 14(1), 71–100. https://doi.org/10.1016/0304-405X(85)90044-3 | Establishes informed vs. uninformed order flow fractions                        |


## 5. Agent Diversity Verification

```
Diversity Check:
  Different time horizons:
    - Very short: HotMoneyFunder (threshold-triggered, immediate 60% exit)
    - Short: ContagionTrader (composite signal, contemporaneous), NoiseTrader (random each round)
    - Patient: IMFRescuer (waits for −5%; gradual deployment), ValueContrarian (waits for −8%)

  Different information sets:
    - Deviation only: HotMoneyFunder, IMFRescuer, ValueContrarian
    - Dual-signal: ContagionTrader (deviation + price_return)
    - None: NoiseTrader

  Conflicting incentives:
    - HotMoneyFunder + ContagionTrader sell → IMFRescuer + ValueContrarian buy (at different thresholds)
    - NoiseTrader random direction; net-neutral over time

  Mix of stabilising/destabilising:
    - Strongly Destabilising (×2 types): HotMoneyFunder (2 instances), ContagionTrader (2 instances)
    - Strongly Stabilising: IMFRescuer (1 instance, deep pockets)
    - Stabilising: ValueContrarian (2 instances, private sector)
    - Neutral: NoiseTrader (3 instances)
    Total: 10 agents
```


## 6. Parameter Table

| Parameter                  | Value      | Source Citation                                                | Description                                   | Sensitivity                                                 |
|----------------------------|------------|----------------------------------------------------------------|-----------------------------------------------|-------------------------------------------------------------|
| `initial_price`            | 100.0      | Design baseline                                                | Starting exchange rate                        | Low                                                         |
| `fundamental_value`        | 100.0      | Pre-crisis equilibrium                                         | True fundamental (constant)                   | Low                                                         |
| `price_impact` (λ)         | 0.04       | Calibrated for EM thin liquidity; higher than developed market | Price sensitivity to net demand               | **High** — doubling to 0.08 doubles crisis depth            |
| `mean_reversion` (γ)       | 0.02       | Radelet & Sachs (1998): persistent currency crises             | Speed of recovery toward F                    | **High** — increasing to 0.10 eliminates crisis persistence |
| `noise_std` (σ)            | 0.02       | FX market noise calibration                                    | Gaussian noise std                            | Low                                                         |
| `reversal_threshold`       | 0.02       | Radelet & Sachs (1998): 2–3% threshold for hot money reversal  | HotMoneyFunder sell trigger                   | **High** — reduces crisis onset round significantly         |
| `sell_ratio` (HMF)         | 0.60       | Calvo (1998): 50–80% exit in sudden stop                       | Fraction of HotMoneyFunder position sold      | High                                                        |
| `contagion_weight`         | 0.60       | Kaminsky & Reinhart (1999): fundamental channel primary        | Deviation weight in ContagionTrader signal    | Medium                                                      |
| `cross_border_sensitivity` | 0.40       | Caramazza et al. (2004): 30–40% portfolio rebalancing          | Price_return weight in ContagionTrader signal | Medium                                                      |
| `contagion_threshold`      | −0.025     | Calibrated to activate 2–5 rounds after HotMoneyFunder         | ContagionTrader composite signal threshold    | High                                                        |
| `rescue_threshold`         | −0.05      | Corsetti et al. (1999): IMF activates after 5–35% depreciation | IMFRescuer activation threshold               | **High**                                                    |
| `buy_ratio` (IMF)          | 0.25       | Tranche-based disbursement structure                           | IMFRescuer per-round capital deployment       | Medium                                                      |
| `initial_cash` (IMF)       | $5,000,000 | Sovereign scale rescue capacity                                | IMFRescuer capital reserves                   | **High** — reducing to $500K eliminates floor effectiveness |
| `oversold_threshold`       | −0.08      | Brunnermeier (2009): private buyers require deeper discount    | ValueContrarian buy trigger                   | Medium                                                      |
| `overbought_threshold`     | +0.10      | Recovery premium exit                                          | ValueContrarian sell trigger                  | Low                                                         |
| `trade_probability` (NT)   | 0.30       | Black (1986): higher noise in crisis markets                   | NoiseTrader activity rate                     | Low                                                         |


## 7. Communication and Round Structure

```
Round N:
  1. Market broadcasts state to all investors
     Payload: {price, prev_price, fundamental, deviation, volume, round}

  2. Each investor:
     a. perceive() — extract market_data from inbound
     b. decide()   — apply threshold/signal/random strategy
     c. act()      — update portfolio; send order to Market

  3. Market:
     a. perceive() — collect all investor orders
     b. decide()   — apply P(t+1) = P(t) + λ×D(t) + γ×[F−P(t)] + ε(t)
     c. act()      — broadcast new market state

  4. Logging via HistoryBuffer
```

Topology: Star — Market broadcasts to all 10 investors; investors respond to Market.

Initialization: All agents start at equilibrium (price = fundamental = 100.0). HotMoneyFunder's large initial position creates crisis vulnerability that activates on the first negative shock (via noise term ε or deliberate initial shock).


## 8. Historical Case Studies

### Event: 1997 Asian Financial Crisis

- **Date**: July 2, 1997 – January 1998 (peak crisis period)
- **Market**: Thai baht, Indonesian rupiah, South Korean won, Malaysian ringgit; regional equity indices
- **Trigger**: Thai baht depegged from USD after months of defending the peg; immediate 15–20% depreciation triggered capital flight
- **Timeline**:
  - Pre-crisis (1994–1997): Massive capital inflows to Asia driven by fixed exchange rates and yield differentials; short-term debt accumulation
  - July 2, 1997: Baht depegged; 15–20% immediate depreciation
  - July–August 1997: Contagion to Philippines, Malaysia, Indonesia
  - October 1997: HK dollar attacks; S&P downgrade of Korean sovereign debt
  - November 1997: IMF Thailand program ($17.2B); Indonesia program ($43B)
  - December 1997: Korea IMF program ($58B)
  - January 1998: Indonesian rupiah −83% peak-to-trough; street protests; political instability
- **Quantitative Data**:
  - Thai baht: −55% vs. USD (July 1997 – January 1998)
  - Indonesian rupiah: −83% peak-to-trough
  - South Korean won: −54% vs. USD
  - Malaysian ringgit: −48% vs. USD (before capital controls imposed)
  - Regional equity indices: −40% to −60% in USD terms
  - IMF total commitments: ~$117 billion across three main programs
- **Agent Mapping**:
  - US and European hedge funds + Japanese money market funds that provided short-term financing → `HotMoneyFunder` (2 instances; large positions; threshold at 2% deviation)
  - Global banks rebalancing Asian portfolio exposure → `ContagionTrader` (2 instances; composite signal combining regional stress and momentum)
  - IMF + bilateral creditors (US, Japan, others) → `IMFRescuer` (1 instance; large cash; 5% activation threshold)
  - Long-horizon value investors who accumulated positions in Q1 1998 → `ValueContrarian`
  - Retail FX speculators and random order flow → `NoiseTrader`
- **Lessons for Simulation**:
  - Maximum price deviation target: [30%, 60%] matching documented currency depreciations
  - Crisis onset: within rounds 10–20 (consistent with 1–3 week contagion spread)
  - IMF rescue round: after deviation reaches −5% to −10% (consistent with historical activation delays)
  - Recovery: partial; prices recover 50–70% of loss within simulation window (consistent with 18-24 month recovery in most affected countries)
  - Source: Corsetti, G., Pesenti, P., & Roubini, N. (1999); Kaminsky, G. L., & Reinhart, C. M. (1999)


## 9. Variant Comparison Preview

| Aspect                 | Rule                                     | LLM                                         | RuleLLM                          | Rag                                                   |
|------------------------|------------------------------------------|---------------------------------------------|----------------------------------|-------------------------------------------------------|
| Decision Logic         | Deterministic formulas; exact thresholds | Persona-guided reasoning; crisis psychology | Formulas in == DECISION RULES == | Rules + historical crisis knowledge retrieval         |
| Determinism            | Fully deterministic                      | Stochastic                                  | Semi-deterministic               | Stochastic                                            |
| Crisis Emergence Speed | Fast (formula triggers exactly)          | Variable (persona hesitation possible)      | Near-Rule                        | Near-RuleLLM + historical knowledge nuance            |
| Contagion Fidelity     | Exact signal formula                     | Qualitative contagion narrative             | Exact signal in prompt           | Signal + Kaminsky-Reinhart knowledge                  |
| IMF Timing             | Exact −5% threshold                      | Patient but possibly delayed                | Exact −5% in prompt              | Threshold + conditionality nuance from retrieved docs |
| Behavioral Realism     | Low                                      | High                                        | Medium-High                      | Highest                                               |
| Reproducibility        | High                                     | Low                                         | Medium                           | Medium                                                |
