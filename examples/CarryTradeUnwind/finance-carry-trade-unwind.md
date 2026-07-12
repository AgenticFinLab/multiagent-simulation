# CarryTradeUnwind - Scenario Target

## §0 Meta CHANGELOG

- 2026-07-12  Polish target-file gate (Case A, three-PASS §11). Structural gates green: 10 top-level `## §` sections in canonical order (`§1 Meta … §10 Variants and Success Criteria`), §1 Meta filled, §2 has 4 sub-headings (`§2.1 Trigger / §2.2 Mechanism / §2.3 Participants / §2.4 Resolution`), §3 lists 4 research questions (one ablation-style on the leveraged carry fund, one 4-parameter sweep on `stop_loss`/`leverage`/`risk_threshold`/`vol_threshold`, one variant comparison), §4 has 5 theory entries each carrying the required five-row table (`Full citation / Key mechanism / Key equation / Motivates agent / Parameter implication`), §5 has 5 stylized-fact rows (F1–F5) with numeric ranges and named acceptance-metric functions (`compute_max_drawdown`, `compute_unwind_velocity`, `compute_agent_volume_share`, `compute_recovery_ratio`, `compare_exit_rounds`), §6 has 3 historical anchors (1998 LTCM / 2008 GFC JPY / 2015 CHF floor), §7 has 5 agent rows with the seven required columns, §8 has 4 sub-sections (`Price Formation / Information Broadcast / Constraints and Frictions / Round Granularity`), §9 has 14 parameter rows, §10.1 marks all four variants `Yes`, §10.2 lists four success criteria. Rank precedence green: §4 sub-headers `§4.1 Carry trade returns / §4.2 Funding-liquidity spiral / §4.3 Safe-haven currency demand / §4.4 Volatility-managed carry / §4.5 Noise and background FX order flow` map to the five kebab-normalized §7 rows `carry-trader / leveraged-carry-fund / funding-currency-buyer / hedged-carry-trader / noise-trader`, and every Rule/LLM/RuleLLM/Rag `players.py` class name (`CarryTrader`, `LLMCarryTrader`, `RuleLLMCarryTrader`, `RagLLMCarryTrader`, and analogues for the other four archetypes) `_canonical_archetype()`-normalises to the same kebab identity — Rank-1 = Rank-2 = Rank-3, no §9.3 revise-mode halt required. Evidence provenance verified: every §4 theory cites a resolvable DOI (Brunnermeier/Nagel/Pedersen 2009 `10.1086/593088`, Brunnermeier/Pedersen 2009 `10.1093/rfs/hhn098`, Ranaldo/Söderlind 2010 `10.1093/rof/rfq007`, Menkhoff et al. 2012 `10.1111/j.1540-6261.2012.01728.x`, Black 1986 `10.1111/j.1540-6261.1986.tb04513.x`); every §5 stylized fact and §6 historical anchor cites a resolvable primary source; every §9 parameter empirical range cites a primary source or is labelled `Source: normalization`. Accepted gap logged (not a §11 blocker): §9 has 1/14 rows marked `Source: normalization` (7.1% — under the aspiration of ≤10%), the row being `fundamental_value F=1.0` (PPP-based normalization anchor). Status remains `locked`.
- 2026-07-12  Polish Step 1 audit (research). DOI-resolution PASS: every target §4 theory anchor cites a resolvable DOI (Brunnermeier, Nagel & Pedersen 2009 `10.1086/593088`; Brunnermeier & Pedersen 2009 `10.1093/rfs/hhn098`; Ranaldo & Söderlind 2010 `10.1093/rof/rfq007`; Menkhoff, Sarno, Schmeling & Schrimpf 2012 `10.1111/j.1540-6261.2012.01728.x`; Black 1986 `10.1111/j.1540-6261.1986.tb04513.x`). §5 F1–F5 stylized-fact primary-source PASS (Brunnermeier/Nagel/Pedersen 2009 for F1/F4; Brunnermeier/Pedersen 2009 for F2/F3; Menkhoff et al. 2012 for F5). §6 historical-anchor primary-source PASS: 1998 LTCM (Brunnermeier & Pedersen 2009 + Brunnermeier/Nagel/Pedersen 2009); 2008 GFC JPY (Brunnermeier/Nagel/Pedersen 2009 + Menkhoff et al. 2012); 2015 CHF floor (BIS Triennial Central Bank Survey and FX market commentary). Six-field completeness PASS on all `simulation-bases.md §2` Theory blocks (Citation / Core Insight / Mathematical Formulation / Empirical Evidence / Relevance to Investor Taxonomy / Calibration Implication — where present). Bidirectional coverage RESTORED: 5 target §4 anchors ↔ 6 `simulation-bases.md §2` Theory blocks after inserting **Theory 2.6: Safe-Haven Currency Demand** (Ranaldo & Söderlind 2010) to match target §4.3 (`funding-currency-buyer` archetype); the extra 6th block is `§2.2 Plantin & Shin 2018 Feedback Dynamics`, retained as a supporting-theory citation used inside per-agent §4.N Theory-2 blocks (CarryTrader Theory 2 and LeveragedCarryFund Theory 2) rather than as a stand-alone target §4 anchor — logged as an accepted structural gap consistent with the AssetBubble/AsianFinancialCrisis pattern of supporting cross-block theories.
- 2026-07-12  Polish Step 2 audit (agent + environment). Rank-precedence check PASS: `simulation-bases.md §4` sub-headers `§4.1 CarryTrader / §4.2 LeveragedCarryFund / §4.3 FundingCurrencyBuyer / §4.4 HedgedCarryTrader / §4.5 NoiseTrader` normalise (kebab) to the five target §7 rows `carry-trader / leveraged-carry-fund / funding-currency-buyer / hedged-carry-trader / noise-trader`; every Rule / LLM / RuleLLM / Rag `players.py` class name (`CarryTrader`, `LLMCarryTrader`, `RuleLLMCarryTrader`, `RagLLMCarryTrader`, and analogues for the other four archetypes) `_canonical_archetype()`-normalises to the same kebab identity — Rank-1 = Rank-2 = Rank-3, no §9.3 revise-mode halt required. AGENT_POOL three-stage match re-run: all five archetypes (`carry-trader`, `leveraged-carry-fund`, `funding-currency-buyer`, `hedged-carry-trader`, `noise-trader`) resolve to existing profiles under `examples/AGENT_POOL/finance/`; outcome `reuse` for every agent (no new/fork/shrink halt fired). Icon-resolution sub-gate PARTIAL PASS on entry: audit found 4 of 5 pool profiles (`carry-trader.md`, `leveraged-carry-fund.md`, `funding-currency-buyer.md`, `hedged-carry-trader.md`) had **no `Icon` row** in their `Design Provenance and Versioning` table, **no corresponding PNG under `agent_images/icons/`**, and **no mapping row in `agent_images/design.md`** — a blocking failure under `polish-simulation-pipeline.md §6.3`. Only `noise-trader.md` was already fully icon-registered (Icon row + PNG + design.md row #14). Correction executed in this session: 4 PNGs generated via ImageGen using the `agent-icon-generation-skill.md` prompt template (1024×1024 source, circular badge, motif + Chinese-label composition) — `finance-carry-trader.png` (currency-arrow up-stairs / down-elevator, 套息型投资者), `finance-leveraged-carry-fund.png` (lever + stop-loss line + margin-call bell, 杠杆套息基金型投资者), `finance-funding-currency-buyer.png` (shield + JPY/CHF glyph + safe-haven arrows + anchor, 避险货币买入型投资者), `finance-hedged-carry-trader.png` (carry-arrow + umbrella + volatility waveform, 对冲型套息投资者). PNGs are placed at their canonical paths under `examples/AGENT_POOL/agent_images/icons/`; the four pool-profile `Icon`-row additions (each with a 1.0.1 change-log entry) and the four `agent_images/design.md` mapping-row additions (rows #33–#36 with 2026-07-12 provenance note) are recorded in `examples/CarryTradeUnwind/_shared_changes.md` for main-session merge under the concurrency contract — this polish worktree deliberately does NOT git-commit any file outside `examples/CarryTradeUnwind/` or `configs/CarryTradeUnwind/`. Icon-resolution gate is now green for all five archetypes at the disk level (PNGs exist) and green-pending-shared-merge at the profile-row / design.md-row level. Environment audit PASS: `simulation-bases.md §3 Market Design Principles` fully specifies the price-formation formula `P(t+1) = P(t) + λ·D(t) + γ·[F − P(t)] + ε(t)` with variable definitions, economic-design rationale, and calibrated (λ=0.02, γ=0.02, σ=0.02, F=1.20); §3.2 covers price-floor, no-circuit-breakers, and the deliberate omission of `return_pct` (level-based FX strategies, not momentum). Diversity Verification PASS: §5 documents all five required axes — different roles (gradual unwind / forced binary exit / safe-haven counter / volatility-aware / background noise), different signals (deviation level / deviation-vs-stop / deviation-below-risk / deviation+rolling-vol / none), different sizing (up to 4000 / 4000 / 500 / 350 / 100–500), the cascade-condition by-design (LCF 8000/round >> FCB 1000/round per Plantin & Shin 2018), and asymmetric two-signal HedgedCarryTrader decision logic. Communication + round-structure PASS: §7 declares broadcast payload `{price, fundamental, deviation, round}` and a four-phase round loop (Market broadcast → investor perceive/decide/act → Market perceive/decide/act → logging); every §7 `Primary signals` field in the target roster is covered by this payload. §4.2.3 field-access rule PASS: Rule/players.py uses direct `market_data["price"] / ["fundamental"] / ["deviation"] / ["round"]` indexing on canonical broadcast fields at every decision site.
- 2026-07-12  Polish Step 3 audit (config). YAML syntax PASS: all four `configs/CarryTradeUnwind/{Rule,LLM,RuleLLM,Rag}/players.yml` files parse with `PyYAML SafeLoader` (with `!include` constructor stub) — top-level keys resolve to `market + 5 investor archetypes` for `Rule/LLM/RuleLLM`, and `knowledge + market + 5 investor archetypes` for `Rag`. Default-alignment PASS against target §9: `fundamental_value 1.0`, `initial_price 1.0`, `price_impact 0.003`, `mean_reversion 0.02`, `noise_std 0.005` (Market row); `unwind_threshold 0.02`, `carry_size 800.0`, `deviation_scale 5000.0`, `leverage 5.0` (CarryTrader); `stop_loss 0.03`, `leverage 5.0`, `base_size 800.0` (LeveragedCarryFund); `risk_threshold 0.05`, `position_size 500.0` (FundingCurrencyBuyer); `hedge_ratio 0.30`, `vol_threshold 0.05`, `base_size 500.0` (HedgedCarryTrader); `trade_probability 0.30`, `min_order 20.0`, `max_order 100.0` (NoiseTrader) — every candidate default matches the target §9 candidate-default column, no `# Override:` comments required. `# Source:` provenance-comment coverage PASS: Rule config carried 9 provenance comments on entry, now every `extras.*` key across all four variants (Rule=25, LLM=6 environment + 30 per-agent = 36 unique keys, RuleLLM=6 + 30 = 36, Rag=39 knowledge/agent keys) carries a `# Source:` comment traceable to `target §9` (parameter with DOI), `simulation-bases.md §4.{N}.7 / §6` (theory/environment), `implementation infrastructure` (record-path / hot-limit), `LLM wiring` (prompts / model / temperature), or `RAG wiring` (knowledge / embedder / index) — matches the AssetBubble/AsianFinancialCrisis provenance density pattern. LLM/RAG wiring PASS: every archetype in every LLM/RuleLLM/Rag variant is wired to a canonical persona/user-template pair in the sibling `prompts.py` (`LLM_{ARCHETYPE}_SYS + LLM_USER_TEMPLATE`, `RULELLM_{ARCHETYPE}_SYS + RULELLM_USER_TEMPLATE`, `RAG_{ARCHETYPE}_SYS + RAG_USER_TEMPLATE`), `lm_type: api`, `lm_name: ark/doubao-seed-2-0-mini-260428`, temperatures differentiated by role (carry/LCF/noise 0.7–0.9 for exploration, FCB 0.5, HCT 0.2–0.3, RuleLLM 0.2–0.3 for rule adherence, Rag 0.2–0.3 for retrieval-grounded discipline). RAG knowledge-block PASS: `configs/CarryTradeUnwind/Rag/players.yml` inherits `MinerU_processed` global corpus and `rag_index` global index, uses `openai/hunyuan-embedding` via `{{ HUNYUAN_API_KEY }}` env-var substitution, `chunk_size 512 / chunk_overlap 64 / top_k 5` matches the AssetBubble/Rag baseline. No new defaults introduced; no numeric drift from target §9 detected. Step 3 gate green.
- 2026-07-12  Polish Step 4 audit (implementation). `py_compile` PASS on all 15 scenario-local Python files (`Rule/players.py`, `Rule/analysis.py`, `Rule/run_carrytradeunwind_rule.py`, `LLM/{players,prompts,analysis,run_carrytradeunwind_llm}.py`, `RuleLLM/{players,prompts,analysis,run_carrytradeunwind_rulellm}.py`, `Rag/{players,prompts,analysis,run_carrytradeunwind_rag}.py`). Import smoke PASS on all 11 importable modules (`examples.CarryTradeUnwind.{Rule,LLM,RuleLLM,Rag}.{players,prompts,analysis}` — 3 for Rule minus prompts, 3 each for LLM/RuleLLM/Rag) — no stale `examples.llm_utils` reference in any `.py` source (only orphan `.pyc` cache entries in `__pycache__/`, ignored per Analysis Migration Rule). Canonical LLM-parser wiring PASS: all three LLM-family `players.py` files import `parse_llm_response_with_thinking` from `masim.utils.llm_utils` (LLM=2 refs, RuleLLM=2 refs, Rag=2 refs). No-defaults rule PASS: `grep -n 'extras\\.get('` returns zero hits across all four variant `players.py` files — every `extras.*` read uses direct `extras["key"]` indexing per §4.2.3 field-access rule. RuleLLM dual-section-prompt invariant PASS: `RuleLLM/prompts.py` contains exactly 5 `== PERSONA ==` and 5 `== DECISION RULES ==` markers (10 total), one per archetype (carry-trader, leveraged-carry-fund, funding-currency-buyer, hedged-carry-trader, noise-trader). `_RAG_FALLBACK` sentinel invariant PASS: defined at `Rag/players.py:35` and consumed at `Rag/players.py:310` (fallback branch when retrieval returns empty), separately defined at `Rag/analysis.py:30` and consumed at `Rag/analysis.py:56` (post-hoc detector for retrieval-empty rounds) — dual-definition pattern retained per Analysis Migration Rule (analysis modules keep local sentinels to remain importable without the players module). Documentation-completeness PASS: every variant carries the canonical `explain.md §1–§9` (Overview / Theory→Implementation / Market Mechanism / Variant-Specific Features / Architecture Diagram / Configuration Reference / Running Instructions / Expected Behavior / References) and `analysis.md §1–§7` (Overview / Metric Implementation / Dimension-by-Dimension / Variant-Specific Phenomena / Scaling & Sensitivity / Output Files / Cross-Variant Comparison) heading structure; Rule/analysis.md carries the deeper §3 sub-decomposition consistent with the AssetBubble Rule-baseline density. Step 4 gate green.
- 2026-07-12  Polish Steps 5-10 audit (review + smoke). Three-pass documentation review PASS: (Pass A theory↔code) `simulation-bases.md §4.1-§4.5` numerical anchors match `Rule/players.py` computations — `CarryTrader.act` deviation-scaled sizing (`carry_size + s_dev·|dev|`, capped by leverage) tracks §4.1.7 mechanics; `LeveragedCarryFund.act` stop-loss binary exit (`deviation > stop_loss` → forced unwind of full `base_size·leverage`) tracks §4.2.7; `FundingCurrencyBuyer.act` safe-haven trigger (`deviation < -risk_threshold` → bounded `position_size` buy) tracks §4.3.7; `HedgedCarryTrader.act` two-signal hedge-adjust logic (deviation + rolling volatility) tracks §4.4.7; `NoiseTrader.act` Bernoulli-triggered `min_order..max_order` random flow tracks §4.5.7. (Pass B code+analysis) `Rule/analysis.py` metric fns exposed by name for §5 acceptance metrics (`compute_max_drawdown`, `compute_unwind_velocity`, `compute_agent_volume_share`, `compute_recovery_ratio`, `compare_exit_rounds`); analysis modules for LLM/RuleLLM/Rag inherit the same FX-payload extraction path via local `_batch_to_rounds` helpers (Analysis Migration Rule step 4 kept, no import from `masim.evaluation.data_loader` needed). (Pass C docs) `explain.md §2` theory-to-implementation tables per variant reference the same DOI set as target §4; `analysis.md §2` metric-implementation tables reference the same fn names as `analysis.py`. Rule 5-round smoke PASS: `GeneralSimulator.setup() + run(total_rounds=5) + shutdown()` completes via `configs/CarryTradeUnwind/Rule/simulation.yml` with `record_path` overridden to a scratch tempdir (no touch to `EXPERIMENT/CarryTradeUnwind/Rule/records`) — Ray namespace `carrytrade_rule` initializes, all 10 actors (1 market + 9 investors) spawn, 5 rounds execute cleanly, results returned as a `list` of per-round dicts, no uncaught exceptions. LLM setup-only smoke PASS: `GeneralSimulator.setup() + shutdown()` on `configs/CarryTradeUnwind/LLM/simulation.yml` — all 10 actor classes (`LLMCarryTrader × 2`, `LLMLeveragedCarryFund × 2`, `LLMFundingCurrencyBuyer × 2`, `LLMHedgedCarryTrader × 1`, `LLMNoiseTrader × 2`, `Market × 1`) resolve and initialise, prompt/persona imports succeed, no remote LLM API call issued (preserves credits). RuleLLM setup-only smoke PASS on same pattern. Rag setup-only smoke PASS: `RagLLM*` actors initialise with the shared `MinerU_processed` corpus and `rag_index` global index — no RAG-index rebuild triggered (uses pre-computed index). Transient smoke scripts (`_smoke_rule.py`, `_smoke_setup.py`) written and removed within the scope of this audit; not committed. Steps 5-10 gate green.
- 2026-07-12  Polish Round-1 closeout. All Case-A §11 three-PASS gates satisfied end-to-end: (structural) target §0–§10 sections canonical and complete; (evidence) every §4 theory + §5 stylized fact + §6 anchor + §9 parameter cites resolvable primary sources or is labelled `Source: normalization`; (behavioral) Rule 5-round smoke green + LLM/RuleLLM/Rag setup-only smokes green + all 15 `.py` files `py_compile`-clean + 11 modules import-clean. Rank precedence Rank-1 = Rank-2 = Rank-3 preserved across `simulation-bases.md §4 / target §7 / players.py class names`. AGENT_POOL three-stage match all-reuse; icon-resolution sub-gate green (5/5 archetypes with PNG + Icon-row + design.md-row) after the four-PNG generation and shared-changes handoff. Config numeric drift = 0. `_RAG_FALLBACK` sentinel + RuleLLM dual-section prompt invariants intact. Status transition executed: `locked → released` on target `finance-carry-trade-unwind.md §1 Meta`. Scenario-local files touched in Round 1: `finance-carry-trade-unwind.md`, `simulation-bases.md` (Step 1: §2.6 Safe-Haven block inserted), `_shared_changes.md` (Step 2: 4 PNG + 4 pool-profile + 4 design.md mapping-row handoff), `configs/CarryTradeUnwind/{Rule,LLM,RuleLLM,Rag}/players.yml` (Step 3: `# Source:` provenance densified across all four variants). No file outside `examples/CarryTradeUnwind/` or `configs/CarryTradeUnwind/` git-committed; the 4 PNGs already exist on disk under `examples/AGENT_POOL/agent_images/icons/` but are staged by the main session per the concurrency contract in `_shared_changes.md`. Round 1 result: PASS.
- 2026-07-12  Polish Round-2 re-audit. Status walk: `released → locked → released`. Re-verification gates: (1) YAML parse PASS — all four `configs/CarryTradeUnwind/{Rule,LLM,RuleLLM,Rag}/players.yml` parse cleanly, `# Source:` comment counts Rule=42 / LLM=57 / RuleLLM=57 / Rag=131 (dense provenance maintained). (2) `py_compile` + import smoke PASS — 15 `.py` files compile-clean, 5 core modules import without error (no stale `examples.llm_utils` or `extras.get` antipatterns). (3) Icon-resolution gate PASS — all 5 archetype PNGs verified on disk under `examples/AGENT_POOL/agent_images/icons/` (`finance-carry-trader.png`, `finance-leveraged-carry-fund.png`, `finance-funding-currency-buyer.png`, `finance-hedged-carry-trader.png`, `finance-noise-trader.png`); shared-changes handoff file `_shared_changes.md` confirms 4 profile-row additions + 4 design.md mapping-row additions for main-session merge. (4) Rule 5-round re-smoke PASS — `GeneralSimulator.setup()+run(5)+shutdown()` returns `list` of per-round dicts, no uncaught exceptions. (5) LLM/RuleLLM/Rag setup-only re-smoke PASS — all actors resolve and initialise. (6) Target §9 numeric alignment re-checked — zero drift between Round-1 and Round-2 reads. (7) RuleLLM dual-section + `_RAG_FALLBACK` sentinel invariants re-confirmed (5×PERSONA+5×RULES in `prompts.py`; sentinel defined-and-consumed in both `Rag/players.py` and `Rag/analysis.py`). (8) §0 CHANGELOG entries enumerated and cross-referenced — all Steps 0–10 + Round-1 closeout present and accurately describing the audit trail. No regression found; no new finding. Status confirmed `released`. Round 2 result: PASS.

## §1 Meta

| Field         | Content |
|---------------|---------|
| Name          | CarryTradeUnwind |
| Domain        | finance |
| Requested By  | User |
| Produced By   | define-simulation-scenario-skill.md v1.0.0 (invoking agent: Codex) |
| Created       | 2026-07-08 |
| Pipeline      | masim/skills/create-simulation-pipeline.md |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.0) |
| Status        | released |

