# EuropeanDebtCrisis — Scenario Target

## §0 Meta CHANGELOG

- 2026-07-15  Polish target-file gate (Case B): target file generated from existing downstream artefacts by polish-simulation-pipeline. Pre-consistency check PASS: 5 simulation-bases.md §4.N blocks (PeripheryBondSeller, CreditorPanicker, CoreBondBuyer, ECBIntervenor, HedgedFund) all have matching Rule/LLM/RuleLLM/Rag players.py classes and configs/EuropeanDebtCrisis/{V}/players.yml entries. Status set to `locked`.
- 2026-07-15  Polish run against skill baseline (define/agent-design/implement) — Round 1 Closeout.
             - Step 0 (target-file gate): Case B, reverse-reconstructed from existing artefacts, locked.
             - Step 1 (research audit): DOI-resolution PASS on 5 §4 anchors (De Grauwe 2011 10.2139/ssrn.1930063, Acharya et al. 2014 10.1111/jofi.12206, De Grauwe & Ji 2013 10.1016/j.jimonfin.2012.11.003, Krishnamurthy & Vissing-Jorgensen 2012 10.1257/aer.102.6.2332, Shleifer & Vishny 1997 10.1111/j.1540-6261.1997.tb03807.x, Brunnermeier & Pedersen 2009 10.1093/rfs/hhn098). Six-field completeness PASS on all 5 simulation-bases.md §2 Theory blocks. Bidirectional coverage PASS: 5 target §4 anchors maps 5 simulation-bases.md §2 Theory blocks.
             - Step 2 (agent + env): 5 archetypes polished; AGENT_POOL three-stage match outcome `reuse` for all 5 (profiles exist as stubs at finance/{stem}.md); icon-completeness §6.3 HARD GATE PASS (5 PNGs generated, 5 design.md mapping rows #63-#67 added, 5 profile Icon rows verified). Root doc §3/§5/§7 structural audit PASS.
             - Step 3 (config audit): all 4 variants polished; YAML parse PASS (16/16 files); `# Source:` traceability added to Rule/players.yml (30 annotations, from 0).
             - Step 4 (impl audit): py_compile PASS (4 variants); import smoke PASS (4 variants); no-defaults rule PASS; RuleLLM dual-section prompt invariant PASS (5 == PERSONA == + 5 == DECISION RULES == pairs); _RAG_FALLBACK define+reference PASS (added module-level constant + replaced inline string).
             - Steps 5-10 (review + smoke): Rule 5-round e2e PASS; LLM/RuleLLM/Rag setup-only PASS. explain.md §2 bidirectional PASS (5 theory-impl mapping rows in Rule). analysis.md §2 bidirectional PASS (6 metric-function rows in Rule).
             Status: locked -> released.
- 2026-07-15  Polish Round 2 re-audit — full re-verification PASS. Step 0: target file exists, Case A. Step 1: 5 target §4 anchors bidirectional with 5 simulation-bases.md §2 Theory blocks; 8 DOI references present. Step 2: AGENT_POOL three-stage match `reuse` x5; §6.3 icon-completeness 20/20 checks PASS (profile+Icon row+PNG+design.md mapping). Step 3: YAML parse 16/16 PASS; `# Source:` 38 annotations in Rule/players.yml; variant folders 4/4 match §10.1. Step 4: py_compile PASS x4; import smoke PASS x4; no-defaults 0 violations; RuleLLM dual-section 5 pairs PASS; _RAG_FALLBACK define+reference PASS. Steps 5-10: Rule 5-round e2e PASS; LLM/RuleLLM/Rag setup-only PASS. Status confirmed: `released`.

## §1 Meta

| Field         | Content                                                |
|---------------|--------------------------------------------------------|
| Name          | EuropeanDebtCrisis                                     |
| Domain        | finance                                                |
| Requested By  | a77                                                    |
| Produced By   | polish-simulation-pipeline (reverse-reconstruct from existing artefacts) |
| Created       | 2026-07-15                                             |
| Pipeline      | masim/skills/polish-simulation-pipeline.md             |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md       |
| Status        | released                                               |

## §2 Phenomenon Statement

### §2.1 Trigger

The phenomenon starts from a liquid peripheral sovereign bond market whose price is initially below fundamental value, reflecting pre-existing fiscal-confidence stress. A sequence of risk events (fiscal revelations, bank-sovereign linkages, creditor funding withdrawal) convinces short-horizon creditors that sovereign default risk is self-fulfilling. The trigger is not a fundamental insolvency event; it is a coordination shift in which more creditors believe that other creditors will withdraw funding, making withdrawal individually rational.

### §2.2 Mechanism

The core mechanism is a self-fulfilling doom loop: falling peripheral bond prices raise implied yields, which worsen debt-sustainability metrics, which trigger creditor panic and bank funding withdrawal, which produces further selling. Limits to arbitrage prevent hedge funds from instantly closing spreads because funding constraints, mark-to-market risk, and policy uncertainty limit stabilizing capital. Flight-to-quality reallocates capital from periphery to core, withdrawing liquidity. The ECB backstop can break the loop by credibly committing to buy peripheral bonds, removing the bad equilibrium.

### §2.3 Participants

The causal participants are periphery bond sellers, creditor panickers, core bond buyers, ECB intervenors, and hedged funds. Periphery bond sellers and creditor panickers supply destabilizing sell pressure based on deviation thresholds. Core bond buyers provide flight-to-quality demand. Hedged funds provide bounded arbitrage stabilization. The ECB intervenor provides the decisive backstop that halts the self-fulfilling spiral.

### §2.4 Resolution

The crisis resolves when the ECB backstop credibly intervenes, changing market expectations and order flow. Peripheral bond prices recover toward fundamental value as speculative selling abates and arbitrage capital returns. The end state is convergence toward fundamental value, with recovery speed dependent on intervention timing and credibility.

## §3 Research Goals

1. Does the rule-based model produce a self-fulfilling sovereign crisis in which peripheral bond price falls at least 15% below fundamental value?
2. Does the sovereign-bank doom loop (CreditorPanicker) amplify the initial sell pressure from PeripheryBondSeller?
3. Does ECB intervention at the -20% threshold stabilize the crisis and produce recovery within 15 rounds?
4. How sensitive are crisis depth and duration to the price-impact coefficient and intervention threshold?
5. Do Rule, LLM, RuleLLM, and Rag variants differ measurably in crisis timing, depth, recovery speed, and intervention effectiveness?

## §4 Theoretical Anchors

### §4.1 Self-Fulfilling Sovereign Crisis

| Field | Content |
|-------|---------|
| Full citation | De Grauwe, P. (2011). The governance of a fragile eurozone. CESifo Working Paper. https://doi.org/10.2139/ssrn.1930063 |
| Key mechanism (<=30 words) | In a monetary union, investor expectations of default can become self-fulfilling because member states cannot print their own currency. |
| Key equation | `sell if deviation(t) < sell_threshold` |
| Motivates agent | periphery-bond-seller |
| Parameter implication | `sell_threshold` in [-0.15, -0.05] determines crisis onset point. |

### §4.2 Sovereign-Bank Doom Loop

| Field | Content |
|-------|---------|
| Full citation | Acharya, V. V., Drechsler, I., & Schnabl, P. (2014). A pyrrhic victory? Bank bailouts and sovereign credit risk. *Journal of Finance*, 69(6), 2689-2739. https://doi.org/10.1111/jofi.12206 |
| Key mechanism (<=30 words) | Bank balance sheets deteriorate when sovereign bonds fall; expected bank rescues increase sovereign risk; creditors withdraw funding. |
| Key equation | `panic if deviation(t) < panic_threshold; sell_quantity = min(700, position)` |
| Motivates agent | creditor-panicker |
| Parameter implication | `panic_threshold` in [-0.25, -0.10] controls doom-loop amplification onset. |

### §4.3 Flight to Quality

| Field | Content |
|-------|---------|
| Full citation | De Grauwe, P., & Ji, Y. (2013). Self-fulfilling crises in the eurozone. *Journal of International Money and Finance*, 34, 15-36. https://doi.org/10.1016/j.jimonfin.2012.11.003; Krishnamurthy, A., & Vissing-Jorgensen, A. (2012). *American Economic Review*, 102(6), 2332-2367. https://doi.org/10.1257/aer.102.6.2332 |
| Key mechanism (<=30 words) | Crisis reallocates capital from risky peripheral bonds toward safer core sovereign assets, lowering core yields and withdrawing periphery liquidity. |
| Key equation | `buy when deviation(t) < flight_threshold; sell when deviation(t) > 0.10` |
| Motivates agent | core-bond-buyer |
| Parameter implication | `flight_threshold` in [-0.15, -0.05] controls flight-to-quality activation. |

### §4.4 Central-Bank Backstop

| Field | Content |
|-------|---------|
| Full citation | Draghi, M. (2012). Verbatim remarks at the Global Investment Conference, London; De Grauwe, P. (2011). https://doi.org/10.2139/ssrn.1930063 |
| Key mechanism (<=30 words) | A credible lender-of-last-resort commitment removes the bad equilibrium by assuring investors that disorderly funding failure will be countered. |
| Key equation | `intervene if deviation(t) < intervention_threshold; buy_quantity = min(800, cash/P(t))` |
| Motivates agent | ecb-intervenor |
| Parameter implication | `intervention_threshold` in [-0.30, -0.10] determines backstop activation depth. |

### §4.5 Limits to Arbitrage in Crisis Markets

| Field | Content |
|-------|---------|
| Full citation | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x; Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 |
| Key mechanism (<=30 words) | Arbitrage funds can buy distressed bonds, but funding constraints, redemption pressure, and margin risk limit their stabilizing capacity. |
| Key equation | `buy when deviation(t) < -entry_threshold; sell when deviation(t) > entry_threshold` |
| Motivates agent | hedged-fund |
| Parameter implication | `entry_threshold` in [0.03, 0.15] controls arbitrage entry point. |

## §5 Stylized Facts

| # | Stylized Fact | Source | Acceptance Metric |
|---|---|---|---|
| F1 | Peripheral sovereign spreads moved beyond fiscal fundamentals during 2010-2012 | De Grauwe & Ji (2013) https://doi.org/10.1016/j.jimonfin.2012.11.003 | CDI > 0.10 (crisis depth exceeds 10% of fundamental) |
| F2 | Sovereign-bank contagion amplified initial spread widening | Acharya et al. (2014) https://doi.org/10.1111/jofi.12206 | AR > 0.5 (creditor panic adds measurable sell pressure) |
| F3 | Flight-to-quality compressed core yields during peripheral stress | De Grauwe & Ji (2013); Krishnamurthy & Vissing-Jorgensen (2012) | CoreBondBuyer buy volume > 0 during crisis rounds |
| F4 | ECB OMT commitment compressed spreads without immediate large purchases | Draghi (2012) | IER > 0.5 (intervention covers majority of crisis rounds) |
| F5 | Hedge fund arbitrage was bounded by funding constraints | Shleifer & Vishny (1997); Brunnermeier & Pedersen (2009) | APR in [0.0, 0.30] (positive but bounded profit) |

## §6 Historical / Empirical Anchors

### §6.1 Greek Sovereign Debt Crisis (2010-2012)

Greek 10-year yields rose from single digits to extreme crisis levels; restructuring followed in 2012. Peripheral selling, creditor withdrawal, and ECB responses are the primary calibration anchors.

### §6.2 Spanish and Italian Spread Crisis (2011-2012)

Spanish 10-year spread over Germany peaked around 600+ bps in mid-2012. Italian spreads widened sharply despite large and liquid markets. Demonstrates sovereign-bank doom loop and flight-to-quality.

### §6.3 Draghi "Whatever It Takes" and OMT (2012-07)

Peripheral spreads compressed after ECB commitment without immediate large purchases. Demonstrates backstop credibility and crisis-resolution mechanism.

## §7 Agent Roster

| Agent (kebab) | Archetype | Theory Family | Market Role | Time Horizon | Primary Signals |
|---|---|---|---|---|---|
| periphery-bond-seller | PeripheryBondSeller | Self-fulfilling crisis (De Grauwe 2011) | destabilizing | short | deviation, sell_threshold |
| creditor-panicker | CreditorPanicker | Sovereign-bank doom loop (Acharya et al. 2014) | destabilizing | short | deviation, panic_threshold |
| core-bond-buyer | CoreBondBuyer | Flight to quality (De Grauwe & Ji 2013) | stabilizing | medium | deviation, flight_threshold |
| ecb-intervenor | ECBIntervenor | Central-bank backstop (Draghi 2012) | stabilizing | long | deviation, intervention_threshold |
| hedged-fund | HedgedFund | Limits to arbitrage (Shleifer & Vishny 1997) | stabilizing (bounded) | medium | deviation, entry_threshold |

## §8 Environment Specification

### §8.1 Price Formation

The market represents a peripheral sovereign bond price. Price updates via:
```
P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 0.01)
```
where D(t) = buy_volume - sell_volume, lambda = price_impact, gamma = mean_reversion, epsilon ~ N(0, sigma^2).

### §8.2 Information Broadcast

Market broadcasts: `price`, `fundamental`, `deviation`, `round`.

### §8.3 Constraints and Frictions

No short-selling in this scenario. Agents can only sell what they hold. ECB has larger initial cash to represent central-bank firepower. Hedged funds use symmetric entry threshold.

### §8.4 Round Granularity

200 rounds per full experiment. Each round: market receives orders, computes net demand, updates price, broadcasts market_data; investors perceive, decide, act.

## §9 Parameter Seeds

| Parameter | Default | Empirical Range | Belongs to | Source citation |
|---|---|---|---|---|
| initial_price | 95.0 | [80, 100] | market | normalization (starts below fundamental) |
| fundamental_value | 100.0 | [100, 100] | market | normalization |
| price_impact | 0.05 | [0.01, 0.15] | market | De Grauwe (2011) sovereign bond sensitivity |
| mean_reversion | 0.02 | [0.005, 0.05] | market | fiscal-fundamental reversion speed |
| noise_std | 0.01 | [0.001, 0.05] | market | market microstructure noise |
| sell_threshold | -0.10 | [-0.15, -0.05] | periphery-bond-seller | De Grauwe (2011) crisis onset |
| panic_threshold | -0.15 | [-0.25, -0.10] | creditor-panicker | Acharya et al. (2014) doom-loop onset |
| flight_threshold | -0.08 | [-0.15, -0.05] | core-bond-buyer | De Grauwe & Ji (2013) flight activation |
| intervention_threshold | -0.20 | [-0.30, -0.10] | ecb-intervenor | Draghi (2012) backstop depth |
| entry_threshold | 0.07 | [0.03, 0.15] | hedged-fund | Shleifer & Vishny (1997) arbitrage entry |
| initial_cash | 1000000.0 | - | all investors | normalization |
| initial_position (PBS) | 500 | [100, 1000] | periphery-bond-seller | initial periphery bond holdings |
| initial_position (CP) | 400 | [100, 800] | creditor-panicker | creditor funding exposure |
| initial_cash (ECB) | 5000000.0 | - | ecb-intervenor | large central-bank firepower |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Decision Mechanism |
|---|---|---|
| Rule | Yes | Deterministic deviation-threshold rules |
| LLM | Yes | Persona-only crisis reasoning |
| RuleLLM | Yes | Persona plus explicit threshold rules |
| Rag | Yes | Crisis literature retrieval plus LLM reasoning |

### §10.2 Pass / Fail Criteria

| Criterion | Metric | Threshold |
|---|---|---|
| Crisis emergence | CDI | > 0.10 |
| Crisis duration | CD | > 5 rounds |
| Intervention effectiveness | IER | > 0.50 |
| Spread recovery | SRT | < 30 rounds |
