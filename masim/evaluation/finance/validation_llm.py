"""LLM-Based Simulation Validation Module

Uses Large Language Models to evaluate whether simulation results are consistent
with established financial theory. Each scenario has rigorous prompts containing:
- Academic theoretical foundations
- Expected quantitative behaviors
- Diagnostic criteria for validity assessment

This complements the rule-based validation.py with nuanced LLM judgment.

Usage:
    from masim.evaluation.finance.validation_llm import (
        LLMValidator,
        validate_with_llm,
    )

    validator = LLMValidator(model="gpt-4")
    result = validator.validate("AssetBubble", summary_data)
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable


@dataclass
class LLMValidationResult:
    """Result of LLM-based validation."""

    scenario: str
    is_valid: bool
    confidence: float  # 0-1, LLM's confidence in judgment
    reasoning: str  # Detailed reasoning
    theory_alignment: Dict[str, Any]  # Per-theory alignment scores
    suggestions: List[str]  # Improvement suggestions
    raw_response: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "scenario": self.scenario,
            "is_valid": self.is_valid,
            "confidence": round(self.confidence, 3),
            "reasoning": self.reasoning,
            "theory_alignment": self.theory_alignment,
            "suggestions": self.suggestions,
        }


# =============================================================================
# FINANCIAL THEORY PROMPTS - Rigorous Academic Foundations
# =============================================================================

ASSET_BUBBLE_THEORY = """
## Asset Bubble Theory (Kindleberger-Minsky Model)

### Theoretical Foundation
Asset bubbles follow the Kindleberger-Minsky framework (Kindleberger, 2000; Minsky, 1986):

1. **Displacement Phase**: An exogenous shock (new technology, policy change) creates 
   profit opportunities. Prices begin rising from fundamental value.

2. **Boom Phase**: Credit expansion fuels price increases. Positive feedback emerges:
   - Rising prices → increased collateral value → more borrowing → more buying
   - Extrapolative expectations: agents project recent returns into future

3. **Euphoria Phase**: Prices detach significantly from fundamentals (typically 20-50% 
   deviation). Speculation dominates. Greater fool theory prevails.

4. **Critical Phase**: Smart money exits. Price growth decelerates. Margin calls begin.

5. **Crash Phase**: Panic selling cascade. Prices fall rapidly (>15% drawdown typical).
   Fire sales amplify decline. Credit contracts.

### Expected Quantitative Signatures
- Price deviation from fundamental: 20-50% at peak (Shiller, 2000)
- Gradual formation: Peak should occur after 30%+ of simulation
- Crash magnitude: >15% max drawdown
- Asymmetric dynamics: Rise slower than fall (3:1 to 5:1 ratio typical)
- Volume spike during crash phase

### Academic References
- Kindleberger, C. P. (2000). Manias, Panics, and Crashes
- Minsky, H. P. (1986). Stabilizing an Unstable Economy
- Shiller, R. J. (2000). Irrational Exuberance
- Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and Crashes. Econometrica
"""

HERD_EFFECT_THEORY = """
## Herding Behavior Theory (Information Cascade Model)

### Theoretical Foundation
Herding emerges from information cascades (Bikhchandani, Hirshleifer, & Welch, 1992):

1. **Information Asymmetry**: Agents have private signals about asset value but 
   can observe others' actions (not their signals).

2. **Cascade Formation**: When public information (inferred from actions) overwhelms
   private signals, agents rationally ignore their own information and follow others.

3. **Cascade Dynamics**:
   - Early movers reveal information through actions
   - Later agents weight observed actions heavily
   - Convergence of behavior despite heterogeneous beliefs
   - Fragility: small shocks can break cascades

### Quantitative Signatures (LSV Measure)
The Lakonishok-Shleifer-Vishny (1992) measure quantifies herding:
- Bid Coefficient of Variation (CV) < 0.15 indicates convergence
- Directional agreement > 70% indicates coordinated behavior
- Cross-sectional dispersion decline during herding episodes

