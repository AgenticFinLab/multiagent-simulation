"""Reasoning view — per-round agent decision logic explorer.

Displays each agent's reasoning, analysis, and order parameters for every
round of a completed simulation.  LLM agents show their chain-of-thought
text; Rule agents show order details (no textual reasoning is recorded for
formula-based decisions).
"""

import streamlit as st

from masim.interface.config_loader import (
    get_agent_roster,
    scenario_display_name,
)
from masim.interface.data_loader import load_rounds, RoundData, ReplayAgentAction
from masim.interface.locale import t


# ---------------------------------------------------------------------------
# Colour / styling helpers
# ---------------------------------------------------------------------------

_ACTION_COLOURS = {
    "BUY": "#28a745",
    "SELL": "#dc3545",
    "HOLD": "#6c757d",
}


def _action_badge(action: str) -> str:
    colour = _ACTION_COLOURS.get(action.upper(), "#6c757d")
    return (
        f"<span style='background:{colour};color:white;padding:2px 8px;"
        f"border-radius:4px;font-size:0.8rem;font-weight:600;'>"
        f"{action.upper()}</span>"
    )


# ---------------------------------------------------------------------------
# Main page renderer
# ---------------------------------------------------------------------------


def render_reasoning_page(scenario_name: str):
    """Render the reasoning/decision-logic exploration page.

    Args:
        scenario_name: Active scenario key (e.g. 'AssetBubble/Rule' or
            'CUSTOMIZED_SIMULATION/team-x-exp-00000000-Scenario/Default/Rule')
    """
    # Header row: back button + title
    col_back, col_title = st.columns([1, 5])
    with col_back:
        st.markdown("<div style='margin-top:18px'/>", unsafe_allow_html=True)
        if st.button(t("reasoning.back"), key="reasoning_back", use_container_width=True):
            st.session_state.current_page = st.session_state.get(
                "previous_page", "Simulation"
            )
            st.rerun()
            return  # guard: st.rerun() should halt, but return to be safe
    with col_title:
        display_name = scenario_display_name(scenario_name)
        st.title(t("reasoning.title").replace("{name}", display_name))

    st.markdown("---")

    # Load round data
    rounds = _load_cached_rounds(scenario_name)
    if not rounds:
        st.warning(t("reasoning.no_data"))
        return

    n_rounds = len(rounds)

    # --- Controls row: round selector + agent filter ---
    ctrl_left, ctrl_right = st.columns([2, 3])

    with ctrl_left:
        selected_round_num = st.number_input(
            t("reasoning.select_round"),
            min_value=1,
            max_value=n_rounds,
            value=1,
            step=1,
            key="reasoning_round_selector",
        )

    # Build agent roster for filter
    roster = get_agent_roster(scenario_name)
    agent_names = {m["id"]: m["name"] for m in roster}
    all_agent_ids = list(agent_names.keys())

    # Also include any agents that appear in data but not in config roster
    round_data = rounds[selected_round_num - 1]
    for act in round_data.agent_actions:
        if act.agent_id not in agent_names:
            agent_names[act.agent_id] = act.agent_id
            all_agent_ids.append(act.agent_id)

    with ctrl_right:
        filter_options = [t("reasoning.all_agents")] + [
            f"{agent_names.get(aid, aid)}" for aid in all_agent_ids
        ]
        selected_filter = st.selectbox(
            t("reasoning.filter_agent"),
            options=filter_options,
            key="reasoning_agent_filter",
        )

    st.markdown("")

    # --- Market state for this round ---
    mb = round_data.market_broadcast
    if mb and mb.stock_price is not None:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(t("simulation.stock_price"), f"{mb.stock_price:.4f}")
        with m2:
            if mb.stock_return is not None:
                pct = mb.stock_return * 100
                st.metric(t("simulation.return"), f"{pct:+.4f}%")
        with m3:
            if mb.fundamental is not None:
                st.metric("Fundamental", f"{mb.fundamental:.4f}")
        st.markdown("---")

    # --- Agent decision cards ---
    actions_by_id = {a.agent_id: a for a in round_data.agent_actions}

    # Determine which agents to show
    if selected_filter == t("reasoning.all_agents"):
        display_ids = all_agent_ids
    else:
        # Find the agent_id matching the selected display name
        idx = filter_options.index(selected_filter) - 1  # -1 for "All Agents"
        display_ids = [all_agent_ids[idx]] if idx >= 0 else all_agent_ids

    if not display_ids:
        st.info(t("reasoning.no_agents"))
        return

    for agent_id in display_ids:
        action = actions_by_id.get(agent_id)
        agent_display = agent_names.get(agent_id, agent_id)

        with st.container(border=True):
            _render_agent_reasoning_card(
                agent_id, agent_display, action, selected_round_num
            )


# ---------------------------------------------------------------------------
# Single agent card
# ---------------------------------------------------------------------------


def _render_agent_reasoning_card(
    agent_id: str,
    display_name: str,
    action: ReplayAgentAction | None,
    round_num: int,
):
    """Render a single agent's reasoning card for one round."""
    if action is None:
        # Agent had no recorded action this round
        st.markdown(
            f"**{display_name}** &nbsp; {_action_badge('HOLD')}",
            unsafe_allow_html=True,
        )
        st.caption(f"{t('simulation.hold')} — Round {round_num}")
        return

    # Header: agent name + action badge
    action_str = action.action_str
    st.markdown(
        f"**{display_name}** &nbsp; {_action_badge(action_str)}"
        f" &nbsp; <span style='color:#555;font-size:0.85rem;'>"
        f"({action.strategy or agent_id})</span>",
        unsafe_allow_html=True,
    )

    # Order details
    details_parts = []
    if action.price is not None:
        details_parts.append(f"**{t('simulation.price')}:** {action.price:.4f}")
    qty = action.quantity
    if qty != 0:
        details_parts.append(f"**{t('simulation.qty')}:** {abs(qty):.2f}")

    if details_parts:
        st.markdown(" &nbsp;|&nbsp; ".join(details_parts))

    # Reasoning (LLM agents)
    reasoning = action.reasoning
    analysis = action.analysis

    if analysis:
        st.markdown(
            "<div style='background:#f8f9fa;border-left:3px solid #0B3D91;"
            "padding:10px 14px;margin:8px 0;border-radius:4px;"
            "font-size:0.88rem;line-height:1.5;'>"
            f"<b>💭 {t('simulation.analysis')}:</b><br>{_escape_html(analysis)}"
            "</div>",
            unsafe_allow_html=True,
        )
    if reasoning:
        st.markdown(
            f"<div style='background:#fff3cd;border-left:3px solid #ffc107;"
            f"padding:8px 12px;margin:4px 0;border-radius:4px;"
            f"font-size:0.85rem;'>"
            f"<b>📝 {t('simulation.reasoning')}:</b> {_escape_html(reasoning)}"
            f"</div>",
            unsafe_allow_html=True,
        )

    if not analysis and not reasoning:
        st.caption(t("reasoning.rule_no_reasoning"))


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _escape_html(text: str) -> str:
    """Escape HTML special characters and convert newlines to <br>."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


def _load_cached_rounds(scenario_name: str):
    """Load round data from disk (fast SSD read, no cache needed)."""
    return load_rounds(scenario_name)
