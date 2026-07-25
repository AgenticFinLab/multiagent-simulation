"""Analysis view component for displaying simulation results and charts."""

import json
import os
import streamlit as st
from pathlib import Path
from typing import Tuple
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
            st.session_state.current_page = st.session_state.get(
                "previous_page", "Simulation"
            )
            st.rerun()
    with col_title:
        display_name = scenario_display_name(scenario_name)
        st.title(f"Analysis — {display_name}")

    st.markdown("---")

    # A forced rerun (triggered by the toolbar's "Run Analysis" when the
    # analysis is missing or stale) must regenerate charts even if old PNGs
    # still exist on disk — otherwise the stale fast path would short-circuit.
    force_rerun = st.session_state.pop("force_analysis_rerun", False)
    analysis_path = get_analysis_path(scenario_name)
    charts_exist = analysis_path is not None and any(analysis_path.glob("*.png"))

    if charts_exist and not force_rerun:
        # ── Fast path: fresh charts already on disk, display immediately ────────────
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

    # ── Need to (re)generate charts: none exist yet, or a forced refresh ─────────
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
    analysis_path = get_analysis_path(scenario_name)

    if analysis_path and analysis_path.exists():
        _display_analysis_results(scenario_name, analysis_path)
    else:
        st.error("Analysis output directory not found after running analysis.")


