---
name: agent-design-finance
purpose: Financial / market-trading domain instantiation of the Universal Simulation Agent Design Handbook (`agent-design-skill.md`). Supplies row label substitutions, value palettes, real-world counterpart enumerations, and example specifications for participant agents whose decisions take the form of orders against a tradable asset.
status: canonical
audience: Authors and reviewers of participant-agent specifications for financial multi-agent simulations (any investor, trader, dealer, market maker, arbitrageur, liquidity provider, fundamentalist, contrarian, regulator, or other market participant).
extends: agent-design-skill.md
rfc2119: This document uses MUST / MUST NOT / SHOULD / MAY in the RFC-2119 sense.
---

# Financial Domain Instantiation — Agent Design Handbook Companion

This file is the **financial / market-trading instantiation** of the canonical
agent design handbook at `masim/format/agent-design-skill.md`. It supplies
row label substitutions, value palettes, and example specifications that
financial-domain authors apply on top of the canonical schema. Sections,
headers, validation rules, and copy-paste skeleton structure are governed
by the core handbook unchanged.

A financial-domain specification MUST conform to the core handbook AND
apply the substitutions in this companion. The companion adds no new
sections; where a label or palette is given here, it replaces the canonical
generic form in the handbook.

---

## 1. Scope

Apply this companion when the agent's decisions take the form of orders
against a tradable asset, or quotes / inventory adjustments inside a market
microstructure. Examples: investors, traders, dealers, market makers,
arbitrageurs, liquidity providers, fundamentalists, momentum chasers,
contrarians, herders, value buyers, regulators, central-bank intervention
agents.

Do NOT use this companion for opinion-dynamics, information-diffusion, or
non-trading social-simulation agents — those domains will have their own
companion files when authored.

---

## 2. Title Conventions

The H1 sentence-cased role phrase MUST describe the agent's market role
(e.g. "Anchoring-bias retail trader", "Liquidity-providing market maker",
"Trend-following momentum trader"). Class identifiers (`AnchoringBiasInvestor`)
are reserved for the embedded form inside `simulation-bases.md §4`.

---

## 3. Summary Row Instantiations

| Canonical row (handbook §3.2) | Financial-domain row label | Value palette                                                                                                           |
|-------------------------------|----------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Theory Family                 | Theory Family              | Behavioral Finance / Microstructure / Information Cascade / Limits to Arbitrage / Market Microstructure / Quant / Macro |
| System Role                   | **Market Role**            | **Destabilising** / **Stabilising** / **Context-dependent** — <one-line>                                                |

All other rows (Archetype, Time Horizon, Risk Tolerance, Information
Asymmetry, Determinism) keep their canonical labels and value palettes
unchanged.

---

## 4. Real-World Counterpart Enumeration

§3.3 of the handbook requires that the real-world participant be named.
Common financial-domain counterparts:

- Retail trader / individual investor
- Institutional investor (mutual fund, pension fund, sovereign wealth fund)
- Market maker / dealer
- Arbitrageur / statistical arbitrageur
- High-frequency trader (latency arbitrageur, market-making HFT)
- Liquidity provider / liquidity demander
- Trend follower / momentum trader
- Contrarian / mean-reversion trader
- Fundamentalist / value investor
- Noise trader / herder
- Hedger / portfolio insurer
- Regulator / central-bank intervention agent

The author MUST pick one or more from this list, or supply a more specific
counterpart with a citation that locates it in the financial literature.

---

## 5. Stylized Facts Catalogue

§3.3 of the handbook requires the agent to name the stylized facts it helps
produce. Common financial-domain stylized facts:

- Fat-tailed return distributions (excess kurtosis)
- Volatility clustering and long-memory volatility
- Slow decay of return-magnitude autocorrelation (volatility persistence)
- Negligible linear return autocorrelation
- Leverage effect (negative return-volatility correlation)
- Momentum and short-run trend persistence
- Long-run reversal
- Sustained mispricing relative to fundamentals
- Bubble formation and crash dynamics
- Herding cascades and information cascades
- Liquidity dry-ups and flash crashes
- Time-varying bid-ask spread and depth
- Volume-volatility co-movement

The author MUST cite at least one paper that documents the stylized fact
they claim the agent helps produce.

---

## 6. Regime Labels and Activation Table

§3.5 of the handbook requires a regime contribution table. For financial-
domain scenarios:

- The table label `System Contribution by Regime` is relabelled
  **`Market Contribution by Regime`**.
