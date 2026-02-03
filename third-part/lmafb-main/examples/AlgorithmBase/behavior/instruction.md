
---

# Investor Type II — Behavioral Investor (Psychology-Driven Decision Maker)

## 🎯 Concept Overview

**Investor Type II** represents a *psychological decision-maker*, whose actions are driven not by rational optimization, but by **subjective perception** of gains, losses, and risks.
This investor evaluates outcomes relative to an internal **reference point**, feels losses more intensely than equal gains, and distorts both probabilities and risk perception.
Type II models how emotional and cognitive biases shape portfolio choices, forming a self-contained behavioral paradigm parallel to the other investor types.

---

## 🧮 Core Decision Formulas

### 1️⃣ Reference-Dependent Value Function

[
V(x; r_0) =
\begin{cases}
(x - r_0)^{\alpha}, & x \ge r_0 \

* \lambda (r_0 - x)^{\beta}, & x < r_0
  \end{cases}
  ]

* **x**: realized outcome or wealth

* **r₀**: psychological reference point (target or break-even)

* **α, β ∈ (0, 1)**: curvature for gains and losses (diminishing sensitivity)

* **λ > 1**: loss-aversion coefficient — losses hurt more than equivalent gains

This asymmetric utility defines how the investor “feels” about each possible outcome.

---

### 2️⃣ Subjective Risk Perception

[
\tilde{\sigma}^2 = \kappa , \sigma^2
]

* **σ²**: objective market variance
* **κ**: perception factor

  * κ < 1 → underestimates risk (overconfident)
  * κ > 1 → overestimates risk (fearful)

The investor bases risk control on *felt* volatility (\tilde{\sigma}), not the true one.

---

### 3️⃣ Reference-Point Pressure

Let the gap between perceived target and current wealth be:

[
\Delta r = r_0 - W_t
]

Behavioral intensity function:

[
\phi_{\text{reference}}(\Delta r) =
\begin{cases}
1 + a|\Delta r|, & \Delta r > 0 \quad (\text{catch-up behavior})\
1 - b|\Delta r|, & \Delta r \le 0 \quad (\text{gain protection})
\end{cases}
]

* **a > 0**: “chasing” aggressiveness when behind target
* **b > 0**: de-risking strength when ahead of target

---

### 4️⃣ Risk Dampening Function

[
\phi_{\text{risk}}(\tilde{\sigma}) = \frac{1}{1 + c , \tilde{\sigma}}
]

* **c > 0** controls sensitivity to perceived volatility
* higher perceived risk → smaller exposure

---

### 5️⃣ Behavioral Allocation Rule

The investor’s **target risky allocation** combines both effects:

[
\omega^* = \phi_{\text{risk}}(\tilde{\sigma}) \times \phi_{\text{reference}}(\Delta r)
]

Then clamp within feasible bounds:

[
0 \le \omega^* \le \min(1 - \text{cash_reserve}, \text{max_position})
]

This is a closed-form behavioral policy — no mean-variance or Kelly optimization involved.

---

## ⚙️ Parameter Configuration

| Parameter                  | Symbol | Description                             |
|----------------------------|--------|-----------------------------------------|
| `reference_point`          | r₀     | Mental benchmark for gains/losses       |
| `reference_update_rate`    | ρ      | Speed at which r₀ adapts to wealth      |
| `alpha_gain`               | α      | Sensitivity to gains (concavity)        |
| `beta_loss`                | β      | Sensitivity to losses (convexity)       |
| `loss_aversion`            | λ      | Pain of losses relative to gains        |
| `risk_perception_kappa`    | κ      | Risk under/over-estimation factor       |
| `probability_weight_gamma` | γ      | Probability distortion parameter        |
| `catchup_intensity`        | a      | Aggressiveness when below reference     |
| `protect_intensity`        | b      | Conservativeness when above reference   |
| `c_risk_scale`             | c      | Risk-exposure sensitivity               |
| `min_cash_reserve`         | —      | Minimum fraction of wealth kept in cash |
| `max_position_size`        | —      | Maximum allowable exposure              |
| `transaction_cost_rate`    | —      | Cost per unit traded                    |
| `rebalancing_threshold`    | —      | Minimum deviation to trigger trading    |

---

## 🧱 Model Assumptions

* Decisions are **emotion-based**, not utility-maximizing.
* **Reference point** evolves adaptively:
  [
  r_{0,t} = (1 - ρ)r_{0,t-1} + ρ W_t
  ]
* **Risk perception** is subjective ((\tilde{\sigma})), not market-estimated.
* **Probability weighting** may be nonlinear (Prelec-style).
* No Bayesian learning or rational expectation updates.
* Cash and position limits are applied only as execution constraints.

---

## 🪜 Decision Flow

1. Observe market prices and current wealth (W_t).
2. Update reference point (r_{0,t}) according to ρ.
3. Compute perceived risk (\tilde{\sigma}) using κ.
4. Calculate reference pressure term (\phi_{\text{reference}}(\Delta r)).
5. Calculate risk dampening term (\phi_{\text{risk}}(\tilde{\sigma})).
6. Combine them to obtain target allocation (\omega^*).
7. Compare current and target allocations; rebalance if deviation exceeds threshold.
8. Submit buy/sell orders and record reasoning.

---

## 📘 Theoretical References

* Kahneman, D., & Tversky, A. (1979). *Prospect Theory: An Analysis of Decision under Risk.* Econometrica.
* Prelec, D. (1998). *The Probability Weighting Function.* Econometrica.
* Barberis, N., & Thaler, R. (2003). *A Survey of Behavioral Finance.* Handbook of the Economics of Finance.
* Benartzi, S., & Thaler, R. (1995). *Myopic Loss Aversion and the Equity Premium Puzzle.*

---

**In summary:**

> **Investor Type II** formalizes the *behavioral dimension* of investment decisions.
> It portrays investors whose portfolio choices emerge from perceived reference points, emotional loss aversion, and distorted risk perception — creating rich, realistic dynamics independent of rational or learning-based paradigms.

---