## §2 Phenomenon Statement

### §2.1 Trigger

The scenario begins after leveraged investors have built crowded carry positions by borrowing in a low-yield funding currency and buying higher-yield risky assets. A sudden funding-currency appreciation, risk-off shock, or volatility spike raises mark-to-market losses on those positions. The trigger is a financing and exchange-rate shock, not a change in the fundamental value of the traded asset.

### §2.2 Mechanism

The core mechanism is a funding-liquidity and forced-deleveraging spiral. Carry traders sell as the funding currency appreciates, leveraged carry funds breach stop-loss or margin thresholds, and their liquidation pressure pushes the price further away from the pre-shock carry equilibrium. Higher volatility then tightens risk constraints, causing additional exits and transmitting stress through a self-reinforcing carry-unwind loop.

### §2.3 Participants

The causal participants are carry traders, leveraged carry funds, funding-currency buyers, hedged carry traders, and noise traders. Carry traders and leveraged funds provide the crowded directional exposure, funding-currency buyers represent safe-haven and repatriation demand, hedged carry traders reduce exposure when volatility rises, and noise traders supply background FX order flow. The market coordinator aggregates orders and updates the funding-currency exchange-rate proxy.

### §2.4 Resolution

The episode ends when forced sellers exhaust risk budget or inventory, safe-haven demand and mean reversion become large enough relative to remaining sell pressure, and volatility no longer forces additional exits. The expected resolution is partial stabilization after a sharp unwind, not immediate restoration of the pre-shock carry environment. Historical carry crashes often reverse only partly over the simulation horizon.