def run_analysis(scenario_name: str) -> Tuple[bool, str]:
    """Run the analysis script for a scenario.

    Path resolution rules — the *bundle-local* copy is authoritative for any
    Customized project bundle. Once the user creates a project the bundle is
    a self-contained unit; we never fall back to the shipped
    ``examples/{Scenario}/`` code tree, otherwise edits made inside the
    bundle (or future divergences from shipped code) would be silently
    ignored.

    Cases:

    1. ``CUSTOMIZED_SIMULATION/{bundle}/Customized-agents``
       → ``examples/CUSTOMIZED_SIMULATION/{bundle}/Customized-agents/Rule/analysis.py``
       (bundle Customize path — Rule variant is authoritative for analysis;
       LLM/Rule-LLM/Rag variants delegate to the same maths.)

    2. ``CUSTOMIZED_SIMULATION/{bundle}/Default/{variant}``
       → ``examples/CUSTOMIZED_SIMULATION/{bundle}/Default/{variant}/analysis.py``
       (bundle Default path — variant-specific script inside the bundle.)

    3. ``CUSTOMIZED_SIMULATION/Default-{S}-{V}-rN`` (legacy rounds-adjusted
       shipped-scenario copy, has no bundle-local code) → shipped
       ``examples/{S}/{V}/analysis.py``.

    4. Anything else (raw shipped scenario) → shipped
       ``examples/{scenario_name}/analysis.py`` with Rule variant fallback.

    For case (1) we also idempotently call ``_localize_bundle_imports`` so
    that legacy bundles created BEFORE import-localisation landed also work
    — the marker comment in the prelude prevents duplicate injection.

    Args:
        scenario_name: Name of the scenario (may be a CUSTOMIZED_SIMULATION key)

    Returns:
        Tuple of (success, message)
    """
    from ..config_loader import get_analysis_path, _resolve_display_key
    from ..customized.config_writer import _localize_bundle_imports

    try:
        _project_root = Path(__file__).resolve().parents[3]

        # Config path is uniform: configs/{scenario_name}/simulation.yml.
        config_path = _project_root / "configs" / scenario_name / "simulation.yml"

        # ── Resolve the analysis script + PYTHONPATH additions ──────────────
        # ``extra_pythonpath`` — list of directories prepended to PYTHONPATH so
        # bundle-local short-form imports (``from metrics import REGISTRY``)
        # resolve inside the bundle. Empty for shipped scenarios where the
        # existing ``from examples.{S}.metrics import …`` shape works.
        script_path: Path
        extra_pythonpath: list[str] = []

        parts = scenario_name.split("/")
        if (
            scenario_name.startswith("CUSTOMIZED_SIMULATION/")
            and len(parts) == 3
            and parts[2] == "Customized-agents"
        ):
            # Case 1: project bundle Customize path — ALWAYS use bundle-local.
            bundle_name = parts[1]
            bundle_examples = (
                _project_root / "examples" / "CUSTOMIZED_SIMULATION"
                / bundle_name / "Customized-agents"
            )
            bundle_configs = (
                _project_root / "configs" / "CUSTOMIZED_SIMULATION"
                / bundle_name / "Customized-agents"
            )
            script_path = bundle_examples / "Rule" / "analysis.py"

            # Heal legacy bundles created before import-localisation: idempotent
            # thanks to the sys.path prelude marker inside _localize_bundle_imports.
            if bundle_examples.exists():
                try:
                    scenario_base = bundle_name.rsplit("-", 1)[-1]
                    _localize_bundle_imports(
                        example_dir=bundle_examples,
                        config_dir=bundle_configs,
                        scenario_name=scenario_base,
                        bundle_name=bundle_name,
                    )
                except Exception:
                    # Non-fatal: if healing fails, the shipped-import shape
                    # may still work when PYTHONPATH covers project root.
                    pass

            # Bundle-local Python files use short-form imports (``from metrics
            # import REGISTRY``, ``from Rule.players import Market``). Adding
            # the bundle's Customized-agents/ to PYTHONPATH is what makes them
            # resolve locally instead of from the shipped examples/.
            extra_pythonpath.append(str(bundle_examples))
        elif (
            scenario_name.startswith("CUSTOMIZED_SIMULATION/")
            and len(parts) >= 4
            and parts[2] == "Default"
        ):
            # Case 2: project bundle Default path.
            bundle_name = parts[1]
            variant = parts[3]
            bundle_examples = (
                _project_root / "examples" / "CUSTOMIZED_SIMULATION"
                / bundle_name / "Default" / variant
            )
            script_path = bundle_examples / "analysis.py"
            extra_pythonpath.append(str(bundle_examples.parent))
        else:
            # Cases 3–4: legacy Default-{S}-{V}-rN or plain shipped scenarios.
            display_key = _resolve_display_key(scenario_name)
            script_path = _project_root / "examples" / display_key / "analysis.py"
            if not script_path.exists() and "/" not in display_key:
                script_path = (
                    _project_root / "examples" / display_key / "Rule" / "analysis.py"
                )

        if not script_path.exists():
            return False, f"Analysis script not found: {script_path}"
        if not config_path.exists():
            return False, f"Config not found: {config_path}"

        # Remove charts from any previous run before regenerating. Older
        # versions of an analysis script may have used a different filename
        # scheme (e.g. 01_anchoringeffect_dynamics.png vs 01_price_dynamics.png);
        # since the current script writes different names it never overwrites
        # those leftovers, so they pile up and show as duplicate 00/01/02…
        # numbers in the gallery. Clearing first guarantees the gallery matches
        # exactly what this run produced.
        analysis_dir = get_analysis_path(scenario_name)
        if analysis_dir and analysis_dir.exists():
            for old_png in analysis_dir.glob("*.png"):
                try:
                    old_png.unlink()
                except OSError:
                    pass

        # The analysis script does ``from masim import ...``; when run as a
        # subprocess Python only puts the SCRIPT's own directory on sys.path
        # (not cwd), so the top-level ``masim`` package is invisible. Inject
        # the project root via PYTHONPATH so the import resolves without
        # requiring an installed/editable package. Bundle-local dirs are
        # prepended so short-form imports resolve *inside* the bundle before
        # any shipped package of the same short name (defence in depth).
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            filter(
                None,
                [*extra_pythonpath, str(_project_root), env.get("PYTHONPATH", "")],
            )
        )

        result = subprocess.run(
            [sys.executable, str(script_path), "-c", str(config_path)],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(_project_root),
            env=env,
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
    import re as _re

    # 1. Summary metrics + validation
    summary_path = analysis_path / "summary.json"
    if summary_path.exists():
        _display_summary(summary_path)
        st.markdown("---")

    # 2. Charts — deduplicate by numeric prefix
    all_images = sorted(analysis_path.glob("*.png"))
    if not all_images:
        st.info("No analysis charts found.")
        return

    # Group by leading numeric prefix (e.g., "01_", "02_"). When multiple
    # files share a prefix (old vs new naming scheme), keep only the newest.
    _PREFIX_RE = _re.compile(r"^(\d+)[_\-]")
    prefix_groups: dict = {}  # prefix -> list of Path
    no_prefix: list = []
    for img in all_images:
        m = _PREFIX_RE.match(img.name)
        if m:
            prefix_groups.setdefault(m.group(1), []).append(img)
        else:
            no_prefix.append(img)

    images: list = []
    for prefix in sorted(prefix_groups.keys()):
        group = prefix_groups[prefix]
        if len(group) == 1:
            images.append(group[0])
        else:
            # Keep only the newest file in this prefix group
            images.append(max(group, key=lambda p: p.stat().st_mtime))
    images.extend(sorted(no_prefix))

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
    # The richest validation card lives under scenario_metrics.validation; the
    # top-level "validation" is usually an empty placeholder (score=null), which
    # previously showed the useless "Validation result available" line with no
    # Fit Score. Pick the first candidate that actually carries a score.
    validation = {}
    for cand in (
        summary.get("scenario_metrics", {}).get("validation"),
        summary.get("validation"),
        summary.get("universal_metrics", {}).get("validation"),
    ):
        if isinstance(cand, dict) and cand.get("score") is not None:
            validation = cand
            break
    if not validation:
        validation = summary.get("scenario_metrics", {}).get("validation") or {}

    score = validation.get("score", validation.get("fit_score"))
    interpretation = validation.get("interpretation", "")

    # Fit Score — shown as a neutral data card. The interface ONLY reports the
    # number from the data; it does NOT synthesise a PASS/FAIL verdict or use
    # traffic-light colouring (those are conclusions, not raw data).
    if score is not None:
        pct = score if score > 1 else score * 100
        st.markdown(
            f"""
            <div style="
                background:#2b2b3d;
                border-radius:10px;
                padding:14px 16px;
                text-align:center;
                color:white;
                font-size:22px;
                font-weight:bold;
                width:160px;
            ">
                {pct:.1f}%
                <div style="font-size:12px;font-weight:normal;margin-top:2px;">Fit Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Validation criteria — faithful data only: observed value, target band and
    # the per-criterion score. No verdict marks are added by the interface.
    criteria = validation.get("criteria", {})
    if criteria:
        c_cols = st.columns(min(len(criteria), 4))
        for i, (name, crit) in enumerate(criteria.items()):
            with c_cols[i % 4]:
                label = name.replace("_", " ").title()
                val = crit.get("value")
                val_str = (
                    f"{val:.3f}" if isinstance(val, (int, float)) else str(val)
                )
                parts = []
                if crit.get("target") is not None:
                    parts.append(f"Target: {crit['target']}")
                if isinstance(crit.get("score"), (int, float)):
                    parts.append(f"Score: {crit['score']:.3f}")
                st.metric(label, val_str, help="  |  ".join(parts) or None)

    # Advisories — verbatim notes from the data
    advisories = validation.get("advisories", [])
    if advisories:
        for note in advisories:
            st.caption(note)

    # Full textual analysis, verbatim from summary.json
    if interpretation:
        st.subheader("Detailed Analysis")
        st.code(interpretation, language=None)

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
