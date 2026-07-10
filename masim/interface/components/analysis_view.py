"""Analysis view component for displaying simulation results and charts."""

import json
import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import sys


def render_analysis_page(scenario_name: str):
    """Render the full analysis page for a scenario.

    If analysis charts already exist in EXPERIMENT/{scenario}/analysis/ they
    are displayed immediately without re-running the analysis script.  The
    script is only invoked when the directory is absent or contains no PNGs.

    Args:
        scenario_name: Name of the scenario to analyze
    """
    from ..config_loader import (
        check_simulation_results,
        get_analysis_path,
        get_scenario_info,
        scenario_display_name,
    )

    # Header row: back button + title
    col_back, col_title = st.columns([1, 5])
    with col_back:
        st.markdown("<div style='margin-top:18px'/>", unsafe_allow_html=True)
        if st.button("← Back", width="stretch"):
            st.session_state.current_page = "Simulation"
            st.rerun()
    with col_title:
        display_name = scenario_display_name(scenario_name)
        st.title(f"Analysis — {display_name}")

    st.markdown("---")

    analysis_path = get_analysis_path(scenario_name)
    charts_exist = analysis_path is not None and any(analysis_path.glob("*.png"))

    if charts_exist:
        # ── Fast path: charts already on disk, display immediately ──────────────────
        _display_analysis_results(scenario_name, analysis_path)

        # Offer a re-run button at the bottom so the user can refresh results
        st.markdown("---")
        if st.button(
            "🔄 Re-run Analysis",
            help="Re-execute the analysis script and refresh the charts",
        ):
            with st.spinner("Running analysis script…"):
                success, message = run_analysis(scenario_name)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(f"Analysis failed: {message}")
                with st.expander("Error detail"):
                    st.code(message)
        return

    # ── No charts yet: check for raw simulation data ─────────────────────────────
    has_results = check_simulation_results(scenario_name)
    if not has_results:
        st.warning("No simulation results found for this scenario.")
        st.info("Please run the simulation first, then click **View Analysis**.")
        return

    # Auto-run analysis if charts not yet produced
    with st.spinner("Running analysis script… This may take a moment."):
        success, message = run_analysis(scenario_name)
    if not success:
        st.error(f"Analysis failed: {message}")
        with st.expander("Error detail"):
            st.code(message)
        return
    st.success(message)
    analysis_path = get_analysis_path(scenario_name)

    if analysis_path and analysis_path.exists():
        _display_analysis_results(scenario_name, analysis_path)
    else:
        st.error("Analysis output directory not found after running analysis.")


def run_analysis(scenario_name: str) -> Tuple[bool, str]:
    """Run the analysis script for a scenario.

    Args:
        scenario_name: Name of the scenario

    Returns:
        Tuple of (success, message)
    """
    try:
        script_path = Path("examples") / scenario_name / "analysis.py"
        config_path = Path("configs") / scenario_name / "simulation.yml"

        if not script_path.exists():
            return False, f"Analysis script not found: {script_path}"
        if not config_path.exists():
            return False, f"Config not found: {config_path}"

        result = subprocess.run(
            [sys.executable, str(script_path), "-c", str(config_path)],
            capture_output=True,
            text=True,
            timeout=180,
        )

        if result.returncode == 0:
            return True, "Analysis completed successfully"
        else:
            return False, result.stderr[:1000] or result.stdout[:1000]

    except subprocess.TimeoutExpired:
        return False, "Analysis timed out (> 3 minutes)"
    except Exception as e:
        return False, f"Error running analysis: {str(e)}"


# ---------------------------------------------------------------------------
# Internal display helpers
# ---------------------------------------------------------------------------


def _display_analysis_results(scenario_name: str, analysis_path: Path):
    """Display summary metrics, validation badge, and all charts."""

    # 1. Summary metrics + validation
    summary_path = analysis_path / "summary.json"
    if summary_path.exists():
        _display_summary(summary_path)
        st.markdown("---")

    # 2. Charts
    images = sorted(analysis_path.glob("*.png"))
    if not images:
        st.info("No analysis charts found.")
        return

    st.header("Analysis Charts")
    # Single-column for wide figures; 2-col grid otherwise
    if len(images) == 1:
        img = images[0]
        title = img.stem.replace("_", " ").replace("-", " ").title()
        st.subheader(title)
        desc = _chart_description(img.stem)
        if desc:
            st.caption(desc)
        st.image(str(img), width="stretch")
    else:
        cols = st.columns(2)
        for i, img_path in enumerate(images):
            with cols[i % 2]:
                title = img_path.stem.replace("_", " ").replace("-", " ").title()
                st.subheader(title)
                desc = _chart_description(img_path.stem)
                if desc:
                    st.caption(desc)
                st.image(str(img_path), width="stretch")