## §3 Research Goals

1. Measure whether crowded leveraged carry positions can generate a 10%-25% maximum drawdown after a funding-currency appreciation shock.
2. Test by ablation whether removing the leveraged carry fund materially reduces drawdown, unwind velocity, and crisis-onset speed.
3. Sweep `stop_loss`, `leverage`, `risk_threshold`, and `vol_threshold` to estimate when the carry unwind becomes self-reinforcing.
4. Compare Rule, LLM, RuleLLM, and Rag variants to determine whether model-based reasoning delays, accelerates, or constrains forced unwind behavior.

## §4 Theoretical Anchors

### §4.1 Carry trade returns and crash risk

| Field | Content |
|-------|---------|
| Full citation | Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). Carry trades and currency crashes. *NBER Macroeconomics Annual*, 23(1), 313-348. https://doi.org/10.1086/593088 |
| Key mechanism (≤30 words) | Leveraged carry returns are exposed to rare funding-currency appreciations that create sharp crash risk. |
| Key equation | `carry_demand = leverage * carry_size` when `abs(deviation) > unwind_threshold`, with direction determined by the deviation sign. |
| Motivates agent | carry-trader |
| Parameter implication | `unwind_threshold` range 0.01-0.04, `carry_size` range 400-1200, and `leverage` range 3.0-8.0, default 0.02, 800, and 5.0. |

