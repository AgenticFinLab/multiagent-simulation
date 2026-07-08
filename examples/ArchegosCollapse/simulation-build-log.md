# ArchegosCollapse — Pipeline Build Log

## §0 Meta

| Field       | Content                                                 |
|-------------|---------------------------------------------------------|
| Name        | ArchegosCollapse                                        |
| Target file | examples/ArchegosCollapse/finance-archegos-collapse.md  |
| Target spec | masim/skills/define-simulation-scenario-skill.md (v1.2) |
| Domain      | finance                                                 |
| Pipeline    | masim/skills/create-simulation-pipeline.md              |
| Status      | released                                                |

## §A AGENT_POOL Reuse-or-Create Gate Log

| Candidate archetype             | Stage reached | Outcome        | Pool file                                                      |
|---------------------------------|---------------|----------------|----------------------------------------------------------------|
| concentrated-fund               | 3             | reuse approved | examples/AGENT_POOL/finance/concentrated-fund.md               |
| prime-broker-first-mover        | 3             | reuse approved | examples/AGENT_POOL/finance/prime-broker-first-mover.md        |
| prime-broker-delayed-liquidator | 3             | reuse approved | examples/AGENT_POOL/finance/prime-broker-delayed-liquidator.md |
| block-trade-buyer               | 3             | reuse approved | examples/AGENT_POOL/finance/block-trade-buyer.md               |
| information-trader              | 3             | reuse approved | examples/AGENT_POOL/finance/information-trader.md              |

Gate rationale: the current finance pool contains Archegos-specific standalone profiles for all five target §7 archetypes. Stage 1 matched filenames exactly, Stage 2 matched the seven-row Summary fingerprints, and Stage 3 confirmed compatible mechanisms, signal sets, parameters, and I/O contracts. No new pool file was required in this create-pipeline replay.

## §B Research Notes (extends target §4 - §6)

### §B.1 Core Theories

- Becketti (2021), DOI `10.18651/ER/v106n3Becketti`: verifies hidden TRS leverage, margin-breach forced close-out, and the concentrated-fund margin threshold / sell-ratio calibration.
- Gorton & Metrick (2012), DOI `10.1016/j.jfineco.2011.03.016`: verifies creditor-run incentives and the payoff advantage of earlier liquidation, used for the two prime-broker thresholds.
- Grossman & Miller (1988), DOI `10.1111/j.1540-6261.1988.tb04594.x`: verifies block-trade liquidity provision when discounts compensate inventory risk, used for block-buyer activation.
- Kyle (1985), DOI `10.2307/1913210`: verifies information-advantaged trading from order-flow signals, used for the information-trader detection and front-running rule.

### §B.2 Empirical Stylized Facts

F1-F5 from target §5 are represented in `analysis-bases.md §2` and implemented by `examples/ArchegosCollapse/Rule/analysis.py::calculate_metrics()`: trough deviation, cascade duration, broker loss ratio, delayed-broker ablation delta, and recovery gap.

### §B.3 Historical Events

Target §6.1 is the March 22-29, 2021 Archegos Capital Management collapse. The design maps Archegos to `concentrated-fund`, Morgan Stanley-style early liquidation to `prime-broker-first-mover`, Credit Suisse / Nomura-style delayed liquidation to `prime-broker-delayed-liquidator`, discounted block buyers to `block-trade-buyer`, and early order-flow short sellers to `information-trader`.

### §B.4 Canonical Role Taxonomy

| Candidate archetype             | Theory family           | Real-world counterpart                                                   | Domain role                | Primary signals                         | Pipeline confirmation |
|---------------------------------|-------------------------|--------------------------------------------------------------------------|----------------------------|-----------------------------------------|-----------------------|
| concentrated-fund               | Leverage (§4.1)         | family office or hedge fund with concentrated total-return-swap exposure | Destabilising              | price, fundamental, deviation, position | confirmed             |
| prime-broker-first-mover        | Leverage (§4.2)         | Morgan Stanley-type dealer with early risk-management stance             | Destabilising              | price, fundamental, deviation, position | confirmed             |
| prime-broker-delayed-liquidator | Leverage (§4.2)         | Credit Suisse or Nomura-type dealer with delayed reaction                | Destabilising              | price, fundamental, deviation, position | confirmed             |
| block-trade-buyer               | Liquidity (§4.3)        | opportunistic institutional buyer of distressed block trades             | Stabilising                | price, fundamental, deviation, cash     | confirmed             |
| information-trader              | Informed Trading (§4.4) | hedge fund that detects early distress via order-flow signals            | Destabilising then neutral | price, prev_price, deviation, return    | confirmed             |

### §B.5 Parameter Estimates

Target §9 parameter seeds are echoed in `simulation-bases.md §6` and `configs/ArchegosCollapse/{Rule,LLM,RuleLLM,Rag}/players.yml` with source comments. The only normalization-only row is `fundamental value`, within the target §11 cap.

## §C Open Questions and Risks

- Defer: LLM, RuleLLM, and Rag full 200-round execution requires live provider credentials from `.env`; deterministic Rule is the smoke-run baseline for this create-pipeline replay.
- Defer: several citations are regulatory/report URLs rather than DOI-bearing peer-reviewed papers; they are retained because they are primary sources for the historical Archegos event.

## §D Build Log

| Phase                       | Date       | Outcome      | Reviewer  | Notes                                                                                                                                                                                                                                                                                               |
|-----------------------------|------------|--------------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Structure check             | 2026-06-30 | partial pass | Codex     | Added `simulation-build-log.md`; upstream target file remains absent as legacy gap.                                                                                                                                                                                                                 |
| AGENT_POOL gate             | 2026-06-30 | pass         | Codex     | All five agents classified as `new`; pool files created in `examples/AGENT_POOL/finance/`.                                                                                                                                                                                                          |
| Root §4 normalization       | 2026-06-30 | pass         | Codex     | Replaced legacy §4 with handbook-aligned embedded form and pool source links.                                                                                                                                                                                                                       |
| Polish supersession         | 2026-07-01 | superseded   | QoderWork | Superseded by polish audit; polish trail lives in target §1 Meta CHANGELOG (`finance-archegos-collapse.md`) + git history. This build-log is retained for historical reference only and is not maintained by the polish pipeline.                                                                   |
| Round-2 polish supersession | 2026-07-06 | superseded   | QoderWork | Superseded by Round-2 polish audit under the evaluation-first baseline (`masim/evaluation/README.md`, Pass 2 Analysis Migration Rule); Round-2 trail lives in target §1 Meta CHANGELOG + git history (`polish(archegos): step {0..closeout}` commits). Build-log remains historical reference only. |
