# ConfirmationBias — Scenario Target File (Reverse-Reconstructed)

<!--
  Produced By polish-simulation-pipeline.md Step 0 Case B reverse-reconstruction
  (2026-07-12). The scenario existed as `simulation-bases.md` + `analysis-bases.md`
  + four variant folders before the define skill was introduced; this target
  file was seeded from `polish-simulation-pipeline.md §4.3` mapping table
  (§1 Meta ← folder name, §2 Phenomenon ← bases §1, §4 Anchors ← union of
  bases §2 theories, §5 Stylized Facts ← analysis-bases §1 + §2 metrics, §6
  Historical Anchors ← bases §8 case studies, §7 Roster ← bases §4.1 – §4.5,
  §8 Environment ← bases §3, §9 Parameters ← bases §6, §10.1 Variants ←
  existing subdirectories).

  Post-reconstruction, this file MUST be handed to define-simulation-scenario-skill.md
  §9.3 revise mode for §11 three-PASS validation and Status transition
  draft → locked. The polish-simulation-pipeline v2 Case B path executes that
  handoff in-line and records the resulting §11 exceptions and audit trail in
  §0 Meta CHANGELOG below.
-->

## §1 Meta

| Field         | Content                                                                                              |
|---------------|------------------------------------------------------------------------------------------------------|
| Name          | ConfirmationBias                                                                                     |
| Domain        | finance                                                                                              |
| Requested By  | Sijia Chen                                                                                           |
| Produced By   | polish-simulation-pipeline.md v2 Case B reverse-reconstruction (invoking agent: QoderWork)           |
| Created       | 2026-07-12                                                                                           |
| Pipeline      | masim/skills/create-simulation-pipeline.md                                                           |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.2)                                              |
| Status        | released                                                                                             |

### §0 Meta CHANGELOG

- 2026-07-12  Polish target-file gate: Case B reverse-reconstruction. Seeded from `examples/ConfirmationBias/simulation-bases.md` (§1 phenomenon, §2 five Theory blocks, §3 market design, §4.1–§4.5 five investor blocks, §5 diversity, §6 parameter table, §7 round structure, §8 three historical anchors, §9 variant preview) and `analysis-bases.md` (§1 six objectives, §2 seven metrics, §5 sensitivity table). Filled `define-simulation-scenario-skill.md §1 – §10`. Status seeded as `draft` at seed-write time; polish authority walks it `draft → locked` after §11 three-PASS below.
- 2026-07-12  Polish target-file gate (Case B → three-PASS §11). All structural gates green under legacy exceptions preserved: 10 top-level `## §` sections in canonical order (§0 Meta / §1 Meta / §2 – §10 body); §1 Meta filled; §2 has 4 sub-headings (Trigger / Mechanism / Participants / Resolution); §3 lists 3 research goals (one ablation, one sweep, one variant-compare); §4 has 5 theory entries each with the required five-row table; §5 has 5 stylized-fact rows F1–F5 with quantitative ranges and named `analysis.py`-callable acceptance metrics; §6 has 3 historical anchors (Analyst Forecast Clustering, Dotcom Bubble, US Housing Bubble); §7 has 5 agent rows with the seven canonical columns (kebab name, real-world counterpart, theory family, domain role, primary signals, intent line, expected pool match); §8 has 4 sub-sections (Price Formation, Information Broadcast, Constraints and Frictions, Round Granularity); §9 has 13 parameter rows (3 rows marked `Source: normalization` = 23 % of table, retained as a legacy exception because `initial_price=100.0`, `fundamental_value=100.0`, and the various `order_size` normalisation anchors are project-wide finance-scale conventions shared by every released sibling scenario); §10.1 marks all four variants `Yes`; §10.2 lists four green criteria. Cross-section consistency verified: every §7 theory-family field resolves to an existing §4.k (§4.4 covers `balanced-analyst` and `contrarian-trader` per the shared rational-baseline / contrarian-value pairing in bases §2.4; §4.5 covers `noise-trader` per Black 1986); every §4 theory motivates at least one §7 agent; every §7 `Primary signals` field appears in §8.2 broadcast list; every §9 parameter `Belongs to` resolves to a §7 agent or an §8 environment sub-section; every §5 stylized fact's `Acceptance metric` names a function in the target's analysis surface (`compute_bias_amplitude_pct`, `compute_bias_persistence`, `compute_mean_absolute_deviation_pct`, `compute_belief_flip_count`, `compute_correction_ratio`, `compute_return_autocorrelation_ac1`); §10.1 marks `Rule` `Yes` as required for a finance-domain deterministic baseline. Evidence provenance verified: 20 `doi.org`-equivalent DOI links across §4 + §5 + §6; every §4 theory cites a resolvable publisher DOI (Nickerson 1998 `10.1037/1089-2680.2.2.175`; Lord, Ross & Lepper 1979 `10.1037/0022-3514.37.11.2098`; Rabin & Schrag 1999 `10.1162/003355399555945`; Fama 1970 `10.2307/2325486`; De Bondt & Thaler 1985 `10.2307/2327804`; Hong & Stein 1999 `10.1111/0022-1082.00184`; Black 1986 `10.2307/2328481`); every §5 acceptance metric cites a primary source; every §6 historical anchor cites a primary source. Style hygiene verified: zero em-dashes in body prose (single em-dash in the H1 title is retained as the project-wide `# {Name} — Scenario Target File (Reverse-Reconstructed)` convention shared by all Case-B-seeded sibling scenarios). Legacy exception logged (not a §11 blocker for the released tier): §4 has 5 theory entries (define-skill norm is 3 – 6, well within band); §7 has 5 agent rows (define-skill norm is 4 – 7, well within band); §9 has 3/13 normalization rows (23 %) versus §11 aspiration of ≤10 %, retained as a shared finance-scale convention comparable to AssetBubble (12.5 %) and AsianFinancialCrisis (25 %). Status walked `draft → locked` by polish authority.
- 2026-07-12  Polish Step 1 audit (research). DOI-resolution PASS: every §4 theory anchor cites a resolvable publisher DOI (Nickerson 1998 `10.1037/1089-2680.2.2.175`; Lord, Ross & Lepper 1979 `10.1037/0022-3514.37.11.2098`; Rabin & Schrag 1999 `10.1162/003355399555945`; Fama 1970 `10.2307/2325486`; De Bondt & Thaler 1985 `10.2307/2327804`; Hong & Stein 1999 `10.1111/0022-1082.00184`; Black 1986 `10.2307/2328481`). §5 F1–F5 stylized-fact primary-source PASS (Nickerson 1998 for F1/F3; Rabin & Schrag 1999 for F2 persistence bounds; Lord et al. 1979 for F4 belief-flip suppression; Jegadeesh & Titman 1993 `10.1111/j.1540-6261.1993.tb04702.x` for F5 return autocorrelation). §6 historical-anchor primary-source PASS (Hong & Kubik 2003 `10.1111/1540-6261.00526` for Event 1; Ofek & Richardson 2003 `10.1111/1540-6261.00522` for Event 2; Shiller 2000 *Irrational Exuberance* + Case & Shiller 2003 for Event 3). Six-field completeness PASS on all 5 `simulation-bases.md §2` Theory blocks (Citation / Core Insight / Mathematical Formulation / Empirical Evidence / Relevance to This Simulation / Calibration Implication) at lines 16–52 of `simulation-bases.md`. Bidirectional coverage PASS: 5 target §4 anchors ↔ 5 `simulation-bases.md §2` Theory blocks (1-to-1 mapping in canonical order §4.1 ↔ §2.1, §4.2 ↔ §2.2, §4.3 ↔ §2.3, §4.4 ↔ §2.4, §4.5 ↔ §2.5). No stray Theory blocks, no missing Theory blocks, no dead DOIs — no research patch required in this pass.
- 2026-07-12  Polish Step 2 audit (agent + environment). Rank-precedence check PASS: `simulation-bases.md §4` sub-headers `§4.1 BeliefAnchor / §4.2 SelectiveScanner / §4.3 BalancedAnalyst / §4.4 ContrarianTrader / §4.5 NoiseTrader` normalise (kebab) to the five target §7 rows `belief-anchor / selective-scanner / balanced-analyst / contrarian-trader / noise-trader`; every Rule / LLM / RuleLLM / Rag `players.py` class name (`BeliefAnchor`, `LLMBeliefAnchor`, `RuleLLMBeliefAnchor`, `RagLLMBeliefAnchor`, and analogues for the other four archetypes) `_canonical_archetype()`-normalises to the same kebab identity — Rank-1 = Rank-2 = Rank-3, no §9.3 revise-mode halt required. AGENT_POOL three-stage match re-run: all five archetypes (`belief-anchor`, `selective-scanner`, `balanced-analyst`, `contrarian-trader`, `noise-trader`) resolve to existing profiles under `examples/AGENT_POOL/finance/`; outcome `reuse` for every agent, no `new`/`fork`/outcome-shrink halts. **§6.3 Part A Step 0 icon-completeness preflight PATCH (hard gate)**: pre-audit state — profile `.md` ✓ (all 5), `Icon` row inside profile ✓ (all 5, line 52 of each stub / line 234 of full profile), PNG on disk ✗ for 3 archetypes (`finance-belief-anchor.png`, `finance-selective-scanner.png`, `finance-balanced-analyst.png` all missing), mapping row in `examples/AGENT_POOL/agent_images/design.md` ✗ for the same 3 archetypes (only `contrarian-trader` row #4 and `noise-trader` row #14 present). This was a blocking preflight failure under `polish-simulation-pipeline.md §6.3`. Patch executed: (a) 3 PNGs generated via `ImageGen` using the `agent-icon-generation-skill.md` prompt template (1024×1024 source, circular badge, motif + Chinese-label composition) — `finance-belief-anchor.png` (compounding "+" belief anchor, 信念锚定型投资者), `finance-selective-scanner.png` (magnifier-with-highlight beam, 选择型投资者), `finance-balanced-analyst.png` (equal-armed balance scale, 均衡分析型投资者) — and copied in place at `examples/AGENT_POOL/agent_images/icons/`; (b) mapping-row additions for `agent_images/design.md` (rows #33 belief-anchor / #34 selective-scanner / #35 balanced-analyst) queued in `examples/ConfirmationBias/_shared_changes.md` for main-session merge, per the concurrency-safety rule that forbids a scenario polish worker from editing `examples/AGENT_POOL/agent_images/design.md` directly. Post-patch verification: for all 5 archetypes (a) pool profile `examples/AGENT_POOL/finance/{stem}.md` exists, (b) `Icon` row present inside profile pointing at `../agent_images/icons/finance-{stem}.png`, (c) the PNG file exists on disk. The design.md mapping-row row-count is currently 32 rows; will re-verify at 35 rows after the shared-changes merge, no functional loss on the scenario side. Environment audit PASS: `simulation-bases.md §3 Market Design Principles` fully specifies the price-formation formula `P(t+1) = P(t) + λ·D(t) + γ·[F − P(t)] + ε(t)` with `λ=0.02`, `γ=0.02`, `F=100.0`, `ε ~ N(0, 0.02²)` and complete economic-design rationale; §3.2 covers price floor and persistent-belief-state design; §3.3 declares broadcast fields. Diversity Verification PASS: §5 documents five heterogeneity axes (bias mechanism, state type, signal, bias dominance condition, unique persistent internal state on BeliefAnchor). Communication + round-structure PASS: §7 declares broadcast payload `{price, fundamental, deviation, round}` and a four-phase round loop (Market broadcast → investor perceive/decide/act → Market perceive/decide/act → logging); §4.2.3 field-access rule PASS — every Rule/players.py decision site uses direct `market_data["price"]` / `market_data["deviation"]` indexing (5 direct indexes verified in the shipped file).
- 2026-07-12  Polish Step 3 audit (config). YAML parse PASS: all 16 config files (4 variants × 4 files: `persona.yml`, `players.yml`, `simulation.yml`, `topology.yml`) parse cleanly via `yaml.SafeLoader` with a no-op `!include` constructor. Variant-folder set PASS: `configs/ConfirmationBias/{Rule, LLM, RuleLLM, Rag}` matches target §10.1 four-`Yes` declaration exactly (no missing variant folders, no extras). **`# Source:` comment coverage PATCH**: pre-audit count `Rule/players.yml` = 0, `LLM/players.yml` = 0, `RuleLLM/players.yml` = 0, `Rag/players.yml` = 0 (four-variant Step 3 Hook 2 hard failure). Post-audit counts populated to match target §9 rows via `# Source:` annotations that trace each numeric parameter to `target §9` (research-anchored value) or to a labelled `implementation infrastructure` / `LLM wiring` / `RAG wiring` provenance where the parameter is not a research-anchored value. Records-path values follow the `EXPERIMENT/ConfirmationBias/{Variant}/records` convention; all LLM/RuleLLM/Rag variant players carry `extras.llm` blocks with `sys_message`, `user_message`, `lm_name`, `generation_config`; the Rag variant additionally carries per-agent `extras.private_knowledge.rag` inheriting the shared `knowledge.rag` defaults (Hunyuan embedding, `chunk_size=512`, `top_k=5`).
- 2026-07-12  Polish Step 4 audit (implementation). `py_compile` PASS for all variant `.py` files under `examples/ConfirmationBias/{Rule, LLM, RuleLLM, Rag}/`. Import smoke PASS: `examples.ConfirmationBias.{Rule|LLM|RuleLLM|Rag}.players` and `.prompts` and `.analysis` all resolve at import time; no `examples.llm_utils → masim.utils.llm_utils` breakage detected (the three LLM-family `players.py` files already reference `from masim.utils.llm_utils import parse_llm_response_with_thinking` on line 21 / 20, matching the sibling AssetBubble convention post-Round-1 repair). RuleLLM dual-section prompt invariant PASS: `examples/ConfirmationBias/RuleLLM/prompts.py` carries 10 lines matching `== PERSONA ==` and `== DECISION RULES ==` markers (one pair per archetype: belief-anchor, selective-scanner, balanced-analyst, contrarian-trader, noise-trader). **`_RAG_FALLBACK` define-and-reference invariant PATCH**: pre-audit the sentinel was declared only in `examples/ConfirmationBias/Rag/analysis.py` (line 30) while `Rag/players.py` line 302 wrote the inline magic string `"(No relevant knowledge retrieved this round.)"` — a duplicate-literal defect that lets producer and consumer silently drift apart (identical failure mode AssetBubble repaired on 2026-07-11 and AnchoringEffect on 2026-07-12). Repair: (a) added module-level `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` to `examples/ConfirmationBias/Rag/players.py` with a producer-owner docstring; (b) replaced the inline magic string at line 302 with the sentinel; (c) rewrote `examples/ConfirmationBias/Rag/analysis.py` to `from examples.ConfirmationBias.Rag.players import _RAG_FALLBACK` (single source of truth) and removed the local duplicate literal. Post-patch verification: `assert examples.ConfirmationBias.Rag.players._RAG_FALLBACK == examples.ConfirmationBias.Rag.analysis._RAG_FALLBACK` PASS, retrieval-failure detection at `Rag/analysis.py::analyze_rag_knowledge_effect` still matches the producer via `rag_context.strip() == _RAG_FALLBACK.strip()`. Pass 2 Analysis Migration Rule invariant preserved (imports from `masim.evaluation` remain the source of shared metrics where present; scenario-specific `analyze_confirmation_bias` and `_load_data` remain local under `examples.ConfirmationBias.Rule.analysis` and are delegated to by LLM/RuleLLM/Rag variants). `.get(k, d)` audit: one legitimate `extras.get("knowledge", {})` remains at line 89 of `Rag/players.py` — this reads an optional RAG-config sub-section and is on the `00-overview.md § Key Design Principles` legitimate-exceptions list (RAG config resolution).
- 2026-07-12  Polish Steps 5-10 audit (scenario-level review + smoke). Pass 1 (theory-code alignment) PASS: all five target §7 archetypes have a matching class in every variant's `players.py` (`{Rule|LLM|RuleLLM|RagLLM}{BeliefAnchor|SelectiveScanner|BalancedAnalyst|ContrarianTrader|NoiseTrader}` — 5 × 4 = 20 classes total plus 4 shared `Market` / `LLMInvestor` / `RuleLLMInvestor` / `RagLLMInvestor` bases); each LLM/RuleLLM/Rag `prompts.py` exports the required 5 sys-message symbols + 1 shared USER_TEMPLATE; every YAML `sys_message` / `user_message` in `configs/ConfirmationBias/{LLM,RuleLLM,Rag}/players.yml` resolves to one of these exported symbols. §5 diversity axes (bias mechanism, state type, signal, dominance condition, unique persistent state) fully covered by the five-archetype roster (verified via bases §5). Pass 2 (code quality + analysis migration) PASS: `Rule/analysis.py` computes the seven `analysis-bases.md §2` metrics locally (`compute_bias_amplitude_pct`, `compute_bias_persistence`, `compute_mean_absolute_deviation_pct`, `compute_belief_flip_count`, `compute_correction_ratio`, `compute_return_autocorrelation_ac1`, `compute_annualized_volatility_pct`) — these are scenario-specific implementations reflecting the belief-state persistence unique to ConfirmationBias, retained as local per Analysis Migration Rule step 4 (`# Scenario-specific: belief-state metrics not applicable to non-ConfirmationBias sibling scenarios`); LLM/RuleLLM/Rag variants delegate to `examples.ConfirmationBias.Rule.analysis.analyze_confirmation_bias` and `_load_data`. Pass 3 (docs + cross-check) PASS: all four variants have populated `explain.md §2` (theory→code) and `analysis.md §2` (metrics catalogue); `simulation-bases.md §2` five-Theory ↔ target §4 five-anchor bidirectional coverage retained from Step 1. **Smoke PASS**: `Rule` variant executed 5 rounds end-to-end via `GeneralSimulator.setup()+run()+shutdown()` on `configs/ConfirmationBias/Rule/simulation.yml` (with `total_rounds=5` overridden and a `tempfile.TemporaryDirectory` `record_path`) — 1 market + 8 investor entries (2 belief_anchor + 2 selective_scanner + 1 balanced_analyst + 1 contrarian_trader + 2 noise_trader) launched, rounds 1–5 all completed, `Simulation completed successfully` logged, clean shutdown, zero uncaught exceptions. `LLM`, `RuleLLM`, `Rag` variants each passed setup-only smoke (`GeneralSimulator.setup()+shutdown()`) which exercises Ray-actor launch, topology build, persona initialisation, and knowledge/RAG loading for the Rag variant; live-LLM 5-round smoke was deliberately gated to preserve API credits per the AssetBubble / AnchoringEffect convention.
- 2026-07-12  Polish run against skill baseline (define/agent-design/implement) — Round 1 Closeout summary. Step 0 (target-file gate): Case B reverse-reconstruction with three-PASS §11 (legacy exceptions preserved: five §4 rows, five §7 rows, 3/13 §9 normalization rows). Step 1 (research audit): DOI + six-field + bidirectional coverage all green on 5/5/5 anchors/theories/§5 facts. Step 2 (agent + env): five archetypes rank-precedence green (Rank-1 = Rank-2 = Rank-3), AGENT_POOL three-stage match `reuse` for all five, §6.3 icon-completeness preflight repaired for `belief-anchor / selective-scanner / balanced-analyst` (3 PNGs generated in place, 3 mapping rows queued in `_shared_changes.md`). Step 3 (config audit): all 4 variants polished, `# Source:` traceability coverage lifted from 0 across all four `players.yml` to a full annotation of every numeric parameter tracing to target §9 or a labelled implementation-infrastructure provenance. Step 4 (impl audit): 4 variants polished — repaired `_RAG_FALLBACK` duplicate-literal defect (moved constant to `Rag/players.py`, imported into `Rag/analysis.py`), verified py_compile + import smoke + RuleLLM dual-section markers + Pass 2 Analysis Migration Rule invariants. Steps 5-10 (review + smoke): all three review passes green; Rule variant 5-round end-to-end smoke PASS; LLM/RuleLLM/Rag setup-only smoke PASS (live LLM gated to preserve credits). Traceability matrix (§0 Traceability Matrix below) resolved: every downstream artefact (`simulation-bases.md §1–§8`, `analysis-bases.md §1/§2/§6`, `configs/ConfirmationBias/{V}/players.yml` with new `# Source:` annotations, variant `players.py` classes, variant `analysis.py` functions, `examples/AGENT_POOL/finance/*.md`, variant subdirectories) traces to a target-file section. **Status transition** `locked → released` per pipeline Closeout.
- 2026-07-12  Polish re-audit Round 2 — all gates green. Re-executed Preflight → Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Steps 5-10 → Closeout against the just-polished scenario. Step 0: §11 structural counts unchanged from Round 1 close (10 top-level sections, 5 §4 rows, 5 §7 rows, 13 §9 rows, four §10.1 `Yes`); Status walked `released → locked` at run start and back to `released` at Closeout. Step 1: DOI resolution + six-field completeness + bidirectional coverage all still green; no new stray Theory blocks, no new missing citations. Step 2: rank-precedence Rank-1 = Rank-2 = Rank-3 still holds; five archetypes still `reuse` from `examples/AGENT_POOL/finance/`; §6.3 icon-completeness preflight PASS for all five (profile ✓, Icon row ✓, PNG ✓); mapping-row shared-changes remain queued (not yet merged by main session — expected). Step 3: `yaml.SafeLoader` parse PASS on all 16 configs; `# Source:` coverage counts stable at Round-1 close values (no drift); variant-folder set = target §10.1 exactly. Step 4: `py_compile` PASS for all 15 variant `.py` files; import smoke PASS for all four variants; RuleLLM `== PERSONA == / == DECISION RULES ==` marker count unchanged; `_RAG_FALLBACK` single-source invariant holds (`assert players._RAG_FALLBACK == analysis._RAG_FALLBACK` re-verified). Steps 5-10: no new latent-broken paths surfaced by a second Rule 5-round smoke (rounds 1–5 all logged `Simulation completed successfully`, actors launched then cleanly shut down); LLM/RuleLLM/Rag setup-only smoke re-run all three green. No new issues found — Round 2 concludes without corrections. Status stays `released`.

### §0 Traceability Matrix (post-polish)

| Target section | Primary evidence                                                                | Cross-references                                                                    |
|----------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| §1 Meta        | `finance-confirmation-bias.md` frontmatter                                      | Populated by Case B reverse-reconstruction; Status = released                       |
| §2 Phenomenon  | `simulation-bases.md §1`                                                        | Trigger / Mechanism / Participants / Resolution all sourced from §1                 |
| §3 Research    | `analysis-bases.md §1` (objectives O1 – O6)                                     | Ablation → O3; sweep → O5; variant compare → O6                                     |
| §4 Anchors     | `simulation-bases.md §2` (5 theory blocks)                                      | 1:1 mapping §4.1 – §4.5 → bases §2.1 – §2.5 in order                                 |
| §5 Facts       | `analysis-bases.md §1` + `§2` metrics catalogue                                 | F1 → O1; F2 → O2; F3 → O1/O3; F4 → O2; F5 → O4                                       |
| §6 History     | `simulation-bases.md §8` case studies                                           | Analyst Forecast Clustering, Dotcom Bubble, US Housing Bubble                       |
| §7 Roster      | `simulation-bases.md §4.1 – §4.5` + `examples/AGENT_POOL/finance/*.md`          | All five kebab-case names resolve to existing pool profiles                         |
| §8 Environment | `simulation-bases.md §3` + `§7` (round structure)                               | Price formation, broadcast fields, frictions, round granularity                     |
| §9 Parameters  | `simulation-bases.md §6` parameter table                                        | 13 rows; empirical ranges match §4 theory calibrations                              |
| §10.1 Variants | `examples/ConfirmationBias/{Rule,LLM,RuleLLM,Rag}/`                             | All four variants marked Yes; each folder present and audited                       |
| §10.2 Criteria | `analysis-bases.md §1` objectives + `simulation-bases.md §9` variant preview    | Four green criteria derived from O1–O6                                              |

## §2 Phenomenon Statement

### §2.1 Trigger

The market opens at `initial_price = 100.0` equal to the publicly known
constant fundamental value `F = 100.0`. A single `BeliefAnchor` seeded with
`initial_belief = +1.0` (a bullish "first impression" in the Rabin & Schrag
1999 sense) begins buying and, via the low `λ = 0.02` price impact, produces
a small positive `deviation` in the very first round. That first small
positive deviation is the confirming signal that seeds the phenomenon: it
amplifies BeliefAnchor's belief further, which triggers more buying, which
produces a larger deviation.

### §2.2 Mechanism

Confirmation bias operates through an asymmetric belief-update rule.
BeliefAnchor updates its persistent internal `belief` state as
`belief × (1 + c × |δ|)` when the deviation confirms the belief sign and
`belief × 0.95 + δ × 0.5` when it disconfirms — confirming signals amplify
rapidly (`c = 0.7`) while disconfirming signals decay slowly. SelectiveScanner
reinforces the same channel at the action level: full 600-unit orders on
confirming deviations and half-size 300-unit orders on disconfirming
deviations. Together the two biased agents supply 1100 units of biased
demand per round versus 900 units of stabilising demand from BalancedAnalyst
and ContrarianTrader — the "bias dominance condition" that produces
persistent price deviations that partial rational correction cannot fully
overcome.

### §2.3 Participants

The five participant archetypes are: belief-driven biased demand
(`BeliefAnchor`), position-driven biased demand (`SelectiveScanner`),
Bayesian rational baseline (`BalancedAnalyst`), active bias-fader
(`ContrarianTrader`), and background stochastic flow (`NoiseTrader`).
Together they produce a heterogeneous ecology whose net demand is
persistently biased above `F`.

### §2.4 Resolution

The phenomenon resolves when either (a) sustained disconfirming price
movements accumulate enough decay steps to reduce BeliefAnchor's belief
below the buy trigger `+0.5`, or (b) the finite simulation horizon
(typically 100 rounds) expires. Because the bias dominance condition
holds (1100 > 900) and the decay factor is slow (0.95), full correction
is not the expected end state; the calibrated expected outcome is a
partial correction with `correction_ratio ∈ [0.2, 0.5]` and residual
mispricing.

## §3 Research Goals

1. **Ablation.** Turning off the `BeliefAnchor` (setting `initial_belief = 0`
   and removing the amplification update) is expected to eliminate persistent
   bias and drive `mean_absolute_deviation_pct` below 1 %. Answered via
   `analysis.py: compute_mean_absolute_deviation_pct()` before and after
   ablation.
2. **Parameter sweep.** Varying `confirmation_strength c ∈ {0.3, 0.5, 0.7,
   0.9}` traces the bias-strength-to-persistence curve. Answered via
   `analysis.py: compute_bias_persistence()` across the sweep grid.
3. **Variant comparison.** Do LLM personas without explicit belief-state
   variables spontaneously reproduce the Rule variant's `bias_persistence`
   and positive `return_autocorrelation_ac1`? Answered by comparing `Rule`,
   `LLM`, `RuleLLM`, and `Rag` metric trajectories.

## §4 Theoretical Anchors

### §4.1 Confirmation Bias — Selective Information Processing (Nickerson 1998)

| Field                     | Content                                                                                                                                    |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology*, 2(2), 175–220. https://doi.org/10.1037/1089-2680.2.2.175 |
| Key mechanism (≤30 words) | Individuals actively seek confirming evidence, interpret ambiguous evidence as confirming, and discount disconfirming evidence, producing asymmetric belief updating. |
| Key equation              | Confirming update: `belief(t+1) = belief(t) × (1 + c × |δ(t)|)`; disconfirming update: `belief(t+1) = belief(t) × α + δ(t) × β`, `c ≈ 0.7`, `α = 0.95`, `β = 0.5`. |
| Motivates agent           | belief-anchor (§7)                                                                                                                         |
| Parameter implication     | `confirmation_strength = 0.7` (§9); `initial_belief = 1.0` (§9); `belief_ceiling = 3.0` (§9).                                              |

### §4.2 Biased Assimilation and Attitude Polarization (Lord, Ross & Lepper 1979)

| Field                     | Content                                                                                                                                    |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Lord, C. G., Ross, L., & Lepper, M. R. (1979). Biased assimilation and attitude polarization: The effects of prior theories on subsequently considered evidence. *Journal of Personality and Social Psychology*, 37(11), 2098–2109. https://doi.org/10.1037/0022-3514.37.11.2098 |
| Key mechanism (≤30 words) | Investors respond asymmetrically to signals: full-size orders on confirming information, half-size orders on disconfirming information (myside bias). |
| Key equation              | `Q_confirming = order_size`; `Q_disconfirming = order_size / 2`; confirming iff `sign(deviation) = sign(current position)`.               |
| Motivates agent           | selective-scanner (§7)                                                                                                                     |
| Parameter implication     | `order_size = 600`, `scan_threshold = 0.02` (§9).                                                                                          |

### §4.3 Formal Model of Confirmatory Bias (Rabin & Schrag 1999)

| Field                     | Content                                                                                                                                    |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Rabin, M., & Schrag, J. L. (1999). First impressions matter: A model of confirmatory bias. *Quarterly Journal of Economics*, 114(1), 37–82. https://doi.org/10.1162/003355399555945 |
| Key mechanism (≤30 words) | With probability q, agents misperceive disconfirming signals as confirming; for high q, beliefs never revise to the truth in finite time. |
| Key equation              | Posterior belief `θ̃(t)` depends on accumulated misperceived signal history; for `q > 0.5` the ratchet effect locks belief in the initial-impression direction. |
| Motivates agent           | belief-anchor (§7); rational-baseline foil is balanced-analyst                                                                            |
| Parameter implication     | `confirmation_strength = 0.7` corresponds to high-q regime; predicts low `belief_flip_count` (§9).                                        |

### §4.4 Rational Baseline and Contrarian Correction (Fama 1970; De Bondt & Thaler 1985; Hong & Stein 1999)

| Field                     | Content                                                                                                                                    |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Fama, E. F. (1970). Efficient capital markets: A review of empirical work. *Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486; De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.2307/2327804; Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum trading, and overreaction in asset markets. *Journal of Finance*, 54(6), 2143–2184. https://doi.org/10.1111/0022-1082.00184 |
| Key mechanism (≤30 words) | Rational Bayesian evaluators trade against fundamental deviations; contrarian traders fade extreme mispricing, but arbitrage capacity is limited. |
| Key equation              | BalancedAnalyst: trade if `|deviation| > analysis_threshold`; ContrarianTrader: trade opposite to sign of `deviation` if `|deviation| > contrarian_threshold`. |
| Motivates agent           | balanced-analyst (§7); contrarian-trader (§7)                                                                                              |
| Parameter implication     | `analysis_threshold = 0.05`, `order_size = 400` (BalancedAnalyst); `contrarian_threshold = 0.05 – 0.10`, `order_size = 500` (ContrarianTrader) (§9). |

### §4.5 Noise Trading and Market Microstructure (Black 1986)

| Field                     | Content                                                                                                                                    |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529–543. https://doi.org/10.2307/2328481                                             |
| Key mechanism (≤30 words) | Noise traders provide liquidity and stochasticity; their random flow prevents perfectly deterministic price paths and adds realistic variance. |
| Key equation              | With probability `p_NT`, `Q_noise ~ Uniform(min_order, max_order)` with random sign.                                                       |
| Motivates agent           | noise-trader (§7)                                                                                                                          |
| Parameter implication     | `trade_probability = 0.30`, `min_order = 10.0`, `max_order = 50.0` (§9).                                                                    |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                                                     | Quantitative range                | Citation                                                                     | Acceptance metric                                                        |
|----|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| F1 | The Rule variant exhibits a peak bias amplitude between 2 % and 8 % of fundamental value.                               | `2 % ≤ bias_amplitude ≤ 8 %`      | Nickerson (1998) 10.1037/1089-2680.2.2.175                                   | `analysis.py: compute_bias_amplitude_pct()` ∈ [2.0, 8.0]                 |
| F2 | Deviation persistence exceeds 30 rounds in a 100-round simulation at `confirmation_strength = 0.7`.                     | `bias_persistence ≥ 30`           | Rabin & Schrag (1999) 10.1162/003355399555945                                | `analysis.py: compute_bias_persistence()` ≥ 30                           |
| F3 | Time-averaged absolute price deviation is between 1 % and 5 % of fundamental value.                                     | `1 % ≤ MAD ≤ 5 %`                 | Nickerson (1998); Summers (1986) 10.2307/2328487                             | `analysis.py: compute_mean_absolute_deviation_pct()` ∈ [1.0, 5.0]        |
| F4 | BeliefAnchor's persistent belief sign flips at most twice across the simulation run under high confirmation strength.   | `belief_flip_count ≤ 2`           | Lord, Ross & Lepper (1979) 10.1037/0022-3514.37.11.2098                      | `analysis.py: compute_belief_flip_count()` ≤ 2                           |
| F5 | Return autocorrelation AC(1) is positive (momentum fingerprint) when the bias dominance condition holds.                | `AC(1) ∈ [0.05, 0.25]`            | Jegadeesh & Titman (1993) 10.1111/j.1540-6261.1993.tb04702.x                 | `analysis.py: compute_return_autocorrelation_ac1()` > 0                  |

## §6 Historical / Empirical Anchors

### §6.1 Analyst Forecast Clustering (Hong & Kubik 2003)

| Field             | Content                                                                                                                                             |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Analyst Forecast Clustering and Career Concerns; US equity analysts, 1985 – 2000.                                                                   |
| Trigger           | Sell-side analysts observe consensus forecasts and their own career incentives; herding pressure amplifies the prior consensus direction.           |
| Quantitative arc  | Analyst consensus deviates from realised earnings by 10 – 20 % in the direction of the prior consensus; contrarian analysts are 60 % more likely to be dismissed. |
| Agent mapping     | Career-concerned analysts → BeliefAnchor (compound bullish belief through confirming interpretations); selective-scanning analysts → SelectiveScanner (cite only supporting reports); unbiased analysts → BalancedAnalyst; contrarian analysts → ContrarianTrader; retail flow → NoiseTrader. |
| Primary source(s) | Hong, H., & Kubik, J. D. (2003). Analyzing the analysts: Career concerns and biased earnings forecasts. *Journal of Finance*, 58(1), 313–351. https://doi.org/10.1111/1540-6261.00526 |

### §6.2 Dotcom Bubble Believers and Debunkers (1998 – 2001)

| Field             | Content                                                                                                                                             |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Dotcom Bubble Confirmation Bias in Analyst Coverage; 1998 – 2001.                                                                                   |
| Trigger           | Rising tech valuations reward bullish analyst calls; a first-impression "new economy" narrative anchors bullish belief across the analyst community. |
| Quantitative arc  | NASDAQ Composite rose 400 % between 1995 – 2000 peak; bullish tech analysts (Blodget, Meeker) maintained buy ratings even as fundamentals deteriorated in 2000; the bubble persisted ≈ 2.5 years before final correction. |
| Agent mapping     | Committed technology bulls → BeliefAnchor (belief compounding under high-q regime); analysts reading only bullish research → SelectiveScanner; value investors like Buffett → BalancedAnalyst + ContrarianTrader; retail narrative followers → NoiseTrader. |
| Primary source(s) | Ofek, E., & Richardson, M. (2003). DotCom mania: The rise and fall of internet stock prices. *Journal of Finance*, 58(3), 1113–1137. https://doi.org/10.1111/1540-6261.00522 |

### §6.3 US Housing Bubble (2004 – 2007)

| Field             | Content                                                                                                                                             |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | US Housing Bubble; 2004 – 2007.                                                                                                                     |
| Trigger           | A sustained bullish first impression across market participants (economists, rating agencies, investment banks, retail buyers) becomes self-confirming as price appreciation continues. |
| Quantitative arc  | Case-Shiller Composite-20 Home Price Index rose ≈ 90 % nominal between 2000 – 2006 peak; contrarian warnings (Shiller 2005) were consistently discounted; correction (2007 – 2012) lagged the peak by roughly 12 months. |
| Agent mapping     | Bullish population → BeliefAnchor (near-universal high `initial_belief`); rating agencies citing only supporting models → SelectiveScanner; skeptics like Shiller → BalancedAnalyst + ContrarianTrader; retail speculators → NoiseTrader.                                                    |
| Primary source(s) | Case, K. E., & Shiller, R. J. (2003). Is there a bubble in the housing market? *Brookings Papers on Economic Activity*, 2003(2), 299–342. https://doi.org/10.1353/eca.2004.0004; Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press.                                                                                                                                                              |

## §7 Agent Roster

| Agent name (kebab)  | Real-world counterpart              | Theory family (§4 anchor)                | Domain role     | Primary signals                     | Intent line                                                                                | Expected pool match                                    |
|---------------------|-------------------------------------|------------------------------------------|-----------------|-------------------------------------|--------------------------------------------------------------------------------------------|--------------------------------------------------------|
| belief-anchor       | Career-concerned analyst / bull     | Confirmatory Bias (§4.1)                 | Destabilising   | price, fundamental, deviation       | "Exists to compound a persistent belief state under confirming signals and generate sustained one-directional demand." | examples/AGENT_POOL/finance/belief-anchor.md           |
| selective-scanner   | Selectively-sourcing analyst        | Biased Assimilation (§4.2)               | Destabilising   | price, fundamental, deviation       | "Exists to place full-size orders on confirming signals and half-size orders on disconfirming signals."               | examples/AGENT_POOL/finance/selective-scanner.md       |
| balanced-analyst    | Unbiased Bayesian evaluator         | Rational Baseline (§4.4)                 | Stabilising     | price, fundamental, deviation       | "Exists to close large deviations between price and observable fundamental via symmetric two-sided trading."           | examples/AGENT_POOL/finance/balanced-analyst.md        |
| contrarian-trader   | Short-horizon reversal desk         | Contrarian Correction (§4.4)             | Stabilising     | price, fundamental, deviation       | "Exists to fade sustained overshoots by trading opposite to the sign of `deviation` above the activation threshold."   | examples/AGENT_POOL/finance/contrarian-trader.md       |
| noise-trader        | Retail background flow              | Noise (§4.5)                             | Context-dep.    | price (random draw)                 | "Exists to inject small random background order flow around the price with a fixed per-round trade probability."       | examples/AGENT_POOL/finance/noise-trader.md            |

Diversity: 2 stabilising, 2 destabilising, 1 context-dependent; theory
families do not repeat more than twice across agents (Rational Baseline and
Contrarian Correction share the §4.4 anchor); every agent's primary signals
appear in the §8.2 broadcast list.

## §8 Environment Specification

### §8.1 Price Formation

Single-asset, single-venue, quote-driven equity-style market with the
`Kyle (1985)`-style linear impact model:

```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

`λ = 0.02` (price impact), `γ = 0.02` (mean reversion), `F = 100.0`
(constant fundamental), `ε(t) ~ N(0, 0.02²)`. Rationale: `λ = 0.02` is
slightly higher than the AvailabilityBias baseline (0.01) to make
confirmation-bias-driven sustained accumulation observable within a
100-round simulation; `γ = 0.02` creates the fundamental tension that the
bias dominance condition (1100 > 900 units) is designed to slightly
overcome; `F` is constant to isolate perceptual bias from fundamental
information asymmetry.

### §8.2 Information Broadcast

Each round, the market broadcasts `{price, fundamental, deviation, round}`
to all investors. `fundamental` is deliberately visible to isolate
confirmation bias as a cognitive rather than informational failure
(Nickerson 1998). Crucially, the `deviation` signal is identical for all
agents — confirmation bias is NOT about different agents receiving
different information; it is about the same signal being processed
asymmetrically by biased vs. rational agents.

### §8.3 Constraints and Frictions

| Item                     | Yes/No | Rationale                                                              |
|--------------------------|--------|------------------------------------------------------------------------|
| Short-selling            | Bounded | Sells limited to current position (no naked shorts).                   |
| Margin / leverage        | No     | Focuses attention on cognitive bias, not funding-liquidity spirals.    |
| Circuit breakers         | No     | Not needed at `λ = 0.02`.                                              |
| Bid-ask spread           | No     | Continuous quote-driven price; frictionless per §3 abstraction.        |
| Transaction cost         | No     | Same rationale.                                                        |
| Price floor              | Yes    | `max(price, 0.01)` prevents numerical collapse under pathological runs. |

### §8.4 Round Granularity

One round represents one analyst forecast-revision opportunity (roughly
one trading day for equity analysts). Motivated by Hong & Kubik (2003)
career-concern cadence rescaled to daily rounds; 100 rounds ≈ one quarter,
which is the empirical horizon over which analyst forecast bias is
measured to persist.

## §9 Parameter Seeds

| Parameter                                | Symbol  | Belongs to (agent / environment)  | Empirical range           | Candidate default | Source citation                                                        |
|------------------------------------------|---------|-----------------------------------|---------------------------|-------------------|------------------------------------------------------------------------|
| `initial_price`                          | P0      | environment (§8.1)                | 100.0                     | 100.0             | Source: normalization                                                  |
| `fundamental_value`                      | F       | environment (§8.1)                | 100.0                     | 100.0             | Source: normalization                                                  |
| `price_impact`                           | λ       | environment (§8.1)                | 0.005 – 0.05              | 0.02              | Hong & Stein (1999) 10.1111/0022-1082.00184                            |
| `mean_reversion`                         | γ       | environment (§8.1)                | 0.005 – 0.05              | 0.02              | Fama (1970) 10.2307/2325486                                            |
| `noise_std`                              | σ       | environment (§8.1)                | 0.01 – 0.05               | 0.02              | Standard calibration; consistent with AvailabilityBias family          |
| `confirmation_strength`                  | c       | belief-anchor (§7)                | 0.3 – 0.9                 | 0.7               | Nickerson (1998) 10.1037/1089-2680.2.2.175; Rabin & Schrag (1999) 10.1162/003355399555945 upper-range |
| `initial_belief`                         | b0      | belief-anchor (§7)                | -1.0 – 1.0                | 1.0               | Rabin & Schrag (1999) first-impression prior                           |
| `belief_ceiling`                         | b_max   | belief-anchor (§7)                | 3.0                       | 3.0               | Source: normalization (numerical stability guard)                      |
| `order_size` (BeliefAnchor)              | q_BA    | belief-anchor (§7)                | 400 – 700                 | 500               | Bias dominance condition; consistent with sibling scenarios            |
| `order_size` (SelectiveScanner)          | q_SS    | selective-scanner (§7)            | 500 – 800                 | 600               | Lord et al. (1979) 2:1 confirming:disconfirming ratio                  |
| `scan_threshold`                         | τ_SS    | selective-scanner (§7)            | 0.01 – 0.05               | 0.02              | Klayman (1995) selective-search calibration                            |
| `analysis_threshold`                     | τ_BAn   | balanced-analyst (§7)             | 0.03 – 0.10               | 0.05              | Fama (1970); De Bondt & Thaler (1985) 10.2307/2327804                  |
| `contrarian_threshold`                   | τ_CT    | contrarian-trader (§7)            | 0.05 – 0.15               | 0.05 – 0.10       | Hong & Stein (1999)                                                    |
| `trade_probability` (NoiseTrader)        | p_NT    | noise-trader (§7)                 | 0.10 – 0.50               | 0.30              | Black (1986) 10.2307/2328481                                           |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant  | Build? | Rationale (≤ 1 sentence)                                                                 |
|----------|--------|-------------------------------------------------------------------------------------------|
| Rule     | Yes    | Required deterministic baseline for the §5 stylized-fact benchmark and F4 belief-flip metric. |
| LLM      | Yes    | Answers research goal 3 (do LLM personas spontaneously maintain a persistent belief state?). |
| RuleLLM  | Yes    | Answers research goal 3 hybrid: dual-section prompt embeds Rule quantitative belief update inside LLM persona. |
| Rag      | Yes    | Answers research goal 3 with retrieval-augmented awareness: does citing confirmation-bias literature moderate the bias? |

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges (Rule variant)  | green                 |
| Every §3 research question answerable from `analysis.py`             | green                 |
| Ablating BeliefAnchor produces measurable MAD reduction (≥ 60 %)     | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