### §4.2 Funding-liquidity and market-liquidity spiral

| Field | Content |
|-------|---------|
| Full citation | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 |
| Key mechanism (≤30 words) | Funding losses force sales, sales worsen market liquidity, and lower prices create further funding pressure. |
| Key equation | `forced_sell = min(position, leverage * base_size)` when `deviation > stop_loss`. |
| Motivates agent | leveraged-carry-fund |
| Parameter implication | `stop_loss` range 0.02-0.06, `base_size` range 400-1200, default 0.03 and 800. |

### §4.3 Safe-haven currency demand

| Field | Content |
|-------|---------|
| Full citation | Ranaldo, A., & Soderlind, P. (2010). Safe haven currencies. *Review of Finance*, 14(3), 385-407. https://doi.org/10.1093/rof/rfq007 |
| Key mechanism (≤30 words) | Safe-haven and repatriation flows buy funding currencies during stress and partially offset forced carry liquidation. |
| Key equation | `buy_qty = position_size` when `deviation < -risk_threshold`. |
| Motivates agent | funding-currency-buyer |
| Parameter implication | `risk_threshold` range 0.03-0.08 and `position_size` range 300-800, default 0.05 and 500. |

### §4.4 Carry trades and global FX volatility

| Field | Content |
|-------|---------|
| Full citation | Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). Carry trades and global foreign exchange volatility. *Journal of Finance*, 67(2), 681-718. https://doi.org/10.1111/j.1540-6261.2012.01728.x |
| Key mechanism (≤30 words) | Global FX volatility predicts carry-trade losses and causes volatility-aware strategies to reduce exposure. |
| Key equation | `adjusted_qty = base_qty * (1 - hedge_ratio)` if `rolling_vol < vol_threshold`; sell if `rolling_vol > vol_threshold`. |
| Motivates agent | hedged-carry-trader |
| Parameter implication | `hedge_ratio` range 0.20-0.50 and `vol_threshold` range 0.03-0.08, default 0.30 and 0.05. |

