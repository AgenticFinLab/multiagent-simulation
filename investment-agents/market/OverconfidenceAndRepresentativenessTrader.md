# Overconfidence, hindsight, and representativeness-biased traders

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Overconfidence, hindsight, and representativeness-biased traders |
| Merged profiles | 7 |
| Scenarios | HindsightBias, OverconfidenceBias, RepresentativenessBias, ReversalEffect |
| Observed names | Category Overgeneralizer, Hindsight Overconfident, Outcome Learner, Overconfident Trader, Pattern Matcher, Self Attributor |

## Consolidated Definition and Goals

- **HindsightBias / Hindsight Overconfident**: **Summary**: Implements Fischhoff (1975) hindsight bias -- the agent interprets price moves as "obviously" predictable in retrospect, amplifying momentum by buying when deviation > 0.02 and selling when deviation < -0.02.
- **HindsightBias / Outcome Learner**: **Summary**: Implements Fischhoff & Beyth (1975) outcome bias and Odean (1998) selective attribution -- the agent attributes gains to skill and losses to bad luck, producing asymmetric momentum that is stronger in bull phases.
- **OverconfidenceBias / Overconfident Trader**: 1. **Summary**: OverconfidentTrader inflates perceived signal precision and trades on deviations that calibrated traders might ignore. It is the primary destabilizing role. 2. **Theoretical and Empirical Foundation**: Daniel et al. (1998) and Odean (1998) support the signal-overprecision and excess-turnover mechanism. 3. **Design Purpose and Activation Scenarios**: Activates when the perceived signal exceeds a low threshold. Its market purpose is to convert weak mispricing into large order flow. 4. **Behavioral Framework**: Uses `signal = deviation * precision_overestimate`. If `abs(signal) > 0.01`, it trades in the signal direction with size capped by `base_size`, cash, and inventory. 5. **Decision Process Walkthrough**: Read price and fundamental, compute deviation, inflate it, select buy/sell direction, cap quantity, and emit a reasoned canonical order. 6. **Worked Numerical Example**: If deviation is `+2%` and `precision_overestimate = 2.0`, perceived signal is `+4%`, crossing threshold and producing a buy order subject to available cash. 7. **Academic References**: Daniel et al. (1998), Odean (1998), Barber and Odean (2001).
- **OverconfidenceBias / Self Attributor**: 1. **Summary**: SelfAttributor raises confidence after favorable conditions and discounts negative evidence. It creates path-dependent risk taking. 2. **Theoretical and Empirical Foundation**: Biased self-attribution in Daniel et al. (1998) and Gervais and Odean (2001, DOI `10.1093/rfs/14.1.1`) motivates the role. 3. **Design Purpose and Activation Scenarios**: Activates when an existing position and positive deviation make success feel skill-based, or when losses trigger exposure trimming. 4. **Behavioral Framework**: Positive deviation with inventory increases buy size by `confidence_boost`; negative deviation beyond a threshold can trigger a sell. 5. **Decision Process Walkthrough**: Observe current inventory, read deviation, apply confidence boost or loss trim, then cap order by cash/inventory. 6. **Worked Numerical Example**: With `base_size = 400` and `confidence_boost = 0.5`, a positive state can request `600` shares before cash constraints. 7. **Academic References**: Daniel et al. (1998), Gervais and Odean (2001).
- **RepresentativenessBias / Category Overgeneralizer**: **Summary**: A destabilizing investor that maps a small sample of recent price movement into a dramatic category such as "growth star" or "falling knife".
- **RepresentativenessBias / Pattern Matcher**: **Summary**: A destabilizing investor that treats short price deviations as evidence of a familiar prototype. It amplifies recent patterns and underweights base rates.
- **ReversalEffect / Overconfident Trader**: **Summary**: Overweights recent signals and trades too aggressively. **Theoretical and Empirical Basis**: Overconfidence models of excessive trading and delayed correction. **Design Purpose**: Amplify the initial move and increase reversal amplitude. **Behavioral Framework**: Uses `reaction_threshold`, `overconfidence_factor`, and `overconfidence_multiplier`. **Decision Process**: Convert recent returns into larger directional orders than a calibrated investor would place. **Worked Numerical Example**: A +4% return is inflated by the overconfidence factor and can trigger a larger buy order. **Academic References**: Daniel, Hirshleifer, and Subrahmanyam (1998), DOI: 10.1111/0022-1082.00077; Barber and Odean (2001), DOI: 10.1111/0022-1082.00308.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.1 -- HindsightOverconfident
- Theoretical basis: Knew-it-all-along effect (Fischhoff, 1975).
- LLM-driven HindsightOverconfident: excessive confidence from hindsight reasoning. Theory: simulation-bases.md Section 4.1.
- RuleLLM HindsightOverconfident: excessive confidence from hindsight reasoning. Theory: simulation-bases.md Section 4.1.
- RAG HindsightOverconfident: excessive confidence from hindsight reasoning. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.2 -- OutcomeLearner
- Theoretical basis: Outcome bias (Fischhoff & Beyth, 1975).
- LLM-driven OutcomeLearner: judges decisions by outcomes, not process. Theory: simulation-bases.md Section 4.2.
- RuleLLM OutcomeLearner: judges decisions by outcomes, not process. Theory: simulation-bases.md Section 4.2.
- RAG OutcomeLearner: judges decisions by outcomes, not process. Theory: simulation-bases.md Section 4.2.
- Theoretical basis: simulation-bases.md Section 4.1 -- OverconfidentTrader.
- Theoretical basis: simulation-bases.md Section 4.2 -- SelfAttributor.
- Theory: simulation-bases.md Section 4.2 -- CategoryOvergeneralizer
- Theoretical basis: base-rate neglect and small-sample extrapolation.
- LLM-driven category generalizer -- small-sample extrapolation. Theory: simulation-bases.md Section 4.2.
- RuleLLM category generalizer -- rule-guided extrapolation. Theory: simulation-bases.md Section 4.2.
- RagLLM category generalizer -- small-sample extrapolation with retrieval. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.1 -- PatternMatcher
- Theoretical basis: representativeness heuristic; salient prototypes
- LLM-driven pattern matcher -- prototype-based trading. Theory: simulation-bases.md Section 4.1.
- RuleLLM pattern matcher -- rule-guided prototype trading. Theory: simulation-bases.md Section 4.1.
- RagLLM pattern matcher -- prototype trading with retrieved context. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.3.
- LLM OverconfidentTrader. Theory: simulation-bases.md Section 4.3.
- Hybrid OverconfidentTrader. Theory: simulation-bases.md Section 4.3.
- RAG OverconfidentTrader. Theory: simulation-bases.md Section 4.3.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| HindsightBias | Hindsight Overconfident | [HindsightBias__HindsightOverconfident.md](../HindsightBias__HindsightOverconfident.md) |
| HindsightBias | Outcome Learner | [HindsightBias__OutcomeLearner.md](../HindsightBias__OutcomeLearner.md) |
| OverconfidenceBias | Overconfident Trader | [OverconfidenceBias__OverconfidentTrader.md](../OverconfidenceBias__OverconfidentTrader.md) |
| OverconfidenceBias | Self Attributor | [OverconfidenceBias__SelfAttributor.md](../OverconfidenceBias__SelfAttributor.md) |
| RepresentativenessBias | Category Overgeneralizer | [RepresentativenessBias__CategoryOvergeneralizer.md](../RepresentativenessBias__CategoryOvergeneralizer.md) |
| RepresentativenessBias | Pattern Matcher | [RepresentativenessBias__PatternMatcher.md](../RepresentativenessBias__PatternMatcher.md) |
| ReversalEffect | Overconfident Trader | [ReversalEffect__OverconfidentTrader.md](../ReversalEffect__OverconfidentTrader.md) |