### Expected Patterns
- CV should drop significantly during herding episodes (from ~0.20 to <0.10)
- Price deviation >15% from fundamental during strong herding
- At least one clear herding episode in 100+ round simulation
- Cascade persistence: herding episodes last 5-20 rounds

### Academic References
- Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A Theory of Fads, Fashion, 
  Custom, and Cultural Change as Informational Cascades. JPE
- Lakonishok, J., Shleifer, A., & Vishny, R. W. (1992). The Impact of Institutional 
  Trading on Stock Prices. JFE
- Banerjee, A. V. (1992). A Simple Model of Herd Behavior. QJE
"""

FLASH_CRASH_THEORY = """
## Flash Crash Theory (Market Microstructure)

### Theoretical Foundation
Flash crashes result from market microstructure fragility (Kirilenko et al., 2017):

1. **Liquidity Withdrawal**: High-frequency traders (HFTs) simultaneously withdraw
   liquidity when detecting unusual order flow or volatility.

2. **Feedback Loop**:
   - Large sell order → price impact → stop-loss triggers
   - HFT withdrawal → wider spreads → larger price impact
   - Momentum traders amplify decline

3. **Recovery Mechanism**:
   - Circuit breakers or trading halts
   - Value investors recognize mispricing
   - Liquidity providers re-enter at attractive spreads

### Quantitative Signatures
- Crash magnitude: 5-20% drop (May 2010 Flash Crash: ~9% in minutes)
- Crash speed: <10 rounds (real-world: minutes)
- V-shaped recovery: Price recovers >50% of decline
- Volatility spike: 5-10x normal during crash

### Expected Patterns
- Rapid drawdown: Peak-to-trough in <10 rounds
- Partial or full recovery within 2x crash duration
- Extreme volume during crash and recovery
- Return to near pre-crash levels (within 5% of original)

### Academic References
- Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: 
  High-Frequency Trading in an Electronic Market. JF
- SEC/CFTC. (2010). Findings Regarding the Market Events of May 6, 2010
- Easley, D., López de Prado, M. M., & O'Hara, M. (2011). The Microstructure of the 
  Flash Crash. JPM
"""

MARKET_CRASH_THEORY = """
## Market Crash Theory (Panic Selling Cascade)

### Theoretical Foundation
Market crashes differ from flash crashes in duration and mechanism (Brunnermeier, 2009):

1. **Build-up Phase**: Vulnerabilities accumulate (leverage, overvaluation, 
   concentration risk) over extended period.

2. **Trigger Event**: Negative news/shock reveals vulnerabilities.
   - Margin calls force selling
   - Risk limits trigger de-leveraging
   - Flight to quality/liquidity

3. **Cascade Dynamics** (Minsky Moment):
   - Forced selling → price decline → more margin calls
   - Asset fire sales at distressed prices
   - Credit contraction amplifies decline

4. **L-shaped or U-shaped Recovery**:
   - Unlike flash crashes, recovery is slow
   - Fundamental repair needed (debt restructuring, recapitalization)

### Quantitative Signatures
- Crash magnitude: 20-50% peak-to-trough (2008: ~57%, 1929: ~89%)
- Duration: 10-30 rounds (real-world: weeks to months)
- Slow recovery or no recovery within simulation
- Volatility persistence: elevated for extended period

### Expected Patterns
- Gradual decline (not instant like flash crash)
- Multiple failed rallies before bottom
- Correlation spike (all assets decline together)
- Volume elevated throughout crash period

### Academic References
- Brunnermeier, M. K. (2009). Deciphering the Liquidity and Credit Crunch 2007-2008. JEP
- Minsky, H. P. (1986). Stabilizing an Unstable Economy
- Adrian, T., & Shin, H. S. (2010). Liquidity and Leverage. JFI
"""

MOMENTUM_EFFECT_THEORY = """
## Momentum Effect Theory (Return Continuation)

### Theoretical Foundation
Momentum is the tendency for past winners to continue outperforming (Jegadeesh & Titman, 1993):

1. **Behavioral Explanations**:
   - Underreaction: Investors slowly incorporate information
   - Confirmation bias: Seek information confirming existing positions
   - Disposition effect: Sell winners too early, limiting price discovery

