"""Simulation Validation Module

Provides scenario-specific validation functions to assess whether simulation results
are reasonable, correct, and accurately capture the target financial phenomenon.

Each validator returns a ValidationResult containing:
- is_valid: Boolean indicating if simulation produced valid results
- score: Float 0-1 indicating accuracy/fit (1.0 = perfect match to theory)
- criteria: Dict of individual criterion scores
- interpretation: Detailed human-readable interpretation with financial context

Academic Standards:
    Each validation function is based on empirical stylized facts and academic
    literature defining expected behavior for each financial phenomenon.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    """Result of simulation validation."""

    scenario: str
    is_valid: bool
    score: float  # 0-1, overall fit score
    criteria: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "scenario": self.scenario,
            "is_valid": self.is_valid,
            "score": round(self.score, 4),
            "criteria": self.criteria,
            "interpretation": self.interpretation,
        }


# =============================================================================
# DETAILED INTERPRETATION BUILDERS
# =============================================================================


def _build_asset_bubble_interpretation(
    is_valid: bool,
    overall_score: float,
    max_deviation_pct: float,
    max_drawdown: float,
    peak_round: int,
    total_rounds: int,
    bubble_score: float,
    crash_score: float,
    formation_score: float,
) -> str:
    """Build detailed interpretation for AssetBubble validation."""
    lines = []

    # Overall verdict with context
    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== ASSET BUBBLE SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Bubble magnitude analysis
    lines.append("[1] BUBBLE MAGNITUDE ANALYSIS")
    lines.append(
        f"    Observed: Price deviated {max_deviation_pct:.1f}% from fundamental value"
    )
    lines.append(
        f"    Expected: 20-50% deviation (Kindleberger-Minsky bubble dynamics)"
    )
    lines.append(f"    Score: {bubble_score:.1%}")

    if max_deviation_pct < 15:
        lines.append(
            "    Assessment: INSUFFICIENT - Price deviation too small to constitute a bubble."
        )
        lines.append(
            "    In real markets, bubbles typically show 20%+ deviation from fundamentals."
        )
        lines.append(
            "    This may indicate: (a) agents too rational, (b) insufficient positive feedback,"
        )
        lines.append("    or (c) simulation rounds too few for bubble formation.")
    elif 15 <= max_deviation_pct < 20:
        lines.append("    Assessment: MARGINAL - Minor bubble formation detected.")
        lines.append(
            "    The deviation suggests early-stage speculative behavior but not a full bubble."
        )
    elif 20 <= max_deviation_pct <= 50:
        lines.append("    Assessment: OPTIMAL - Realistic bubble magnitude observed.")
        lines.append(
            "    This matches empirical evidence from historical bubbles (e.g., Dot-com: ~40%,"
        )
        lines.append(
            "    Housing 2006: ~30% above trend). The positive feedback loop is functioning."
        )
    elif 50 < max_deviation_pct <= 80:
        lines.append(
            "    Assessment: ELEVATED - Bubble larger than typical historical cases."
        )
        lines.append(
            "    While extreme bubbles do occur (e.g., Tulip Mania, Bitcoin 2017),"
        )
        lines.append("    consider if agent behavior is overly speculative.")
    else:
        lines.append("    Assessment: EXTREME - Unrealistically large bubble.")
        lines.append(
            "    Such extreme deviations (>80%) are rare even in historical manias."
        )
        lines.append(
            "    This may indicate model instability or unrealistic agent parameters."
        )
    lines.append("")

    # Crash analysis
    lines.append("[2] CRASH DYNAMICS ANALYSIS")
    lines.append(f"    Observed: Maximum drawdown of {max_drawdown:.1f}%")
    lines.append(f"    Expected: >15% drawdown following bubble peak (Minsky Moment)")
    lines.append(f"    Score: {crash_score:.1%}")

    if max_drawdown > -5:
        lines.append(
            "    Assessment: NO CRASH - No significant price decline observed."
        )
        lines.append(
            "    A proper bubble simulation should exhibit a crash phase where"
        )
        lines.append("    speculative prices collapse toward fundamental value.")
        lines.append(
            "    This may indicate: (a) simulation ended before crash, (b) missing panic mechanism."
        )
    elif -15 <= max_drawdown <= -5:
        lines.append(
            "    Assessment: MINOR CORRECTION - Small decline, not a true crash."
        )
        lines.append(
            "    Real bubble crashes (1929, 2000, 2008) show 30-50%+ declines."
        )
        lines.append(
            "    The simulation may lack sufficient sell pressure or panic dynamics."
        )
    elif -30 <= max_drawdown < -15:
        lines.append("    Assessment: MODERATE CRASH - Reasonable crash magnitude.")
        lines.append("    This is consistent with typical post-bubble corrections.")
        lines.append("    The panic selling cascade appears to be functioning.")
    else:
        lines.append("    Assessment: SEVERE CRASH - Strong crash dynamics observed.")
        lines.append(
            "    This matches major historical crashes (e.g., 1929: -89%, 2008: -57%)."
        )
        lines.append("    The fire-sale feedback mechanism is strongly present.")
    lines.append("")

    # Formation timing analysis
    lines.append("[3] BUBBLE FORMATION TIMING")
    lines.append(f"    Observed: Price peaked at round {peak_round} of {total_rounds}")
    lines.append(
        f"    Expected: Peak after round {int(total_rounds * 0.3)} (gradual formation)"
    )
    lines.append(f"    Score: {formation_score:.1%}")

    peak_pct = peak_round / total_rounds * 100
    if peak_pct < 20:
        lines.append(
            "    Assessment: TOO EARLY - Bubble formed and crashed too quickly."
        )
        lines.append("    Real bubbles take time to form as positive feedback builds.")
        lines.append(
            "    The simulation may have overly aggressive initial speculation."
        )
    elif 20 <= peak_pct < 40:
        lines.append(
            "    Assessment: EARLY BUT ACCEPTABLE - Relatively fast bubble formation."
        )
        lines.append("    Some bubbles do form quickly with strong catalysts.")
    elif 40 <= peak_pct <= 70:
        lines.append("    Assessment: OPTIMAL - Realistic bubble formation timeline.")
        lines.append("    The gradual build-up matches Kindleberger's phases:")
        lines.append("    Displacement → Boom → Euphoria → Critical → Crash.")
    else:
        lines.append("    Assessment: LATE PEAK - Bubble peaked late in simulation.")
        lines.append(
            "    The crash phase may be truncated. Consider longer simulation."
        )
    lines.append("")

    # Final summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            "The simulation successfully reproduces key features of asset bubble dynamics:"
        )
        lines.append(
            "positive feedback driving prices above fundamentals, followed by a crash."
        )
        lines.append(
            "The results are consistent with Kindleberger-Minsky theory and empirical stylized facts."
        )
    else:
        lines.append("The simulation does not fully capture expected bubble dynamics.")
        missing = []
        if bubble_score < 0.5:
            missing.append("insufficient price deviation")
        if crash_score < 0.5:
            missing.append("weak/missing crash")
        if formation_score < 0.5:
            missing.append("unrealistic timing")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores across criteria'}."
        )
        lines.append(
            "Consider adjusting agent parameters or extending simulation duration."
        )

    return "\n".join(lines)


def _build_herd_effect_interpretation(
    is_valid: bool,
    overall_score: float,
    avg_cv: float,
    avg_agreement: float,
    max_deviation: float,
    herding_episodes: int,
    total_rounds: int,
    cv_score: float,
    agreement_score: float,
    deviation_score: float,
    episode_score: float,
) -> str:
    """Build detailed interpretation for HerdEffect validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== HERD EFFECT SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Bid convergence analysis
    lines.append("[1] BID CONVERGENCE ANALYSIS (Information Cascade Indicator)")
    lines.append(f"    Observed: Coefficient of Variation (CV) = {avg_cv:.4f}")
    lines.append(f"    Expected: CV < 0.15 during herding (LSV 1992 measure)")
    lines.append(f"    Score: {cv_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if avg_cv < 0.10:
        lines.append("    STRONG CONVERGENCE - Agents' bids are highly clustered.")
        lines.append(
            "    This indicates a powerful information cascade where private signals"
        )
        lines.append(
            "    are being dominated by observed behavior. In real markets, such"
        )
        lines.append(
            "    tight clustering signals herd behavior (Bikhchandani et al., 1992)."
        )
    elif avg_cv < 0.15:
        lines.append("    MODERATE CONVERGENCE - Noticeable bid clustering detected.")
        lines.append(
            "    Agents are partially influenced by others' actions, suggesting"
        )
        lines.append("    an active but not overwhelming cascade mechanism.")
    elif avg_cv < 0.25:
        lines.append("    WEAK CONVERGENCE - Limited bid clustering.")
        lines.append(
            "    Agents maintain some independence in valuation, which may indicate"
        )
        lines.append(
            "    stronger private signals or weaker social observation weight."
        )
    else:
        lines.append("    NO CONVERGENCE - Bids remain dispersed.")
        lines.append("    The heterogeneity suggests agents are relying primarily on")
        lines.append("    private information rather than following the crowd.")
    lines.append("")

    # Directional agreement analysis
    lines.append("[2] DIRECTIONAL AGREEMENT ANALYSIS")
    lines.append(f"    Observed: Agreement ratio = {avg_agreement:.4f}")
    lines.append(f"    Expected: > 0.70 for significant herding")
    lines.append(f"    Score: {agreement_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if avg_agreement > 0.85:
        lines.append(
            "    EXTREME AGREEMENT - Agents are almost unanimously moving in the same direction."
        )
        lines.append(
            "    This mirrors panic buying/selling episodes in real markets where"
        )
        lines.append("    information cascades overwhelm rational price discovery.")
    elif avg_agreement > 0.70:
        lines.append("    STRONG AGREEMENT - Clear directional consensus among agents.")
        lines.append(
            "    This is consistent with empirical studies showing institutional"
        )
        lines.append(
            "    investors often exhibit 70-80% directional agreement during herding."
        )
    elif avg_agreement > 0.55:
        lines.append(
            "    MODERATE AGREEMENT - Some directional consensus, but with dissent."
        )
        lines.append("    This suggests a mix of trend-followers and contrarians.")
    else:
        lines.append("    LOW AGREEMENT - No clear directional consensus.")
        lines.append(
            "    Agents are acting relatively independently, which contradicts"
        )
        lines.append("    the herding hypothesis.")
    lines.append("")

    # Price deviation analysis
    lines.append("[3] PRICE DEVIATION FROM FUNDAMENTAL")
    lines.append(f"    Observed: Maximum deviation = {max_deviation:.2f}%")
    lines.append(f"    Expected: > 15% (herding should distort prices)")
    lines.append(f"    Score: {deviation_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if max_deviation > 25:
        lines.append(
            "    SUBSTANTIAL MISPRICING - Herding caused significant price distortion."
        )
        lines.append("    This demonstrates the market inefficiency that emerges when")
        lines.append("    information cascades dominate fundamental valuation.")
    elif max_deviation > 15:
        lines.append(
            "    MODERATE MISPRICING - Herding visibly affected price discovery."
        )
        lines.append("    The deviation is economically meaningful and consistent with")
        lines.append("    empirical observations of short-term market inefficiency.")
    elif max_deviation > 5:
        lines.append(
            "    MINOR MISPRICING - Some price distortion but within normal bounds."
        )
        lines.append("    Herding effects are present but insufficient to create")
        lines.append("    major market dislocations.")
    else:
        lines.append(
            "    NEGLIGIBLE MISPRICING - Price remained near fundamental value."
        )
        lines.append("    Either herding was too weak or countervailing forces")
        lines.append("    (e.g., arbitrageurs) kept prices efficient.")
    lines.append("")

    # Herding episodes analysis
    lines.append("[4] HERDING EPISODE DETECTION")
    lines.append(
        f"    Observed: {herding_episodes} episode(s) detected in {total_rounds} rounds"
    )
    lines.append(f"    Expected: >= 1 identifiable episode")
    lines.append(f"    Score: {episode_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if herding_episodes >= 3:
        lines.append(
            f"    MULTIPLE CASCADES - {herding_episodes} distinct herding episodes occurred."
        )
        lines.append(
            "    This pattern of repeated cascades matches real market behavior"
        )
        lines.append(
            "    where herding tends to recur, often triggered by news events."
        )
    elif herding_episodes >= 1:
        lines.append(
            f"    CASCADE DETECTED - {herding_episodes} herding episode(s) identified."
        )
        lines.append("    The simulation successfully generated the cascade dynamics")
        lines.append("    predicted by Bikhchandani's information cascade theory.")
    else:
        lines.append("    NO CASCADE - No clear herding episodes identified.")
        lines.append("    This suggests the cascade mechanism failed to trigger,")
        lines.append(
            "    possibly due to strong private signals or insufficient observation."
        )
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            "The simulation successfully reproduces herding behavior characteristics:"
        )
        lines.append(
            "- Agents exhibit coordinated behavior (bid convergence + directional agreement)"
        )
        lines.append("- Price deviates from fundamental due to cascade dynamics")
        lines.append(
            "- Results align with Bikhchandani-Hirshleifer-Welch (1992) cascade theory."
        )
    else:
        lines.append("The simulation does not fully capture expected herding dynamics.")
        missing = []
        if cv_score < 0.5:
            missing.append("insufficient bid convergence")
        if agreement_score < 0.5:
            missing.append("weak directional agreement")
        if deviation_score < 0.5:
            missing.append("minimal price deviation")
        if episode_score < 0.5:
            missing.append("no clear herding episodes")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append(
            "Consider: increasing observation weight, reducing private signal strength,"
        )
        lines.append("or extending simulation to allow cascade development.")

    return "\n".join(lines)


def _build_flash_crash_interpretation(
    is_valid: bool,
    overall_score: float,
    max_drawdown: float,
    crash_duration: int,
    recovery_detected: bool,
    total_rounds: int,
    severity_score: float,
    speed_score: float,
    recovery_score: float,
) -> str:
    """Build detailed interpretation for FlashCrash validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== FLASH CRASH SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Crash severity analysis
    lines.append("[1] CRASH SEVERITY ANALYSIS")
    lines.append(f"    Observed: Maximum drawdown = {max_drawdown:.2f}%")
    lines.append(f"    Expected: 5-20% drop (May 2010 Flash Crash: ~9%)")
    lines.append(f"    Score: {severity_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if max_drawdown < -20:
        lines.append(
            "    EXTREME SEVERITY - Drawdown exceeds typical flash crash magnitude."
        )
        lines.append(
            "    While the May 6, 2010 crash reached ~9%, some individual stocks"
        )
        lines.append(
            "    dropped >60%. This extreme level suggests strong feedback effects."
        )
        lines.append(
            "    In real markets, circuit breakers would likely trigger earlier."
        )
    elif max_drawdown < -10:
        lines.append(
            "    REALISTIC SEVERITY - Drawdown matches historical flash crash magnitude."
        )
        lines.append("    This is consistent with the May 2010 event where the DJIA")
        lines.append("    dropped ~9% before recovering. The liquidity withdrawal")
        lines.append("    mechanism is functioning as expected.")
    elif max_drawdown < -5:
        lines.append("    MODERATE SEVERITY - Noticeable crash but below major events.")
        lines.append("    This represents a significant but contained liquidity event,")
        lines.append("    similar to smaller intraday volatility spikes.")
    else:
        lines.append("    INSUFFICIENT SEVERITY - Drawdown too small for flash crash.")
        lines.append(
            "    Flash crashes by definition involve rapid, significant declines."
        )
        lines.append("    The simulation may lack sufficient HFT withdrawal dynamics.")
    lines.append("")

    # Crash speed analysis
    lines.append("[2] CRASH SPEED ANALYSIS")
    lines.append(f"    Observed: Peak-to-trough in {crash_duration} rounds")
    lines.append(f"    Expected: < 10 rounds (flash = rapid)")
    lines.append(f"    Score: {speed_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if crash_duration <= 3:
        lines.append("    EXTREMELY RAPID - Near-instantaneous price collapse.")
        lines.append("    This mimics the speed of algorithmic trading crashes where")
        lines.append("    HFT systems react in milliseconds. The cascade effect")
        lines.append("    propagated faster than human intervention could respond.")
    elif crash_duration <= 7:
        lines.append("    RAPID - Flash crash speed is realistic.")
        lines.append("    This matches the May 2010 event timeline where the")
        lines.append("    main decline occurred over approximately 5 minutes.")
        lines.append("    Liquidity dried up quickly as market makers withdrew.")
    elif crash_duration <= 15:
        lines.append("    MODERATE SPEED - Decline occurred gradually.")
        lines.append("    This is slower than a classic flash crash but still")
        lines.append("    represents rapid price adjustment. May indicate")
        lines.append("    some market-maker resilience.")
    else:
        lines.append("    TOO SLOW - Not a flash crash by definition.")
        lines.append("    Flash crashes are characterized by their speed.")
        lines.append("    A multi-round decline suggests a different mechanism")
        lines.append("    (possibly fundamental-driven market crash).")
    lines.append("")

    # Recovery analysis
    lines.append("[3] V-SHAPED RECOVERY ANALYSIS")
    lines.append(f"    Observed: Recovery detected = {recovery_detected}")
    lines.append(
        f"    Expected: V-shaped recovery (defining flash crash characteristic)"
    )
    lines.append(f"    Score: {recovery_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if recovery_detected:
        lines.append("    RECOVERY CONFIRMED - Price bounced back after crash.")
        lines.append("    This V-shaped recovery is the hallmark of flash crashes,")
        lines.append("    distinguishing them from fundamental-driven crashes.")
        lines.append("    It indicates the crash was a temporary liquidity event,")
        lines.append("    not a change in fundamental value. Value investors or")
        lines.append("    returning market makers provided stabilizing liquidity.")
    else:
        lines.append("    NO RECOVERY - Price did not recover post-crash.")
        lines.append("    Without recovery, this may not be a flash crash but rather")
        lines.append("    a fundamental-driven market decline. Flash crashes by")
        lines.append("    definition involve prices returning toward pre-crash levels")
        lines.append("    as liquidity is restored and mispricing is corrected.")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append("The simulation successfully reproduces flash crash dynamics:")
        lines.append(
            "- Rapid, significant price decline (liquidity withdrawal cascade)"
        )
        lines.append("- V-shaped recovery as stabilizing forces enter")
        lines.append(
            "- Results align with Kirilenko et al. (2017) flash crash microstructure."
        )
    else:
        lines.append(
            "The simulation does not fully capture expected flash crash characteristics."
        )
        missing = []
        if severity_score < 0.5:
            missing.append("insufficient crash magnitude")
        if speed_score < 0.5:
            missing.append("crash too slow")
        if recovery_score < 0.5:
            missing.append("no V-shaped recovery")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append(
            "Consider: enhancing HFT withdrawal dynamics, adding stop-loss triggers,"
        )
        lines.append("or implementing value investor agents for recovery.")

    return "\n".join(lines)


def _build_market_crash_interpretation(
    is_valid: bool,
    overall_score: float,
    max_drawdown: float,
    crash_duration: int,
    recovery_detected: bool,
    total_rounds: int,
    severity_score: float,
    duration_score: float,
    pattern_score: float,
) -> str:
    """Build detailed interpretation for MarketCrash validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== MARKET CRASH SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Crash severity analysis
    lines.append("[1] CRASH SEVERITY ANALYSIS")
    lines.append(f"    Observed: Maximum drawdown = {max_drawdown:.2f}%")
    lines.append(f"    Expected: 20-50% (1929: -89%, 2008: -57%, 1987: -34%)")
    lines.append(f"    Score: {severity_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if max_drawdown < -50:
        lines.append("    CATASTROPHIC - Drawdown rivals worst historical crashes.")
        lines.append("    This level of decline is consistent with 1929 or severe")
        lines.append("    emerging market crises where systemic failures occur.")
        lines.append("    The deleveraging cascade appears extremely severe.")
    elif max_drawdown < -30:
        lines.append("    SEVERE CRASH - Major market crash magnitude.")
        lines.append(
            "    This matches events like 2008 Financial Crisis (-57% peak-to-trough)"
        )
        lines.append("    or 1987 Black Monday (-34%). The Minsky Moment dynamics")
        lines.append(
            "    of forced selling and credit contraction are clearly present."
        )
    elif max_drawdown < -20:
        lines.append("    SIGNIFICANT CRASH - Substantial but contained decline.")
        lines.append("    This represents a meaningful market crash, though not")
        lines.append("    as severe as the worst historical episodes. May indicate")
        lines.append("    some stabilizing forces or circuit breakers.")
    elif max_drawdown < -10:
        lines.append("    CORRECTION - Moderate decline, borderline crash.")
        lines.append("    While significant, this is at the lower end of what")
        lines.append("    constitutes a 'crash'. Consider whether agent leverage")
        lines.append("    or panic dynamics are sufficiently strong.")
    else:
        lines.append("    INSUFFICIENT - Decline too small for market crash.")
        lines.append("    Market crashes by definition involve major declines.")
        lines.append("    The simulation may lack panic selling or leverage effects.")
    lines.append("")

    # Duration analysis
    lines.append("[2] CRASH DURATION ANALYSIS")
    lines.append(f"    Observed: Crash developed over {crash_duration} rounds")
    lines.append(f"    Expected: 10-30 rounds (unlike instant flash crashes)")
    lines.append(f"    Score: {duration_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if crash_duration < 5:
        lines.append("    TOO RAPID - This resembles a flash crash, not market crash.")
        lines.append(
            "    Market crashes involve prolonged decline with failed rallies,"
        )
        lines.append("    not instantaneous collapse. The distinction matters:")
        lines.append("    flash crashes are liquidity events, market crashes are")
        lines.append("    fundamental deleveraging events.")
    elif crash_duration < 10:
        lines.append("    RAPID BUT ACCEPTABLE - Quick crash development.")
        lines.append("    Some historical crashes (1987 Black Monday) did occur")
        lines.append("    relatively quickly, though most unfold over weeks/months.")
    elif crash_duration <= 30:
        lines.append("    REALISTIC DURATION - Crash timeline matches theory.")
        lines.append("    This allows for the typical pattern of failed rallies,")
        lines.append("    continued margin calls, and cascading deleveraging")
        lines.append("    described by Brunnermeier (2009).")
    else:
        lines.append("    PROLONGED - Extended crash duration.")
        lines.append("    Very long crashes do occur (e.g., 2000-2002 dot-com bust")
        lines.append("    took 2+ years). This represents deep structural adjustment.")
    lines.append("")

    # Recovery pattern analysis
    lines.append("[3] RECOVERY PATTERN ANALYSIS")
    lines.append(f"    Observed: Recovery detected = {recovery_detected}")
    lines.append(f"    Expected: L-shaped or U-shaped (slow/no recovery)")
    lines.append(f"    Score: {pattern_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if not recovery_detected:
        lines.append("    L-SHAPED PATTERN - No recovery within simulation.")
        lines.append("    This is characteristic of market crashes where fundamental")
        lines.append("    damage requires extended repair (debt restructuring,")
        lines.append(
            "    recapitalization). Differs from V-shaped flash crash recovery."
        )
        lines.append("    The 2008 crash took years to recover from.")
    else:
        lines.append("    RECOVERY DETECTED - Some price rebound occurred.")
        lines.append("    Market crashes typically have slow U-shaped recoveries")
        lines.append("    rather than V-shaped. If recovery was quick, verify")
        lines.append("    this isn't actually flash crash behavior.")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append("The simulation successfully reproduces market crash dynamics:")
        lines.append("- Severe price decline driven by forced selling/deleveraging")
        lines.append("- Extended crash duration (not instantaneous)")
        lines.append("- Results align with Brunnermeier (2009) deleveraging theory.")
    else:
        lines.append("The simulation does not fully capture expected crash dynamics.")
        missing = []
        if severity_score < 0.5:
            missing.append("insufficient crash magnitude")
        if duration_score < 0.5:
            missing.append("unrealistic timeline")
        if pattern_score < 0.5:
            missing.append("wrong recovery pattern")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append(
            "Consider: increasing agent leverage, adding margin call triggers,"
        )
        lines.append("or implementing fire sale dynamics.")

    return "\n".join(lines)


def _build_momentum_effect_interpretation(
    is_valid: bool,
    overall_score: float,
    acf_lag1: float,
    avg_trend_duration: float,
    positive_momentum: bool,
    total_rounds: int,
    acf_score: float,
    trend_score: float,
    direction_score: float,
) -> str:
    """Build detailed interpretation for MomentumEffect validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== MOMENTUM EFFECT SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Autocorrelation analysis
    lines.append("[1] RETURN AUTOCORRELATION ANALYSIS")
    lines.append(f"    Observed: ACF(1) = {acf_lag1:.4f}")
    lines.append(f"    Expected: Positive ACF > 0.05 (Jegadeesh & Titman, 1993)")
    lines.append(f"    Score: {acf_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if acf_lag1 > 0.15:
        lines.append("    STRONG MOMENTUM - High positive autocorrelation.")
        lines.append(
            "    Returns strongly predict future returns in the same direction."
        )
        lines.append("    This exceeds typical empirical levels and suggests powerful")
        lines.append("    trend-following behavior among agents.")
    elif acf_lag1 > 0.05:
        lines.append("    MODERATE MOMENTUM - Significant positive autocorrelation.")
        lines.append("    This matches empirical findings: Jegadeesh & Titman (1993)")
        lines.append(
            "    documented monthly return autocorrelations of 3-8% at 3-12 month horizons."
        )
        lines.append(
            "    Underreaction to information is generating return continuation."
        )
    elif acf_lag1 > 0:
        lines.append("    WEAK MOMENTUM - Small positive autocorrelation.")
        lines.append(
            "    Some momentum is present but weaker than typical empirical levels."
        )
        lines.append(
            "    Agents may be partially incorporating information efficiently."
        )
    else:
        lines.append("    NO MOMENTUM - Zero or negative autocorrelation.")
        lines.append(f"    ACF = {acf_lag1:.4f} suggests no return continuation.")
        lines.append("    This contradicts the momentum effect literature.")
        lines.append("    Agents may be overreacting rather than underreacting.")
    lines.append("")

    # Trend duration analysis
    lines.append("[2] TREND PERSISTENCE ANALYSIS")
    lines.append(
        f"    Observed: Average trend duration = {avg_trend_duration:.1f} rounds"
    )
    lines.append(f"    Expected: 5-20 rounds (short-term momentum, not reversal)")
    lines.append(f"    Score: {trend_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if avg_trend_duration > 20:
        lines.append("    EXTENDED TRENDS - Very long trend persistence.")
        lines.append("    While momentum exists, such long trends may indicate")
        lines.append("    permanent price changes rather than temporary momentum.")
        lines.append("    Eventually, reversal should dominate (De Bondt & Thaler).")
    elif avg_trend_duration >= 5:
        lines.append("    REALISTIC TREND DURATION - Matches momentum theory.")
        lines.append("    Empirical momentum strategies typically use 3-12 month")
        lines.append("    formation periods. This suggests appropriate underreaction")
        lines.append("    dynamics with eventual mean reversion.")
    elif avg_trend_duration >= 2:
        lines.append("    SHORT TRENDS - Brief momentum periods.")
        lines.append("    Trends reverse quickly, suggesting either rapid information")
        lines.append("    incorporation or strong contrarian forces.")
    else:
        lines.append("    NO CLEAR TRENDS - Random walk behavior.")
        lines.append("    Prices appear to follow a random walk without persistence.")
        lines.append("    This is inconsistent with momentum effect literature.")
    lines.append("")

    # Direction analysis
    lines.append("[3] MOMENTUM DIRECTION ANALYSIS")
    lines.append(f"    Observed: Positive momentum present = {positive_momentum}")
    lines.append(f"    Expected: True (past winners should continue outperforming)")
    lines.append(f"    Score: {direction_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if positive_momentum:
        lines.append("    CORRECT DIRECTION - Past winners continue outperforming.")
        lines.append("    This is the defining characteristic of momentum:")
        lines.append("    'buy winners, sell losers' generates positive returns.")
        lines.append("    Behavioral explanation: investors underreact to news.")
    else:
        lines.append("    WRONG DIRECTION - No winner continuation.")
        lines.append("    Momentum is defined as past performance predicting future")
        lines.append("    performance in the SAME direction. Without this,")
        lines.append("    the phenomenon is not momentum but possibly reversal.")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append("The simulation successfully reproduces momentum effect:")
        lines.append("- Positive return autocorrelation (winners keep winning)")
        lines.append("- Reasonable trend persistence before reversal")
        lines.append(
            "- Results align with Jegadeesh-Titman (1993) underreaction theory."
        )
    else:
        lines.append(
            "The simulation does not fully capture expected momentum dynamics."
        )
        missing = []
        if acf_score < 0.5:
            missing.append("weak/negative autocorrelation")
        if trend_score < 0.5:
            missing.append("abnormal trend duration")
        if direction_score < 0.5:
            missing.append("wrong momentum direction")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append(
            "Consider: strengthening trend-following behavior, slowing information"
        )
        lines.append("diffusion, or reducing contrarian agent proportion.")

    return "\n".join(lines)


def _build_reversal_effect_interpretation(
    is_valid: bool,
    overall_score: float,
    long_lag_acf: float,
    mean_reversion_detected: bool,
    reversal_magnitude: float,
    acf_score: float,
    reversion_score: float,
    magnitude_score: float,
) -> str:
    """Build detailed interpretation for ReversalEffect validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== REVERSAL EFFECT SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Long-lag autocorrelation analysis
    lines.append("[1] LONG-LAG AUTOCORRELATION ANALYSIS")
    lines.append(f"    Observed: ACF at long lag = {long_lag_acf:.4f}")
    lines.append(f"    Expected: Negative ACF < -0.05 (De Bondt & Thaler, 1985)")
    lines.append(f"    Score: {acf_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if long_lag_acf < -0.15:
        lines.append("    STRONG REVERSAL - High negative long-lag autocorrelation.")
        lines.append("    Prices strongly mean-revert, correcting past overreactions.")
        lines.append("    This exceeds typical empirical levels but demonstrates")
        lines.append("    the overreaction correction mechanism clearly.")
    elif long_lag_acf < -0.05:
        lines.append("    MODERATE REVERSAL - Significant negative autocorrelation.")
        lines.append("    This matches empirical evidence: De Bondt & Thaler (1985)")
        lines.append("    found 3-5 year losers outperforming winners by 25-30%.")
        lines.append("    The market corrects previous overreaction to news.")
    elif long_lag_acf < 0:
        lines.append("    WEAK REVERSAL - Small negative autocorrelation.")
        lines.append("    Some mean reversion present but weaker than expected.")
        lines.append("    Overreaction may be less pronounced than theoretical models.")
    else:
        lines.append("    NO REVERSAL - Zero or positive long-lag autocorrelation.")
        lines.append(f"    ACF = {long_lag_acf:.4f} suggests no mean reversion.")
        lines.append("    This contradicts the reversal effect literature.")
        lines.append("    The market may not be correcting overreactions.")
    lines.append("")

    # Mean reversion analysis
    lines.append("[2] MEAN REVERSION TO FUNDAMENTAL")
    lines.append(f"    Observed: Mean reversion detected = {mean_reversion_detected}")
    lines.append(f"    Expected: True (prices should return toward fundamental)")
    lines.append(f"    Score: {reversion_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if mean_reversion_detected:
        lines.append(
            "    REVERSION CONFIRMED - Price moved back toward fundamental value."
        )
        lines.append(
            "    This is the economic essence of reversal: overreaction causes"
        )
        lines.append("    mispricing, which is subsequently corrected as the market")
        lines.append("    recognizes the true fundamental value.")
    else:
        lines.append("    NO REVERSION - Price did not return to fundamental.")
        lines.append("    Without mean reversion, the reversal effect is incomplete.")
        lines.append("    The simulation may have permanent price shocks rather than")
        lines.append("    temporary overreaction patterns.")
    lines.append("")

    # Reversal magnitude analysis
    lines.append("[3] REVERSAL MAGNITUDE ANALYSIS")
    lines.append(f"    Observed: Reversal magnitude = {reversal_magnitude:.2f}%")
    lines.append(f"    Expected: 5-15% correction of previous deviation")
    lines.append(f"    Score: {magnitude_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if reversal_magnitude > 15:
        lines.append("    STRONG REVERSAL - Large price correction occurred.")
        lines.append("    This indicates significant prior overreaction that")
        lines.append("    was substantially corrected. Matches more extreme")
        lines.append("    historical reversals.")
    elif reversal_magnitude > 5:
        lines.append("    MODERATE REVERSAL - Meaningful price correction.")
        lines.append("    This aligns with typical contrarian strategy returns,")
        lines.append("    where past losers outperform past winners by 5-10% annually.")
    elif reversal_magnitude > 0:
        lines.append("    WEAK REVERSAL - Small price correction.")
        lines.append("    Some reversal present but economically modest.")
        lines.append("    May indicate limited initial overreaction.")
    else:
        lines.append("    NO REVERSAL - No price correction detected.")
        lines.append("    Without meaningful reversal magnitude, the effect is absent.")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append("The simulation successfully reproduces reversal effect:")
        lines.append("- Negative long-lag autocorrelation (past losers outperform)")
        lines.append("- Price mean-reverts toward fundamental value")
        lines.append(
            "- Results align with De Bondt-Thaler (1985) overreaction hypothesis."
        )
    else:
        lines.append(
            "The simulation does not fully capture expected reversal dynamics."
        )
        missing = []
        if acf_score < 0.5:
            missing.append("weak/positive long-lag ACF")
        if reversion_score < 0.5:
            missing.append("no mean reversion")
        if magnitude_score < 0.5:
            missing.append("insufficient reversal magnitude")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append(
            "Consider: increasing overreaction parameters, adding contrarian agents,"
        )
        lines.append("or extending simulation to allow long-horizon effects.")

    return "\n".join(lines)


def _build_volatility_clustering_interpretation(
    is_valid: bool,
    overall_score: float,
    return_acf: float,
    sq_return_acf: float,
    clustering_ratio: float,
    return_score: float,
    sq_return_score: float,
    ratio_score: float,
) -> str:
    """Build detailed interpretation for VolatilityClustering validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== VOLATILITY CLUSTERING SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Return ACF analysis
    lines.append("[1] RETURN AUTOCORRELATION ANALYSIS (Should be ~0)")
    lines.append(f"    Observed: Return ACF(1) = {return_acf:.4f}")
    lines.append(f"    Expected: |ACF| < 0.1 (market efficiency)")
    lines.append(f"    Score: {return_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if abs(return_acf) < 0.05:
        lines.append("    NEAR-ZERO - Returns are essentially unpredictable.")
        lines.append("    This is the first stylized fact of Cont (2001):")
        lines.append("    returns show negligible autocorrelation, consistent with")
        lines.append("    market efficiency where price changes are random.")
    elif abs(return_acf) < 0.10:
        lines.append("    LOW - Returns show minimal predictability.")
        lines.append("    Some deviation from perfect efficiency but within")
        lines.append("    acceptable bounds for realistic markets.")
    else:
        lines.append(f"    ANOMALOUS - Return ACF = {return_acf:.4f} too high.")
        lines.append("    Returns should be unpredictable; high ACF suggests")
        lines.append("    momentum/reversal patterns that contradict")
        lines.append("    the volatility clustering focus.")
    lines.append("")

    # Squared return ACF analysis
    lines.append("[2] SQUARED RETURN AUTOCORRELATION (Should be > 0)")
    lines.append(f"    Observed: Squared Return ACF(1) = {sq_return_acf:.4f}")
    lines.append(f"    Expected: ACF > 0.10 (volatility persistence)")
    lines.append(f"    Score: {sq_return_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if sq_return_acf > 0.20:
        lines.append("    STRONG CLUSTERING - High volatility persistence.")
        lines.append("    'Large changes tend to be followed by large changes'")
        lines.append("    (Mandelbrot, 1963). This matches GARCH dynamics where")
        lines.append(
            "    σ²_t depends on past σ² and shocks. Volatility is predictable."
        )
    elif sq_return_acf > 0.10:
        lines.append("    MODERATE CLUSTERING - Significant volatility persistence.")
        lines.append("    This matches empirical evidence from financial markets:")
        lines.append("    Bollerslev (1986) GARCH models typically show α + β > 0.9.")
        lines.append("    High/low volatility regimes persist over time.")
    elif sq_return_acf > 0:
        lines.append("    WEAK CLUSTERING - Some volatility persistence.")
        lines.append("    Squared returns show mild predictability, suggesting")
        lines.append("    some GARCH-like dynamics but weaker than typical markets.")
    else:
        lines.append("    NO CLUSTERING - Volatility is not persistent.")
        lines.append(f"    Squared return ACF = {sq_return_acf:.4f} is negative/zero.")
        lines.append("    This contradicts one of the most robust stylized facts.")
    lines.append("")

    # Clustering ratio analysis
    lines.append("[3] CLUSTERING RATIO ANALYSIS")
    lines.append(
        f"    Observed: Ratio = {clustering_ratio:.2f} (sq_ACF / |return_ACF|)"
    )
    lines.append(f"    Expected: Ratio > 2 (volatility more predictable than returns)")
    lines.append(f"    Score: {ratio_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if clustering_ratio > 5:
        lines.append("    EXCELLENT SEPARATION - Clear stylized fact reproduction.")
        lines.append("    Returns are random, but volatility is highly predictable.")
        lines.append("    This is the defining characteristic that makes")
        lines.append("    GARCH models so successful in financial modeling.")
    elif clustering_ratio > 2:
        lines.append("    GOOD SEPARATION - Volatility more predictable than returns.")
        lines.append("    The simulation correctly captures the asymmetry:")
        lines.append("    you cannot predict return direction, but you can")
        lines.append("    predict return magnitude.")
    elif clustering_ratio > 1:
        lines.append("    WEAK SEPARATION - Marginal effect.")
        lines.append("    Both returns and volatility show similar predictability,")
        lines.append("    which partially contradicts the stylized facts.")
    else:
        lines.append("    NO SEPARATION - Stylized fact not reproduced.")
        lines.append("    Returns should be unpredictable while volatility is not.")
        lines.append("    The simulation does not capture this key asymmetry.")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append("The simulation successfully reproduces volatility clustering:")
        lines.append("- Returns near-unpredictable (efficient market)")
        lines.append("- Squared returns highly autocorrelated (GARCH dynamics)")
        lines.append(
            "- Results align with Bollerslev (1986) and Cont (2001) stylized facts."
        )
    else:
        lines.append(
            "The simulation does not fully capture expected volatility dynamics."
        )
        missing = []
        if return_score < 0.5:
            missing.append("returns too predictable")
        if sq_return_score < 0.5:
            missing.append("weak volatility persistence")
        if ratio_score < 0.5:
            missing.append("poor stylized fact separation")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append("Consider: adding heterogeneous reaction speeds, implementing")
        lines.append(
            "GARCH-like variance dynamics, or including news arrival clustering."
        )

    return "\n".join(lines)


def _build_disposition_effect_interpretation(
    is_valid: bool,
    overall_score: float,
    pgr: float,
    plr: float,
    disposition_coefficient: float,
    pgr_score: float,
    asymmetry_score: float,
    coefficient_score: float,
) -> str:
    """Build detailed interpretation for DispositionEffect validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== DISPOSITION EFFECT SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # PGR analysis
    lines.append("[1] PROPORTION OF GAINS REALIZED (PGR) ANALYSIS")
    lines.append(f"    Observed: PGR = {pgr:.4f}")
    lines.append(f"    Expected: PGR > 0.20 (investors sell winners)")
    lines.append(f"    Score: {pgr_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    lines.append("    PGR measures: (Realized Gains) / (Realized Gains + Paper Gains)")
    if pgr > 0.40:
        lines.append("    HIGH PGR - Investors frequently realize gains.")
        lines.append("    Strong evidence of 'selling winners too early' behavior.")
        lines.append("    Prospect theory explains this: risk-averse in gains,")
        lines.append("    investors lock in profits to avoid potential loss.")
    elif pgr > 0.20:
        lines.append("    MODERATE PGR - Normal gain-taking behavior.")
        lines.append("    Consistent with empirical findings (Odean 1998)")
        lines.append("    where retail investors have PGR around 0.15-0.25.")
    elif pgr > 0:
        lines.append("    LOW PGR - Infrequent gain realization.")
        lines.append("    Investors may be holding winners, which contradicts")
        lines.append("    the disposition effect hypothesis.")
    else:
        lines.append("    ZERO PGR - No gain realization observed.")
        lines.append(
            "    Without realized gains, disposition effect cannot be measured."
        )
    lines.append("")

    # Asymmetry analysis
    lines.append("[2] PGR vs PLR ASYMMETRY (Core Disposition Test)")
    lines.append(f"    Observed: PGR = {pgr:.4f}, PLR = {plr:.4f}")
    lines.append(f"    Expected: PGR > PLR (sell winners, hold losers)")
    lines.append(f"    Score: {asymmetry_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    lines.append("    The disposition effect = systematic tendency to:")
    lines.append("    - Sell winners too early (high PGR)")
    lines.append("    - Hold losers too long (low PLR)")
    if pgr > plr:
        ratio = pgr / plr if plr > 0 else float("inf")
        lines.append(f"    DISPOSITION CONFIRMED - PGR/PLR ratio = {ratio:.2f}")
        lines.append("    Investors are more likely to realize gains than losses.")
        lines.append("    This matches Kahneman-Tversky prospect theory:")
        lines.append("    - Risk-averse in gains (sell to lock in profit)")
        lines.append("    - Risk-seeking in losses (hold hoping for recovery)")
    elif pgr == plr:
        lines.append("    NO ASYMMETRY - PGR equals PLR.")
        lines.append("    Investors treat gains and losses symmetrically.")
        lines.append(
            "    This is rational behavior but contradicts disposition effect."
        )
    else:
        lines.append("    REVERSE DISPOSITION - PLR > PGR.")
        lines.append("    Investors realize losses more readily than gains.")
        lines.append("    This is tax-efficient but opposite to disposition effect.")
        lines.append(
            "    May indicate sophisticated investors or institutional traders."
        )
    lines.append("")

    # Disposition coefficient analysis
    lines.append("[3] DISPOSITION COEFFICIENT (PGR - PLR)")
    lines.append(f"    Observed: Coefficient = {disposition_coefficient:.4f}")
    lines.append(f"    Expected: > 0.05 (meaningful disposition effect)")
    lines.append(f"    Score: {coefficient_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if disposition_coefficient > 0.15:
        lines.append("    STRONG EFFECT - Large disposition coefficient.")
        lines.append("    The asymmetry between gain/loss realization is pronounced.")
        lines.append("    This exceeds typical empirical findings and suggests")
        lines.append("    agents exhibit strong loss aversion (λ >> 2).")
    elif disposition_coefficient > 0.05:
        lines.append("    MODERATE EFFECT - Meaningful disposition coefficient.")
        lines.append("    This aligns with Odean (1998) findings where investors")
        lines.append("    show PGR-PLR differences of 5-15 percentage points.")
        lines.append("    Loss aversion (λ ≈ 2.25) is driving behavior.")
    elif disposition_coefficient > 0:
        lines.append("    WEAK EFFECT - Small positive coefficient.")
        lines.append("    Some disposition effect present but economically minor.")
        lines.append("    Agents may have weaker loss aversion than typical investors.")
    else:
        lines.append("    NO/REVERSE EFFECT - Non-positive coefficient.")
        lines.append("    Without PGR > PLR, the disposition effect is absent.")
        lines.append("    Agents are not exhibiting prospect theory behavior.")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append("The simulation successfully reproduces disposition effect:")
        lines.append("- PGR > PLR (sell winners, hold losers)")
        lines.append("- Positive disposition coefficient")
        lines.append("- Results align with Shefrin-Statman (1985) and Odean (1998).")
    else:
        lines.append(
            "The simulation does not fully capture expected disposition dynamics."
        )
        missing = []
        if pgr_score < 0.5:
            missing.append("low gain realization")
        if asymmetry_score < 0.5:
            missing.append("no PGR > PLR asymmetry")
        if coefficient_score < 0.5:
            missing.append("weak/negative disposition coefficient")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append("Consider: implementing prospect theory utility function,")
        lines.append("adding reference point tracking, or increasing loss aversion λ.")

    return "\n".join(lines)


def _build_short_squeeze_interpretation(
    is_valid: bool,
    overall_score: float,
    max_price_spike: float,
    spike_speed: int,
    feedback_detected: bool,
    spike_score: float,
    speed_score: float,
    feedback_score: float,
) -> str:
    """Build detailed interpretation for ShortSqueeze validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== SHORT SQUEEZE SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Price spike analysis
    lines.append("[1] PRICE SPIKE ANALYSIS")
    lines.append(f"    Observed: Maximum price spike = {max_price_spike:.1f}%")
    lines.append(f"    Expected: > 50% (GameStop 2021: ~1,700%, VW 2008: ~400%)")
    lines.append(f"    Score: {spike_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if max_price_spike > 200:
        lines.append("    EXTREME SPIKE - Massive price increase.")
        lines.append("    This rivals the most dramatic historical squeezes.")
        lines.append("    The supply-demand imbalance from short covering")
        lines.append("    created extreme upward pressure with limited float.")
    elif max_price_spike > 100:
        lines.append("    STRONG SPIKE - Major price surge.")
        lines.append("    This represents a significant short squeeze event.")
        lines.append("    Short sellers faced substantial losses on margin calls,")
        lines.append("    forcing covering that amplified the rally.")
    elif max_price_spike > 50:
        lines.append("    MODERATE SPIKE - Noticeable price surge.")
        lines.append("    A meaningful squeeze occurred, though less dramatic")
        lines.append("    than famous cases. Short covering pressure was present")
        lines.append("    but perhaps limited by lower short interest.")
    else:
        lines.append("    WEAK SPIKE - Insufficient price increase.")
        lines.append("    Short squeezes typically produce >50% spikes.")
        lines.append("    The simulation may lack sufficient short interest")
        lines.append("    or coordinated buying pressure.")
    lines.append("")

    # Spike speed analysis
    lines.append("[2] SPIKE SPEED ANALYSIS")
    lines.append(f"    Observed: Spike developed over {spike_speed} rounds")
    lines.append(f"    Expected: < 15 rounds (rapid, not gradual)")
    lines.append(f"    Score: {speed_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if spike_speed <= 5:
        lines.append("    EXTREMELY RAPID - Near-vertical price spike.")
        lines.append("    Short covering cascade occurred very quickly.")
        lines.append("    This matches the GameStop squeeze where prices")
        lines.append("    exploded over a few trading days.")
    elif spike_speed <= 10:
        lines.append("    RAPID - Fast price acceleration.")
        lines.append("    The squeeze dynamics unfolded quickly as margin calls")
        lines.append("    triggered forced covering in a compressed timeframe.")
    elif spike_speed <= 15:
        lines.append("    MODERATE SPEED - Reasonable squeeze timeline.")
        lines.append("    Some squeezes develop over 1-2 weeks as different")
        lines.append("    short sellers hit margin thresholds at different times.")
    else:
        lines.append("    SLOW - Gradual price increase.")
        lines.append("    This is more characteristic of fundamental appreciation")
        lines.append(
            "    than a squeeze. True squeezes involve rapid, forced covering."
        )
    lines.append("")

    # Feedback loop analysis
    lines.append("[3] FEEDBACK LOOP DETECTION")
    lines.append(f"    Observed: Positive feedback detected = {feedback_detected}")
    lines.append(f"    Expected: True (price rise → margin calls → more covering)")
    lines.append(f"    Score: {feedback_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if feedback_detected:
        lines.append("    FEEDBACK CONFIRMED - Self-reinforcing dynamics present.")
        lines.append("    The key short squeeze mechanism is functioning:")
        lines.append("    Price increase → shorts face losses → margin calls →")
        lines.append("    forced buying → more price increase → repeat.")
        lines.append("    This positive feedback distinguishes squeezes from")
        lines.append("    normal price appreciation.")
    else:
        lines.append("    NO FEEDBACK - Linear rather than exponential dynamics.")
        lines.append("    Without the feedback loop, this is not a true squeeze.")
        lines.append("    Squeezes require the self-reinforcing mechanism of")
        lines.append("    forced covering driving prices even higher.")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append("The simulation successfully reproduces short squeeze dynamics:")
        lines.append("- Significant price spike from supply-demand imbalance")
        lines.append("- Rapid price acceleration from forced covering")
        lines.append("- Positive feedback loop between price and short covering.")
    else:
        lines.append("The simulation does not fully capture expected squeeze dynamics.")
        missing = []
        if spike_score < 0.5:
            missing.append("insufficient price spike")
        if speed_score < 0.5:
            missing.append("spike too slow")
        if feedback_score < 0.5:
            missing.append("no feedback loop")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append(
            "Consider: increasing short interest, adding margin call triggers,"
        )
        lines.append("or implementing coordinated buying mechanism.")

    return "\n".join(lines)


def _build_liquidity_dryup_interpretation(
    is_valid: bool,
    overall_score: float,
    spread_increase: float,
    depth_decrease: float,
    impact_increase: float,
    spread_score: float,
    depth_score: float,
    impact_score: float,
) -> str:
    """Build detailed interpretation for LiquidityDryup validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== LIQUIDITY DRY-UP SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Spread analysis
    lines.append("[1] BID-ASK SPREAD ANALYSIS")
    lines.append(
        f"    Observed: Spread increased by {spread_increase:.1f}x during stress"
    )
    lines.append(f"    Expected: 3-10x increase (Brunnermeier-Pedersen, 2009)")
    lines.append(f"    Score: {spread_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if spread_increase > 10:
        lines.append("    EXTREME WIDENING - Spreads expanded dramatically.")
        lines.append("    Market makers almost completely withdrew liquidity.")
        lines.append("    This matches severe stress episodes like 2008 or")
        lines.append("    March 2020 COVID crash where spreads blew out.")
    elif spread_increase > 5:
        lines.append("    SIGNIFICANT WIDENING - Major spread expansion.")
        lines.append("    This aligns with Grossman-Miller (1988): market makers")
        lines.append(
            "    require higher compensation for inventory risk during stress."
        )
        lines.append("    Liquidity provision becomes expensive.")
    elif spread_increase > 3:
        lines.append("    MODERATE WIDENING - Noticeable spread increase.")
        lines.append("    Some liquidity withdrawal occurred, consistent with")
        lines.append("    market maker risk management. Trading costs rose.")
    elif spread_increase > 1.5:
        lines.append("    MILD WIDENING - Small spread increase.")
        lines.append("    Liquidity reduced but market makers largely stayed.")
        lines.append("    This suggests stress was not severe enough.")
    else:
        lines.append("    NO WIDENING - Spreads remained stable.")
        lines.append("    Without spread widening, no liquidity dry-up occurred.")
        lines.append("    Market makers maintained normal provision.")
    lines.append("")

    # Depth analysis
    lines.append("[2] MARKET DEPTH ANALYSIS")
    lines.append(f"    Observed: Depth decreased by {depth_decrease:.1f}%")
    lines.append(f"    Expected: 50-90% reduction at each price level")
    lines.append(f"    Score: {depth_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if depth_decrease > 80:
        lines.append("    SEVERE DEPTH LOSS - Order book nearly empty.")
        lines.append("    Market makers almost completely withdrew quotes.")
        lines.append("    Even small orders would cause large price impact.")
        lines.append("    This is the essence of liquidity dry-up.")
    elif depth_decrease > 50:
        lines.append("    SIGNIFICANT DEPTH LOSS - Major reduction in quotes.")
        lines.append("    Brunnermeier-Pedersen illiquidity spiral at work:")
        lines.append("    price drop → margin constraints → withdrawal → less depth.")
    elif depth_decrease > 30:
        lines.append("    MODERATE DEPTH LOSS - Partial withdrawal.")
        lines.append("    Some market makers remained active but reduced size.")
        lines.append("    Liquidity provision became more cautious.")
    else:
        lines.append("    MINIMAL DEPTH LOSS - Depth largely maintained.")
        lines.append("    Market makers continued providing liquidity.")
        lines.append("    This contradicts expected dry-up dynamics.")
    lines.append("")

    # Price impact analysis
    lines.append("[3] PRICE IMPACT ANALYSIS")
    lines.append(f"    Observed: Price impact increased by {impact_increase:.1f}x")
    lines.append(f"    Expected: 3-5x increase in impact per unit volume")
    lines.append(f"    Score: {impact_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    if impact_increase > 5:
        lines.append("    EXTREME IMPACT - Orders move prices dramatically.")
        lines.append("    The Amihud (2002) illiquidity measure spiked.")
        lines.append("    Trading became very expensive as thin order book")
        lines.append("    meant even small trades moved prices significantly.")
    elif impact_increase > 3:
        lines.append("    HIGH IMPACT - Significant price sensitivity.")
        lines.append("    This matches empirical findings during crises:")
        lines.append("    the same trade size has 3-5x larger impact when")
        lines.append("    liquidity is withdrawn.")
    elif impact_increase > 1.5:
        lines.append("    MODERATE IMPACT - Some price sensitivity increase.")
        lines.append("    Orders had more impact than normal but not severely.")
        lines.append("    Partial liquidity dry-up scenario.")
    else:
        lines.append("    NORMAL IMPACT - No significant change.")
        lines.append("    Without increased price impact, liquidity appears stable.")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            "The simulation successfully reproduces liquidity dry-up dynamics:"
        )
        lines.append("- Bid-ask spreads widened significantly")
        lines.append("- Market depth declined as makers withdrew")
        lines.append("- Price impact increased substantially")
        lines.append(
            "- Results align with Brunnermeier-Pedersen (2009) illiquidity spiral."
        )
    else:
        lines.append(
            "The simulation does not fully capture expected liquidity dynamics."
        )
        missing = []
        if spread_score < 0.5:
            missing.append("insufficient spread widening")
        if depth_score < 0.5:
            missing.append("depth remained stable")
        if impact_score < 0.5:
            missing.append("price impact unchanged")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append("Consider: implementing market maker inventory limits, adding")
        lines.append("volatility-based withdrawal triggers, or funding constraints.")

    return "\n".join(lines)


def _build_equity_premium_interpretation(
    is_valid: bool,
    overall_score: float,
    equity_premium: float,
    stock_allocation: float,
    evaluation_horizon: int,
    premium_score: float,
    allocation_score: float,
    horizon_score: float,
) -> str:
    """Build detailed interpretation for EquityPremium validation."""
    lines = []

    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== EQUITY PREMIUM PUZZLE SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Premium analysis
    lines.append("[1] EQUITY PREMIUM ANALYSIS")
    lines.append(f"    Observed: Equity premium = {equity_premium:.2f}% (annualized)")
    lines.append(f"    Expected: 4-8% (historical US: ~6%)")
    lines.append(f"    Score: {premium_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    lines.append("    The equity premium = excess return of stocks over bonds.")
    if equity_premium > 10:
        lines.append("    EXCESSIVE PREMIUM - Higher than historical average.")
        lines.append("    While ~6% is typical, some periods show higher premia.")
        lines.append("    This may indicate agents are more risk-averse or")
        lines.append("    myopic (evaluate frequently) than typical investors.")
    elif equity_premium > 6:
        lines.append("    HIGH PREMIUM - Matches historical US data.")
        lines.append("    This is the 'puzzle': standard expected utility")
        lines.append("    cannot explain why investors demand such high")
        lines.append("    compensation for equity risk (Mehra & Prescott, 1985).")
    elif equity_premium > 4:
        lines.append("    MODERATE PREMIUM - Reasonable equity premium.")
        lines.append("    Within the range explained by myopic loss aversion:")
        lines.append("    Benartzi & Thaler (1995) showed λ≈2.25 + annual")
        lines.append("    evaluation produces ~6% premium demand.")
    elif equity_premium > 0:
        lines.append("    LOW PREMIUM - Below historical average.")
        lines.append("    Investors may have longer evaluation horizons")
        lines.append("    (see more gains, less loss aversion impact).")
    else:
        lines.append("    NEGATIVE/ZERO PREMIUM - Stocks underperformed.")
        lines.append("    This contradicts the equity premium puzzle premise.")
    lines.append("")

    # Allocation analysis
    lines.append("[2] STOCK ALLOCATION ANALYSIS")
    lines.append(f"    Observed: Stock allocation = {stock_allocation:.1f}%")
    lines.append(f"    Expected: 20-70% depending on evaluation frequency")
    lines.append(f"    Score: {allocation_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    lines.append(
        "    Myopic loss aversion predicts allocation depends on evaluation horizon:"
    )
    lines.append(
        "    - Frequent (monthly) evaluation → see losses often → low allocation (~20%)"
    )
    lines.append(
        "    - Infrequent (5-year) evaluation → see gains mostly → high allocation (~70%)"
    )
    if stock_allocation < 30:
        lines.append(
            f"    LOW ALLOCATION ({stock_allocation:.1f}%) - Consistent with myopic investors."
        )
        lines.append("    Frequent evaluation means high probability of seeing losses,")
        lines.append("    which loss-averse agents strongly dislike.")
    elif stock_allocation < 50:
        lines.append(
            f"    MODERATE ALLOCATION ({stock_allocation:.1f}%) - Balanced portfolio."
        )
        lines.append(
            "    Suggests intermediate evaluation horizon or moderate loss aversion."
        )
    else:
        lines.append(
            f"    HIGH ALLOCATION ({stock_allocation:.1f}%) - Consistent with long-horizon."
        )
        lines.append("    Infrequent evaluation means stocks mostly show gains,")
        lines.append("    making loss aversion less binding.")
    lines.append("")

    # Evaluation horizon analysis
    lines.append("[3] EVALUATION HORIZON EFFECT")
    lines.append(f"    Observed: Evaluation horizon = {evaluation_horizon} periods")
    lines.append(f"    Expected: Shorter horizon → higher premium demand")
    lines.append(f"    Score: {horizon_score:.1%}")
    lines.append("")
    lines.append("    Interpretation:")
    lines.append("    Benartzi-Thaler (1995) key insight:")
    lines.append("    - 1 year horizon: P(stock loss) ≈ 36% → require high premium")
    lines.append("    - 20 year horizon: P(stock loss) ≈ 5% → accept lower premium")
    if evaluation_horizon <= 1:
        lines.append("    MYOPIC - Very short evaluation horizon.")
        lines.append("    Agents evaluate portfolio value constantly.")
        lines.append("    This maximizes loss aversion impact and premium demand.")
    elif evaluation_horizon <= 5:
        lines.append("    SHORT HORIZON - Frequent evaluation.")
        lines.append("    Typical retail investor behavior (check quarterly).")
        lines.append("    Still generates substantial equity premium puzzle.")
    elif evaluation_horizon <= 20:
        lines.append("    MEDIUM HORIZON - Moderate evaluation frequency.")
        lines.append("    More sophisticated investors or pension-fund behavior.")
        lines.append("    Reduces myopia effect but still meaningful.")
    else:
        lines.append("    LONG HORIZON - Infrequent evaluation.")
        lines.append("    This reduces the equity premium puzzle:")
        lines.append("    with rare evaluation, losses are rarely observed.")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            "The simulation successfully reproduces equity premium puzzle dynamics:"
        )
        lines.append("- Meaningful equity premium (stocks outperform bonds)")
        lines.append("- Allocation consistent with myopic loss aversion")
        lines.append("- Results align with Benartzi-Thaler (1995) MLA theory.")
    else:
        lines.append("The simulation does not fully capture expected premium dynamics.")
        missing = []
        if premium_score < 0.5:
            missing.append("equity premium outside expected range")
        if allocation_score < 0.5:
            missing.append("allocation inconsistent with MLA")
        if horizon_score < 0.5:
            missing.append("evaluation horizon effect absent")
        lines.append(
            f"Key issues: {', '.join(missing) if missing else 'marginal scores'}."
        )
        lines.append(
            "Consider: implementing loss aversion (λ≈2.25), varying evaluation"
        )
        lines.append("horizons across agents, or adding reference-dependent utility.")

    return "\n".join(lines)


def validate_asset_bubble(
    market_prices: Dict[int, float],
    fundamental: float,
    max_deviation_pct: float,
    max_drawdown: float,
    total_rounds: int,
) -> ValidationResult:
    """
    Validate AssetBubble simulation results.

    Expected Behavior (Kindleberger 2000, Shiller 2000):
    - Price deviation should reach 20-50% above fundamental
    - Crash (drawdown) should occur after bubble peak
    - Bubble should form gradually (not instant)
    - Recovery should not exceed original bubble peak

    Args:
        market_prices: {round: price} dict
        fundamental: Fundamental value
        max_deviation_pct: Maximum price deviation percentage
        max_drawdown: Maximum drawdown percentage
        total_rounds: Total simulation rounds

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Bubble magnitude (target: 20-50%)
    bubble_score = 0.0
    if 20 <= max_deviation_pct <= 50:
        bubble_score = 1.0
    elif 10 <= max_deviation_pct < 20:
        bubble_score = 0.5 + (max_deviation_pct - 10) / 20
    elif 50 < max_deviation_pct <= 80:
        bubble_score = 1.0 - (max_deviation_pct - 50) / 60
    elif max_deviation_pct > 80:
        bubble_score = 0.3  # Unrealistic bubble
    else:
        bubble_score = max_deviation_pct / 20  # Too small

    criteria["bubble_magnitude"] = {
        "value": max_deviation_pct,
        "target": "20-50%",
        "score": round(bubble_score, 3),
        "passed": 15 < max_deviation_pct < 80,
    }

    # Criterion 2: Crash occurrence (target: >15% drawdown)
    crash_score = 0.0
    if max_drawdown < -15:
        crash_score = min(1.0, abs(max_drawdown) / 30)
    elif max_drawdown < -5:
        crash_score = 0.3

    criteria["crash_occurrence"] = {
        "value": max_drawdown,
        "target": "< -15%",
        "score": round(crash_score, 3),
        "passed": max_drawdown < -15,
    }

    # Criterion 3: Gradual formation (not instant)
    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    peak_round = prices_list.index(max(prices_list))
    formation_score = 0.0
    if peak_round > total_rounds * 0.3:  # Peak after 30% of simulation
        formation_score = min(1.0, peak_round / (total_rounds * 0.5))
    else:
        formation_score = peak_round / (total_rounds * 0.3)

    criteria["gradual_formation"] = {
        "value": peak_round,
        "target": f"peak > round {int(total_rounds * 0.3)}",
        "score": round(formation_score, 3),
        "passed": peak_round > total_rounds * 0.2,
    }

    # Overall score
    overall_score = bubble_score * 0.4 + crash_score * 0.4 + formation_score * 0.2
    is_valid = overall_score > 0.5 and max_deviation_pct > 15

    interpretation = _build_asset_bubble_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        max_deviation_pct=max_deviation_pct,
        max_drawdown=max_drawdown,
        peak_round=peak_round,
        total_rounds=total_rounds,
        bubble_score=bubble_score,
        crash_score=crash_score,
        formation_score=formation_score,
    )

    return ValidationResult(
        scenario="AssetBubble",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_herd_effect(
    avg_cv: float,
    avg_agreement: float,
    max_deviation: float,
    herding_episodes: int,
    total_rounds: int,
) -> ValidationResult:
    """
    Validate HerdEffect simulation results.

    Expected Behavior (Bikhchandani 1992, LSV 1992):
    - Bid CV should drop below 0.10 during herding
    - Directional agreement should exceed 0.8 during herding
    - Price should deviate >15% from fundamental
    - At least one herding episode should be detected

    Args:
        avg_cv: Average coefficient of variation of bids
        avg_agreement: Average directional agreement
        max_deviation: Maximum price deviation from fundamental
        herding_episodes: Number of detected herding episodes
        total_rounds: Total simulation rounds

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Bid convergence (target: avg CV < 0.15)
    cv_score = 0.0
    if avg_cv < 0.10:
        cv_score = 1.0
    elif avg_cv < 0.15:
        cv_score = 1.0 - (avg_cv - 0.10) / 0.10
    elif avg_cv < 0.20:
        cv_score = 0.5 - (avg_cv - 0.15) / 0.10
    else:
        cv_score = max(0, 0.3 - (avg_cv - 0.20) / 0.20)

    criteria["bid_convergence"] = {
        "value": avg_cv,
        "target": "< 0.15",
        "score": round(cv_score, 3),
        "passed": avg_cv < 0.15,
    }

    # Criterion 2: Directional agreement (target: > 0.7)
    agreement_score = 0.0
    if avg_agreement > 0.8:
        agreement_score = 1.0
    elif avg_agreement > 0.7:
        agreement_score = 0.8 + (avg_agreement - 0.7) * 2
    elif avg_agreement > 0.6:
        agreement_score = 0.5 + (avg_agreement - 0.6) * 3
    else:
        agreement_score = max(0, avg_agreement / 0.6 * 0.5)

    criteria["directional_agreement"] = {
        "value": avg_agreement,
        "target": "> 0.7",
        "score": round(agreement_score, 3),
        "passed": avg_agreement > 0.7,
    }

    # Criterion 3: Price deviation (target: > 15%)
    deviation_score = min(1.0, max_deviation / 20) if max_deviation > 0 else 0

    criteria["price_deviation"] = {
        "value": max_deviation,
        "target": "> 15%",
        "score": round(deviation_score, 3),
        "passed": max_deviation > 15,
    }

    # Criterion 4: Herding episodes detected
    episode_score = min(1.0, herding_episodes / 2) if herding_episodes > 0 else 0

    criteria["herding_episodes"] = {
        "value": herding_episodes,
        "target": ">= 1",
        "score": round(episode_score, 3),
        "passed": herding_episodes >= 1,
    }

    # Overall score
    overall_score = (
        cv_score * 0.3
        + agreement_score * 0.3
        + deviation_score * 0.2
        + episode_score * 0.2
    )
    is_valid = overall_score > 0.5 and (avg_cv < 0.15 or avg_agreement > 0.7)

    interpretation = _build_herd_effect_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        avg_cv=avg_cv,
        avg_agreement=avg_agreement,
        max_deviation=max_deviation,
        herding_episodes=herding_episodes,
        total_rounds=total_rounds,
        cv_score=cv_score,
        agreement_score=agreement_score,
        deviation_score=deviation_score,
        episode_score=episode_score,
    )

    return ValidationResult(
        scenario="HerdEffect",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_flash_crash(
    max_drawdown: float,
    crash_duration: int,
    recovery_detected: bool,
    total_rounds: int,
) -> ValidationResult:
    """
    Validate FlashCrash simulation results.

    Expected Behavior (Kirilenko 2017, SEC 2010):
    - Rapid crash: >5% drop in <10 rounds
    - V-shaped recovery within reasonable time
    - Volatility spike during crash

    Args:
        max_drawdown: Maximum drawdown percentage (negative)
        crash_duration: Number of rounds from peak to trough
        recovery_detected: Whether price recovered after crash
        total_rounds: Total simulation rounds

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Crash magnitude (target: 5-20% drop)
    crash_score = 0.0
    abs_dd = abs(max_drawdown)
    if 5 <= abs_dd <= 20:
        crash_score = 1.0
    elif abs_dd > 20:
        crash_score = max(0.5, 1.0 - (abs_dd - 20) / 30)
    elif abs_dd >= 3:
        crash_score = (abs_dd - 3) / 4

    criteria["crash_magnitude"] = {
        "value": max_drawdown,
        "target": "-5% to -20%",
        "score": round(crash_score, 3),
        "passed": abs_dd >= 5,
    }

    # Criterion 2: Crash speed (target: < 10 rounds)
    speed_score = 0.0
    if crash_duration <= 5:
        speed_score = 1.0
    elif crash_duration <= 10:
        speed_score = 1.0 - (crash_duration - 5) / 10
    elif crash_duration <= 20:
        speed_score = 0.5 - (crash_duration - 10) / 20
    else:
        speed_score = 0.1

    criteria["crash_speed"] = {
        "value": crash_duration,
        "target": "< 10 rounds",
        "score": round(speed_score, 3),
        "passed": crash_duration < 10,
    }

    # Criterion 3: Recovery (V-shape)
    recovery_score = 1.0 if recovery_detected else 0.3

    criteria["recovery"] = {
        "value": recovery_detected,
        "target": True,
        "score": round(recovery_score, 3),
        "passed": recovery_detected,
    }

    # Overall score
    overall_score = crash_score * 0.4 + speed_score * 0.4 + recovery_score * 0.2
    is_valid = overall_score > 0.5 and abs_dd >= 5 and crash_duration < 15

    interpretation = _build_flash_crash_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        max_drawdown=max_drawdown,
        crash_duration=crash_duration,
        recovery_detected=recovery_detected,
        total_rounds=total_rounds,
        severity_score=crash_score,
        speed_score=speed_score,
        recovery_score=recovery_score,
    )

    return ValidationResult(
        scenario="FlashCrash",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_market_crash(
    max_drawdown: float,
    crash_duration: int,
    recovery_detected: bool,
    total_rounds: int,
) -> ValidationResult:
    """
    Validate MarketCrash simulation results.

    Expected Behavior (Brunnermeier 2009, Minsky 1986):
    - Significant drawdown: >20%
    - Slower than flash crash: 10-30 rounds
    - L-shaped or U-shaped (not V-shaped like flash crash)

    Args:
        max_drawdown: Maximum drawdown percentage (negative)
        crash_duration: Number of rounds from peak to trough
        recovery_detected: Whether price recovered
        total_rounds: Total simulation rounds

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Crash magnitude (target: 20-50% drop)
    abs_dd = abs(max_drawdown)
    crash_score = 0.0
    if 20 <= abs_dd <= 50:
        crash_score = 1.0
    elif 15 <= abs_dd < 20:
        crash_score = 0.7 + (abs_dd - 15) / 16.67
    elif abs_dd > 50:
        crash_score = max(0.5, 1.0 - (abs_dd - 50) / 50)
    else:
        crash_score = abs_dd / 20

    criteria["crash_magnitude"] = {
        "value": max_drawdown,
        "target": "-20% to -50%",
        "score": round(crash_score, 3),
        "passed": abs_dd >= 15,
    }

    # Criterion 2: Crash speed (target: 10-30 rounds - slower than flash crash)
    speed_score = 0.0
    if 10 <= crash_duration <= 30:
        speed_score = 1.0
    elif crash_duration < 10:
        speed_score = 0.5 + crash_duration / 20  # Too fast = flash crash
    elif crash_duration <= 50:
        speed_score = 1.0 - (crash_duration - 30) / 40
    else:
        speed_score = 0.3

    criteria["crash_duration"] = {
        "value": crash_duration,
        "target": "10-30 rounds",
        "score": round(speed_score, 3),
        "passed": 5 <= crash_duration <= 40,
    }

    # Criterion 3: Recovery pattern (L or U shaped, not V)
    # For market crash, slow/no recovery is actually expected
    recovery_score = 0.7 if not recovery_detected else 0.5

    criteria["recovery_pattern"] = {
        "value": "slow/none" if not recovery_detected else "detected",
        "target": "L or U shaped",
        "score": round(recovery_score, 3),
        "passed": True,  # Either pattern is acceptable
    }

    overall_score = crash_score * 0.5 + speed_score * 0.3 + recovery_score * 0.2
    is_valid = overall_score > 0.5 and abs_dd >= 15

    interpretation = _build_market_crash_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        max_drawdown=max_drawdown,
        crash_duration=crash_duration,
        recovery_detected=recovery_detected,
        total_rounds=total_rounds,
        severity_score=crash_score,
        duration_score=speed_score,
        pattern_score=recovery_score,
    )

    return ValidationResult(
        scenario="MarketCrash",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_momentum_effect(
    autocorrelation_lag1: float,
    trend_duration_avg: float,
    total_rounds: int,
) -> ValidationResult:
    """
    Validate MomentumEffect simulation results.

    Expected Behavior (Jegadeesh & Titman 1993):
    - Positive return autocorrelation at short lags (1-5)
    - Trend persistence for 5-20 rounds
    - Returns should be predictable from past returns

    Args:
        autocorrelation_lag1: Autocorrelation of returns at lag 1
        trend_duration_avg: Average duration of same-sign return streaks
        total_rounds: Total simulation rounds

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Positive autocorrelation (target: > 0.1)
    ac_score = 0.0
    if autocorrelation_lag1 > 0.15:
        ac_score = 1.0
    elif autocorrelation_lag1 > 0.1:
        ac_score = 0.8 + (autocorrelation_lag1 - 0.1) * 4
    elif autocorrelation_lag1 > 0.05:
        ac_score = 0.5 + (autocorrelation_lag1 - 0.05) * 6
    elif autocorrelation_lag1 > 0:
        ac_score = autocorrelation_lag1 * 10
    else:
        ac_score = 0.0  # Negative = reversal, not momentum

    criteria["autocorrelation"] = {
        "value": autocorrelation_lag1,
        "target": "> 0.1",
        "score": round(ac_score, 3),
        "passed": autocorrelation_lag1 > 0.05,
    }

    # Criterion 2: Trend duration (target: 5-20 rounds)
    trend_score = 0.0
    if 5 <= trend_duration_avg <= 20:
        trend_score = 1.0
    elif 3 <= trend_duration_avg < 5:
        trend_score = 0.5 + (trend_duration_avg - 3) / 4
    elif trend_duration_avg > 20:
        trend_score = max(0.5, 1.0 - (trend_duration_avg - 20) / 30)
    else:
        trend_score = trend_duration_avg / 5

    criteria["trend_duration"] = {
        "value": trend_duration_avg,
        "target": "5-20 rounds",
        "score": round(trend_score, 3),
        "passed": trend_duration_avg >= 3,
    }

    overall_score = ac_score * 0.6 + trend_score * 0.4
    is_valid = overall_score > 0.4 and autocorrelation_lag1 > 0

    # Determine if positive momentum present
    positive_momentum = autocorrelation_lag1 > 0
    direction_score = 1.0 if positive_momentum else 0.0

    interpretation = _build_momentum_effect_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        acf_lag1=autocorrelation_lag1,
        avg_trend_duration=trend_duration_avg,
        positive_momentum=positive_momentum,
        total_rounds=total_rounds,
        acf_score=ac_score,
        trend_score=trend_score,
        direction_score=direction_score,
    )

    return ValidationResult(
        scenario="MomentumEffect",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_reversal_effect(
    autocorrelation_long: float,
    winner_loser_spread: Optional[float],
    total_rounds: int,
) -> ValidationResult:
    """
    Validate ReversalEffect simulation results.

    Expected Behavior (De Bondt & Thaler 1985):
    - Negative autocorrelation at long lags (15-30)
    - Past losers outperform past winners
    - Mean reversion to fundamental

    Args:
        autocorrelation_long: Autocorrelation at lag 15-20
        winner_loser_spread: Return difference (losers - winners), if computed
        total_rounds: Total simulation rounds

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Negative long-lag autocorrelation
    ac_score = 0.0
    if autocorrelation_long < -0.1:
        ac_score = 1.0
    elif autocorrelation_long < -0.05:
        ac_score = 0.7 + abs(autocorrelation_long + 0.05) * 6
    elif autocorrelation_long < 0:
        ac_score = 0.4 + abs(autocorrelation_long) * 6
    else:
        ac_score = max(0, 0.3 - autocorrelation_long * 3)

    criteria["long_lag_acf"] = {
        "value": autocorrelation_long,
        "target": "< -0.05",
        "score": round(ac_score, 3),
        "passed": autocorrelation_long < 0,
    }

    # Criterion 2: Winner-Loser spread (if available)
    if winner_loser_spread is not None:
        wl_score = 1.0 if winner_loser_spread > 0 else 0.3
        criteria["winner_loser_spread"] = {
            "value": winner_loser_spread,
            "target": "> 0 (losers outperform)",
            "score": round(wl_score, 3),
            "passed": winner_loser_spread > 0,
        }
        overall_score = ac_score * 0.6 + wl_score * 0.4
    else:
        overall_score = ac_score
        wl_score = 0.0

    is_valid = overall_score > 0.4 and autocorrelation_long < 0

    # For interpretation
    mean_reversion_detected = autocorrelation_long < 0
    reversal_magnitude = abs(autocorrelation_long) * 100  # Convert to percentage-like
    reversion_score = 1.0 if mean_reversion_detected else 0.0
    magnitude_score = (
        min(1.0, reversal_magnitude / 10) if mean_reversion_detected else 0.0
    )

    interpretation = _build_reversal_effect_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        long_lag_acf=autocorrelation_long,
        mean_reversion_detected=mean_reversion_detected,
        reversal_magnitude=reversal_magnitude,
        acf_score=ac_score,
        reversion_score=reversion_score,
        magnitude_score=magnitude_score,
    )

    return ValidationResult(
        scenario="ReversalEffect",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_volatility_clustering(
    return_acf: float,
    squared_return_acf: float,
    clustering_ratio: float,
) -> ValidationResult:
    """
    Validate VolatilityClustering simulation results.

    Expected Behavior (Bollerslev 1986, Cont 2001):
    - Return ACF ≈ 0 (efficient market)
    - Squared return ACF > 0 (volatility clusters)
    - Clustering ratio (sq_ACF / return_ACF) > 2

    Args:
        return_acf: Autocorrelation of returns at lag 1
        squared_return_acf: Autocorrelation of squared returns at lag 1
        clustering_ratio: squared_return_acf / abs(return_acf)

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Return ACF near zero
    return_score = 0.0
    if abs(return_acf) < 0.1:
        return_score = 1.0 - abs(return_acf) * 5
    elif abs(return_acf) < 0.2:
        return_score = 0.5 - (abs(return_acf) - 0.1) * 2.5
    else:
        return_score = 0.1

    criteria["return_acf"] = {
        "value": return_acf,
        "target": "≈ 0 (|ACF| < 0.15)",
        "score": round(return_score, 3),
        "passed": abs(return_acf) < 0.15,
    }

    # Criterion 2: Squared return ACF positive
    sq_score = 0.0
    if squared_return_acf > 0.15:
        sq_score = 1.0
    elif squared_return_acf > 0.1:
        sq_score = 0.8 + (squared_return_acf - 0.1) * 4
    elif squared_return_acf > 0.05:
        sq_score = 0.5 + (squared_return_acf - 0.05) * 6
    elif squared_return_acf > 0:
        sq_score = squared_return_acf * 10

    criteria["squared_return_acf"] = {
        "value": squared_return_acf,
        "target": "> 0.1",
        "score": round(sq_score, 3),
        "passed": squared_return_acf > 0.05,
    }

    # Criterion 3: Clustering ratio
    ratio_score = min(1.0, clustering_ratio / 3) if clustering_ratio > 0 else 0

    criteria["clustering_ratio"] = {
        "value": clustering_ratio,
        "target": "> 2",
        "score": round(ratio_score, 3),
        "passed": clustering_ratio > 1.5,
    }

    overall_score = return_score * 0.3 + sq_score * 0.4 + ratio_score * 0.3
    is_valid = overall_score > 0.4 and squared_return_acf > 0

    interpretation = _build_volatility_clustering_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        return_acf=return_acf,
        sq_return_acf=squared_return_acf,
        clustering_ratio=clustering_ratio,
        return_score=return_score,
        sq_return_score=sq_score,
        ratio_score=ratio_score,
    )

    return ValidationResult(
        scenario="VolatilityClustering",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_short_squeeze(
    max_price_spike: float,
    short_covering_detected: bool,
    feedback_loop_detected: bool,
) -> ValidationResult:
    """
    Validate ShortSqueeze simulation results.

    Expected Behavior:
    - Price spike > 50%
    - Short covering (forced buying) visible
    - Feedback loop: covering → price rise → more covering

    Args:
        max_price_spike: Maximum price increase from start (%)
        short_covering_detected: Whether shorts were forced to cover
        feedback_loop_detected: Whether positive feedback was observed

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Price spike magnitude
    spike_score = 0.0
    if max_price_spike >= 100:
        spike_score = 1.0
    elif max_price_spike >= 50:
        spike_score = 0.7 + (max_price_spike - 50) / 166.67
    elif max_price_spike >= 30:
        spike_score = 0.4 + (max_price_spike - 30) / 66.67
    else:
        spike_score = max_price_spike / 75

    criteria["price_spike"] = {
        "value": max_price_spike,
        "target": "> 50%",
        "score": round(spike_score, 3),
        "passed": max_price_spike >= 30,
    }

    # Criterion 2: Short covering
    covering_score = 1.0 if short_covering_detected else 0.2

    criteria["short_covering"] = {
        "value": short_covering_detected,
        "target": True,
        "score": round(covering_score, 3),
        "passed": short_covering_detected,
    }

    # Criterion 3: Feedback loop
    feedback_score = 1.0 if feedback_loop_detected else 0.3

    criteria["feedback_loop"] = {
        "value": feedback_loop_detected,
        "target": True,
        "score": round(feedback_score, 3),
        "passed": feedback_loop_detected,
    }

    overall_score = spike_score * 0.4 + covering_score * 0.3 + feedback_score * 0.3
    is_valid = overall_score > 0.5 and max_price_spike >= 30

    # For interpretation - spike_speed is approximated based on spike magnitude
    spike_speed = 5 if max_price_spike > 100 else (10 if max_price_spike > 50 else 15)

    interpretation = _build_short_squeeze_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        max_price_spike=max_price_spike,
        spike_speed=spike_speed,
        feedback_detected=feedback_loop_detected,
        spike_score=spike_score,
        speed_score=covering_score,  # Use covering as proxy for speed
        feedback_score=feedback_score,
    )

    return ValidationResult(
        scenario="ShortSqueeze",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_liquidity_dryup(
    spread_increase_ratio: float,
    depth_decrease_ratio: float,
    price_impact_increase: float,
) -> ValidationResult:
    """
    Validate LiquidityDryup simulation results.

    Expected Behavior (Grossman-Miller 1988, Brunnermeier-Pedersen 2009):
    - Spread widens 3-10x during stress
    - Market depth drops 50-100%
    - Price impact increases significantly

    Args:
        spread_increase_ratio: Max spread / normal spread
        depth_decrease_ratio: (normal depth - min depth) / normal depth
        price_impact_increase: Max impact / normal impact

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Spread widening
    spread_score = 0.0
    if spread_increase_ratio >= 3:
        spread_score = min(1.0, spread_increase_ratio / 5)
    elif spread_increase_ratio >= 2:
        spread_score = 0.5 + (spread_increase_ratio - 2) / 2
    else:
        spread_score = spread_increase_ratio / 4

    criteria["spread_widening"] = {
        "value": spread_increase_ratio,
        "target": "> 3x",
        "score": round(spread_score, 3),
        "passed": spread_increase_ratio >= 2,
    }

    # Criterion 2: Depth decrease
    depth_score = (
        min(1.0, depth_decrease_ratio / 0.8) if depth_decrease_ratio > 0 else 0
    )

    criteria["depth_decrease"] = {
        "value": depth_decrease_ratio,
        "target": "> 50%",
        "score": round(depth_score, 3),
        "passed": depth_decrease_ratio > 0.5,
    }

    # Criterion 3: Price impact
    impact_score = (
        min(1.0, price_impact_increase / 5) if price_impact_increase > 0 else 0
    )

    criteria["price_impact"] = {
        "value": price_impact_increase,
        "target": "> 3x",
        "score": round(impact_score, 3),
        "passed": price_impact_increase > 2,
    }

    overall_score = spread_score * 0.4 + depth_score * 0.3 + impact_score * 0.3
    is_valid = overall_score > 0.4

    interpretation = _build_liquidity_dryup_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        spread_increase=spread_increase_ratio,
        depth_decrease=depth_decrease_ratio * 100,  # Convert to percentage
        impact_increase=price_impact_increase,
        spread_score=spread_score,
        depth_score=depth_score,
        impact_score=impact_score,
    )

    return ValidationResult(
        scenario="LiquidityDryup",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_disposition_effect(
    pgr: float,
    plr: float,
    disposition_coefficient: float,
) -> ValidationResult:
    """
    Validate DispositionEffect simulation results.

    Expected Behavior (Odean 1998, Shefrin & Statman 1985):
    - PGR > PLR (sell winners faster than losers)
    - Disposition coefficient (PGR - PLR) > 0.1
    - Loss holding time > gain holding time

    Args:
        pgr: Proportion of Gains Realized
        plr: Proportion of Losses Realized
        disposition_coefficient: PGR - PLR

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: PGR > PLR
    comparison_score = 1.0 if pgr > plr else 0.2

    criteria["pgr_vs_plr"] = {
        "value": f"PGR={pgr:.3f}, PLR={plr:.3f}",
        "target": "PGR > PLR",
        "score": round(comparison_score, 3),
        "passed": pgr > plr,
    }

    # Criterion 2: Disposition coefficient magnitude
    dc_score = 0.0
    if disposition_coefficient > 0.15:
        dc_score = 1.0
    elif disposition_coefficient > 0.1:
        dc_score = 0.7 + (disposition_coefficient - 0.1) * 6
    elif disposition_coefficient > 0.05:
        dc_score = 0.4 + (disposition_coefficient - 0.05) * 6
    elif disposition_coefficient > 0:
        dc_score = disposition_coefficient * 8
    else:
        dc_score = 0.0

    criteria["disposition_coefficient"] = {
        "value": disposition_coefficient,
        "target": "> 0.1",
        "score": round(dc_score, 3),
        "passed": disposition_coefficient > 0.05,
    }

    overall_score = comparison_score * 0.4 + dc_score * 0.6
    is_valid = overall_score > 0.5 and pgr > plr

    # For interpretation
    pgr_score = min(1.0, pgr / 0.3) if pgr > 0 else 0.0

    interpretation = _build_disposition_effect_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        pgr=pgr,
        plr=plr,
        disposition_coefficient=disposition_coefficient,
        pgr_score=pgr_score,
        asymmetry_score=comparison_score,
        coefficient_score=dc_score,
    )

    return ValidationResult(
        scenario="DispositionEffect",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def validate_equity_premium(
    equity_premium: float,
    myopic_allocation: float,
    long_horizon_allocation: float,
) -> ValidationResult:
    """
    Validate EquityPremium simulation results.

    Expected Behavior (Benartzi & Thaler 1995):
    - Equity premium 4-8% (annualized equivalent)
    - Myopic investors hold less stock than long-horizon
    - Allocation difference 20-40%

    Args:
        equity_premium: E[R_stock] - R_f (annualized or per-round)
        myopic_allocation: Stock allocation of myopic investors
        long_horizon_allocation: Stock allocation of long-horizon investors

    Returns:
        ValidationResult with score and criteria
    """
    criteria = {}

    # Criterion 1: Equity premium magnitude
    premium_score = 0.0
    if 4 <= equity_premium <= 8:
        premium_score = 1.0
    elif 2 <= equity_premium < 4:
        premium_score = 0.5 + (equity_premium - 2) / 4
    elif 8 < equity_premium <= 12:
        premium_score = 1.0 - (equity_premium - 8) / 8
    else:
        premium_score = max(0, 0.3 - abs(equity_premium - 6) / 20)

    criteria["equity_premium"] = {
        "value": equity_premium,
        "target": "4-8%",
        "score": round(premium_score, 3),
        "passed": 2 < equity_premium < 12,
    }

    # Criterion 2: Myopic vs long-horizon allocation
    allocation_diff = long_horizon_allocation - myopic_allocation
    diff_score = 0.0
    if allocation_diff > 0.2:
        diff_score = 1.0
    elif allocation_diff > 0.1:
        diff_score = 0.6 + (allocation_diff - 0.1) * 4
    elif allocation_diff > 0:
        diff_score = allocation_diff * 6
    else:
        diff_score = 0.0

    criteria["allocation_difference"] = {
        "value": allocation_diff,
        "target": "> 20%",
        "score": round(diff_score, 3),
        "passed": allocation_diff > 0.1,
    }

    overall_score = premium_score * 0.5 + diff_score * 0.5
    is_valid = overall_score > 0.4 and equity_premium > 0

    # For interpretation
    allocation_score = diff_score
    horizon_score = 1.0 if allocation_diff > 0 else 0.0
    evaluation_horizon = 1  # Assuming annual evaluation as default

    interpretation = _build_equity_premium_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        equity_premium=equity_premium,
        stock_allocation=myopic_allocation * 100,  # Convert to percentage
        evaluation_horizon=evaluation_horizon,
        premium_score=premium_score,
        allocation_score=allocation_score,
        horizon_score=horizon_score,
    )

    return ValidationResult(
        scenario="EquityPremium",
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )
