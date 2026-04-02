"""Sidebar component for scenario selection and agent information."""

import io
import hashlib
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from typing import Callable, Optional

matplotlib.use("Agg")

from ..config_loader import (
    discover_scenarios,
    get_scenario_info,
    get_agents_info,
    get_scenario_pairs,
    get_topology_info,
    get_market_type,
    get_market_description,
    get_diagram_path,
    SCENARIO_DISPLAY_NAMES,
    CONFIGS_DIR,
    EXPERIMENT_DIR,
)


def render_sidebar(on_scenario_change: Optional[Callable[[str], None]] = None) -> str:
    """Render the sidebar with scenario selection and agent info.

    Args:
        on_scenario_change: Callback when scenario selection changes

    Returns:
        Selected scenario name
    """
    with st.sidebar:
        st.title("MASIM Simulator")
        st.markdown("---")

        # ------------------------------------------------------------------
        # Scenario selection
        # ------------------------------------------------------------------
        st.header("Select Scenario")

        scenario_pairs = get_scenario_pairs()

        scenario_options = []
        for base, llm in scenario_pairs:
            if base == "Demo" or llm == "Demo":
                continue
            if base and llm:
                scenario_options.append(
                    (base, f"{SCENARIO_DISPLAY_NAMES.get(base, base)} (Rule-based)")
                )
                scenario_options.append(
                    (llm, f"{SCENARIO_DISPLAY_NAMES.get(llm, llm)}")
                )
            elif base:
                scenario_options.append((base, SCENARIO_DISPLAY_NAMES.get(base, base)))
            elif llm:
                scenario_options.append((llm, SCENARIO_DISPLAY_NAMES.get(llm, llm)))

        default_idx = 0
        if "selected_scenario" in st.session_state:
            for i, (name, _) in enumerate(scenario_options):
                if name == st.session_state.selected_scenario:
                    default_idx = i
                    break

        selected_display = st.selectbox(
            "Financial Market Scenario",
            options=[opt[1] for opt in scenario_options],
            index=default_idx,
            key="scenario_select",
        )

        selected_scenario = None
        for name, display in scenario_options:
            if display == selected_display:
                selected_scenario = name
                break

        if selected_scenario is None:
            selected_scenario = scenario_options[0][0] if scenario_options else ""

        # Reset simulation state when scenario changes
        if st.session_state.get("selected_scenario") != selected_scenario:
            st.session_state.simulation_running = False
            st.session_state.simulation_completed = False
            st.session_state.current_page = "Simulation"
            # Reset replay state so the new scenario starts fresh
            st.session_state.replay_active = False
            st.session_state.replay_rounds = []
            st.session_state.replay_index = 0
            st.session_state.viewed_round_idx = 0
            st.session_state.sys_messages = []

        st.session_state.selected_scenario = selected_scenario

        # ------------------------------------------------------------------
        # Scenario Info — compact caption style
        # ------------------------------------------------------------------
        info = get_scenario_info(selected_scenario)
        market_type = get_market_type(selected_scenario)
        market_desc = get_market_description(selected_scenario)
        total_rounds = info.get("total_rounds", "N/A")
        description = info.get("description", "")
        agent_type = "LLM-based" if info.get("is_llm") else "Rule-based"

        from masim.interface.data_loader import has_experiment_data
        from masim.interface.config_loader import get_analysis_path

        data_exists = has_experiment_data(selected_scenario)
        analysis_path = get_analysis_path(selected_scenario)
        analysis_exists = analysis_path is not None and any(analysis_path.glob("*.png"))

        st.markdown("---")
        st.subheader("Scenario Info")

        # Status badges
        badge_parts = []
        if data_exists:
            badge_parts.append(
                "<span style='background:#1a5c2a;color:#6ee97b;"
                "font-size:11px;padding:2px 8px;border-radius:10px;"
                "font-weight:600;margin-right:4px'>✔ Data saved</span>"
            )
        if analysis_exists:
            badge_parts.append(
                "<span style='background:#1a3a5c;color:#7ec8e3;"
                "font-size:11px;padding:2px 8px;border-radius:10px;"
                "font-weight:600'>✔ Analysis ready</span>"
            )
        if badge_parts:
            st.markdown("".join(badge_parts), unsafe_allow_html=True)
            st.markdown("")

        # Compact info block
        lines = [
            f"• <b>Finance market:</b> {market_type}",
        ]
        if market_desc:
            lines.append(f"• <b>Description:</b> {market_desc}")
        lines += [
            f"• <b>Agent type:</b> {agent_type}",
            f"• <b>Rounds:</b> {total_rounds}",
        ]
        if description:
            lines.append(f"• <b>Simulation:</b> {description}")

        st.markdown(
            "<p style='font-size:13px; line-height:1.7; margin:0'>"
            + "<br>".join(lines)
            + "</p>",
            unsafe_allow_html=True,
        )

        # ------------------------------------------------------------------
        # Network Topology — use pre-saved diagram from EXPERIMENT/ if
        # available; otherwise generate from config and cache the preview.
        # ------------------------------------------------------------------
        st.markdown("---")
        st.markdown("**Network Topology**")

        diagram_path = get_diagram_path(selected_scenario)
        if diagram_path is not None:
            st.image(str(diagram_path), use_container_width=True)
        else:
            # Generate a full NetworkX topology preview from topology.yml +
            # players.yml and cache it so repeated loads are instant.
            preview_path = _get_or_create_topology_preview(selected_scenario)
            if preview_path is not None:
                st.image(str(preview_path), use_container_width=True)
            else:
                # Last-resort lightweight fallback (no topology.yml)
                topo = get_topology_info(selected_scenario)
                fig = _render_topology_figure(topo)
                buf = io.BytesIO()
                fig.savefig(
                    buf,
                    format="png",
                    bbox_inches="tight",
                    dpi=110,
                    facecolor=fig.get_facecolor(),
                )
                buf.seek(0)
                st.image(buf, use_container_width=True)
                plt.close(fig)

        # ------------------------------------------------------------------
        # Agent cards — show Principle + Instances + Key Params only
        # ------------------------------------------------------------------
        st.markdown("---")
        st.header("Agents")

        agents = get_agents_info(selected_scenario)
        if not agents:
            st.info("No agent configuration found")
        else:
            for agent in agents:
                _render_agent_card(agent)

        # Documentation button — opens full explain.md page
        st.markdown("")
        if st.button(
            "📖 Full Documentation",
            use_container_width=True,
            key="docs_btn",
            help="Read the academic background and model details for this scenario",
        ):
            st.session_state.current_page = "Docs"
            st.rerun()

        st.markdown("---")
        st.caption("MASIM v0.1.0 | Multi-Agent Simulation Platform")

    return selected_scenario


