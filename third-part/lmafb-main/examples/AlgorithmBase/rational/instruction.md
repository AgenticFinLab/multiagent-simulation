
---

# Investor Type I — Risk–Return Oriented Rational Investor

## 🎯 Concept Overview

**Investor Type I** models a *classical rational investor* whose decisions follow the foundations of modern portfolio theory.
This type assumes perfect information and no behavioral or learning biases.
The investor maximizes expected utility under risk using **closed-form analytical formulas** from financial economics.

---

## 🧮 Core Decision Formulas

### 1️⃣ CARA Utility (Constant Absolute Risk Aversion)

[
\omega^* = \frac{\mu - r}{A \cdot \sigma^2}
]

* **μ**: expected return of the risky asset
* **r**: risk-free rate
* **σ²**: variance of returns
* **A**: risk-aversion coefficient

This is the analytical solution from maximizing
[
\max_\omega E[U(W)] = E[R] - \frac{A}{2}Var[R]
]
for a single risky asset.
It represents the optimal weight in the risky asset balancing return and risk.

---

### 2️⃣ Mean–Variance Optimization (Markowitz Framework)

[
\max_\omega ; E[R] - \frac{A}{2} Var[R]
]

This is equivalent to the CARA formulation in the single-asset case.
The investor directly optimizes the trade-off between expected return and risk using a given **risk-aversion parameter A**.

---

### 3️⃣ Kelly Criterion (Growth-Optimal Allocation)

[
f^* = \frac{\mu - r}{\sigma^2}
]

* Maximizes the *long-term geometric growth rate* of wealth.
* Represents the most aggressive risk-taking benchmark.
* In practice, the allocation is scaled by a safety factor `kelly_fraction ∈ (0, 1]` to avoid over-leverage.

---

## ⚙️ Parameter Configuration

| Parameter                   | Symbol | Description                                                                   |
|-----------------------------|--------|-------------------------------------------------------------------------------|
| `risk_aversion_coefficient` | A      | Risk-aversion intensity                                                       |
| `risk_free_rate`            | r      | Baseline risk-free rate                                                       |
| `expected_return_estimate`  | μ      | Investor’s belief about expected return                                       |
| `volatility_estimate`       | σ      | Belief about return volatility                                                |
| `decision_method`           | —      | Choice among `"CARA"`, `"mean_variance_optimization"`, or `"kelly_criterion"` |
| `kelly_fraction`            | —      | Scaling factor for Kelly aggressiveness                                       |

---

## 🧱 Model Assumptions

* **Static beliefs**: μ and σ are exogenous and fixed; the investor does *not* learn or update them.
* **No behavioral biases**: loss aversion, reference dependence, or overconfidence are excluded.
* **No adaptive learning**: Bayesian or Kalman updates are disabled in this type.
* **Rational optimization**: decisions are purely formula-based and analytically tractable.
* **Execution realism**: transaction costs, cash reserves, and position limits are treated as external constraints, not part of the utility formula.

---

## 🪜 Decision Flow

1. Receive market prices and portfolio state.
2. Compute optimal target allocation ω* using one of the three formulas.
3. Compare current vs. target allocation.
4. Rebalance portfolio if deviation exceeds the rebalancing threshold.
5. Send resulting buy/sell orders to the unified market (`AlgorithmicMarket`).

---

## 📘 Theoretical References

* Markowitz, H. (1952). *Portfolio Selection.* Journal of Finance.
* Merton, R. (1971). *Optimum Consumption and Portfolio Rules in a Continuous-Time Model.* JET.
* Kelly, J. (1956). *A New Interpretation of Information Rate.* Bell System Technical Journal.

---

**In summary:**

> Investor Type I formalizes the *risk–return optimization layer* of our framework.
> It represents the baseline rational benchmark against which behavioral, learning, and market-driven investors (Types II–IV) will later be compared.

---
