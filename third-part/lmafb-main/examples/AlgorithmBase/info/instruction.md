
---

# Investor Type III — Information–Learning Oriented Investor

## 🎯 Concept Overview

**Investor Type III** models a *learning agent* whose decision-making evolves over time as new information arrives.
Unlike static rational or psychological investors, this agent continuously updates its beliefs about expected returns, risk, and market structure using Bayesian or reinforcement-style rules.

This type captures investors who adapt to data — quant funds, algorithmic traders, or information arbitrageurs — where **belief dynamics drive portfolio adjustment**.

---

## 🧮 Core Decision Formulas

### 1️⃣ Bayesian Belief Update for Expected Return

The investor maintains a posterior belief about the expected return (\mu_t):

[
\mu_t = (1 - \alpha) \mu_{t-1} + \alpha , r_t
]

* **rₜ**: observed realized return
* **α**: learning rate (0–1), controls how quickly new evidence overwrites old belief
* This is equivalent to an *exponential moving average* belief update.

Optionally, you can write this as a **Bayesian precision-weighted update**:

[
\mu_t = \frac{\tau_{t-1} \mu_{t-1} + \tau_r r_t}{\tau_{t-1} + \tau_r}
]

* **τₜ₋₁, τᵣ** are precision (1/variance) terms controlling trust in prior vs new data.
* This reflects rational learning under uncertainty about returns.

---

### 2️⃣ Volatility Learning (Risk Uncertainty Update)

The investor also refines its belief about volatility:

[
\sigma_t^2 = (1 - \alpha_\sigma)\sigma_{t-1}^2 + \alpha_\sigma (r_t - \mu_t)^2
]

* **αₛ**: volatility learning rate
* This corresponds to an *adaptive variance estimator*, analogous to online-GARCH or recursive variance tracking.

As information accumulates, perceived volatility stabilizes — or reacts quickly to shocks if αₛ is large.

---

### 3️⃣ Information Confidence Decay

Belief confidence decays over time if no new data arrives:

[
\psi_t = \lambda \psi_{t-1}
]

* **ψₜ**: confidence in current belief
* **λ ∈ (0,1)**: memory decay factor
* Intuitively, the longer the market stays uncertain, the more the investor “forgets” old convictions.

This term controls exploration–exploitation balance:
high ψ → stable conviction, low ψ → exploratory trading.

---

### 4️⃣ Dynamic Allocation Decision (Belief-Weighted Rational Rule)

Once beliefs are updated, allocation is computed **using beliefs**, not true parameters:

[
\omega_t^* = \frac{\mu_t - r_f}{A , \sigma_t^2}
]

This formula structurally mirrors the CARA/mean-variance rule,
but here the inputs (\mu_t) and (\sigma_t^2) are *endogenously updated beliefs*.

Hence, Type III = *belief-driven rationality*:
the agent is always “rational within its beliefs,” but the beliefs themselves evolve dynamically.

---

### 5️⃣ Adaptive Learning and Exploration (Optional Extension)

To capture information-seeking behavior, the investor can explore proportionally to uncertainty:

[
\omega_t^{adj} = \omega_t^* + \epsilon_t \cdot (1 - \psi_t)
]

where:

* **εₜ ∼ N(0, σ_{explore})** introduces small exploratory noise;
* **(1 - ψₜ)** scales exploration intensity inversely with confidence.

This mimics active learning:
when unsure, the agent samples more widely; when confident, it stabilizes.

---

## ⚙️ Parameter Configuration

| Parameter                   | Symbol | Description                        |
|-----------------------------|--------|------------------------------------|
| `learning_rate_mean`        | α      | Learning speed for expected return |
| `learning_rate_vol`         | αₛ     | Learning speed for volatility      |
| `memory_decay`              | λ      | Confidence decay factor            |
| `initial_belief_mean`       | μ₀     | Prior expected return              |
| `initial_belief_vol`        | σ₀     | Prior volatility                   |
| `belief_confidence`         | ψ₀     | Initial confidence                 |
| `exploration_noise`         | σₑ     | Magnitude of exploration noise     |
| `risk_aversion_coefficient` | A      | Risk aversion                      |
| `risk_free_rate`            | rₓ     | Risk-free rate                     |
| `min_cash_reserve`          | —      | Minimum cash                       |
| `max_position_size`         | —      | Max risky exposure                 |
| `transaction_cost_rate`     | —      | Cost per trade                     |
| `rebalancing_threshold`     | —      | Drift threshold for trading        |

---

## 🧱 Model Assumptions

* Investors have *imperfect but updatable* beliefs about returns and risk.
* Learning follows exponential or Bayesian update rules.
* Confidence decays with time; beliefs are not static.
* Allocation remains internally rational under current beliefs.
* No emotional or psychological distortions (contrast with Type II).
* No direct forecasting model — learning is purely adaptive.

---

## 🪜 Decision Flow

1. Observe market return (r_t = \frac{P_t - P_{t-1}}{P_{t-1}}).
2. Update expected return (\mu_t) via learning rule.
3. Update volatility belief (\sigma_t^2).
4. Decay confidence ψₜ if no strong signal appears.
5. Compute target allocation (\omega_t^*) using belief-based parameters.
6. Optionally add exploration noise.
7. Compare to current allocation and rebalance if deviation exceeds threshold.

---

## 📘 Theoretical References

* Barberis, N. (2000). *Investing for the Long Run When Returns Are Predictable.* J. Finance.
* Timmermann, A. (1993). *How Learning in Financial Markets Generates Excess Volatility and Predictability.* QJE.
* Vayanos, D., & Woolley, P. (2013). *An Institutional Theory of Momentum and Reversal.* RFS.
* Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction.* MIT Press.

---

**In summary:**

> **Investor Type III** formalizes the *information-driven adaptive investor*.
> It models a trader whose portfolio evolves as a function of updated beliefs — a dynamic equilibrium between learning, uncertainty, and rational action.
> This type captures adaptive intelligence and information assimilation in markets where agents continuously learn from the data stream.

---

