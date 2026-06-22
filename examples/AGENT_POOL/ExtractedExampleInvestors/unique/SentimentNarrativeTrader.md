# Sentiment, narrative, media, and selective-attention traders

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Sentiment, narrative, media, and selective-attention traders |
| Merged profiles | 7 |
| Scenarios | AssetBubble, AvailabilityBias, ConfirmationBias, DotComBubble, SVBBankRun, SouthSeaBubble |
| Observed names | Media Influenced Trader, Narrative Believer, New Economy Evangelist, Recent Event Overweighter, Selective Scanner, Sentiment Trader, Social Media Influencer |

## Consolidated Definition and Goals

- **AssetBubble / Sentiment Trader**: LLM sentiment trader. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.
- **AvailabilityBias / Media Influenced Trader**: The MediaInfluencedTrader is an investor whose perceptions of market conditions are shaped by media framing and social signal amplification rather than direct observation of price-fundamental relationships. When the media covers a market event intensively (proxied by the deviation signal being amplified by media_weight x social_amplification), this investor perceives the event as more significant than it is. This investor does not overweight recent returns (unlike RecentEventOverweighter) but instead overweights the magnitude of any current deviation -- treating deviation as a media-salient signal with 1.2x perceived intensity. This creates a distinct channel: availability through media salience rather than temporal recency.
- **AvailabilityBias / Recent Event Overweighter**: The RecentEventOverweighter is a retail or semi-institutional investor who gives disproportionate weight to the most recent market event in forming their outlook. When the market has just moved sharply (large `return_pct`), this investor perceives the current moment as abnormally significant -- a directionally important signal -- and trades accordingly, regardless of whether the recent move reflects any genuine change in fundamental value. This investor embodies the availability heuristic in its purest market form: the "available" event (the salient recent return) dominates the objective signal (fundamental deviation). In equilibrium, this creates systematic overreaction to recent price moves and underreaction to slow-developing fundamental trends.
- **ConfirmationBias / Selective Scanner**: The SelectiveScanner is an investor who selectively attends to information that supports their current market position. Unlike BeliefAnchor (who maintains an internal belief state), SelectiveScanner operates entirely on current position: it executes full-size orders when the market confirms its existing position, but only half-size orders when the market contradicts it. This asymmetric response to confirming vs. disconfirming signals is the behavioral manifestation of "selective search" -- a classic form of confirmation bias where investors seek out confirming evidence and ignore or discount contrary evidence. The SelectiveScanner is currently long (initial_position > 0), so positive deviation (price above fundamental) confirms the long and triggers full buying; negative deviation threatens the position and triggers muted selling.
- **DotComBubble / New Economy Evangelist**: Narrative-driven buyer who treats internet adoption as a reason to keep buying even under overvaluation. This investor is destabilizing because persistent demand lifts the market above fundamental value.
- **SVBBankRun / Social Media Influencer**: **Summary**: Amplifies negative bank-health signals. **Theoretical and Empirical Foundation**: Information cascades and social contagion. **Design Purpose and Activation Scenarios**: Adds panic pressure when `deviation < -0.05`. **Behavioral Framework**: Public-risk amplification rather than portfolio optimization. **Mathematical Model**: **Decision Process Walkthrough**: Convert negative deviation into proportional sell pressure. **Worked Example**: `deviation=-0.08`, `amplification_factor=2.0`, `position=500` yields 320 sell units. **References**: Bikhchandani, Hirshleifer, and Welch (1992).
- **SouthSeaBubble / Narrative Believer**: **Summary**: A story-driven investor convinced by monopoly and official-support narratives. **Theoretical and Empirical Basis**: Narrative economics and historical mania accounts. **Design Purpose**: Generate bubble demand and momentum-following pressure. **Behavioral Framework**: Uses the retained `abs(deviation) > 0.02` threshold and the same 800-unit cap as insiders. **Decision Process**: Buy into rising overpricing when the narrative appears validated; sell on negative deviation when the story weakens. **Worked Numerical Example**: A 4% positive deviation produces a 200-unit raw buy quantity. **Academic References**: Shiller (2017) and South Sea Bubble histories.

## Consolidated Financial Theory

- LLM sentiment trader. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.
- Theory: simulation-bases.md Section 4.2 -- MediaInfluencedTrader
- Theoretical basis: Schwarz et al. (1991); Tetlock (2007) -- Media-driven availability channel.
- LLM-driven trader influenced by media coverage and social signals. Theory: simulation-bases.md Section 4.2.
- RuleLLM -- influenced by media coverage and social signals. Theory: simulation-bases.md Section 4.2.
- RAG-augmented -- influenced by media coverage and social signals. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.1 -- RecentEventOverweighter
- Theoretical basis: Tversky & Kahneman (1973) -- Availability heuristic recency channel.
- LLM-driven trader who overweights recent dramatic market events. Theory: simulation-bases.md Section 4.1.
- RuleLLM -- overweights recent dramatic market events. Theory: simulation-bases.md Section 4.1.
- RAG-augmented -- overweights recent dramatic market events. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.2 -- SelectiveScanner
- Theoretical basis: Lord, Ross & Lepper (1979) biased assimilation; filters market
- LLM-driven selective scanner -- seeks confirming information, ignores contradictions. Theory: simulation-bases.md Section 4.2.
- RuleLLM-driven selective scanner -- seeks confirming info, ignores contradictions. Theory: simulation-bases.md Section 4.2.
- RAG-augmented selective scanner -- seeks confirming info, ignores contradictions. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.1 -- NewEconomyEvangelist
- Theoretical basis: Shiller (2000) narrative economics; tech evangelists dismiss P/E ratios as irrelevant.
- LLM-driven new economy evangelist -- ignores valuation, buys internet narrative. Theory: simulation-bases.md Section 4.1.
- RuleLLM-driven new economy evangelist -- narrative rules embedded. Theory: simulation-bases.md Section 4.1.
- RAG-augmented new economy evangelist -- narrative-driven buyer with historical bubble context. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.2 -- SocialMediaInfluencer
- Theoretical basis: information cascade and social-contagion amplification.
- LLM-driven social media influencer amplifying panic signals. Theory: simulation-bases.md Section 4.2.
- Hybrid Rule+LLM social media influencer with amplification rules. Theory: simulation-bases.md Section 4.2.
- RAG-augmented social media influencer with amplification rules and retrieved knowledge. Theory: simulation-bases.md Section 4.2.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AssetBubble | Sentiment Trader | [AssetBubble__SentimentTrader.md](../AssetBubble__SentimentTrader.md) |
| AvailabilityBias | Media Influenced Trader | [AvailabilityBias__MediaInfluencedTrader.md](../AvailabilityBias__MediaInfluencedTrader.md) |
| AvailabilityBias | Recent Event Overweighter | [AvailabilityBias__RecentEventOverweighter.md](../AvailabilityBias__RecentEventOverweighter.md) |
| ConfirmationBias | Selective Scanner | [ConfirmationBias__SelectiveScanner.md](../ConfirmationBias__SelectiveScanner.md) |
| DotComBubble | New Economy Evangelist | [DotComBubble__NewEconomyEvangelist.md](../DotComBubble__NewEconomyEvangelist.md) |
| SVBBankRun | Social Media Influencer | [SVBBankRun__SocialMediaInfluencer.md](../SVBBankRun__SocialMediaInfluencer.md) |
| SouthSeaBubble | Narrative Believer | [SouthSeaBubble__NarrativeBeliever.md](../SouthSeaBubble__NarrativeBeliever.md) |