- Regime palette (pick ≥2 rows; rename freely if a different label is more
  natural for the scenario):

| Regime palette                    | Typical use                                             |
|-----------------------------------|---------------------------------------------------------|
| Calm / Stress                     | Default for any market scenario                         |
| Bull / Bear                       | Long-horizon directional regimes                        |
| Boom / Bust                       | Asset-bubble or credit-cycle scenarios                  |
| Pre-crisis / Crisis / Post-crisis | Crisis-replication scenarios (LTCM, GFC, Asian, …)      |
| Normal / Panic / Recovery         | Crash-replication scenarios (Black Monday, Flash Crash) |
| Pre-event / Event / Post-event    | Discrete-shock scenarios (rate hike, earnings, …)       |
| Liquidity-rich / Liquidity-poor   | Microstructure-focused scenarios                        |
| Low-vol / High-vol                | Volatility-regime-focused scenarios                     |

The three columns (Regime, Contribution, Mechanism) and their order MUST
NOT change.

---

## 7. Action Space Row Labels

§3.6.3 of the handbook defines eight canonical generic aspects. Financial-
domain authors substitute the row labels as follows. Aspect dimensions and
row order MUST NOT change.

| Canonical aspect (handbook) | Financial-domain row label | Example specification                                    |
|-----------------------------|----------------------------|----------------------------------------------------------|
| Action types allowed        | Order types allowed        | market / limit / IOC / hold-no-op                        |
| Action parameter rule       | Price level rule           | limit price = `P + δ`; do not cross spread               |
| Sizing rule                 | Order quantity rule        | `Q* = min(base_size, wealth_cap, inventory_room)`        |
| Action lifetime             | Order lifetime             | 1 tick / GTC / cancel after K ticks                      |
| Revision policy             | Cancellation policy        | cancel-replace on signal change / never / on regime flip |
| State constraint            | Inventory constraint       | `                                                        |
| Resource cap                | Wealth / leverage cap      | cash floor, notional ceiling, leverage limit             |
| Exit rule                   | Stop-loss / kill rule      | drawdown trigger, or "none"                              |

Environment-imposed limits — exchange matching engine, tick grid, fee
schedule, latency model, message-rate caps, regulator-imposed circuit
breakers — MUST NOT appear here. They belong to the scenario / environment
specification, not the agent design.

---

## 8. Worked Substitution Example

```markdown
#### Action Space

| Aspect                | Specification                                       |
|-----------------------|-----------------------------------------------------|
| Order types allowed   | limit, hold-no-op                                   |
| Price level rule      | bid = anchor − k·σ; ask = anchor + k·σ; no crossing |
| Order quantity rule   | Q* = min(base_size, wealth_floor / price)           |
| Order lifetime        | 1 tick                                              |
| Cancellation policy   | cancel-replace each tick on stale anchor            |
| Inventory constraint  |                                                     |
| Wealth / leverage cap | cash ≥ 0; no margin                                 |
| Stop-loss / kill rule | none                                                |
```

This is the financial-domain instantiation of handbook §3.6.3. Compare
against the canonical generic form in `agent-design-skill.md §3.6.3` to
verify all eight aspect dimensions are still visibly covered.

---

## 9. Validation Addendum

In addition to the core handbook's §4 Validation Checklist, a financial-
domain specification MUST also satisfy:

- [ ] The Theory Family value comes from the §3 palette in this companion,
      or is justified by a citation that places the theory in financial
      literature.
- [ ] The real-world counterpart (handbook §3.3 paragraph 1) is named from
      the §4 enumeration in this companion, or is justified by a citation.
- [ ] At least one stylized fact (handbook §3.3 paragraph 3) is named from
      the §5 catalogue in this companion, with a citation.
- [ ] The Summary table uses **Market Role** (not the canonical generic
      `System Role`), and the Activation table is labelled **Market
      Contribution by Regime** (not `System Contribution by Regime`).
- [ ] The Action Space uses the §7 financial-domain row labels above.
- [ ] No environment-imposed market-microstructure rules (matching engine,
      tick grid, fees, latency, regulator-imposed caps) appear anywhere in
      the specification.

---

## 10. Status

| Field   | Content                              |
|---------|--------------------------------------|
| Version | 1.0.0                                |
| Created | 2026-06-11                           |
| Status  | canonical                            |
| Extends | `masim/format/agent-design-skill.md` |