# ---------------------------------------------------------------------------
# Agent card
# ---------------------------------------------------------------------------


def _render_agent_card(agent: dict):
    """Render a compact agent card with Theory, Principle, Instances, and key params.

    Args:
        agent: Agent info dict from get_agents_info
    """
    icon = "🏦" if agent.get("role") == "coordinator" else "👤"
    instances = agent.get("instances", 1)
    instances_text = (
        f"{instances} instance" if instances == 1 else f"{instances} instances"
    )
    theory = agent.get("theory", "")
    principle = agent.get("principle", "")

    with st.expander(f"{icon} {agent.get('name', 'Unknown')}"):
        if theory:
            # Theory rendered as a small coloured pill
            st.markdown(
                f"<span style='"
                f"background:#1a3a5c; color:#7ec8e3; "
                f"font-size:11px; padding:2px 8px; "
                f"border-radius:10px; font-weight:600;'"
                f">{theory}</span>",
                unsafe_allow_html=True,
            )
            st.markdown("")
        if principle:
            st.caption(f"Principle: {principle}")
        st.caption(f"Instances: {instances_text}")

        params = agent.get("params", {})
        if params:
            st.caption("Key Parameters:")
            for key, value in params.items():
                display_key = key.replace("_", " ").title()
                st.caption(f"  • {display_key}: {value}")


# ---------------------------------------------------------------------------
# Pre-simulation topology preview (NetworkX, full quality)
# ---------------------------------------------------------------------------


