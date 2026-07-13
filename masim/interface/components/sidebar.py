"""Sidebar component for scenario selection and agent information."""

import io
import hashlib
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import streamlit as st
from typing import Callable, Optional

matplotlib.use("Agg")

# Agent icon library (kebab-case PNGs keyed by player base id).
ICON_ROOT = (
    Path(__file__).resolve().parents[3]
    / "examples"
    / "AGENT_POOL"
    / "agent_images"
    / "icons"
)

from ..config_loader import (
    get_scenario_info,
    get_agents_info,
    get_topology_info,
    get_market_type,
    get_market_description,
    get_diagram_path,
    scenario_display_name,
    _resolve_display_key,
    CONFIGS_DIR,
    EXPERIMENT_DIR,
    _configs_path,
    _experiment_path,
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
        project_name = st.session_state.get("project_name", "")
        if project_name:
            st.caption(f"Project: {project_name}")
        st.markdown("---")

        # ------------------------------------------------------------------
        # Committed-scenario display (read-only)
        # ------------------------------------------------------------------
        # The scenario (and variant) is committed back in Stage 1 (scenario
        # picker -> "Choose how to run it"), so the sidebar never offers a
        # scenario / variant picker here. We simply show the committed
        # scenario -- or the customized bundle -- read-only, then render its
        # config detail below as a brief introduction.
        active = st.session_state.get("selected_scenario", "")
        if active.startswith("CUSTOMIZED_SIMULATION/"):
            customized_id = active.split("/", 1)[1] if "/" in active else active
            if customized_id.startswith("Default-"):
                # A rounds-adjusted copy of a shipped scenario. There is no
                # user-built roster to edit, so we simply render the bundle's
                # own config below in the standard read-only display mode.
                # The bundle is metadata-identical to the source scenario, so
                # show that scenario's display name (not the raw bundle id).
                selected_scenario = active
                st.session_state.selected_scenario = active
                st.subheader(scenario_display_name(_resolve_display_key(active)))
            else:
                st.subheader("Customized bundle")
                st.markdown(
                    f"<div style='font-size:13px;line-height:1.6;'>"
                    f"✨ <b>{customized_id}</b><br>"
                    f"<span style='color:#9ba8bb;'>Built from your custom "
                    f"roster in Stage 2.</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Edit roster",
                    width="stretch",
                    key="sidebar_edit_customized",
                    help="Return to Stage 2 to modify the agent lineup.",
                ):
                    st.session_state.workflow_stage = "customize"
                    st.rerun()

                # Compact read-only bundle summary (rounds + roster size).
                try:
                    info = get_scenario_info(active)
                    rounds = info.get("total_rounds") or info.get("rounds") or "-"
                except Exception:
                    rounds = "-"
                try:
                    agents = get_agents_info(active)
                    roster_size = sum(
                        int(a.get("instances", 1) or 1) for a in agents
                    )
                    roster_kinds = len(agents)
                except Exception:
                    roster_size = 0
                    roster_kinds = 0

                st.markdown(
                    f"<div style='margin-top:8px;font-size:12px;"
                    f"line-height:1.6;color:#cbd2dc;'>"
                    f"• Rounds: <b>{rounds}</b><br>"
                    f"• Roster: <b>{roster_size}</b> agents"
                    f" ({roster_kinds} archetypes)"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("---")
                st.caption("MASIM v0.1.0 | Multi-Agent Simulation Platform")
                return active
        elif active:
            # A shipped scenario committed in Stage 1. Show its name here;
            # the read-only detail block below acts as the brief intro.
            selected_scenario = active
            st.session_state.selected_scenario = active
            st.subheader(scenario_display_name(active))
        else:
            st.warning("No scenario selected. Use the top bar to pick one.")
            st.session_state.selected_scenario = ""
            return ""

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
        # Network Topology — dynamic D3 force-directed diagram matching the
        # Experience-mode preview and the Project-mode Default preview.
        # Falls back to the legacy static preview only when no topology is
        # available for the scenario.
        # ------------------------------------------------------------------
        st.markdown("---")
        st.markdown("**Network Topology**")

        topo = get_topology_info(selected_scenario)
        agents_for_topo = get_agents_info(selected_scenario)
        if topo.get("nodes"):
            from .topology_d3 import render_d3_topology
            render_d3_topology(topo, agents_for_topo, height=320)
        else:
            icon_preview = _get_or_create_icon_topology_preview(selected_scenario)
            if icon_preview is not None:
                st.image(str(icon_preview), width="stretch")
            else:
                diagram_path = get_diagram_path(selected_scenario)
                if diagram_path is not None:
                    st.image(str(diagram_path), width="stretch")
                else:
                    preview_path = _get_or_create_topology_preview(selected_scenario)
                    if preview_path is not None:
                        st.image(str(preview_path), width="stretch")
                    else:
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
                        st.image(buf, width="stretch")
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
            width="stretch",
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

    # A rounds-adjusted Default bundle shares the source scenario's topology,
    # so cache/render the preview against the original scenario key.
    scenario_name = _resolve_display_key(scenario_name)
    topology_path = _configs_path(scenario_name) / "topology.yml"
    players_path = _configs_path(scenario_name) / "players.yml"

    if not topology_path.exists():
        return None

    # Compute a content-hash over source files to detect staleness
    hash_src = _file_content_hash(topology_path)
    if players_path.exists():
        hash_src += _file_content_hash(players_path)
    config_fingerprint = hashlib.md5(hash_src.encode()).hexdigest()[:8]

    preview_dir = _experiment_path(scenario_name) / "records" / "diagrams"
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


def _load_yaml_lenient(path: Path) -> dict:
    """Load a config YAML, ignoring custom tags such as ``!include``.

    The topology preview only needs structural data (num_instances,
    connections), so unknown tags (e.g. ``persona: !include persona.yml``)
    are safely resolved to None instead of raising.
    """
    import yaml

    class _LenientLoader(yaml.SafeLoader):
        pass

    _LenientLoader.add_constructor(
        "!include", lambda loader, node: None
    )
    _LenientLoader.add_multi_constructor(
        "", lambda loader, tag_suffix, node: None
    )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=_LenientLoader) or {}


def _icon_for_base(base_key: str) -> Optional[Path]:
    """Map a player base id (snake_case) to its agent icon PNG, if any.

    Icons are stored kebab-cased with a ``finance-`` domain prefix in
    ``agent_images/icons`` (e.g. the player ``anchored_trader`` ->
    ``finance-anchored-trader.png``). The market coordinator has no icon
    and returns None so callers draw the hub explicitly.
    """
    if not base_key or base_key == "market":
        return None
    candidate = ICON_ROOT / f"finance-{base_key.replace('_', '-')}.png"
    return candidate if candidate.exists() else None


def _get_or_create_icon_topology_preview(scenario_name: str) -> Optional[Path]:
    """Render a star-topology diagram whose nodes are agent icons.

    Each concrete investor instance is drawn as its agent icon (mapped from
    the player base id); the market hub is a labelled gold circle. Nodes with
    no matching icon fall back to a coloured circle. The image is cached at
    ``EXPERIMENT/{scenario}/records/diagrams/topology_icons.png`` and rebuilt
    only when topology.yml / players.yml change.

    Args:
        scenario_name: Scenario key (rounds-adjusted Default bundles resolve
            to their source scenario).

    Returns:
        Path to the icon preview PNG, or None if topology.yml is missing.
    """
    scenario_name = _resolve_display_key(scenario_name)
    topology_path = _configs_path(scenario_name) / "topology.yml"
    players_path = _configs_path(scenario_name) / "players.yml"
    if not topology_path.exists():
        return None

    # Fingerprint config so edits invalidate the cached image.
    hash_src = _file_content_hash(topology_path)
    if players_path.exists():
        hash_src += _file_content_hash(players_path)
    fingerprint = hashlib.md5(hash_src.encode()).hexdigest()[:8]

    preview_dir = _experiment_path(scenario_name) / "records" / "diagrams"
    preview_path = preview_dir / "topology_icons.png"
    fingerprint_path = preview_dir / ".topology_icons_hash"
    if (
        preview_path.exists()
        and fingerprint_path.exists()
        and fingerprint_path.read_text().strip() == fingerprint
    ):
        return preview_path

    try:
        topo_cfg = _load_yaml_lenient(topology_path)

        instances: dict = {}
        if players_path.exists():
            players_cfg = _load_yaml_lenient(players_path)
            for pid, pcfg in players_cfg.items():
                if isinstance(pcfg, dict):
                    n = pcfg.get("num_instances", 1)
                    instances[pid] = int(n) if n else 1

        raw_connections: dict = topo_cfg.get("connections", {})
        raw_sources: list = topo_cfg.get("sources", [])
        hub = raw_sources[0] if raw_sources else "market"

        def _expand(node: str) -> list:
            n = instances.get(node, 1)
            return [node] if n <= 1 else [f"{node}_{i}" for i in range(1, n + 1)]

        # Collect every concrete node referenced by the topology.
        node_set: set = set()
        for src, targets in raw_connections.items():
            node_set.update(_expand(src))
            if isinstance(targets, list):
                for tgt in targets:
                    node_set.update(_expand(tgt))
        investor_nodes = sorted(n for n in node_set if n != hub)
        if not investor_nodes:
            return None

        preview_dir.mkdir(parents=True, exist_ok=True)
        fig = _render_icon_topology_figure(hub, investor_nodes, raw_connections)
        fig.savefig(
            str(preview_path),
            dpi=150,
            facecolor="#ffffff",
            bbox_inches="tight",
            pad_inches=0.1,
        )
        plt.close(fig)
        fingerprint_path.write_text(fingerprint)
        return preview_path

    except Exception as e:
        print(f"[topology_icons] Failed to generate icon preview for {scenario_name}: {e}")
        return None


def _base_of_node(node: str) -> str:
    """Strip a trailing ``_<n>`` instance suffix to recover the base player id."""
    import re

    return re.sub(r"_\d+$", "", node)


def _place_node_icon(ax, img_path: Path, x: float, y: float, half: float) -> None:
    """Draw an agent icon centered at (x, y) with the given data half-size."""
    img = mpimg.imread(str(img_path))
    ax.imshow(
        img,
        extent=(x - half, x + half, y - half, y + half),
        zorder=5,
        interpolation="antialiased",
    )


def _render_icon_topology_figure(hub: str, investor_nodes: list, connections: dict):
    """Build the matplotlib figure for the icon star topology.

    Args:
        hub: hub node id (typically ``market``).
        investor_nodes: concrete investor instance ids on the ring.
        connections: raw base-key connection map (for edge direction hints).

    Returns:
        matplotlib Figure (caller is responsible for saving/closing).
    """
    n_inv = len(investor_nodes)
    radius = max(1.2, 0.16 * n_inv)
    icon_half = min(0.18, max(0.08, 0.85 * np.pi * radius / max(n_inv, 1) / 2))

    pos = {hub: np.array([0.0, 0.0])}
    for i, node in enumerate(investor_nodes):
        angle = 2 * np.pi * i / max(n_inv, 1) - np.pi / 2
        pos[node] = np.array([radius * np.cos(angle), radius * np.sin(angle)])

    fig_size = max(5.0, radius * 2.4)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.set_aspect("equal")
    ax.axis("off")

    # Edges: hub <-> each investor.
    hub_pos = pos[hub]
    for node in investor_nodes:
        p = pos[node]
        ax.plot(
            [hub_pos[0], p[0]],
            [hub_pos[1], p[1]],
            color="#9aa4b2",
            lw=1.0,
            alpha=0.7,
            zorder=1,
        )

    # Hub node — labelled gold box.
    from matplotlib.patches import FancyBboxPatch

    hub_r = icon_half * 1.15
    box_w = hub_r * 2.6
    box_h = hub_r * 1.6
    ax.add_patch(
        FancyBboxPatch(
            (hub_pos[0] - box_w / 2, hub_pos[1] - box_h / 2),
            box_w,
            box_h,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            linewidth=1.5,
            edgecolor="#f0a500",
            facecolor="#f0a500",
            zorder=6,
        )
    )
    ax.text(
        hub_pos[0],
        hub_pos[1],
        "Market",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
        color="#0e1117",
        zorder=7,
    )

    # Investor nodes — agent icon or coloured-circle fallback.
    import re

    for node in investor_nodes:
        p = pos[node]
        base = _base_of_node(node)
        icon_path = _icon_for_base(base)
        if icon_path is not None:
            try:
                _place_node_icon(ax, icon_path, p[0], p[1], icon_half)
            except Exception:
                ax.add_patch(plt.Circle(p, icon_half, color="#3a86ff", zorder=5))
        else:
            ax.add_patch(plt.Circle(p, icon_half, color="#3a86ff", zorder=5))

        # Label from the base id (clean map lookup); append the instance
        # number when the player was expanded into multiple instances.
        label = _shorten_node_label(base)
        suffix = re.match(r".*_(\d+)$", node)
        if suffix:
            label = f"{label} {suffix.group(1)}"
        ax.text(
            p[0],
            p[1] - icon_half - 0.08,
            label,
            ha="center",
            va="top",
            fontsize=6.5 if len(label) > 10 else 7.5,
            color="#0e1117",
            zorder=7,
        )

    lim = radius + icon_half + 0.4
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    plt.tight_layout(pad=0.2)
    return fig


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
        st.write(scenario_display_name(scenario_name))

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
