"""Interactive D3.js force-directed topology graph for the Experience mode.

Embeds a self-contained HTML/SVG component via ``st.components.v1.html``
that renders agent nodes (with circular icon avatars), directed links,
hover tooltips, and click-to-highlight interactions.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import streamlit.components.v1 as components
import streamlit as st

# ---------------------------------------------------------------------------
# Asset paths (same constants used across the interface layer)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ICON_ROOT = _PROJECT_ROOT / "examples" / "AGENT_POOL" / "agent_images" / "icons"

# Variant prefixes that may appear on identity strings in scenario configs.
# Every non-Rule variant identity is expected to follow ``{variant}_{archetype}``
# (Rule identities also carry the ``rule_`` prefix). Assets (icons, .md profiles)
# are keyed by the pure archetype stem, so the prefix is stripped before lookup.
_VARIANT_PREFIXES: tuple[str, ...] = ("rule_", "llm_", "rulellm_", "ragllm_")


def _canonical_archetype(player_id: str) -> str:
    """Strip a known ``{variant}_`` prefix, returning the pure archetype stem.

    Used for asset resolution (icon PNG, profile ``.md``). Falls through
    unchanged when no known prefix matches (e.g. ``market``).
    """
    for prefix in _VARIANT_PREFIXES:
        if player_id.startswith(prefix):
            return player_id[len(prefix):]
    return player_id


def _image_data_uri(path: Path) -> str:
    """Encode a PNG file as a base64 data URI."""
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _resolve_icon_uri(node_id: str) -> str:
    """Resolve a player_id (snake_case) to a base64 icon data URI, or empty.

    Convention: every agent has an ``.md`` file whose stem equals its
    player_id in kebab-case; the same stem names its icon as
    ``finance-{kebab_id}.png``. Only a direct filename lookup is performed —
    scenarios that need a shared archetype must ship a thin alias ``.md``
    (and a companion icon copy) under the pool.

    The ``market`` hub is intentionally skipped: its icon depends on the
    scenario's coordinator archetype (bond / credit / fx / stock / …) and
    must be resolved via :func:`market_icon_uri` by the caller.
    """
    if not node_id or node_id == "market":
        return ""
    archetype = _canonical_archetype(node_id)
    kebab = archetype.replace("_", "-")
    candidate = _ICON_ROOT / f"finance-{kebab}.png"
    if candidate.exists():
        return _image_data_uri(candidate)
    return ""


def market_icon_uri(scenario_base: str) -> str:
    """Return the base64-encoded market coordinator icon for a scenario.

    Delegates to :func:`config_loader.get_market_icon_path`, which reads
    the scenario's ``players.yml → market.archetype:`` field and maps
    it to ``examples/AGENT_POOL/agent_images/icons/market/{archetype}.png``.

    Callers wire the result into the topology renderer via
    ``icon_uris={"market": market_icon_uri(base), …}`` so the hub
    node shows the actual market family (stock / FX / credit / crypto /
    deposit / derivatives / bond / opinion / information) instead of the
    generic gold-circle fallback. Returns an empty string when the
    scenario has no archetype-bound icon.
    """
    if not scenario_base:
        return ""
    # Lazy import to avoid a hard dependency on the config loader at
    # module-import time (topology_d3 is used from many entry points).
    from ..config_loader import get_market_icon_path

    path = get_market_icon_path(scenario_base)
    if path is None or not path.exists():
        return ""
    return _image_data_uri(path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_d3_topology(
    topology: dict[str, Any],
    agents: list[dict[str, Any]],
    height: int = 420,
    icon_uris: dict[str, str] | None = None,
) -> None:
    """Render an interactive D3.js force-directed topology graph.

    Args:
        topology: Output of ``get_topology_info()`` — keys: nodes, connections,
                  topology_type, sources.
        agents: Output of ``get_agents_info()`` — list of dicts with id, name,
                theory, instances, role.
        height: Pixel height for the embedded HTML component.
        icon_uris: Optional mapping ``node_id -> data URI`` that takes
                   precedence over the built-in ``finance-{stem}.png`` resolver.
                   Used by the customize preview to display icons for
                   non-finance domains (e.g., ``opinion/``).
    """
    # Build lookup: node_id -> agent metadata
    agent_map: dict[str, dict] = {}
    for a in agents:
        agent_map[a["id"]] = a

    # Build D3 graph data — expand each agent type into individual instances
    # (e.g. anchored_trader x2 → anchored_trader_1, anchored_trader_2).
    nodes: list[dict] = []
    # Track base_key → list of expanded instance IDs for link expansion.
    expansion_map: dict[str, list[str]] = {}

    for node_id in topology["nodes"]:
        meta = agent_map.get(node_id, {})
        is_hub = node_id in topology.get("sources", [])
        count = meta.get("instances", 1)
        icon_uri = (icon_uris or {}).get(node_id) or _resolve_icon_uri(node_id)
        base_name = meta.get(
            "name", _canonical_archetype(node_id).replace("_", " ").title()
        )
        theory = meta.get("theory") or meta.get("principle") or ""

        if is_hub or count <= 1:
            # Single node (hub or singleton agent)
            nodes.append({
                "id": node_id,
                "name": base_name,
                "theory": theory,
                "icon": icon_uri,
                "isHub": is_hub,
            })
            expansion_map[node_id] = [node_id]
        else:
            # Expand into numbered instances
            instance_ids = []
            for i in range(1, count + 1):
                inst_id = f"{node_id}_{i}"
                instance_ids.append(inst_id)
                nodes.append({
                    "id": inst_id,
                    "name": f"{base_name} #{i}",
                    "theory": theory,
                    "icon": icon_uri,
                    "isHub": False,
                })
            expansion_map[node_id] = instance_ids

    # Expand links: replace base keys with all their instances.
    links: list[dict] = []
    connections = topology.get("connections", {})
    for src, targets in connections.items():
        if not isinstance(targets, list):
            continue
        src_ids = expansion_map.get(src, [src])
        for tgt in targets:
            tgt_ids = expansion_map.get(tgt, [tgt])
            for s in src_ids:
                for t in tgt_ids:
                    links.append({"source": s, "target": t})

    graph_json = json.dumps({"nodes": nodes, "links": links})

    html = _build_html(graph_json, height)
    components.html(html, height=height, scrolling=False)


# ---------------------------------------------------------------------------
# Expand-to-modal wrapper
# ---------------------------------------------------------------------------

_EXPAND_CSS_FLAG = "_topology_expand_css_injected"


def _inject_expand_css() -> None:
    """Inject scoped CSS for the topology expand button once per session."""
    if st.session_state.get(_EXPAND_CSS_FLAG):
        return
    st.markdown(
        """
        <style>
        [class*="st-key-topology_expand_"] button {
            font-size: 2.9rem !important;
            font-weight: 900 !important;
            padding: 0 8px !important;
            min-height: 0 !important;
            height: auto !important;
            line-height: 1.0 !important;
            color: #17212b !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            text-shadow: 0 0 0.6px currentColor, 0 0 0.6px currentColor;
            float: right;
        }
        [class*="st-key-topology_expand_"] button:hover {
            color: #000000 !important;
            background: rgba(23, 33, 43, 0.10) !important;
            border-radius: 6px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.session_state[_EXPAND_CSS_FLAG] = True


@st.dialog("Network topology", width="large")
def _topology_dialog(
    topology: dict[str, Any],
    agents: list[dict[str, Any]],
    icon_uris: dict[str, str] | None,
    caption: str | None,
) -> None:
    """Modal that re-renders the same topology at a much larger canvas."""
    if caption:
        st.caption(caption)
    if not topology or not topology.get("nodes"):
        st.caption("No topology data available.")
        return
    render_d3_topology(topology, agents, height=620, icon_uris=icon_uris)


def render_d3_topology_with_expand(
    topology: dict[str, Any],
    agents: list[dict[str, Any]],
    *,
    height: int = 340,
    icon_uris: dict[str, str] | None = None,
    key: str,
    title: str | None = "Network topology",
    dialog_caption: str | None = None,
) -> None:
    """Render a D3 topology with a compact expand icon that opens a modal.

    The expand button (⤢) appears in the top-right corner adjacent to
    the ``title``. Clicking it opens a large modal that re-renders the
    exact same topology data at height=620 for detailed inspection.

    Args:
        topology: Same shape as ``render_d3_topology``.
        agents: Same shape as ``render_d3_topology``.
        height: Compact-view height in px.
        icon_uris: Optional icon overrides forwarded to both the compact
            renderer and the modal.
        key: Suffix used to uniqueness-scope the expand button widget key.
            Must be unique per topology on the same page.
        title: Section header rendered above the compact view. Pass
            ``None`` to suppress (useful when the caller already rendered
            a matching header).
        dialog_caption: Optional caption line shown inside the modal.
    """
    _inject_expand_css()
    if title is not None:
        title_col, expand_col = st.columns([4, 1])
        with title_col:
            st.markdown(f"**{title}**")
        with expand_col:
            if st.button(
                "⤢",
                key=f"topology_expand_{key}",
                help=f"Expand the {title.lower()}",
                type="tertiary",
            ):
                _topology_dialog(topology, agents, icon_uris, dialog_caption)
    else:
        # No title: still expose an expand button on its own row.
        if st.button(
            "⤢",
            key=f"topology_expand_{key}",
            help="Expand the network topology",
            type="tertiary",
        ):
            _topology_dialog(topology, agents, icon_uris, dialog_caption)
    render_d3_topology(topology, agents, height=height, icon_uris=icon_uris)


# ---------------------------------------------------------------------------
# HTML + D3 template
# ---------------------------------------------------------------------------

def _build_html(graph_json: str, height: int) -> str:
    """Generate self-contained HTML with embedded D3.js force graph.

    Uses a CDN with an onerror fallback that displays a graceful offline
    message instead of a blank/broken graph when the network is unavailable.
    """
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://d3js.org/d3.v7.min.js" onerror="document.getElementById('d3-error').style.display='flex';document.getElementById('d3-graph').style.display='none';"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: transparent; overflow: hidden; }}
  svg {{ display: block; width: 100%; height: {height}px; }}
  #d3-error {{
    display: none; align-items: center; justify-content: center;
    height: {height}px; font: 14px/1.5 -apple-system, BlinkMacSystemFont, sans-serif;
    color: #64748b; text-align: center; padding: 2rem;
  }}
  .tooltip {{
    position: absolute; pointer-events: none;
    background: #fff; border: 1px solid #dde4ea;
    border-radius: 8px; padding: 8px 12px;
    font: 12px/1.4 -apple-system, BlinkMacSystemFont, sans-serif;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    opacity: 0; transition: opacity 0.15s;
    max-width: 220px; z-index: 10;
  }}
  .tooltip .tt-name {{ font-weight: 700; color: #1a2633; margin-bottom: 2px; }}
  .tooltip .tt-theory {{ font-size: 11px; color: #5a6b78; }}
  .tooltip .tt-count {{ font-size: 10px; color: #8a9aa8; margin-top: 3px; }}
  .link {{ stroke: #c0c8d0; stroke-width: 1.5; fill: none; }}
  .link.highlighted {{ stroke: #2a5fa6; stroke-width: 2.5; }}
  .link.dimmed {{ stroke: #eaeef2; stroke-width: 1; }}
  .node-label {{
    font: 10px/1 -apple-system, BlinkMacSystemFont, sans-serif;
    fill: #4a5b6a; text-anchor: middle; pointer-events: none;
  }}
  .node.dimmed {{ opacity: 0.25; }}
</style>
</head>
<body>
<div id="d3-error"><p>Network topology visualization requires an internet connection.<br>Please check your network and refresh.</p></div>
<div id="d3-graph">
<div id="graph"></div>
<div class="tooltip" id="tooltip"></div>
</div>
<script>
(function() {{
  if (typeof d3 === 'undefined') return;
  const data = {graph_json};
  const width = document.body.clientWidth || 500;
  const height = {height};
  const hubRadius = 28, nodeRadius = 20;

  const svg = d3.select("#graph").append("svg")
    .attr("width", width).attr("height", height);

  // Arrowhead marker
  svg.append("defs").append("marker")
    .attr("id", "arrow").attr("viewBox", "0 -5 10 10")
    .attr("refX", 24).attr("refY", 0)
    .attr("markerWidth", 6).attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path").attr("d", "M0,-4L8,0L0,4")
    .attr("fill", "#c0c8d0");

  // Circular clip paths for icons
  const defs = svg.select("defs");
  data.nodes.forEach(n => {{
    const r = n.isHub ? hubRadius : nodeRadius;
    defs.append("clipPath").attr("id", "clip-" + n.id)
      .append("circle").attr("r", r).attr("cx", 0).attr("cy", 0);
  }});

  // Force simulation
  const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(d => d.id).distance(70))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide().radius(d => (d.isHub ? hubRadius : nodeRadius) + 8));

  // Pin hub nodes near center
  data.nodes.forEach(n => {{
    if (n.isHub) {{ n.fx = width / 2; n.fy = height / 2; }}
  }});

  // Links
  const link = svg.append("g").selectAll("line")
    .data(data.links).enter().append("line")
    .attr("class", "link")
    .attr("marker-end", "url(#arrow)");

  // Node groups
  const node = svg.append("g").selectAll("g")
    .data(data.nodes).enter().append("g")
    .attr("class", "node")
    .call(d3.drag()
      .on("start", dragStart)
      .on("drag", dragging)
      .on("end", dragEnd));

  // Node visuals
  node.each(function(d) {{
    const g = d3.select(this);
    const r = d.isHub ? hubRadius : nodeRadius;
    if (d.icon) {{
      g.append("image")
        .attr("href", d.icon)
        .attr("width", r * 2).attr("height", r * 2)
        .attr("x", -r).attr("y", -r)
        .attr("clip-path", "url(#clip-" + d.id + ")");
      // Border: gold when this is the market hub (preserves the
      // "hub" visual language even though we now show a real icon),
      // subtle gray for regular agent nodes.
      g.append("circle").attr("r", r)
        .attr("fill", "none")
        .attr("stroke", d.isHub ? "#d4a843" : "#dde4ea")
        .attr("stroke-width", d.isHub ? 2 : 1.5);
    }} else if (d.isHub) {{
      // Market hub: gold circle
      g.append("circle").attr("r", r)
        .attr("fill", "#fdf6e3").attr("stroke", "#d4a843").attr("stroke-width", 2);
      g.append("text")
        .attr("text-anchor", "middle").attr("dy", "0.35em")
        .style("font-size", "11px").style("font-weight", "700").style("fill", "#8a6d14")
        .text("Market");
    }} else {{
      // Agent without icon: neutral blue circle with initial
      g.append("circle").attr("r", r)
        .attr("fill", "#e8f0fb").attr("stroke", "#7baed4").attr("stroke-width", 1.5);
      const initial = d.name ? d.name.charAt(0).toUpperCase() : "?";
      g.append("text")
        .attr("text-anchor", "middle").attr("dy", "0.35em")
        .style("font-size", "12px").style("font-weight", "700").style("fill", "#2a5fa6")
        .text(initial);
    }}
  }});

  // Labels below nodes. Agents always get a name label; the market hub
  // shows a "Market" caption only when it displays an icon (otherwise
  // the "Market" text is already rendered inside the gold circle).
  node.filter(d => !d.isHub).append("text")
    .attr("class", "node-label")
    .attr("dy", d => (d.isHub ? hubRadius : nodeRadius) + 14)
    .text(d => {{
      const name = d.name;
      return name.length > 14 ? name.substring(0, 12) + "..." : name;
    }});
  node.filter(d => d.isHub && d.icon).append("text")
    .attr("class", "node-label")
    .attr("dy", hubRadius + 14)
    .style("font-weight", "700")
    .style("fill", "#8a6d14")
    .text("Market");

  // Tooltip
  const tooltip = d3.select("#tooltip");

  node.on("mouseover", function(event, d) {{
    let html = '<div class="tt-name">' + d.name + '</div>';
    if (d.theory) html += '<div class="tt-theory">' + d.theory + '</div>';
    if (d.instances > 1) html += '<div class="tt-count">' + d.instances + ' instances</div>';
    tooltip.html(html).style("opacity", 1)
      .style("left", (event.pageX + 12) + "px")
      .style("top", (event.pageY - 10) + "px");
  }})
  .on("mousemove", function(event) {{
    tooltip.style("left", (event.pageX + 12) + "px")
      .style("top", (event.pageY - 10) + "px");
  }})
  .on("mouseout", function() {{
    tooltip.style("opacity", 0);
  }});

  // Click to highlight
  let selectedNode = null;
  node.on("click", function(event, d) {{
    event.stopPropagation();
    if (selectedNode === d.id) {{
      // Deselect
      selectedNode = null;
      link.attr("class", "link");
      node.attr("class", "node");
    }} else {{
      selectedNode = d.id;
      // Connected node IDs
      const connected = new Set();
      connected.add(d.id);
      data.links.forEach(l => {{
        const sid = typeof l.source === "object" ? l.source.id : l.source;
        const tid = typeof l.target === "object" ? l.target.id : l.target;
        if (sid === d.id) connected.add(tid);
        if (tid === d.id) connected.add(sid);
      }});
      link.attr("class", l => {{
        const sid = typeof l.source === "object" ? l.source.id : l.source;
        const tid = typeof l.target === "object" ? l.target.id : l.target;
        if (sid === d.id || tid === d.id) return "link highlighted";
        return "link dimmed";
      }});
      node.attr("class", n => connected.has(n.id) ? "node" : "node dimmed");
    }}
  }});

  // Click background to deselect
  svg.on("click", function() {{
    selectedNode = null;
    link.attr("class", "link");
    node.attr("class", "node");
  }});

  // Tick
  simulation.on("tick", () => {{
    link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
    node.attr("transform", d => "translate(" + d.x + "," + d.y + ")");
  }});

  // Drag handlers
  function dragStart(event, d) {{
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x; d.fy = d.y;
  }}
  function dragging(event, d) {{
    d.fx = event.x; d.fy = event.y;
  }}
  function dragEnd(event, d) {{
    if (!event.active) simulation.alphaTarget(0);
    if (!d.isHub) {{ d.fx = null; d.fy = null; }}
  }}
}})();
</script>
</body>
</html>"""
