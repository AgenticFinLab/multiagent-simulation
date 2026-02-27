"""
Herding Behavior Metrics

Functions to detect and measure herd behavior in financial simulations.
Based on academic literature on behavioral finance and information cascades.

References:
    - Bikhchandani, Hirshleifer, Welch (1992): Information Cascades
    - Lakonishok, Shleifer, Vishny (1992): LSV Herding Measure
    - Chang, Cheng, Khorana (2000): CSAD measure
    - Christie & Huang (1995): Cross-sectional dispersion

Metrics Summary:
    | Metric                     | Formula                   | Herding Signal    |
    |----------------------------|---------------------------|-------------------|
    | Bid Convergence (CV)       | σ(bids) / μ(bids)         | CV < 0.05 = Strong|
    | Directional Agreement (DA) | |Σ sign(ΔBid)| / N        | DA > 0.8 = Strong |
    | Information Cascade        | contrarian_ratio          | ICM > 0.6 = Strong|
    | Cross-Sectional Std        | σ(bids)                   | Lower = More      |
"""

from typing import Dict, List, Tuple
import numpy as np
from scipy import stats


def calculate_bid_convergence_cv(
    investor_bids: Dict[str, Dict[int, float]],
) -> Dict[int, float]:
    """
    Calculate Bid Convergence Index using Coefficient of Variation (CV).

    Measures how closely investors' bids cluster together.
    Lower CV = more convergence = stronger herding behavior.

    Formula: CV_t = std(Bid_1,t, ..., Bid_N,t) / mean(Bid_1,t, ..., Bid_N,t)

    Interpretation:
        - CV < 0.05: Strong herding - bids highly converged
        - 0.05 ≤ CV < 0.10: Moderate herding
        - 0.10 ≤ CV < 0.20: Weak herding / normal market
        - CV ≥ 0.20: Dispersed opinions - no herding

    Args:
        investor_bids: {investor_id: {round: bid_price}}

    Returns:
        {round: cv_value}
    """
    # Collect all rounds
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())

    cv_series = {}
    for r in sorted(all_rounds):
        bids_at_r = [bids[r] for bids in investor_bids.values() if r in bids]
        if len(bids_at_r) >= 2:
            mean_bid = np.mean(bids_at_r)
            if mean_bid > 0:
                cv_series[r] = float(np.std(bids_at_r) / mean_bid)

    return cv_series


def calculate_directional_agreement(
    investor_bids: Dict[str, Dict[int, float]],
) -> Dict[int, float]:
    """
    Calculate Directional Agreement - measures behavioral alignment.

    Captures whether investors are moving in the same direction,
    regardless of the magnitude of their changes.

    Formula: DA_t = |Σ(sign(Bid_{i,t} - Bid_{i,t-1}))| / N

    Interpretation:
        - DA = 1: All investors moving same direction (strong herding)
        - DA ≈ 0.5: Random/divergent behavior
        - DA > 0.8: Significant behavioral alignment

    Based on: Chang, Cheng, Khorana (2000)

    Args:
        investor_bids: {investor_id: {round: bid_price}}

    Returns:
        {round: agreement_value}
    """
    # Get all rounds sorted
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())
    rounds = sorted(all_rounds)

    if len(rounds) < 2:
        return {}

    agreement_series = {}
    for i in range(1, len(rounds)):
        r_curr, r_prev = rounds[i], rounds[i - 1]

        directions = []
        for _, bids in investor_bids.items():
            if r_curr in bids and r_prev in bids:
                delta = bids[r_curr] - bids[r_prev]
                if delta > 0:
                    directions.append(1)
                elif delta < 0:
                    directions.append(-1)
                else:
                    directions.append(0)

        if len(directions) > 0:
            agreement = abs(sum(directions)) / len(directions)
            agreement_series[r_curr] = float(agreement)

    return agreement_series


def calculate_cascade_measure(
    investor_bids: Dict[str, Dict[int, float]],
    market_prices: Dict[int, float],
    fundamental: float,
) -> Dict[int, float]:
    """
    Calculate Information Cascade Measure.

    Based on Bikhchandani et al. (1992): measures when investors ignore
    their private signals and follow the market trend.

    Logic:
        - If price > fundamental, rational private signal = SELL
        - If investor bids ABOVE market price, they're ignoring signal = CASCADE
        - Cascade ratio = proportion of investors ignoring private signals

    Interpretation:
        - ICM > 0.6: Strong cascade - most investors following the herd
        - ICM ≈ 0.5: Mixed behavior
        - ICM < 0.4: Investors following their private signals

    Args:
        investor_bids: {investor_id: {round: bid_price}}
        market_prices: {round: price}
        fundamental: Fundamental value for signal calculation

    Returns:
        {round: cascade_ratio}
    """
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())

    cascade_series = {}
    for r in sorted(all_rounds):
        if r not in market_prices:
            continue

        price = market_prices[r]

        contrarian_count = 0
        total_count = 0

        for _, bids in investor_bids.items():
            if r not in bids:
                continue

            bid = bids[r]
            total_count += 1

            # Private signal based on fundamental
            private_signal = "buy" if price < fundamental else "sell"

            # Actual behavior based on bid vs market
            actual = "buy" if bid > price else "sell"

            # If actual != private signal, investor is following cascade
            if private_signal != actual:
                contrarian_count += 1

        if total_count > 0:
            cascade_series[r] = float(contrarian_count / total_count)

    return cascade_series


