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

from typing import Dict, List, Tuple, Any
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


# ===========================================================================
# Registry-Compatible Metric Functions (m_* prefix)
#
# These functions use the standard MASim data contract and are registered
# into MetricsRegistry via BEHAVIORAL_METRICS.
# ===========================================================================

from masim.evaluation.registry import Metric, MetricUnavailable
from masim.evaluation.data_loader import payload_buy_sell


# ---------------------------------------------------------------------------
# Category: agent_behaviour (3 metrics)
# ---------------------------------------------------------------------------


def m_agent_action_frequency(data, config):
    """Per-agent {buy, sell, hold} action counts."""
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    per_agent: Dict[str, Dict[str, int]] = {}
    for pid, round_payloads in payloads.items():
        counts = {"buy": 0, "sell": 0, "hold": 0}
        for payload in round_payloads.values():
            action = payload.get("action", "hold")
            counts[action] = counts.get(action, 0) + 1
        per_agent[pid] = counts
    return {"per_agent": per_agent}


def m_silent_agent_count(data, config):
    """Number of agents that never traded; expected 0."""
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    silent: List[str] = []
    for pid, round_payloads in payloads.items():
        traded = any(
            payload.get("action") in ("buy", "sell") for payload in round_payloads.values()
        )
        if not traded:
            silent.append(pid)
    return {
        "silent_agents": silent,
        "silent_count": len(silent),
        "total_agents": len(payloads),
        "silent_ratio": len(silent) / len(payloads) if payloads else 0.0,
    }


def m_agent_volume_buy_sell(data, config):
    """Per-agent buy/sell/total volume from action-based accounting."""
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    per_agent: Dict[str, Dict[str, float]] = {}
    for pid, round_payloads in payloads.items():
        total_buy = 0.0
        total_sell = 0.0
        for payload in round_payloads.values():
            buy, sell = payload_buy_sell(payload)
            total_buy += buy
            total_sell += sell
        per_agent[pid] = {
            "total_buy": total_buy,
            "total_sell": total_sell,
            "total_volume": total_buy + total_sell,
        }
    return {"per_agent": per_agent}


# ---------------------------------------------------------------------------
# Category: agent_behaviour — position/PnL/wealth tracking (5 metrics)
# ---------------------------------------------------------------------------

from masim.evaluation.data_loader import (
    aligned_prices_and_fundamentals,
    per_agent_initial_position,
    per_agent_initial_cash,
)


def m_agent_net_position_ts(data, config):
    """Cumulative position evolution per agent (initial_position + Δ)."""
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    initial_positions = per_agent_initial_position(config)
    per_agent: Dict[str, Dict[str, Any]] = {}
    for pid, round_payloads in payloads.items():
        rounds_sorted = sorted(round_payloads)
        position = float(initial_positions.get(pid, 0.0))
        positions = []
        for round_num in rounds_sorted:
            payload = round_payloads[round_num]
            buy, sell = payload_buy_sell(payload)
            position = position + buy - sell
            positions.append(position)
        per_agent[pid] = {
            "rounds": rounds_sorted,
            "positions": positions,
            "final_position": position,
        }
    return {"per_agent": per_agent}


def m_agent_pnl_terminal(data, config):
    """Terminal mark-to-market PnL per agent.

    Computes each agent's terminal portfolio value = cash + position * final_price
    relative to initial wealth, using standard MASim config fields (initial_cash,
    initial_position) and the payload buy/sell accounting.
    """
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    market_prices = data.get("market_prices")
    if not market_prices:
        raise MetricUnavailable("market_prices is empty")
    initial_cash_map = per_agent_initial_cash(config)
    initial_position_map = per_agent_initial_position(config)
    # Use first available price as initial price for initial value calculation
    first_round = min(market_prices)
    initial_price = float(market_prices[first_round])
    final_round = max(market_prices)
    final_price = float(market_prices[final_round])
    per_agent: Dict[str, Dict[str, float]] = {}
    for pid, round_payloads in payloads.items():
        cash = float(initial_cash_map.get(pid, 0.0))
        position = float(initial_position_map.get(pid, 0.0))
        for round_num in sorted(round_payloads):
            payload = round_payloads[round_num]
            bid_price = float(payload.get("bid_price", 0.0)) or float(
                market_prices.get(round_num, 0.0)
            )
            buy, sell = payload_buy_sell(payload)
            cash -= buy * bid_price
            cash += sell * bid_price
            position += buy - sell
        terminal_value = cash + position * final_price
        initial_value = float(initial_cash_map.get(pid, 0.0)) + float(
            initial_position_map.get(pid, 0.0)
        ) * initial_price
        per_agent[pid] = {
            "terminal_cash": cash,
            "terminal_position": position,
            "terminal_value": terminal_value,
            "initial_value": initial_value,
            "pnl": terminal_value - initial_value,
            "pnl_pct": (
                (terminal_value - initial_value) / initial_value * 100
                if initial_value > 0
                else 0.0
            ),
        }
    return {"per_agent": per_agent, "final_price": final_price}