2. **Risk-Based Explanations**:
   - Time-varying risk premia
   - Momentum captures systematic risk factors
   - Compensation for crash risk

3. **Mechanism**:
   - Positive autocorrelation in returns at short horizons (1-12 months)
   - Trend persistence before mean reversion
   - Winner-loser spread generates excess returns

### Quantitative Signatures
- Positive return autocorrelation at lag 1-5 (ρ > 0.05)
- Average trend duration: 5-20 rounds
- Winner portfolio outperforms loser portfolio

### Expected Patterns
- ACF(1) > 0.1 indicates significant momentum
- Trend streaks (same-sign returns) averaging 5+ rounds
- Higher returns for stocks with strong recent performance
- Momentum decay: effect weakens at longer horizons

### Academic References
- Jegadeesh, N., & Titman, S. (1993). Returns to Buying Winners and Selling Losers. JF
- Hong, H., & Stein, J. C. (1999). A Unified Theory of Underreaction, Momentum Trading, 
  and Overreaction in Asset Markets. JF
- Daniel, K., & Moskowitz, T. J. (2016). Momentum Crashes. JFE
"""

REVERSAL_EFFECT_THEORY = """
## Reversal Effect Theory (Mean Reversion)

### Theoretical Foundation
Long-term reversal reflects overreaction correction (De Bondt & Thaler, 1985):

1. **Overreaction Hypothesis**:
   - Investors overweight recent information
   - Prices overshoot fundamental value
   - Subsequent correction generates reversal

2. **Mechanism**:
   - Negative autocorrelation at long horizons (3-5 years)
   - Past losers outperform past winners
   - Contrarian strategies profitable

3. **Relation to Momentum**:
   - Short-term: Momentum (underreaction)
   - Long-term: Reversal (overreaction correction)
   - Transition point: 12-18 months

### Quantitative Signatures
- Negative ACF at long lags (lag 15-30): ρ < -0.05
- Winner-loser spread: Losers outperform by 5-10% annually
- Mean reversion to fundamental value

### Expected Patterns
- ACF becomes negative at longer lags
- Price eventually returns toward fundamental
- Stronger reversal for more extreme prior moves
- Contrarian profits: Buy losers, sell winners

### Academic References
- De Bondt, W. F., & Thaler, R. (1985). Does the Stock Market Overreact? JF
- Fama, E. F., & French, K. R. (1988). Permanent and Temporary Components of Stock 
  Prices. JPE
- Poterba, J. M., & Summers, L. H. (1988). Mean Reversion in Stock Prices. JFE
"""

VOLATILITY_CLUSTERING_THEORY = """
## Volatility Clustering Theory (GARCH Dynamics)

### Theoretical Foundation
Volatility clustering is a universal stylized fact (Bollerslev, 1986; Cont, 2001):

1. **GARCH Process**:
   σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}
   - Current volatility depends on past shocks and past volatility
   - "Large changes tend to be followed by large changes"

2. **Mechanism**:
   - Information arrives in clusters
   - Heterogeneous agent reaction times
   - Feedback between volatility and trading behavior

3. **Stylized Facts** (Cont, 2001):
   - Returns: near-zero autocorrelation (efficient market)
   - Squared/absolute returns: positive autocorrelation (clustering)
   - Fat tails in return distribution
   - Leverage effect (negative returns → higher volatility)

### Quantitative Signatures
- Return ACF ≈ 0 (|ρ| < 0.1)
- Squared return ACF > 0.1 (significant persistence)
- Clustering ratio (sq_ACF / |return_ACF|) > 2
- Volatility persistence: α + β > 0.9

### Expected Patterns
- Clear separation: Returns unpredictable, volatility predictable
- High/low volatility regimes clearly identifiable
- Volatility mean-reversion (eventually returns to average)
- Asymmetric volatility response to up/down moves

### Academic References
- Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. JE
- Cont, R. (2001). Empirical Properties of Asset Returns: Stylized Facts and 
  Statistical Issues. QF
- Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity. Econometrica
"""

SHORT_SQUEEZE_THEORY = """
## Short Squeeze Theory (Supply-Demand Imbalance)

### Theoretical Foundation
Short squeezes occur when short sellers are forced to cover (GameStop 2021, VW 2008):

1. **Setup Conditions**:
   - High short interest (shares short / float > 20%)
   - Limited float (low available shares)
   - Catalyst: positive news, coordinated buying

2. **Squeeze Mechanism**:
   - Buy pressure → price rise
   - Short sellers face margin calls → forced buying
   - Limited supply amplifies price impact
   - Positive feedback: covering → higher price → more covering

3. **Peak and Aftermath**:
   - Parabolic rise (exponential price increase)
   - Sharp reversal once covering complete
   - Price often returns toward fundamental

### Quantitative Signatures
- Price spike: >50-100% increase from base
- Short covering volume: >20% of total volume
- Feedback loop: Acceleration in price rise

### Expected Patterns
- Initial stable period before trigger
- Rapid price acceleration (not linear)
- Peak followed by sharp decline
- Higher volume during squeeze than normal

### Academic References
- SEC Staff Report on Equity and Options Market Structure Conditions in Early 2021
- Porsche-VW Short Squeeze Case Study (2008)
- Lamont, O. A., & Thaler, R. H. (2003). Can the Market Add and Subtract? JEP
"""

LIQUIDITY_DRYUP_THEORY = """
## Liquidity Dry-up Theory (Market Maker Model)

### Theoretical Foundation
Liquidity dry-up follows the Grossman-Miller (1988) and Brunnermeier-Pedersen (2009) models:

1. **Market Maker Inventory Model**:
   - Market makers provide liquidity by absorbing order imbalances
   - Inventory holding is risky → requires compensation
   - During stress: inventory risk increases → spreads widen

2. **Illiquidity Spiral** (Brunnermeier-Pedersen):
   - Price drop → margin constraints → forced selling
   - Forced selling → more price impact (low liquidity)
   - Higher volatility → market makers withdraw
   - Withdrawal → even lower liquidity → spiral continues

3. **Liquidity States**:
   - Normal: Full market maker participation, tight spreads
   - Reduced: Partial withdrawal, wider spreads
   - Dry-up: Minimal liquidity, very wide spreads
   - Crisis: Complete withdrawal, no quotes

### Quantitative Signatures
- Spread increase: 3-10x normal during stress
- Depth decrease: 50-100% reduction
- Price impact: 3-5x higher per unit volume
- Duration: Persists until volatility subsides

### Expected Patterns
- Liquidity correlated with volatility (negative)
- Cascading withdrawal as stress increases
- Recovery lag after volatility normalizes
- Flight to quality (liquidity → safe assets)

### Academic References
- Grossman, S. J., & Miller, M. H. (1988). Liquidity and Market Structure. JF
- Brunnermeier, M. K., & Pedersen, L. H. (2009). Market Liquidity and Funding 
  Liquidity. RFS
- Amihud, Y., & Mendelson, H. (1986). Asset Pricing and the Bid-Ask Spread. JFE
"""

DISPOSITION_EFFECT_THEORY = """
## Disposition Effect Theory (Prospect Theory)

### Theoretical Foundation
The disposition effect (Shefrin & Statman, 1985) emerges from prospect theory (Kahneman & Tversky, 1979):

1. **Prospect Theory Foundations**:
   - Reference dependence: Utility measured relative to reference point (purchase price)
   - Loss aversion: Losses weighted ~2x more than equivalent gains
   - Diminishing sensitivity: Marginal utility decreases away from reference

2. **Value Function**:
   v(x) = x^α           for x ≥ 0 (gains)
   v(x) = -λ(-x)^β      for x < 0 (losses)
   where λ ≈ 2.25 (loss aversion coefficient)

3. **Behavioral Implications**:
   - Risk-seeking in losses: Hold losers hoping for recovery
   - Risk-averse in gains: Sell winners to lock in profits
   - Result: PGR > PLR (Proportion of Gains/Losses Realized)