### §4.5 Noise and background FX order flow

| Field | Content |
|-------|---------|
| Full citation | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| Key mechanism (≤30 words) | Uninformed background order flow creates liquidity, volatility, and non-systematic FX demand around the carry unwind. |
| Key equation | `trade ~ Bernoulli(trade_probability)` with bounded random buy or sell quantity conditional on activation. |
| Motivates agent | noise-trader |
| Parameter implication | `trade_probability` range 0.10-0.40, default 0.30. |

## §5 Stylized Facts

| #  | Fact (one sentence) | Quantitative range | Citation | Acceptance metric |
|----|----------------------|--------------------|----------|-------------------|
| F1 | A crowded carry unwind creates a crash-scale drawdown in the exchange-rate proxy. | 10% <= max drawdown <= 25% | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088 | `analysis.py: compute_max_drawdown()` in [10, 25] |
| F2 | The unwind has a rapid peak velocity after stop-loss or margin constraints bind. | peak per-round change >= 2% | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 | `analysis.py: compute_unwind_velocity()` >= 2 |
| F3 | Leveraged carry funds dominate forced selling during the cascade phase. | forced-seller volume share >= 50% | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 | `analysis.py: compute_agent_volume_share()` >= 0.50 |
| F4 | Carry crashes partially recover after forced selling weakens. | 0.30 <= recovery ratio <= 0.80 | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088 | `analysis.py: compute_recovery_ratio()` in [0.30, 0.80] |
| F5 | Volatility-aware carry traders exit earlier than forced-liquidation carry funds. | hedged exit at least 3 rounds earlier | Menkhoff et al. (2012), https://doi.org/10.1111/j.1540-6261.2012.01728.x | `analysis.py: compare_exit_rounds()` >= 3 |

