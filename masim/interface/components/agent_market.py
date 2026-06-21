"""Agent Market and experiment setup workflow for the Streamlit interface."""

from __future__ import annotations

import base64
import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

import streamlit as st

from ..config_loader import (
    discover_scenario_groups,
    get_scenario_info,
    scenario_display_name,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
IMAGE_ROOT = PROJECT_ROOT / "investor_agent_images"
PROFILE_ROOT = PROJECT_ROOT / "agent_pool" / "ExtractedExampleInvestors" / "unique"
CATALOG_PATH = IMAGE_ROOT / "agent_avatar_map.json"
VARIANT_ORDER = {"Rule": 0, "LLM": 1, "RuleLLM": 2, "Rag": 3}


def _field_from_summary_table(markdown: str, field: str) -> str:
    pattern = rf"^\|\s*{re.escape(field)}\s*\|\s*(.*?)\s*\|\s*$"
    match = re.search(pattern, markdown, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _profile_intro(markdown: str, display_name: str) -> str:
    """Build a short hover description from the profile summary table."""
    archetype = _field_from_summary_table(markdown, "Archetype")
    scenarios = _field_from_summary_table(markdown, "Scenarios")
    count = _field_from_summary_table(markdown, "Merged profiles")

    intro = archetype or display_name
    if count:
        intro += f". {count} merged scenario roles"
    if scenarios:
        scenario_names = [item.strip() for item in scenarios.split(",") if item.strip()]
        preview = ", ".join(scenario_names[:4])
        if len(scenario_names) > 4:
            preview += f" and {len(scenario_names) - 4} more"
        intro += f" across {preview}"
    return intro + "."


def _image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


@st.cache_data(show_spinner=False)
def load_agent_catalog() -> list[dict[str, Any]]:
    """Load avatar metadata and complete Markdown profiles."""
    if CATALOG_PATH.exists():
        raw_items = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    else:
        raw_items = [
            {
                "agent_type": path.stem,
                "display_name": re.sub(r"(?<!^)(?=[A-Z])", " ", path.stem),
                "image_path": f"png/{path.name}",
                "source_profile": str(PROFILE_ROOT / f"{path.stem}.md"),
            }
            for path in sorted((IMAGE_ROOT / "png").glob("*.png"))
        ]

    catalog: list[dict[str, Any]] = []
    for item in raw_items:
        agent_type = item["agent_type"]
        display_name = item.get("display_name", agent_type)
        image_path = IMAGE_ROOT / item.get("image_path", f"png/{agent_type}.png")

        source_value = item.get("source_profile", "")
        source_path = Path(source_value)
        if not source_path.is_absolute():
            source_path = (IMAGE_ROOT / source_path).resolve()
        if not source_path.exists():
            source_path = PROFILE_ROOT / f"{agent_type}.md"

        markdown = source_path.read_text(encoding="utf-8") if source_path.exists() else ""
        catalog.append(
            {
                **item,
                "agent_type": agent_type,
                "display_name": display_name,
                "image_file": str(image_path),
                "image_uri": _image_data_uri(image_path),
                "profile_file": str(source_path),
                "profile_markdown": markdown,
                "intro": _profile_intro(markdown, display_name),
                "archetype": _field_from_summary_table(markdown, "Archetype")
                or display_name,
                "scenarios": _field_from_summary_table(markdown, "Scenarios"),
            }
        )
    return catalog


def _query_agent() -> str:
    if hasattr(st, "query_params"):
        value = st.query_params.get("agent", "")
        return value[0] if isinstance(value, list) else value
    values = st.experimental_get_query_params()
    return values.get("agent", [""])[0]


def _clear_query_agent() -> None:
    if hasattr(st, "query_params"):
        st.query_params.clear()
    else:
        st.experimental_set_query_params()


def _selected_types(catalog: list[dict[str, Any]]) -> list[str]:
    return [
        agent["agent_type"]
        for agent in catalog
        if st.session_state.get(f"market_agent_{agent['agent_type']}", False)
    ]


def _inject_market_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1240px; padding-top: 2rem;}
        .market-kicker {
            color: #287a6d; font-size: 0.78rem; font-weight: 750;
            text-transform: uppercase; letter-spacing: 0;
            margin-bottom: 0.35rem;
        }
        .agent-card {
            border: 1px solid #dce2e8; border-radius: 8px;
            background: #ffffff; overflow: hidden; min-height: 280px;
            box-shadow: 0 1px 2px rgba(20, 32, 44, 0.06);
        }
        .agent-image-link {
            display: block; position: relative; aspect-ratio: 1 / 1;
            overflow: hidden; background: #eef3f6;
        }
        .agent-image-link img {
            width: 100%; height: 100%; object-fit: cover; display: block;
            transition: transform 160ms ease;
        }
        .agent-image-link:hover img {transform: scale(1.025);}
        .agent-hover {
            position: absolute; inset: auto 0 0 0; padding: 0.75rem;
            background: rgba(17, 25, 35, 0.92); color: #f7fafc;
            font-size: 0.74rem; line-height: 1.42;
            opacity: 0; transform: translateY(6px);
            transition: opacity 150ms ease, transform 150ms ease;
        }
        .agent-image-link:hover .agent-hover,
        .agent-image-link:focus .agent-hover {opacity: 1; transform: translateY(0);}
        .agent-card-copy {padding: 0.7rem 0.8rem 0.8rem;}
        .agent-card-name {font-size: 0.92rem; font-weight: 720; color: #17212b;}
        .agent-card-type {font-size: 0.68rem; color: #68737d; margin-top: 0.18rem;}
        .profile-banner {
            border-left: 4px solid #287a6d; background: #f3f7f6;
            padding: 0.9rem 1rem; margin: 0.4rem 0 1rem;
        }
        .portfolio-strip {
            display: flex; gap: 0.45rem; flex-wrap: wrap;
            padding: 0.5rem 0 0.25rem;
        }
        .portfolio-chip {
            display: inline-flex; align-items: center; gap: 0.38rem;
            border: 1px solid #dce2e8; border-radius: 6px;
            padding: 0.28rem 0.48rem; background: #fff;
            color: #26323d; font-size: 0.74rem;
        }
        .portfolio-chip img {width: 24px; height: 24px; border-radius: 4px; object-fit: cover;}
        @media (max-width: 700px) {
            .block-container {padding-top: 1.2rem;}
            .agent-card {min-height: 230px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_workflow_sidebar(step: int, selected_count: int) -> None:
    with st.sidebar:
        st.title("MASIM")
        st.caption("Investment workflow")
        st.markdown("---")
        st.markdown(f"**{'1. Agent Market' if step == 1 else '✓ Agent Market'}**")
        st.caption(f"{selected_count} agents selected")
        st.markdown(f"**{'2. Simulation Setup' if step == 2 else '2. Simulation Setup'}**")
        st.markdown("---")
        st.caption("MASIM v0.1.0")


def _render_profile(agent: dict[str, Any]) -> None:
    st.markdown('<div id="agent-profile"></div>', unsafe_allow_html=True)
    heading, close = st.columns([5, 1])
    with heading:
        st.markdown('<div class="market-kicker">Agent profile</div>', unsafe_allow_html=True)
        st.subheader(agent["archetype"])
    with close:
        if st.button("Close", use_container_width=True, key="close_market_profile"):
            _clear_query_agent()
            st.rerun()

    image_col, profile_col = st.columns([1, 2.8], gap="large")
    with image_col:
        st.image(agent["image_file"], use_container_width=True)
        st.caption(agent["agent_type"])
    with profile_col:
        st.markdown(
            f'<div class="profile-banner">{html.escape(agent["intro"])}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(agent["profile_markdown"] or "Profile content is unavailable.")
    st.divider()


def _render_agent_card(agent: dict[str, Any]) -> None:
    agent_type = agent["agent_type"]
    href = f"?agent={quote(agent_type)}#agent-profile"
    card = f"""
    <div class="agent-card">
      <a class="agent-image-link" href="{href}" target="_self"
         title="{html.escape(agent['intro'], quote=True)}"
         aria-label="Open {html.escape(agent['display_name'])} profile">
        <img src="{agent['image_uri']}" alt="{html.escape(agent.get('alt_text', agent['display_name']))}">
        <span class="agent-hover">{html.escape(agent['intro'])}</span>
      </a>
      <div class="agent-card-copy">
        <div class="agent-card-name">{html.escape(agent['display_name'])}</div>
        <div class="agent-card-type">{html.escape(agent_type)}</div>
      </div>
    </div>
    """
    st.markdown(card, unsafe_allow_html=True)
    st.checkbox(
        "Add to portfolio",
        key=f"market_agent_{agent_type}",
        help=f"Select {agent['display_name']}",
    )


def render_agent_market() -> None:
    """Render step one: browse profiles and compose an investor portfolio."""
    _inject_market_styles()
    catalog = load_agent_catalog()

    # Streamlit removes widget keys while their page is not rendered. Restore
    # checkboxes from the durable portfolio list when users return from setup.
    saved_selection = set(st.session_state.get("selected_market_agents", []))
    for agent in catalog:
        key = f"market_agent_{agent['agent_type']}"
        if key not in st.session_state:
            st.session_state[key] = agent["agent_type"] in saved_selection

    _render_workflow_sidebar(1, len(_selected_types(catalog)))

    st.markdown('<div class="market-kicker">Step 1 of 2</div>', unsafe_allow_html=True)
    st.title("Agent Market")
    st.write("Build an investor portfolio from the available market archetypes.")

    requested_agent = _query_agent()
    by_type = {agent["agent_type"]: agent for agent in catalog}
    if requested_agent in by_type:
        _render_profile(by_type[requested_agent])

    selected_before = _selected_types(catalog)
    controls, count = st.columns([4, 1])
    with controls:
        search = st.text_input(
            "Search agents",
            placeholder="Search by name, role, or scenario",
            label_visibility="collapsed",
        )
    with count:
        st.metric("Selected", len(selected_before))

    query = search.strip().lower()
    filtered = [
        agent
        for agent in catalog
        if not query
        or query in agent["display_name"].lower()
        or query in agent["agent_type"].lower()
        or query in agent["archetype"].lower()
        or query in agent["scenarios"].lower()
    ]

    if not filtered:
        st.info("No agents match this search.")
    else:
        for start in range(0, len(filtered), 4):
            columns = st.columns(4, gap="medium")
            for column, agent in zip(columns, filtered[start : start + 4]):
                with column:
                    _render_agent_card(agent)

    selected = _selected_types(catalog)
    st.session_state.selected_market_agents = selected
    st.divider()
    reset_col, proceed_col = st.columns([1, 3])
    with reset_col:
        if st.button("Clear selection", use_container_width=True, disabled=not selected):
            for agent in catalog:
                st.session_state[f"market_agent_{agent['agent_type']}"] = False
            st.session_state.selected_market_agents = []
            st.rerun()
    with proceed_col:
        if st.button(
            "Proceed to simulation setup",
            type="primary",
            use_container_width=True,
            disabled=not selected,
        ):
            _clear_query_agent()
            st.session_state.workflow_stage = "setup"
            st.rerun()


def _render_portfolio_chips(agents: list[dict[str, Any]]) -> None:
    chips = []
    for agent in agents:
        chips.append(
            '<span class="portfolio-chip">'
            f'<img src="{agent["image_uri"]}" alt="">'
            f'{html.escape(agent["display_name"])}'
            "</span>"
        )
    st.markdown(
        f'<div class="portfolio-strip">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def render_simulation_setup() -> None:
    """Render step two: choose a scenario and variant, then review the roster."""
    _inject_market_styles()
    catalog = load_agent_catalog()
    selected_types = st.session_state.get("selected_market_agents", [])
    selected_set = set(selected_types)
    selected_agents = [a for a in catalog if a["agent_type"] in selected_set]

    if not selected_agents:
        st.session_state.workflow_stage = "agents"
        st.rerun()

    _render_workflow_sidebar(2, len(selected_agents))
    st.markdown('<div class="market-kicker">Step 2 of 2</div>', unsafe_allow_html=True)
    st.title("Simulation Setup")

    back_col, summary_col = st.columns([1, 4])
    with back_col:
        if st.button("Back", use_container_width=True):
            st.session_state.workflow_stage = "agents"
            st.rerun()
    with summary_col:
        _render_portfolio_chips(selected_agents)

    groups = discover_scenario_groups()
    group_names = list(groups)
    if not group_names:
        st.error("No simulation scenarios were found.")
        return

    current = st.session_state.get("selected_scenario", "")
    current_group = current.split("/", 1)[0] if current else group_names[0]
    default_group = group_names.index(current_group) if current_group in group_names else 0

    scenario_col, variant_col = st.columns([2, 3], gap="large")
    with scenario_col:
        selected_group = st.selectbox(
            "Scenario",
            group_names,
            index=default_group,
            format_func=scenario_display_name,
            key="market_scenario_group",
        )

    variant_keys = sorted(
        groups[selected_group],
        key=lambda key: VARIANT_ORDER.get(key.split("/")[-1], 99),
    )
    variant_labels = [key.split("/", 1)[1] if "/" in key else key for key in variant_keys]
    current_variant = current.split("/", 1)[1] if "/" in current else ""
    default_variant = (
        variant_labels.index(current_variant) if current_variant in variant_labels else 0
    )
    with variant_col:
        selected_variant = st.radio(
            "Variant",
            variant_labels,
            index=default_variant,
            horizontal=True,
            key=f"market_variant_{selected_group}",
        )

    selected_scenario = variant_keys[variant_labels.index(selected_variant)]
    st.session_state.selected_scenario = selected_scenario
    info = get_scenario_info(selected_scenario)

    market_col, mode_col, rounds_col = st.columns(3)
    market_col.metric("Market", scenario_display_name(selected_group))
    mode_col.metric("Variant", selected_variant)
    rounds_col.metric("Rounds", info.get("total_rounds", "N/A"))
    if info.get("description"):
        st.caption(info["description"])

    st.divider()
    st.subheader("Selected investor details")
    for agent in selected_agents:
        with st.expander(agent["archetype"], expanded=False):
            image_col, detail_col = st.columns([1, 3], gap="large")
            with image_col:
                st.image(agent["image_file"], use_container_width=True)
                st.caption(agent["agent_type"])
            with detail_col:
                st.markdown(agent["profile_markdown"] or "Profile content is unavailable.")

    st.divider()
    if st.button("Open simulation workspace", type="primary", use_container_width=True):
        st.session_state.workflow_stage = "workspace"
        st.session_state.current_page = "Simulation"
        st.rerun()


def render_selected_portfolio_strip() -> None:
    """Render the selected market portfolio in the simulation workspace."""
    _inject_market_styles()
    catalog = load_agent_catalog()
    selected = set(st.session_state.get("selected_market_agents", []))
    agents = [agent for agent in catalog if agent["agent_type"] in selected]
    if not agents:
        return

    heading, action = st.columns([5, 1])
    with heading:
        st.caption("Selected investor portfolio")
        _render_portfolio_chips(agents)
    with action:
        if st.button("Edit portfolio", use_container_width=True):
            st.session_state.workflow_stage = "agents"
            st.session_state.current_page = "Simulation"
            st.rerun()