### Quantitative Signatures
- PGR (Proportion of Gains Realized) > PLR (Proportion of Losses Realized)
- Disposition coefficient (PGR - PLR) > 0.05
- Loss holding period > gain holding period

### Expected Patterns
- Asymmetric trading: More sales in gains, fewer in losses
- Reference point anchoring: Behavior depends on purchase price
- Disposition effect stronger for inexperienced investors
- Tax inefficiency: Realize gains (taxable), defer losses (not deductible)

### Academic References
- Shefrin, H., & Statman, M. (1985). The Disposition to Sell Winners Too Early and 
  Ride Losers Too Long. JF
- Kahneman, D., & Tversky, A. (1979). Prospect Theory. Econometrica
- Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? JF
"""

EQUITY_PREMIUM_THEORY = """
## Equity Premium Puzzle Theory (Myopic Loss Aversion)

### Theoretical Foundation
The equity premium puzzle (Mehra & Prescott, 1985) is explained by myopic loss aversion 
(Benartzi & Thaler, 1995):

1. **The Puzzle**:
   - Historical equity premium: 6-8% annually (stocks vs. bonds)
   - Standard expected utility cannot explain this with reasonable risk aversion
   - Required risk aversion coefficient > 30 (implausibly high)

2. **Myopic Loss Aversion Solution**:
   - Loss aversion (λ ≈ 2.25): Losses hurt 2x more than gains please
   - Myopia: Investors evaluate portfolios frequently (annually, not over lifetime)
   - Combination: Frequent evaluation + loss aversion → high required premium

3. **Evaluation Frequency Effect**:
   - Short horizon (1 year): P(stock loss) ≈ 36% → low stock allocation
   - Long horizon (20 years): P(stock loss) ≈ 5% → high stock allocation
   - Myopic investors see more losses → demand higher premium

### Quantitative Signatures
- Equity premium: 4-8% annualized
- Myopic allocation: ~20% stocks (frequent evaluators)
- Long-horizon allocation: ~70% stocks (infrequent evaluators)
- Allocation difference: 20-50% based on evaluation horizon

### Expected Patterns
- Stock returns > bond returns over long periods
- Higher volatility for stocks vs. bonds
- Shorter evaluation → lower stock allocation → higher required premium
- Loss probability declines with horizon (time diversification)

### Academic References
- Mehra, R., & Prescott, E. C. (1985). The Equity Premium: A Puzzle. JME
- Benartzi, S., & Thaler, R. H. (1995). Myopic Loss Aversion and the Equity Premium 
  Puzzle. QJE
- Barberis, N., Huang, M., & Santos, T. (2001). Prospect Theory and Asset Prices. QJE
"""

# =============================================================================
# SCENARIO PROMPT TEMPLATES
# =============================================================================

VALIDATION_PROMPT_TEMPLATE = """You are a quantitative finance expert evaluating whether a multi-agent market simulation accurately reproduces the financial phenomenon of {scenario_name}.

## Your Task
Analyze the provided simulation summary data and determine if it is CONSISTENT with established financial theory for {scenario_name}.

{theory_section}

## Simulation Data to Analyze
```json
{summary_data}
```

## Evaluation Criteria
You must evaluate the simulation on these dimensions:

1. **Quantitative Alignment**: Do the numerical metrics match theoretical expectations?
   - Compare actual values to expected ranges from academic literature
   - Flag significant deviations (>2 standard deviations from expected)

2. **Behavioral Patterns**: Does the price/agent dynamics follow expected patterns?
   - Correct sequence of phases (if applicable)
   - Appropriate timing and duration
   - Realistic feedback mechanisms

3. **Stylized Facts**: Does the simulation reproduce known empirical regularities?
   - Statistical properties should match real market data
   - Qualitative patterns should be recognizable

4. **Internal Consistency**: Are the metrics mutually consistent?
   - Cross-check related metrics
   - Flag contradictions