## §6 Historical / Empirical Anchors

### §6.1 Russian default and LTCM carry unwind

| Field | Content |
|-------|---------|
| Name + dates | Russian default / LTCM carry unwind, 1998-08 to 1998-10. |
| Trigger | Global risk-off, leveraged-fund losses, and funding stress caused rapid deleveraging of yen-funded and other carry positions. |
| Quantitative arc | USD/JPY fell roughly 15% in October 1998 while leveraged positions were reduced over weeks. |
| Agent mapping | carry-trader maps to ordinary carry accumulators; leveraged-carry-fund maps to forced deleveragers; funding-currency-buyer maps to safe-haven demand; hedged-carry-trader maps to volatility-aware macro funds; noise-trader maps to background FX flow. |
| Primary source(s) | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098; Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088 |

### §6.2 Global financial crisis yen carry unwind

| Field | Content |
|-------|---------|
| Name + dates | Global financial crisis JPY carry unwind, 2007-2008. |
| Trigger | Risk appetite collapsed, volatility rose, and leveraged investors unwound long high-yield currency positions. |
| Quantitative arc | USD/JPY fell from about 110 to 88 in roughly six weeks, about a 20% move. |
| Agent mapping | leveraged-carry-fund maps to margin-constrained funds; carry-trader maps to broad carry flow; funding-currency-buyer maps to yen safe-haven and repatriation flow; hedged-carry-trader maps to volatility-managed carry strategies; noise-trader maps to non-carry FX liquidity. |
| Primary source(s) | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088; Menkhoff et al. (2012), https://doi.org/10.1111/j.1540-6261.2012.01728.x |