def _display_summary(summary_path: Path):
    """Parse summary.json and render metrics + validation score card.

    Args:
        summary_path: Path to summary.json
    """
    try:
        with open(summary_path, "r") as f:
            summary = json.load(f)
    except Exception as e:
        st.warning(f"Could not load summary.json: {e}")
        return

    st.header("Simulation Results")

    # ── Validation block ──────────────────────────────────────────────────
    validation = summary.get("validation", {})
    if validation:
        score = validation.get("score", validation.get("fit_score", None))
        interpretation = validation.get("interpretation", "")
        passed = validation.get("valid", validation.get("passed", None))

        v_col1, v_col2 = st.columns([2, 1])
        with v_col1:
            if passed is True:
                st.success(f"✅  Validation PASSED — {interpretation}")
            elif passed is False:
                st.error(f"❌  Validation FAILED — {interpretation}")
            else:
                # No explicit boolean; infer from score
                st.info(
                    f"📊  {interpretation}"
                    if interpretation
                    else "Validation result available"
                )
        with v_col2:
            if score is not None:
                pct = score if score > 1 else score * 100
                color = (
                    "#28a745" if pct >= 60 else "#ffc107" if pct >= 40 else "#dc3545"
                )
                st.markdown(
                    f"""
                    <div style="
                        background:{color};
                        border-radius:10px;
                        padding:14px 10px;
                        text-align:center;
                        color:white;
                        font-size:22px;
                        font-weight:bold;
                    ">
                        {pct:.1f}%
                        <div style="font-size:12px;font-weight:normal;margin-top:2px;">Fit Score</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # ── Key scenario-level boolean flags ─────────────────────────────────
    # Render the most informative top-level booleans / strings as big metrics
    highlight_keys = [
        "squeeze_detected",
        "squeeze_intensity",
        "dryup_detected",
        "dryup_severity",
        "disposition_effect_detected",
        "puzzle_explained",
        "bubble_detected",
        "bubble_intensity",
        "crash_detected",
        "crash_severity",
        "herd_detected",
        "momentum_detected",
        "reversal_detected",
        "flash_crash_detected",
        "clustering_detected",
    ]

    top_metrics = {k: v for k, v in summary.items() if k in highlight_keys}
    if top_metrics:
        cols = st.columns(min(len(top_metrics), 4))
        for i, (k, v) in enumerate(top_metrics.items()):
            with cols[i % 4]:
                label = k.replace("_detected", "").replace("_", " ").title()
                if isinstance(v, bool):
                    st.metric(label, "✅ Yes" if v else "❌ No")
                else:
                    st.metric(label, str(v))
        st.markdown("")

    # ── Nested metrics dict ───────────────────────────────────────────────
    metrics = summary.get("metrics", {})
    if metrics:
        st.subheader("Price Metrics")
        m_cols = st.columns(min(len(metrics), 4))
        for i, (key, value) in enumerate(metrics.items()):
            with m_cols[i % 4]:
                label = key.replace("_", " ").title()
                if isinstance(value, float):
                    st.metric(label, f"{value:.4f}")
                else:
                    st.metric(label, str(value))

    # ── Price statistics ──────────────────────────────────────────────────
    price_stats = summary.get("price_statistics", {})
    if price_stats:
        st.subheader("Price Statistics")
        ps_cols = st.columns(min(len(price_stats), 4))
        for i, (key, value) in enumerate(price_stats.items()):
            with ps_cols[i % 4]:
                label = key.replace("_", " ").title()
                if isinstance(value, (int, float)):
                    st.metric(label, f"{value:.2f}")
                else:
                    st.metric(label, str(value))

    # ── Raw JSON expander ─────────────────────────────────────────────────
    with st.expander("View full summary JSON"):
        st.json(summary)


def _chart_description(stem: str) -> str:
    """Return a short caption for a chart filename stem.

    Args:
        stem: Filename without extension (e.g. 'squeeze_analysis')

    Returns:
        Short description string, or empty string if unknown
    """
    descriptions = {
        "price_dynamics": "Price movement and trading volume over time",
        "bubble_analysis": "Bubble detection and deviation from fundamental value",
        "pgr_plr": "Proportion of Gains/Losses Realized (disposition effect)",
        "trading_activity": "Buy/sell activity by investor type",
        "return_distribution": "Distribution of round-over-round returns",
        "portfolio_evolution": "Portfolio positions and P&L over time",
        "liquidity_states": "Market liquidity state classification per round",
        "liquidity_analysis": "Liquidity dry-up dynamics and episode detection",
        "squeeze_analysis": "Short squeeze phases, volume spikes and volatility",
        "equity_premium_analysis": "Equity premium and loss probability by horizon",
        "momentum_analysis": "Momentum signal strength and return autocorrelation",
        "reversal_analysis": "Mean-reversion signal and contrarian trade effectiveness",
        "flash_crash_analysis": "Flash crash trigger, depth and recovery speed",
        "volatility_analysis": "Volatility clustering and GARCH-style regime detection",
        "herd_analysis": "Herding coefficient and synchronisation across agents",
        "crash_analysis": "Market crash depth, speed and contagion dynamics",
        "disposition_analysis": "Disposition effect by strategy — PGR vs PLR",
    }
    for key, desc in descriptions.items():
        if key in stem.lower():
            return desc
    return ""