## Required Output Format
Respond with a JSON object (and ONLY a JSON object, no other text):
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "quantitative_alignment": {{
        "score": 0.0-1.0,
        "details": "explanation of quantitative fit"
    }},
    "behavioral_patterns": {{
        "score": 0.0-1.0,
        "details": "explanation of pattern consistency"
    }},
    "stylized_facts": {{
        "score": 0.0-1.0,
        "details": "explanation of stylized fact reproduction"
    }},
    "internal_consistency": {{
        "score": 0.0-1.0,
        "details": "explanation of cross-metric consistency"
    }},
    "overall_reasoning": "Comprehensive explanation of validity judgment",
    "suggestions": ["list", "of", "improvement", "suggestions"]
}}

Be rigorous and precise. Reference specific numbers from the data and theory.
"""

# Map scenarios to their theory sections
SCENARIO_THEORIES = {
    "AssetBubble": ASSET_BUBBLE_THEORY,
    "HerdEffect": HERD_EFFECT_THEORY,
    "FlashCrash": FLASH_CRASH_THEORY,
    "MarketCrash": MARKET_CRASH_THEORY,
    "MomentumEffect": MOMENTUM_EFFECT_THEORY,
    "ReversalEffect": REVERSAL_EFFECT_THEORY,
    "VolatilityClustering": VOLATILITY_CLUSTERING_THEORY,
    "ShortSqueeze": SHORT_SQUEEZE_THEORY,
    "LiquidityDryup": LIQUIDITY_DRYUP_THEORY,
    "DispositionEffect": DISPOSITION_EFFECT_THEORY,
    "EquityPremium": EQUITY_PREMIUM_THEORY,
}


class LLMValidator:
    """
    LLM-based simulation validator.

    Uses rigorous financial theory prompts to have an LLM evaluate
    whether simulation results are consistent with academic expectations.
    """

    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        llm_client: Optional[Any] = None,
    ):
        """
        Initialize LLM validator.

        Args:
            model: LLM model name (e.g., "gpt-4", "gpt-3.5-turbo")
            api_key: API key for LLM service (optional if using llm_client)
            llm_client: Pre-configured LLM client (optional)
        """
        self.model = model
        self.api_key = api_key
        self.llm_client = llm_client
        self._call_llm: Optional[Callable] = None

    def set_llm_caller(self, caller: Callable[[str], str]) -> None:
        """
        Set custom LLM calling function.

        Args:
            caller: Function that takes prompt string and returns response string
        """
        self._call_llm = caller

    def _default_llm_call(self, prompt: str) -> str:
        """Default LLM call using OpenAI API."""
        try:
            import openai

            if self.api_key:
                openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a quantitative finance expert.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            )
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {e}")

    def _build_prompt(self, scenario: str, summary_data: Dict[str, Any]) -> str:
        """
        Build validation prompt for a scenario.

        Args:
            scenario: Scenario name (e.g., "AssetBubble")
            summary_data: Simulation summary dictionary

        Returns:
            Formatted prompt string
        """
        # Get theory section for scenario
        theory = SCENARIO_THEORIES.get(scenario, "")
        if not theory:
            # Check for LLM variants (e.g., "AssetBubbleLLM" -> "AssetBubble")
            base_scenario = scenario.replace("LLM", "")
            theory = SCENARIO_THEORIES.get(
                base_scenario, "No specific theory available."
            )

        # Format summary data as pretty JSON
        summary_json = json.dumps(summary_data, indent=2, default=str)

        # Build prompt
        prompt = VALIDATION_PROMPT_TEMPLATE.format(
            scenario_name=scenario,
            theory_section=theory,
            summary_data=summary_json,
        )

        return prompt

    def _parse_response(self, response: str, scenario: str) -> LLMValidationResult:
        """
        Parse LLM response into structured result.

        Args:
            response: Raw LLM response string
            scenario: Scenario name

        Returns:
            LLMValidationResult
        """
        try:
            # Try to extract JSON from response
            # Handle cases where LLM adds text before/after JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")

            # Extract theory alignment scores
            theory_alignment = {
                "quantitative_alignment": data.get("quantitative_alignment", {}).get(
                    "score", 0
                ),
                "behavioral_patterns": data.get("behavioral_patterns", {}).get(
                    "score", 0
                ),
                "stylized_facts": data.get("stylized_facts", {}).get("score", 0),
                "internal_consistency": data.get("internal_consistency", {}).get(
                    "score", 0
                ),
            }

            # Build detailed reasoning
            reasoning_parts = []
            for key in [
                "quantitative_alignment",
                "behavioral_patterns",
                "stylized_facts",
                "internal_consistency",
            ]:
                if key in data and "details" in data[key]:
                    reasoning_parts.append(
                        f"**{key.replace('_', ' ').title()}**: {data[key]['details']}"
                    )

            if "overall_reasoning" in data:
                reasoning_parts.append(f"\n**Overall**: {data['overall_reasoning']}")

            return LLMValidationResult(
                scenario=scenario,
                is_valid=data.get("is_valid", False),
                confidence=float(data.get("confidence", 0.5)),
                reasoning="\n\n".join(reasoning_parts),
                theory_alignment=theory_alignment,
                suggestions=data.get("suggestions", []),
                raw_response=response,
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Return failed result with error info
            return LLMValidationResult(
                scenario=scenario,
                is_valid=False,
                confidence=0.0,
                reasoning=f"Failed to parse LLM response: {e}",
                theory_alignment={},
                suggestions=["Retry validation with different LLM parameters"],
                raw_response=response,
            )

    def validate(
        self,
        scenario: str,
        summary_data: Dict[str, Any],
    ) -> LLMValidationResult:
        """
        Validate simulation results using LLM.

        Args:
            scenario: Scenario name (e.g., "AssetBubble", "HerdEffect")
            summary_data: Simulation summary dictionary (from analysis.py)

        Returns:
            LLMValidationResult with judgment and reasoning
        """
        # Build prompt
        prompt = self._build_prompt(scenario, summary_data)

        # Call LLM
        caller = self._call_llm or self._default_llm_call
        response = caller(prompt)

        # Parse and return result
        return self._parse_response(response, scenario)

    def validate_batch(
        self,
        scenarios_data: Dict[str, Dict[str, Any]],
    ) -> Dict[str, LLMValidationResult]:
        """
        Validate multiple scenarios.

        Args:
            scenarios_data: Dict mapping scenario names to summary data

        Returns:
            Dict mapping scenario names to LLMValidationResults
        """
        results = {}
        for scenario, summary_data in scenarios_data.items():
            results[scenario] = self.validate(scenario, summary_data)
        return results


def validate_with_llm(
    scenario: str,
    summary_data: Dict[str, Any],
    model: str = "gpt-4",
    api_key: Optional[str] = None,
    llm_caller: Optional[Callable[[str], str]] = None,
) -> LLMValidationResult:
    """
    Convenience function to validate simulation with LLM.

    Args:
        scenario: Scenario name
        summary_data: Simulation summary dictionary
        model: LLM model name
        api_key: API key (optional)
        llm_caller: Custom LLM calling function (optional)

    Returns:
        LLMValidationResult

    Example:
        >>> summary = json.load(open("analysis/summary.json"))
        >>> result = validate_with_llm("AssetBubble", summary)
        >>> print(f"Valid: {result.is_valid}, Confidence: {result.confidence}")
    """
    validator = LLMValidator(model=model, api_key=api_key)
    if llm_caller:
        validator.set_llm_caller(llm_caller)
    return validator.validate(scenario, summary_data)


def get_theory_prompt(scenario: str) -> str:
    """
    Get the financial theory section for a scenario.

    Useful for inspection or custom prompt building.

    Args:
        scenario: Scenario name

    Returns:
        Theory text string
    """
    base_scenario = scenario.replace("LLM", "")
    return SCENARIO_THEORIES.get(base_scenario, SCENARIO_THEORIES.get(scenario, ""))


def list_supported_scenarios() -> List[str]:
    """
    List all scenarios with LLM validation support.

    Returns:
        List of scenario names
    """
    return list(SCENARIO_THEORIES.keys())
