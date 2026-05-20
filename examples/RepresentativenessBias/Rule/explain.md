# RepresentativenessBias Simulation

## §1 Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Representativeness heuristic causes traders to judge probability by similarity to prototypes rather than base rates |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | RepresentativenessBias simulation with PatternMatcher, CategoryOvergeneralizer, BayesianUpdater |
| **Academic Value** | Understanding representativenessbias through multi-agent simulation |

## §2 Theoretical Foundation

- Kahneman & Tversky (1972): Subjective probability - A judgment of representativeness
- Grether (1980): Bayes rule as a descriptive model
- Barberis, Shleifer & Vishny (1998): A model of investor sentiment
## §3 Agent Descriptions

### PatternMatcher
**Theoretical Basis**: Representativeness heuristic (Kahneman & Tversky, 1972)
**Market Role**: destabilizing
**Description**: Matches current price patterns to historical prototypes, ignoring base rates
**Parameters**: pattern_sensitivity=0.8, base_rate_ignore=0.7

### CategoryOvergeneralizer
**Theoretical Basis**: Base rate neglect (Grether, 1980)
**Market Role**: destabilizing
**Description**: Overgeneralizes from small samples, treating stocks as belonging to dramatic categories
**Parameters**: category_weight=2.0, sample_bias=0.6

### BayesianUpdater
**Theoretical Basis**: Bayesian rationality (Grether, 1980 baseline)
**Market Role**: stabilizing
**Description**: Correctly updates beliefs using Bayes rule, weighing base rates and new evidence
**Parameters**: base_rate_weight=1.0, evidence_weight=1.0

### ContrarianStatistical
**Theoretical Basis**: Contrarian strategy (Barberis et al., 1998)
**Market Role**: stabilizing
**Description**: Trades against pattern-matching mispricing by exploiting base rate deviations
**Parameters**: contrarian_threshold=0.1, position_size=450

### NoiseTrader
**Theoretical Basis**: Noise trader model (Black, 1986)
**Market Role**: neutral
**Description**: Random uninformed trader providing baseline liquidity
**Parameters**: trade_probability=0.3


## §4 Market Dynamics

Price follows: P(t+1) = P(t) + lambda * NetDemand + gamma * (F - P(t)) + epsilon

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity,
representativeness pressure, and rational-correction patterns before accepting a
sample.