def _get_or_create_topology_preview(scenario_name: str) -> Optional[Path]:
    """Return a cached topology preview PNG, generating it if stale or absent.

    The preview is built from topology.yml + players.yml (with num_instances
    expansion so every concrete agent instance appears as its own node).
    It is stored at EXPERIMENT/{scenario}/records/diagrams/topology_preview.png
    and regenerated only when the source config files change (mtime hash).

    Args:
        scenario_name: Scenario directory name.

    Returns:
        Path to the preview PNG, or None if topology.yml is missing.
    """
    import yaml

    topology_path = CONFIGS_DIR / scenario_name / "topology.yml"
    players_path = CONFIGS_DIR / scenario_name / "players.yml"

    if not topology_path.exists():
        return None

    # Compute a content-hash over source files to detect staleness
    hash_src = _file_content_hash(topology_path)
    if players_path.exists():
        hash_src += _file_content_hash(players_path)
    config_fingerprint = hashlib.md5(hash_src.encode()).hexdigest()[:8]

    preview_dir = EXPERIMENT_DIR / scenario_name / "records" / "diagrams"
    preview_path = preview_dir / "topology_preview.png"
    fingerprint_path = preview_dir / ".topology_preview_hash"

    # Use cached version if fingerprint matches
    if (
        preview_path.exists()
        and fingerprint_path.exists()
        and fingerprint_path.read_text().strip() == config_fingerprint
    ):
        return preview_path

    # --- Build expanded TopologyGraph ---
    try:
        with open(topology_path, "r", encoding="utf-8") as f:
            topo_cfg = yaml.safe_load(f) or {}

        # Read num_instances from players.yml for expansion
        instances: dict = {}
        if players_path.exists():
            with open(players_path, "r", encoding="utf-8") as f:
                players_cfg = yaml.safe_load(f) or {}
            for pid, pcfg in players_cfg.items():
                if isinstance(pcfg, dict):
                    n = pcfg.get("num_instances", 1)
                    instances[pid] = int(n) if n else 1

        # Expand connections: base-key nodes → concrete instance nodes
        raw_connections: dict = topo_cfg.get("connections", {})
        raw_sources: list = topo_cfg.get("sources", [])

        expanded_connections: dict = {}
        expanded_sources: list = []

        def _expand_node(node: str) -> list:
            """Return list of concrete node names for a base node key."""
            n = instances.get(node, 1)
            if n <= 1:
                return [node]
            return [f"{node}_{i}" for i in range(1, n + 1)]

        # Expand sources
        for src in raw_sources:
            expanded_sources.extend(_expand_node(src))

        # Expand connections
        for src, targets in raw_connections.items():
            if not isinstance(targets, list):
                continue
            for src_instance in _expand_node(src):
                expanded_targets = []
                for tgt in targets:
                    expanded_targets.extend(_expand_node(tgt))
                expanded_connections[src_instance] = expanded_targets

        expanded_cfg = {
            "sources": expanded_sources,
            "connections": expanded_connections,
        }

        from masim.utils.topology import TopologyGraph

        graph = TopologyGraph(expanded_cfg)

        preview_dir.mkdir(parents=True, exist_ok=True)
        graph.visualize(save_path=str(preview_path))
        fingerprint_path.write_text(config_fingerprint)
        return preview_path

    except Exception as e:
        print(f"[topology_preview] Failed to generate preview for {scenario_name}: {e}")
        return None


def _file_content_hash(path: Path) -> str:
    """Return hex digest of file contents for change detection."""
    return hashlib.md5(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Fallback topology figure (matplotlib, lightweight)
# ---------------------------------------------------------------------------


def _render_topology_figure(topo: dict):
    """Generate a star-topology diagram as a matplotlib Figure.

    Used as last-resort fallback when topology.yml is missing.

    Layout: hub at center, investor nodes on surrounding circle.

    Args:
        topo: topology info dict from get_topology_info()

    Returns:
        matplotlib Figure
    """
    connections = topo.get("connections", {})
    sources = topo.get("sources", [])

    hub = sources[0] if sources else "market"

    all_nodes: set = set()
    for src, targets in connections.items():
        all_nodes.add(src)
        if isinstance(targets, list):
            all_nodes.update(targets)
    investor_nodes = sorted(n for n in all_nodes if n != hub)
    n_inv = len(investor_nodes)

    pos = {hub: np.array([0.0, 0.0])}
    radius = 1.0
    for i, node in enumerate(investor_nodes):
        angle = 2 * np.pi * i / max(n_inv, 1) - np.pi / 2
        pos[node] = np.array([radius * np.cos(angle), radius * np.sin(angle)])

    fig_size = max(3.5, 2.0 + n_inv * 0.35)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")
    ax.set_aspect("equal")
    ax.axis("off")

    # Draw edges with direction arrows
    drawn_pairs: set = set()
    for src, targets in connections.items():
        if not isinstance(targets, list):
            continue
        p1 = pos.get(src)
        if p1 is None:
            continue
        for tgt in targets:
            p2 = pos.get(tgt)
            if p2 is None:
                continue
            pair = (min(src, tgt), max(src, tgt))
            bidirectional = pair in drawn_pairs
            drawn_pairs.add(pair)
            direction = p2 - p1
            length = np.linalg.norm(direction)
            if length == 0:
                continue
            unit = direction / length
            node_r = 0.12
            start = p1 + unit * node_r
            end = p2 - unit * node_r
            color = "#4a90d9" if (src == hub or tgt == hub) else "#888888"
            ax.annotate(
                "",
                xy=end,
                xytext=start,
                arrowprops=dict(
                    arrowstyle="->" if not bidirectional else "<->",
                    color=color,
                    lw=1.2,
                    mutation_scale=12,
                ),
            )

    hub_color = "#f0a500"
    inv_color = "#3a86ff"

    for node, p in pos.items():
        color = hub_color if node == hub else inv_color
        ax.add_patch(plt.Circle(p, 0.12, color=color, zorder=5))
        label = _shorten_node_label(node)
        fontsize = 6.5 if len(label) > 10 else 7.5
        ax.text(
            p[0],
            p[1] - 0.22,
            label,
            ha="center",
            va="top",
            fontsize=fontsize,
            color="white",
            zorder=6,
        )

    topo_type = topo.get("topology_type", "star").title()
    ax.text(
        0.5,
        0.01,
        f"{topo_type} topology",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=7,
        color="#888888",
    )

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.6, 1.5)
    plt.tight_layout(pad=0.2)
    return fig