def calculate_cross_sectional_std(
    investor_bids: Dict[str, Dict[int, float]],
) -> Dict[int, float]:
    """
    Calculate cross-sectional standard deviation of investor bids.

    Inspired by LSV (1992) and CSAD (Chang et al. 2000) measures.
    Lower std = higher herding (investors bid similarly).

    Formula: CSSD_t = std(Bid_1,t, Bid_2,t, ..., Bid_N,t)

    Args:
        investor_bids: {investor_id: {round: bid_price}}

    Returns:
        {round: std_value}
    """
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())

    cross_std = {}
    for r in sorted(all_rounds):
        bids_at_r = [bids[r] for bids in investor_bids.values() if r in bids]
        if len(bids_at_r) >= 2:
            cross_std[r] = float(np.std(bids_at_r))

    return cross_std


def calculate_investor_correlation_matrix(
    investor_bids: Dict[str, Dict[int, float]], min_common_rounds: int = 10
) -> Dict[Tuple[str, str], float]:
    """
    Calculate pairwise correlation matrix between all investors.

    In emergent herding model, look for increasing correlation
    between feedback investors (e.g., Momentum and Aggressive).

    Args:
        investor_bids: {investor_id: {round: bid_price}}
        min_common_rounds: Minimum overlapping rounds required

    Returns:
        {(inv1, inv2): correlation}
    """
    if stats is None:
        # Fallback to numpy if scipy not available
        return _calculate_correlation_numpy(investor_bids, min_common_rounds)

    investor_ids = sorted(investor_bids.keys())
    correlations = {}

    for i, inv1 in enumerate(investor_ids):
        for inv2 in investor_ids[i + 1 :]:
            bids1 = investor_bids[inv1]
            bids2 = investor_bids[inv2]

            common_rounds = sorted(set(bids1.keys()) & set(bids2.keys()))
            if len(common_rounds) < min_common_rounds:
                continue

            vals1 = [bids1[r] for r in common_rounds]
            vals2 = [bids2[r] for r in common_rounds]

            corr, _ = stats.pearsonr(vals1, vals2)
            correlations[(inv1, inv2)] = float(corr)

    return correlations


def _calculate_correlation_numpy(
    investor_bids: Dict[str, Dict[int, float]], min_common_rounds: int
) -> Dict[Tuple[str, str], float]:
    """Fallback correlation calculation using numpy."""
    investor_ids = sorted(investor_bids.keys())
    correlations = {}

    for i, inv1 in enumerate(investor_ids):
        for inv2 in investor_ids[i + 1 :]:
            bids1 = investor_bids[inv1]
            bids2 = investor_bids[inv2]

            common_rounds = sorted(set(bids1.keys()) & set(bids2.keys()))
            if len(common_rounds) < min_common_rounds:
                continue

            vals1 = np.array([bids1[r] for r in common_rounds])
            vals2 = np.array([bids2[r] for r in common_rounds])

            corr = np.corrcoef(vals1, vals2)[0, 1]
            if not np.isnan(corr):
                correlations[(inv1, inv2)] = float(corr)

    return correlations


def calculate_rolling_cv(
    investor_bids: Dict[str, Dict[int, float]], window: int = 20
) -> Dict[int, float]:
    """
    Calculate rolling bid convergence (CV) over time.

    Shows the dynamics of herd formation/dissolution.
    Useful for detecting when herding starts and ends.

    Args:
        investor_bids: {investor_id: {round: bid_price}}
        window: Rolling window size

    Returns:
        {round: rolling_cv}
    """
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())
    rounds = sorted(all_rounds)

    if len(rounds) < window:
        return {}

    rolling_cv = {}
    for i in range(window - 1, len(rounds)):
        r = rounds[i]
        window_rounds = rounds[i - window + 1 : i + 1]

        cvs = []
        for wr in window_rounds:
            bids_at_r = [bids[wr] for bids in investor_bids.values() if wr in bids]
            if len(bids_at_r) >= 2:
                mean_bid = np.mean(bids_at_r)
                if mean_bid > 0:
                    cvs.append(np.std(bids_at_r) / mean_bid)

        if cvs:
            rolling_cv[r] = float(np.mean(cvs))

    return rolling_cv


def detect_herding_episodes(
    cv_series: Dict[int, float], threshold: float = 0.05, min_duration: int = 3
) -> List[Tuple[int, int]]:
    """
    Detect herding episodes based on CV threshold.

    An episode is a consecutive sequence of rounds where CV < threshold.

    Args:
        cv_series: {round: cv_value}
        threshold: CV threshold for herding detection
        min_duration: Minimum consecutive rounds for an episode

    Returns:
        List of (start_round, end_round) tuples
    """
    rounds = sorted(cv_series.keys())
    episodes = []

    in_episode = False
    episode_start = None

    for r in rounds:
        if cv_series[r] < threshold:
            if not in_episode:
                in_episode = True
                episode_start = r
        else:
            if in_episode:
                in_episode = False
                # Check if episode meets minimum duration
                duration = rounds.index(r) - rounds.index(episode_start)
                if duration >= min_duration:
                    episodes.append((episode_start, rounds[rounds.index(r) - 1]))

    # Handle episode that extends to the end
    if in_episode and episode_start is not None:
        duration = rounds.index(rounds[-1]) - rounds.index(episode_start) + 1
        if duration >= min_duration:
            episodes.append((episode_start, rounds[-1]))

    return episodes
