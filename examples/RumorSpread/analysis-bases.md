# RumorSpread Analysis Bases

## §1 Analysis Objectives

RumorSpread analysis verifies whether the model produces a plausible false-rumor
cycle: belief rises through spread actions, distortion accumulates through
retelling, and skeptical or fact-checking agents create delayed correction. The
analysis also separates deterministic behavior from LLM, RuleLLM, and Rag
reasoning effects while preserving the same special `social_action` schema.

Primary objectives are to measure belief-truth divergence, distortion growth,
spread/correction activity, correction lag, role-level belief dispersion, and
RAG retrieval coverage for the Rag variant.

## §2 Core Metrics Catalogue

### §2.1 Belief Level

`def compute_belief_level(states: list[dict]) -> list[float]`

Tracks environment `belief` over rounds. High values indicate widespread belief
in the rumor, regardless of truth.

### §2.2 Belief-Truth Divergence

`def compute_truth_divergence(belief: list[float], truth_value: float) -> dict`

Computes absolute distance between public belief and ground truth. This is the
primary misinformation intensity metric.

### §2.3 Rumor Amplification Ratio

`def compute_rumor_amplification(belief: list[float]) -> float`

Computes peak belief divided by initial belief. Ratios above 1.0 indicate that
social transmission amplified the original rumor seed.

### §2.4 Distortion Index

`def compute_distortion_index(distortion: list[float]) -> dict`

Measures maximum, final, and average distortion. It captures leveling and
sharpening effects from `simulation-bases.md §2.2`.

### §2.5 Spread And Correction Activity

`def compute_activity_balance(spread_count: list[int], correction_count: list[int]) -> dict`

Measures total spread events, total correction events, average action rates, and
the correction-to-spread ratio.

### §2.6 Correction Lag

`def compute_correction_lag(spread_count: list[int], correction_count: list[int]) -> float`

Uses cross-correlation to estimate how many rounds correction activity lags
spread activity.

### §2.7 RAG Retrieval Coverage

`def analyze_rag_knowledge_effect(payloads: dict[str, dict[int, dict]]) -> dict`

Rag-only metric that measures how often `rag_context` contains retrieved content
rather than the canonical fallback text.

## §3 Analysis Dimensions

Analysis is performed by round, by role, by action type, by phase, and by
variant. The key dimensions are belief dynamics, truth divergence, distortion,
spread/correction activity, personal belief dispersion, and LLM/RAG artifact
quality.

## §4 Phase Analysis Framework

The expected phases are rumor seeding, amplification, distortion accumulation,
skeptical challenge, fact-check correction, and residual belief. In a valid
simulation, spread activity should precede correction activity, and belief
should not automatically collapse to truth in early rounds.

## §5 Cross-Variant Comparison Framework

Rule provides the deterministic baseline. LLM measures whether persona-only
reasoning can select coherent social actions. RuleLLM measures the effect of
explicit formula guidance in the prompt. Rag measures whether retrieved
misinformation/correction knowledge changes reasoning and correction coverage.

## §6 Expected Results And Validation

Expected full-round outputs include 200 recorded belief rounds, nonzero spread
activity, nonzero correction activity, bounded belief/distortion in `[0, 1]`,
and a `summary.json` with `validation.score`, `validation.is_valid`, and
`validation.criteria`. Rag additionally writes `rag_stats.json`; retrieval
failure rate should be reviewed if it exceeds 30% and should be reported in the
resource ledger.

Failure signs include missing belief history, all-zero activity, unbounded
belief or distortion, absent `rag_context` in Rag records, or API decisions that
do not conform to `action_type/intensity/reasoning`.

## §7 Visualization Catalogue

The authoritative analysis writes fixed PNG names into `analysis/`:

| File | Content |
|---|---|
| `00_investor_bids.png` | Compatibility plot slot containing the scenario summary figure. |
| `01_rumorspread_dynamics.png` | Belief and truth-divergence dynamics. |
| `02_rumorspread_analysis.png` | Distortion and spread/correction activity. |
| `03_summary.png` | Combined summary visualization. |

The same core visualizations are shared across Rule, LLM, RuleLLM, and Rag.
Rag adds `rag_stats.json` for retrieval-quality analysis.
