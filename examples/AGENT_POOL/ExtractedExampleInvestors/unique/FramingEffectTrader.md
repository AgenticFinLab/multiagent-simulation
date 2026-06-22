# Framing-effect investors and framing arbitrageurs

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Framing-effect investors and framing arbitrageurs |
| Merged profiles | 2 |
| Scenarios | FramingEffect |
| Observed names | Gain Frame Follower, Loss Frame Reactor |

## Consolidated Definition and Goals

- **FramingEffect / Gain Frame Follower**: **Summary**: The GainFrameFollower represents retail investors and individual traders who systematically over-weight gain-framed information. When market prices are above fundamental (positive deviation), this investor interprets the information as a gain and responds with risk-averse buying -- purchasing at a size proportional to the deviation, bounded by cash and a 800-share cap. When prices fall below fundamental, this investor sells proportionally to protect the gain. This agent is destabilizing in rising markets (amplifying positive deviations) and partially stabilizing in falling markets (selling reduces overshooting below fundamental).
- **FramingEffect / Loss Frame Reactor**: **Summary**: The LossFrameReactor represents investors who over-weight loss-framed information, becoming risk-seeking when facing potential losses. The behavioral pattern is paradoxically similar to GainFrameFollower in action direction (both buy on positive deviation, sell on negative), but the underlying motivation differs: LossFrameReactor is driven by risk-seeking under loss (convex value function) rather than gain-chasing. In aggregate, both agents reinforce trends, making them jointly destabilizing.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.1 -- GainFrameFollower
- Theoretical basis: Gain frame risk aversion (Tversky & Kahneman, 1981).
- LLM-driven GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md Section 4.1.
- RuleLLM-driven GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md Section 4.1.
- RAG-augmented GainFrameFollower: overweights gains-framed information. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.2 -- LossFrameReactor
- Theoretical basis: Loss frame risk seeking (Tversky & Kahneman, 1981).
- LLM-driven LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md Section 4.2.
- RuleLLM-driven LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md Section 4.2.
- RAG-augmented LossFrameReactor: overweights loss-framed information. Theory: simulation-bases.md Section 4.2.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| FramingEffect | Gain Frame Follower | [FramingEffect__GainFrameFollower.md](../FramingEffect__GainFrameFollower.md) |
| FramingEffect | Loss Frame Reactor | [FramingEffect__LossFrameReactor.md](../FramingEffect__LossFrameReactor.md) |

