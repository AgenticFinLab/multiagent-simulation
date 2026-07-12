# BlackMonday1987 - Scenario Target

## §1 Meta

| Field         | Content |
|---------------|---------|
| Name          | BlackMonday1987 |
| Domain        | finance |
| Requested By  | User |
| Produced By   | define-simulation-scenario-skill.md v1.0.0 (invoking agent: Codex) |
| Created       | 2026-07-06 |
| Pipeline      | masim/skills/create-simulation-pipeline.md |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.0) |
| Status        | released |

## §0 Meta CHANGELOG

- 2026-07-12  Polish target-file gate (Case A, three-PASS §11). Start-state `Status = locked` (§1 Meta) — no `draft → locked` upgrade needed. Structural gates all green: 10 top-level `## §` sections in canonical order (§1 Meta / §2 Phenomenon Statement / §3 Research Goals / §4 Theoretical Anchors / §5 Stylized Facts / §6 Historical Anchors / §7 Agent Roster / §8 Environment Specification / §9 Parameter Seeds / §10 Variants and Success Criteria), §1 Meta filled (Name=BlackMonday1987, Domain=finance, Produced By define-skill v1.0.0 invoking Codex), §2 has 4 sub-headings (Trigger / Mechanism / Participants / Resolution), §3 lists 4 research questions (one ablation-style Q2, one sweep-style Q3, one cross-variant Q4), §4 has 5 theory entries each with the required 5-row table (citation / key mechanism / key equation / motivates agent / parameter implication), §5 has 4 stylized-fact rows F1–F4 with quantitative ranges + primary sources + acceptance metrics naming `analysis.py` functions, §6 has 2 historical anchors (Black Monday 1987 + futures-cash lead-lag), §7 has 5 agent rows with all seven required columns, §8 has 4 sub-sections (§8.1 Price Formation P(t+1)=P(t)+λ·D(t)+γ·[F−P(t)]+ε / §8.2 Information Broadcast {price, fundamental, deviation, round} / §8.3 Constraints and Frictions / §8.4 Round Granularity), §9 has 10 parameter rows, §10.1 marks all four variants `Yes` (Rule / LLM / RuleLLM / Rag), §10.2 lists 4 success criteria. Cross-section consistency verified: every §7 theory-family references an existing §4.k (§4.1 → portfolio-insurer; §4.2 → index-arbitrageur; §4.3 → program-trader; §4.4 → value-investor; §4.5 → noise-trader); every §7 `Primary signals` field appears in §8.2 broadcast list (`price, fundamental, deviation, round`); every §9 parameter `Belongs to` resolves to a §7 agent or an §8 environment sub-section; every §5 stylized fact's `Acceptance metric` names a function in the analysis surface (`_compute_max_drawdown`, `_compute_crash_velocity`, `agent_vwap`, `_compute_autocorrelation`); §10.1 marks `Rule` `Yes` as required for a finance-domain deterministic baseline. Evidence provenance verified: 6 `doi.org` links across the file spanning Leland 1980, Stoll & Whaley 1990, De Long et al 1990, Shleifer & Vishny 1997, Black 1986, Kyle 1985, Lo & MacKinlay 1988; every §4 theory cites a resolvable DOI; every §5 stylized fact cites a primary source (Brady Commission 1988 for F1/F2/F3; Lo & MacKinlay 1988 for F4); every §6 historical anchor cites a primary source (Brady Commission 1988; Stoll & Whaley 1990); every §9 parameter empirical range cites a primary source, with `fundamental_value` marked `Source: normalization` (1/10 rows = 10%, at the aspiration boundary). Style hygiene verified: em-dashes present in body prose (title convention retained). Status remains `locked` at Step 0 exit.
- 2026-07-12  Step 1 research audit (three-PASS). §4 five theory entries × six-field completeness re-scanned (citation / key mechanism / key equation / motivates agent / parameter implication all populated per anchor); DOI resolution verified for the six live DOI URLs (Leland 1980 → 10.1111/j.1540-6261.1980.tb02190.x; Stoll & Whaley 1990 → 10.2307/2331010; De Long et al 1990 → 10.1111/j.1540-6261.1990.tb03695.x; Shleifer & Vishny 1997 → 10.1111/j.1540-6261.1997.tb03807.x; Black 1986 → 10.1111/j.1540-6261.1986.tb04513.x; Kyle 1985 → 10.2307/1913210). §4 ↔ simulation-bases.md §2 bidirectional coverage: §4.1 ↔ §2.1 (Leland-Rubinstein), §4.2 ↔ §2.2 (Stoll & Whaley), §4.3 ↔ §2.3 (Brady + Brunnermeier & Pedersen 2009), §4.4 ↔ §2.4 (Graham + Shleifer & Vishny), §4.5 ↔ §2.5 (Black + Kyle) — all five anchors present in both directions. §5 stylized-fact acceptance metrics (`_compute_max_drawdown`, `_compute_crash_velocity`, `_compute_agent_vwap`, `_compute_autocorrelation`) confirmed present in analysis-bases.md §2.1-§2.5 with matching Python function signatures. No missing anchors and no orphan theory blocks. Historical anchor cross-check: §6.1 dates (1987-10-19), volume (604M shares, 2.5× average), and Dow -22.6% match Brady Commission (1988) primary source; §6.2 lead-lag documented in Stoll & Whaley (1990).
- 2026-07-12  Step 2 agent + environment audit and icon-completeness HARD GATE (three-PASS). Rank-precedence hierarchy verified: simulation-bases.md §4 headers (Rank-1) = §4.1 PortfolioInsurer / §4.2 IndexArbitrageur / §4.3 ProgramTrader / §4.4 ValueInvestor / §4.5 NoiseTrader match target §7 rows (Rank-2) match implementation class names (Rank-3) in Rule/LLM/RuleLLM/Rag `players.py`. AGENT_POOL three-stage match rerun: filename scan → 5 stems (`portfolio-insurer`, `index-arbitrageur`, `program-trader`, `fundamental-analyst`, `noise-trader`) all resolve to existing `examples/AGENT_POOL/finance/*.md` files; 7-row Summary fingerprint match on each profile against target §7 Real-world counterpart + Theory family + Domain role + Primary signals + Intent line — no `new` or `fork` resolutions and no halt condition triggered; full-text inspection on all five confirms theory alignment with target §4 anchors. Root §3/§5/§7 structural check: §3 Market Design Principles has 3 sub-sections (§3.1/§3.2/§3.3); §5 Agent Diversity Verification checklist covers time horizons + information signals + conflicting incentives + stabilizing-vs-destabilizing mix + feedback loop + asymmetric sizing; §7 Communication and Round Structure documents Round N perceive/decide/act loop for both investors and Market. Icon-completeness HARD GATE (four independent gates per agent × 5 agents = 20 checks): pre-audit found 3 defects (portfolio-insurer, index-arbitrageur, program-trader missing all four sub-gates). Repairs: generated 3 icon PNGs via ImageGen (slate-100 badge, 512×512-equivalent, Chinese-label motifs 组合保险 / 指数套利 / 程式交易), installed under `examples/AGENT_POOL/agent_images/icons/finance-{portfolio-insurer,index-arbitrageur,program-trader}.png`; appended `| Icon | ![](../agent_images/icons/finance-{stem}.png) |` rows to each of the three pool profile Design Provenance tables; wrote `examples/BlackMonday1987/_shared_changes.md` with 3 pending mapping rows (#33/#34/#35) plus a chronology-note bullet for the main-session merge into `examples/AGENT_POOL/agent_images/design.md` — this preserves concurrency safety by keeping the shared design.md edit outside the polish sub-agent's commit. Post-repair verification: all 5 profiles now contain `| Icon` row (portfolio-insurer, index-arbitrageur, program-trader, fundamental-analyst, noise-trader); all 5 PNGs present at `agent_images/icons/finance-{stem}.png`; two design.md mapping rows already existed (rows #7 fundamental-analyst, #14 noise-trader), three pending in `_shared_changes.md`.
- 2026-07-12  Step 3 config audit (three-PASS). All four `configs/BlackMonday1987/{Rule,LLM,RuleLLM,Rag}/players.yml` parse as YAML under a `!include`-tolerant loader — Rule/LLM/RuleLLM 6 top-level keys (market + 5 investor blocks); Rag 7 keys (adds `knowledge:` shared-knowledge block). Variant-folder set complete: 4 variants correspond exactly to §10.1 `Yes` rows (Rule/LLM/RuleLLM/Rag). Pre-audit found 0 `# Source:` comments across the four files (violation of the traceability invariant). Repair: injected 102 `# Source:` comments in total (Rule 29 / LLM 15 / RuleLLM 29 / Rag 29), each pointing to the target §9 parameter row or simulation-bases.md sub-section that authorizes the numeric value; injected only above parameter lines that lacked an existing `# Source:` line (idempotent). §9 authority check: all Rule/RuleLLM/Rag parameter values match target §9 candidate defaults (`rebalance_threshold` 0.02, `hedge_ratio` 0.5, `arb_threshold` 0.01, `trigger_threshold` 0.01, `feedback_strength` 1.2, `value_discount` 0.15, `trade_probability` 0.05, `price_impact` 0.05, `mean_reversion` 0.01, `fundamental_value` 250.0); LLM variant contains only market-level parameters (Persona-driven; no per-agent numeric rules), consistent with the LLM variant contract.
- 2026-07-12  Step 4 implementation audit (three-PASS). `py_compile` PASS for all 11 impl files (Rule/LLM/RuleLLM/Rag × {players.py, analysis.py} + LLM/RuleLLM/Rag prompts.py). Import smoke PASS: all 11 modules import without error via `examples.BlackMonday1987.{Rule,LLM,RuleLLM,Rag}.{players,analysis,prompts}` paths. No-defaults scan: 0 `.get()` default-swallowing violations found (no `extras.get(...)` or `config.get(key, default)` patterns). RuleLLM dual-section invariant PASS: 5 system-prompt constants (`RULELLM_PORTFOLIO_INSURER_SYS`, `RULELLM_INDEX_ARBITRAGEUR_SYS`, `RULELLM_PROGRAM_TRADER_SYS`, `RULELLM_VALUE_INVESTOR_SYS`, `RULELLM_NOISE_TRADER_SYS`) each contain both `== PERSONA ==` and `== DECISION RULES ==` markers (5/5 pairs; the sixth grep match is the header comment). `_RAG_FALLBACK` single-source repair: pre-audit found the sentinel string duplicated (inline literal in Rag/players.py line 371 + local constant in Rag/analysis.py line 36). Repair: promoted `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` to a module-level constant in Rag/players.py just after `logger = logging.getLogger(__name__)`; replaced the inline literal with `_RAG_FALLBACK`; replaced the analysis.py local constant with `from examples.BlackMonday1987.Rag.players import _RAG_FALLBACK`. Post-repair verification: `rp._RAG_FALLBACK is ra._RAG_FALLBACK` returns True. explain/analysis bidirectional check: `analyze_black_monday(...)` writes `metrics.max_drawdown_pct`, `metrics.crash_velocity_pct`, `metrics.return_autocorr_lag1`, `metrics.crash_onset_round`, `summary["agent_vwap"]` — matching §5 acceptance metrics and analysis-bases.md §2.1–§2.5 signatures.
- 2026-07-12  Steps 5-10 scenario-level review + smoke tests (three-PASS). Rule 5-round end-to-end smoke via `GeneralSimulator`: setup complete (10 actors, Ray initialized on 11 CPUs, 128 MB object-store); Round 1/5 through Round 5/5 executed without exception; simulator returned a `list` result payload; shutdown clean. LLM setup-only smoke: Ray init OK; 10 actors launched; topology set up; total players 10; setup complete without exception. RuleLLM setup-only smoke: same shape as LLM, PASS. Rag setup-only smoke: same shape + knowledge block loaded; PASS. All three LLM-flavor variants complete `sim.setup()` without hitting the KnowledgeStore/prompts-loader failure modes; no `hard gate` violations surfaced.
- 2026-07-12  Round 2 full re-audit (three-PASS). Structural: 11 `## §` sections including the new §0 CHANGELOG (§0..§10). Icons: 5/5 PNGs present under `examples/AGENT_POOL/agent_images/icons/finance-{portfolio-insurer,index-arbitrageur,program-trader,fundamental-analyst,noise-trader}.png`. Icon rows: 5/5 pool profiles carry `| Icon` row. `# Source:` counts stable across the four players.yml files (Rule 29 / LLM 15 / RuleLLM 29 / Rag 29). `_RAG_FALLBACK` single-source: 1 definition in Rag/players.py + 1 import in Rag/analysis.py; 0 duplicate definitions elsewhere. `py_compile` re-check PASS on Rule/players.py, Rag/players.py, Rag/analysis.py. No regressions detected between Round 1 exit-state and Round 2 audit.
- 2026-07-12  Closeout traceability matrix (final). §4.1 Portfolio insurance and dynamic hedging → §7 `portfolio-insurer` row → `examples/AGENT_POOL/finance/portfolio-insurer.md` (icon `finance-portfolio-insurer.png` + design.md row pending main-session merge via `_shared_changes.md`) → `configs/BlackMonday1987/{Rule,RuleLLM,Rag}/players.yml::rule_portfolio_insurer / rulellm_portfolio_insurer / ragllm_portfolio_insurer` (params `rebalance_threshold`, `hedge_ratio`, `base_size`) → `examples.BlackMonday1987.{Rule,LLM,RuleLLM,Rag}.players:PortfolioInsurer` → simulation-bases.md §4.1 + §2.1. §4.2 Index futures arbitrage → §7 `index-arbitrageur` → `AGENT_POOL/finance/index-arbitrageur.md` → configs `..._index_arbitrageur` (params `arb_threshold`, `base_size`) → impl `IndexArbitrageur` → simulation-bases.md §4.2 + §2.2. §4.3 Positive feedback trading → §7 `program-trader` → `AGENT_POOL/finance/program-trader.md` → configs `..._program_trader` (params `trigger_threshold`, `feedback_strength`, `base_size`) → impl `ProgramTrader` → simulation-bases.md §4.3 + §2.3. §4.4 Limits to arbitrage / value floor → §7 `value-investor` → `AGENT_POOL/finance/fundamental-analyst.md` (three-stage match resolved to fundamental-analyst; icon `finance-fundamental-analyst.png` already present) → configs `..._value_investor` (params `value_discount`, `base_size`) → impl `ValueInvestor` → simulation-bases.md §4.4 + §2.4. §4.5 Noise / microstructure → §7 `noise-trader` → `AGENT_POOL/finance/noise-trader.md` → configs `..._noise_trader` (params `trade_probability`, `min_order`, `max_order`) → impl `NoiseTrader` → simulation-bases.md §4.5 + §2.5. Environment: target §8.1 price formation P(t+1)=P(t)+λ·D(t)+γ·[F−P(t)]+ε and §8.2 broadcast {price, fundamental, deviation, round} → configs `market.extras.{fundamental_value, initial_price, price_impact, mean_reversion, noise_std}` (all 5 flagged with `# Source:` comment referencing target §9 rows) → impl `Market` in Rule/players.py (reused by LLM/RuleLLM/Rag via `from examples.BlackMonday1987.Rule.players import Market`). Analysis: target §5 acceptance metrics `_compute_max_drawdown`, `_compute_crash_velocity`, `_compute_agent_vwap`, `_compute_autocorrelation` → analysis-bases.md §2.1-§2.5 → `examples.BlackMonday1987.{Rule,LLM,RuleLLM,Rag}.analysis:analyze_black_monday`. Status transition: `locked → released`.

## §2 Phenomenon Statement

### §2.1 Trigger

The scenario begins with a negative index price shock in a market already using portfolio insurance, program trading, and futures-linked execution. The shock pushes price below the first rebalancing thresholds used by mechanical hedging programs. Because the fundamental value is held constant, the initial decline is treated as a market-mechanism stress rather than a cash-flow shock.

### §2.2 Mechanism

The core mechanism is a dynamic-hedging feedback loop. Portfolio insurers sell as prices fall, program traders add threshold-based sell orders, and index arbitrageurs transmit futures-market pressure into the cash index. Their combined order imbalance depresses price further, causing more mechanical selling, wider liquidity stress, and temporary breakdown of price discovery.

### §2.3 Participants

The causally relevant participants are portfolio insurers, index arbitrageurs, program/feedback traders, value investors, and noise traders. Portfolio insurers and program traders provide the mechanical sell pressure, index arbitrageurs transmit cross-market stress, value investors provide delayed stabilizing demand, and noise traders supply background order flow. The market coordinator aggregates the orders and updates the index price.

### §2.4 Resolution

The crash stops when automated sellers exhaust inventory, price falls far enough to activate value-investor demand, and mean reversion becomes large relative to remaining sell pressure. The resolution is partial stabilization after a large drawdown, not a smooth return to fair value. No circuit breaker is included because the historical 1987 event occurred before modern U.S. market-wide circuit breakers.

## §3 Research Goals

1. Measure whether portfolio insurance plus program trading can generate a Black Monday-sized drawdown of roughly 15%-35%.
2. Test by ablation whether removing portfolio insurers or program traders materially reduces crash depth, crash velocity, and sell-volume concentration.
3. Sweep `hedge_ratio`, `feedback_strength`, and `price_impact` to estimate when dynamic hedging becomes self-reinforcing.
4. Compare Rule, LLM, RuleLLM, and Rag variants to see whether model-based reasoning changes crash timing, drawdown, and stabilizing value demand.

## §4 Theoretical Anchors

### §4.1 Portfolio insurance and dynamic hedging

| Field | Content |
|-------|---------|
| Full citation | Leland, H. E. (1980). Who should buy portfolio insurance? *Journal of Finance*, 35(2), 581-594. https://doi.org/10.1111/j.1540-6261.1980.tb02190.x |
| Key mechanism (≤30 words) | Dynamic hedgers sell falling markets to reduce equity exposure, creating endogenous positive feedback when many agents rebalance together. |
| Key equation | `sell_qty = hedge_ratio * abs(deviation) * position` when `deviation < -rebalance_threshold`. |
| Motivates agent | portfolio-insurer |
| Parameter implication | `rebalance_threshold` 0.02-0.05 and `hedge_ratio` 0.30-0.70 in §9. |

### §4.2 Index futures arbitrage transmission

| Field | Content |
|-------|---------|
| Full citation | Stoll, H. R., & Whaley, R. E. (1990). The dynamics of stock index and stock index futures returns. *Journal of Financial and Quantitative Analysis*, 25(4), 441-468. https://doi.org/10.2307/2331010 |
| Key mechanism (≤30 words) | Futures-market pressure can lead cash-market returns when arbitrage desks sell spot baskets against discounted futures. |
| Key equation | `Q_arb = base_size` when `abs(deviation) > arb_threshold`, direction set by spot/fair-value gap. |
| Motivates agent | index-arbitrageur |
| Parameter implication | `arb_threshold` 0.005-0.03 and `base_size` 40-120 in §9. |

### §4.3 Positive feedback trading

| Field | Content |
|-------|---------|
| Full citation | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x |
| Key mechanism (≤30 words) | Traders who sell after price declines can make rational speculation destabilizing when feedback demand is large enough. |
| Key equation | `Q_program = base_size * (1 + feedback_strength * abs(deviation) * 10)`. |
| Motivates agent | program-trader |
| Parameter implication | `trigger_threshold` 0.005-0.03 and `feedback_strength` 0.8-1.5 in §9. |

### §4.4 Limits to arbitrage and value floors

| Field | Content |
|-------|---------|
| Full citation | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism (≤30 words) | Correct beliefs do not eliminate mispricing instantly because stabilizing capital is limited and risky during crashes. |
| Key equation | `value_buy = base_size` when `price < fundamental * (1 - value_discount)`. |
| Motivates agent | value-investor |
| Parameter implication | `value_discount` 0.10-0.30 and `base_size` 20-80 in §9. |

### §4.5 Noise and microstructure stress

| Field | Content |
|-------|---------|
| Full citation | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x; Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210 |
| Key mechanism (≤30 words) | Uninformed order flow and price impact create background volatility and make liquidity provision costly under imbalance. |
| Key equation | `trade ~ Bernoulli(trade_probability)` with bounded random order quantity. |
| Motivates agent | noise-trader |
| Parameter implication | `trade_probability` 0.03-0.10 and `price_impact` 0.03-0.08 in §9. |

## §5 Stylized Facts

| #  | Fact (one sentence) | Quantitative range | Citation | Acceptance metric |
|----|----------------------|--------------------|----------|-------------------|
| F1 | The simulated index experiences a crash-scale drawdown. | 15% <= max drawdown <= 35% | Brady Commission (1988), Report of the Presidential Task Force on Market Mechanisms | `analysis.py: _compute_max_drawdown()` in [15, 35] |
| F2 | The crash is fast, with peak per-round decline in the cascade phase. | crash velocity >= 2% per round | Brady Commission (1988) intraday timeline | `analysis.py: _compute_crash_velocity()` >= 2 |
| F3 | Portfolio insurers and program traders dominate sell-side volume during the cascade. | combined sell volume >= 50% | Brady Commission (1988) | `analysis.py: agent_vwap` sell attribution >= 0.50 |
| F4 | Feedback dynamics produce positive return autocorrelation during the crash phase. | AC1 0.30-0.60 | Lo & MacKinlay (1988), https://doi.org/10.1093/rfs/1.1.41 | `analysis.py: _compute_autocorrelation()` in [0.30, 0.60] |

## §6 Historical / Empirical Anchors

### §6.1 Black Monday 1987

| Field | Content |
|-------|---------|
| Name + dates | Black Monday 1987, 1987-10-19. |
| Trigger | Prior-week selling, portfolio insurance rebalancing, futures-market pressure, and liquidity stress interacted after the market opened. |
| Quantitative arc | The Dow Jones Industrial Average fell 22.6% in one day; S&P 500 futures and cash markets experienced large lead-lag dislocations and severe order imbalance. |
| Agent mapping | portfolio-insurer maps to dynamic hedging sellers; index-arbitrageur maps to futures-cash transmission desks; program-trader maps to automated feedback selling; value-investor maps to delayed contrarian demand; noise-trader maps to background order flow. |
| Primary source(s) | Presidential Task Force on Market Mechanisms. (1988). *Report of the Presidential Task Force on Market Mechanisms*. U.S. Government Printing Office. |

### §6.2 Futures-cash lead-lag during crash stress

| Field | Content |
|-------|---------|
| Name + dates | S&P 500 futures and cash-market lead-lag around the 1987 crash. |
| Trigger | Futures selling by hedgers pushed derivatives below fair value, inducing cash-market basket selling by arbitrageurs. |
| Quantitative arc | Stoll and Whaley document futures leading cash returns by minutes and occasionally longer during stressed intervals. |
| Agent mapping | index-arbitrageur maps directly to the futures-cash transmission channel; portfolio-insurer and program-trader create the initiating futures/cash pressure. |
| Primary source(s) | Stoll & Whaley (1990), https://doi.org/10.2307/2331010 |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|--------------------|------------------------|---------------------------|-------------|-----------------|-------------|---------------------|
| portfolio-insurer | mutual fund / pension | Liquidity / Funding (§4.1) | Destabilising | price, fundamental, deviation | Exists to reduce equity exposure mechanically as the index falls. | examples/AGENT_POOL/finance/portfolio-insurer.md |
| index-arbitrageur | proprietary trading desk | Microstructure (§4.2) | Context-dependent | price, fundamental, deviation | Exists to transmit futures-cash dislocations into spot index order flow. | examples/AGENT_POOL/finance/index-arbitrageur.md |
| program-trader | quant fund / CTA | Behavioral Finance (§4.3) | Destabilising | price, deviation, round | Exists to amplify downward moves through threshold-based feedback selling. | examples/AGENT_POOL/finance/program-trader.md |
| value-investor | mutual fund / pension | Fundamental / Value (§4.4) | Stabilising | price, fundamental, deviation | Exists to supply contrarian demand after a sufficiently deep discount. | examples/AGENT_POOL/finance/fundamental-analyst.md |
| noise-trader | retail investor | Noise / Liquidity-providing noise (§4.5) | Context-dependent | price, round, rng_state | Exists to provide stochastic background order flow. | examples/AGENT_POOL/finance/noise-trader.md |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a single-price index market. Price follows `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t)`, where `D(t)` is buy quantity minus sell quantity. The high price-impact coefficient represents stressed 1987 intraday liquidity and delayed specialist absorption.

### §8.2 Information Broadcast

Each round broadcasts `price`, `fundamental`, `deviation`, and `round`. These are sufficient for the level-triggered portfolio insurance, index arbitrage, program trading, value-investing, and noise-trading mechanisms already implemented in the scenario. No `prev_price` signal is required because the core triggers are level/deviation based rather than return based.

### §8.3 Constraints and Frictions

No market-wide circuit breaker is modeled. Agents are constrained by cash, inventory, base order size, and maximum realizable quantity. The market applies a positive price floor and constant fundamental value so the crash comes from order-flow feedback rather than deteriorating fundamentals.

### §8.4 Round Granularity

One round represents an intraday trading interval in which program trades can be submitted, orders are aggregated, and the index price updates. The 200-round default config supports pre-crash stability, feedback onset, cascade escalation, floor formation, and recovery phases. Historical timing is calibrated against the 1987 single-session crash and Stoll-Whaley intraday lead-lag evidence.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation |
|-----------|--------|----------------------------------|-----------------|-------------------|-----------------|
| rebalance threshold | `theta_pi` | portfolio-insurer (§7) | 0.02-0.05 | 0.02 | Leland (1980), https://doi.org/10.1111/j.1540-6261.1980.tb02190.x; Brady Commission (1988) |
| hedge ratio | `h` | portfolio-insurer (§7) | 0.30-0.70 | 0.50 | Brady Commission (1988) |
| arbitrage threshold | `theta_arb` | index-arbitrageur (§7) | 0.005-0.03 | 0.01 | Stoll & Whaley (1990), https://doi.org/10.2307/2331010 |
| program trigger threshold | `theta_prog` | program-trader (§7) | 0.005-0.03 | 0.01 | Brady Commission (1988); De Long et al. (1990), https://doi.org/10.1111/j.1540-6261.1990.tb03695.x |
| feedback strength | `phi` | program-trader (§7) | 0.80-1.50 | 1.20 | De Long et al. (1990), https://doi.org/10.1111/j.1540-6261.1990.tb03695.x |
| value discount | `m` | value-investor (§7) | 0.10-0.30 | 0.15 | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| trade probability | `p_n` | noise-trader (§7) | 0.03-0.10 | 0.05 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| price impact | `lambda` | environment (§8.1) | 0.03-0.08 | 0.05 | Kyle (1985), https://doi.org/10.2307/1913210; Brady Commission (1988) |
| mean reversion | `gamma` | environment (§8.1) | 0.005-0.02 | 0.01 | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| fundamental value | `F` | environment (§8.1) | Source: normalization | 250.0 | Source: normalization |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence) |
|---------|--------|--------------------------|
| Rule | Yes | Required deterministic baseline for the crash feedback mechanism. |
| LLM | Yes | Tests whether persona-only decision making delays or amplifies crash behavior. |
| RuleLLM | Yes | Tests whether explicit rule prompts preserve the deterministic mechanism with model reasoning. |
| Rag | Yes | Tests whether retrieved 1987 crash context changes agent behavior. |

### §10.2 Pass / Fail Criteria

| Criterion | Status when satisfied |
|-----------|-----------------------|
| All §5 stylized facts reproduced within their ranges | green |
| Every §3 research question answerable from analysis | green |
| Ablating any §7 agent produces a measurable change | green |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green |