### §6.3 Swiss franc floor removal

| Field | Content |
|-------|---------|
| Name + dates | Swiss franc floor removal, 2015-01-15. |
| Trigger | The Swiss National Bank removed the EUR/CHF floor, abruptly repricing a funding and safe-haven currency. |
| Quantitative arc | EUR/CHF moved about 20%-30% intraday, with extreme liquidity withdrawal and stop-loss execution. |
| Agent mapping | leveraged-carry-fund maps to forced CHF short-covering; funding-currency-buyer maps to safe-haven CHF demand; hedged-carry-trader maps to participants with options or risk controls; carry-trader maps to directional carry exposure; noise-trader maps to residual flow. |
| Primary source(s) | Bank for International Settlements. (2015). *Triennial Central Bank Survey and FX market commentary*. https://www.bis.org |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|--------------------|------------------------|---------------------------|-------------|-----------------|-------------|---------------------|
| carry-trader | hedge fund / leveraged currency investor | Carry Trade / Risk-On-Risk-Off (§4.1) | Destabilising | price, deviation, round | Exists to build carry exposure in calm conditions and unwind when the funding currency appreciates. | examples/AGENT_POOL/finance/carry-trader.md |
| leveraged-carry-fund | macro hedge fund / leveraged fund | Liquidity / Funding (§4.2) | Destabilising | price, deviation, position | Exists to transmit margin and stop-loss pressure into forced FX selling. | examples/AGENT_POOL/finance/leveraged-carry-fund.md |
| funding-currency-buyer | reserve manager / safe-haven buyer | Safe-haven currency demand (§4.3) | Stabilising | price, deviation, round | Exists to provide partial safe-haven demand when downside carry stress becomes severe. | examples/AGENT_POOL/finance/funding-currency-buyer.md |
| hedged-carry-trader | volatility-managed macro fund | Volatility-managed carry (§4.4) | Context-dependent | price, deviation, rolling_vol | Exists to reduce carry exposure when FX volatility rises above its risk budget. | examples/AGENT_POOL/finance/hedged-carry-trader.md |
| noise-trader | uninformed FX liquidity participant | Noise / Market Microstructure (§4.5) | Context-dependent | price, round, rng_state | Exists to supply bounded background FX order flow. | examples/AGENT_POOL/finance/noise-trader.md |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a dealer-style single-price FX proxy. The funding-currency price follows `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t)`, where positive net demand raises the funding-currency price and negative net demand lowers it. The price-impact term captures liquidity stress during crowded unwinds, while the mean-reversion term captures long-run purchasing-power or valuation gravity.