def m_agent_sharpe_terminal(data, config):
    """Per-agent Sharpe = mean(round PnL) / std(round PnL).

    Computes round-by-round mark-to-market PnL for each agent and derives
    the Sharpe ratio over the entire simulation.
    """
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    market_prices = data.get("market_prices")
    if not market_prices:
        raise MetricUnavailable("market_prices is empty")
    initial_position_map = per_agent_initial_position(config)
    per_agent: Dict[str, Dict[str, float]] = {}
    for pid, round_payloads in payloads.items():
        position = float(initial_position_map.get(pid, 0.0))
        prev_price = float(market_prices[min(market_prices)])
        round_pnl: List[float] = []
        for round_num in sorted(round_payloads):
            payload = round_payloads[round_num]
            price = float(market_prices.get(round_num, prev_price))
            mtm = position * (price - prev_price)
            buy, sell = payload_buy_sell(payload)
            bid = float(payload.get("bid_price", 0.0)) or price
            trade_pnl = sell * (bid - price) - buy * (bid - price)
            round_pnl.append(mtm + trade_pnl)
            position = position + buy - sell
            prev_price = price
        if not round_pnl:
            continue
        mean_pnl = float(np.mean(round_pnl))
        std_pnl = float(np.std(round_pnl))
        sharpe = mean_pnl / std_pnl if std_pnl > 1e-12 else float("nan")
        per_agent[pid] = {
            "mean_round_pnl": mean_pnl,
            "std_round_pnl": std_pnl,
            "sharpe": sharpe,
        }
    return {"per_agent": per_agent}


def m_agent_wealth_terminal(data, config):
    """Final portfolio value = cash + position * final_price per agent."""
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    _, prices, _ = aligned_prices_and_fundamentals(data)
    final_price = float(prices[-1])
    initial_cash_map = per_agent_initial_cash(config)
    initial_positions_map = per_agent_initial_position(config)
    per_agent: Dict[str, Dict[str, Any]] = {}
    for pid, round_payloads in payloads.items():
        cash = initial_cash_map.get(pid, 0.0)
        position = initial_positions_map.get(pid, 0.0)
        for round_num in sorted(round_payloads):
            payload = round_payloads[round_num]
            buy, sell = payload_buy_sell(payload)
            bid = float(payload.get("bid_price", final_price))
            cash -= buy * bid
            cash += sell * bid
            position = position + buy - sell
        per_agent[pid] = {
            "cash": cash,
            "position": position,
            "wealth": cash + position * final_price,
            "final_price": final_price,
        }
    return {"per_agent": per_agent, "final_price": final_price}


def m_gini_coefficient(data, config):
    """Gini index of terminal wealth across agents.

    Measures wealth concentration: 0 = perfect equality, 1 = one agent holds all.
    Uses the standard MASim data contract for position accounting.
    """
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    _, prices, _ = aligned_prices_and_fundamentals(data)
    final_price = float(prices[-1])
    initial_cash_map = per_agent_initial_cash(config)
    initial_positions_map = per_agent_initial_position(config)
    wealths = []
    for pid, round_payloads in payloads.items():
        cash = initial_cash_map.get(pid, 0.0)
        position = initial_positions_map.get(pid, 0.0)
        for payload in round_payloads.values():
            buy, sell = payload_buy_sell(payload)
            bid = float(payload.get("bid_price", final_price))
            cash -= buy * bid
            cash += sell * bid
            position = position + buy - sell
        wealths.append(cash + position * final_price)
    wealths_arr = np.sort(np.asarray(wealths, dtype=float))
    n = wealths_arr.size
    if n < 2 or np.sum(wealths_arr) <= 0:
        raise MetricUnavailable("insufficient wealth data for Gini")
    index = np.arange(1, n + 1)
    gini = float((2.0 * np.sum(index * wealths_arr) / (n * np.sum(wealths_arr))) - (n + 1) / n)
    return {"value": max(0.0, gini), "n_agents": n}


# ---------------------------------------------------------------------------
# BEHAVIORAL_METRICS — Metric definitions for registry registration
# ---------------------------------------------------------------------------


BEHAVIORAL_METRICS: List[Metric] = [
    Metric(name="agent_action_frequency", category="agent_behaviour", fn=m_agent_action_frequency,
           output_keys=("per_agent",), references=("Glosten & Milgrom (1985)",),
           description="Per-agent {buy, sell, hold} action counts."),
    Metric(name="silent_agent_count", category="agent_behaviour", fn=m_silent_agent_count,
           output_keys=("silent_agents", "silent_count", "total_agents", "silent_ratio"),
           description="Number of agents that never traded; expected 0."),
    Metric(name="agent_volume_buy_sell", category="agent_behaviour", fn=m_agent_volume_buy_sell,
           output_keys=("per_agent",), references=("Black (1986)",),
           description="Per-agent buy/sell/total volume from action-based accounting."),
    Metric(name="agent_net_position_ts", category="agent_behaviour", fn=m_agent_net_position_ts,
           output_keys=("per_agent",), references=("Glosten & Milgrom (1985)",),
           description="Cumulative position over time per agent."),
    Metric(name="agent_pnl_terminal", category="agent_behaviour", fn=m_agent_pnl_terminal,
           output_keys=("per_agent", "final_price"), references=("De Bondt & Thaler (1985)",),
           description="Per-agent terminal mark-to-market PnL."),
    Metric(name="agent_sharpe_terminal", category="agent_behaviour", fn=m_agent_sharpe_terminal,
           output_keys=("per_agent",), references=("Sharpe (1966)",),
           description="Per-agent Sharpe ratio of round-PnL series."),
    Metric(name="agent_wealth_terminal", category="agent_behaviour", fn=m_agent_wealth_terminal,
           output_keys=("per_agent", "final_price"), references=("De Bondt & Thaler (1985)",),
           description="Final portfolio value per agent."),
    Metric(name="gini_coefficient", category="agent_behaviour", fn=m_gini_coefficient,
           output_keys=("value", "n_agents"), references=("Gini (1912)",),
           description="Wealth concentration index at terminal round."),
]