def _shorten_node_label(name: str) -> str:
    """Map a player_id key to a short readable label for diagram nodes."""
    replacements = {
        "market": "Market",
        "momentum_speculator": "Momentum\nSpec.",
        "rational_arbitrageur": "Rational\nArb.",
        "noise_trader": "Noise\nTrader",
        "fundamental_investor": "Fundamental\nInv.",
        "leveraged_buyer": "Leveraged\nBuyer",
        "conservative_holder": "Conservative\nHolder",
        "momentum_investor": "Momentum\nInv.",
        "contrarian_investor": "Contrarian\nInv.",
        "value_investor": "Value\nInv.",
        "trend_follower": "Trend\nFollower",
        "short_seller": "Short\nSeller",
        "market_maker": "Market\nMaker",
        "herd_investor": "Herd\nInv.",
        "informed_trader": "Informed\nTrader",
        "momentum_trader": "Momentum\nTrader",
        "mean_reversion_trader": "MeanRev.\nTrader",
        "high_frequency_trader": "HFT",
        "panic_seller": "Panic\nSeller",
        "long_term_investor": "LT Inv.",
        "retail_investor": "Retail\nInv.",
        "institutional_investor": "Inst.\nInv.",
        "short_term_speculator": "ST Spec.",
        "loss_averse_investor": "Loss Averse",
        "disposition_investor": "Disposition\nInv.",
        "myopic_investor": "Myopic\nInv.",
        "risk_parity_fund": "Risk\nParity",
        "leveraged_hedge_fund": "Lev.\nHedge",
        "passive_investor": "Passive\nInv.",
        "bottom_fisher": "Bottom\nFisher",
        "fundamentalist": "Fundamental.",
        "slow_adapter": "Slow\nAdapter",
        "volatility_trader": "Vol.\nTrader",
        "stop_loss_trader": "StopLoss\nTrader",
        "algorithmic_trader": "Algo\nTrader",
        "retail_trader": "Retail\nTrader",
        "momentum_buyer": "Momentum\nBuyer",
        "institutional_holder": "Inst.\nHolder",
        "liquidity_seeker": "Liq.\nSeeker",
        "value_trader": "Value\nTrader",
        "index_fund": "Index\nFund",
        "technical_trader": "Technical\nTrader",
        "fundamental_trader": "Fundamental\nTrader",
        "overconfident_trader": "Overconf.\nTrader",
        "contrarian_trader": "Contrarian\nTrader",
        "risk_neutral_investor": "Risk\nNeutral",
        "long_horizon_investor": "Long\nHorizon",
        "myopic_loss_averse": "Myopic\nLoss Av.",
        "conservative_investor": "Conserv.\nInv.",
        "aggressive_investor": "Aggressive\nInv.",
        "risk_averse_investor": "Risk\nAverse",
        "index_holder": "Index\nHolder",
        "institutional_investor": "Inst.\nInv.",
        "tax_aware_investor": "Tax\nAware",
        "rational_investor": "Rational\nInv.",
    }
    if name in replacements:
        return replacements[name]
    parts = name.split("_")
    if len(parts) <= 2:
        return " ".join(p.title() for p in parts)
    return " ".join(p.title() for p in parts[:2]) + "."


# ---------------------------------------------------------------------------
# Analysis page sidebar (kept for completeness)
# ---------------------------------------------------------------------------


def render_analysis_sidebar(scenario_name: str):
    """Render sidebar content for analysis page.

    Args:
        scenario_name: Currently selected scenario
    """
    with st.sidebar:
        st.title("MASIM Analysis")
        st.markdown("---")

        st.header("Current Scenario")
        info = get_scenario_info(scenario_name)
        st.write(SCENARIO_DISPLAY_NAMES.get(scenario_name, scenario_name))

        if info.get("description"):
            st.caption(info["description"])

        st.markdown("---")

        from ..config_loader import check_simulation_results

        has_results = check_simulation_results(scenario_name)

        if has_results:
            st.success("Simulation results available")
        else:
            st.warning("No simulation results found")
            st.info("Run the simulation first to see analysis")

        st.markdown("---")
        st.caption("MASIM v0.1.0 | Multi-Agent Simulation Platform")