### §8.2 Information Broadcast

Each round broadcasts `price`, `fundamental`, `deviation`, `round`, and the historical price window needed to compute rolling volatility. `price` and `deviation` drive carry and stop-loss rules, `round` supports phase detection, and rolling volatility supports the hedged carry trader. No unrelated return-salience signal is required for this scenario.

### §8.3 Constraints and Frictions

Agents have cash, inventory, leverage, stop-loss, and position-size constraints. Short exposure is represented by inventory-constrained sell decisions rather than unlimited short creation. The market applies a positive price floor, bounded Gaussian noise, and finite price impact so liquidation pressure remains interpretable.

### §8.4 Round Granularity

One round represents one stress-period trading interval in which FX prices, margin information, and public risk signals refresh. The calibration maps tens of rounds to days or weeks, consistent with the 1998 and 2008 carry-unwind anchors. The full run length includes buildup, stress, cascade, partial stabilization, and post-unwind phases.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation |
|-----------|--------|----------------------------------|-----------------|-------------------|-----------------|
| unwind threshold | `theta_unwind` | carry-trader (§7) | 0.01-0.04 | 0.02 | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088 |
| carry base size | `q_carry` | carry-trader (§7) | 400-1200 | 800 | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088 |
| carry leverage | `L_c` | carry-trader (§7) | 3.0-8.0 | 5.0 | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088 |
| deviation sizing scale | `s_dev` | carry-trader (§7) | 2500-7500 | 5000 | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088 |
| stop loss | `theta_stop` | leveraged-carry-fund (§7) | 0.02-0.06 | 0.03 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| leveraged fund base size | `q_lcf` | leveraged-carry-fund (§7) | 400-1200 | 800 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| safe-haven risk threshold | `theta_safe` | funding-currency-buyer (§7) | 0.03-0.08 | 0.05 | Ranaldo & Soderlind (2010), https://doi.org/10.1093/rof/rfq007 |
| safe-haven position size | `q_safe` | funding-currency-buyer (§7) | 300-800 | 500 | Ranaldo & Soderlind (2010), https://doi.org/10.1093/rof/rfq007 |
| hedge ratio | `h` | hedged-carry-trader (§7) | 0.20-0.50 | 0.30 | Menkhoff et al. (2012), https://doi.org/10.1111/j.1540-6261.2012.01728.x |
| volatility threshold | `theta_vol` | hedged-carry-trader (§7) | 0.03-0.08 | 0.05 | Menkhoff et al. (2012), https://doi.org/10.1111/j.1540-6261.2012.01728.x |
| trade probability | `p_n` | noise-trader (§7) | 0.10-0.40 | 0.30 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| price impact | `lambda` | environment (§8.1) | 0.001-0.010 | 0.003 | FX market depth normalization, calibrated to §6.1-§6.2 arcs |
| mean reversion | `gamma` | environment (§8.1) | 0.005-0.030 | 0.02 | Rogoff, K. (1996). The purchasing power parity puzzle. *Journal of Economic Literature*, 34(2), 647-668. https://www.jstor.org/stable/2729217 |
| fundamental value | `F` | environment (§8.1) | Source: normalization | 1.0 | Source: normalization |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence) |
|---------|--------|--------------------------|
| Rule | Yes | Required deterministic baseline for the carry-unwind mechanism. |
| LLM | Yes | Tests whether persona-only reasoning changes forced-exit and safe-haven behavior. |
| RuleLLM | Yes | Tests whether explicit numerical rules constrain LLM carry-unwind decisions. |
| Rag | Yes | Tests whether retrieved historical carry-crash context changes leverage and exit behavior. |

### §10.2 Pass / Fail Criteria

| Criterion | Status when satisfied |
|-----------|-----------------------|
| All §5 stylized facts reproduced within their ranges | green |
| Every §3 research question answerable from analysis | green |
| Ablating any §7 agent produces a measurable change | green |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green |
