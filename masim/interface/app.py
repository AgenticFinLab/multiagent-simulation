"""Main Streamlit application for MASIM Web Interface."""

import asyncio
import sys
import time
from pathlib import Path

import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from masim.interface.config_loader import (
    discover_scenarios,
    get_scenario_info,
)
from masim.interface.data_loader import has_experiment_data, load_rounds
from masim.interface.simulation_runner import (
    MockSimulationRunner,
    SimulationRunner,
)
from masim.interface.components.sidebar import render_sidebar
from masim.interface.components.analysis_view import render_analysis_page
from masim.interface.components.docs_view import render_docs_page

# Page configuration
st.set_page_config(
    page_title="MASIM - Multi-Agent Simulation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "selected_scenario" not in st.session_state:
    scenarios = discover_scenarios()
    st.session_state.selected_scenario = scenarios[0] if scenarios else ""

if "current_page" not in st.session_state:
    st.session_state.current_page = "Simulation"

if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False

if "simulation_completed" not in st.session_state:
    st.session_state.simulation_completed = False

if "runner" not in st.session_state:
    st.session_state.runner = None

if "use_mock" not in st.session_state:
    st.session_state.use_mock = True

# Replay state — all round data stored here; activity panel reads from it
if "replay_index" not in st.session_state:
    st.session_state.replay_index = 0  # rounds delivered so far (0-based count)

if "replay_rounds" not in st.session_state:
    st.session_state.replay_rounds = []  # list[RoundData] loaded from disk

if "replay_active" not in st.session_state:
    st.session_state.replay_active = False  # True while auto-advancing

if "viewed_round_idx" not in st.session_state:
    st.session_state.viewed_round_idx = 0  # 0-based index of the slider-selected round

# System messages (start / stop / error notices, separate from round data)
if "sys_messages" not in st.session_state:
    st.session_state.sys_messages = []


def main():
    """Main application entry point."""
    selected_scenario = render_sidebar()

    if st.session_state.current_page == "Analysis":
        render_analysis_page(selected_scenario)
    elif st.session_state.current_page == "Docs":
        render_docs_page(selected_scenario)
    else:
        render_simulation_page(selected_scenario)


# ---------------------------------------------------------------------------
# Simulation page
# ---------------------------------------------------------------------------


def render_simulation_page(scenario_name: str):
    """Render the simulation page.

    Layout:
      ┌─ title ──────────────────────────────────────────────────┐
      | [action buttons]                                         |
      | progress bar (auto-advances) / slider (interactive)      |
      | ── Investor Activity ─────────────────────────────────── |
      |   market metrics row                                     |
      |   agent action cards  (2-col grid, refreshes each round) |
      | system notices                                           |
      └──────────────────────────────────────────────────────────┘
    """
    title_col, btn_col = st.columns([3, 1])
    with title_col:
        st.title("Simulation Platform")
    with btn_col:
        st.markdown("<div style='margin-top:18px'/>", unsafe_allow_html=True)
        _render_action_buttons(scenario_name)

    info = get_scenario_info(scenario_name)
    if not info.get("exists"):
        st.error(f"Scenario configuration not found: {scenario_name}")
        return

    rounds = st.session_state.replay_rounds
    n_rounds = len(rounds)
    is_running = st.session_state.simulation_running
    is_completed = st.session_state.simulation_completed

    # ── System notices ─────────────────────────────────────────────────────
    for notice in st.session_state.sys_messages:
        _render_sys_notice(notice)

    if not (is_running or is_completed) or n_rounds == 0:
        return

    # ── Progress slider / bar ──────────────────────────────────────────────
    replay_idx = st.session_state.replay_index  # rounds delivered so far
    progress_frac = (replay_idx / n_rounds) if n_rounds else 0.0

    st.markdown("")
    prog_col, label_col = st.columns([5, 1])

    if is_completed and n_rounds > 1:
        # Interactive slider — lets user browse any round after replay ends
        with prog_col:
            slider_val = st.slider(
                "Round",
                min_value=1,
                max_value=n_rounds,
                value=st.session_state.viewed_round_idx + 1,
                step=1,
                label_visibility="collapsed",
                key="round_slider",
            )
        viewed_idx = slider_val - 1
        st.session_state.viewed_round_idx = viewed_idx
        with label_col:
            st.metric("Round", f"{rounds[viewed_idx].round_num} / {n_rounds}")
    else:
        # Auto-advancing progress bar during replay
        with prog_col:
            st.progress(progress_frac)
        viewed_idx = max(0, replay_idx - 1)  # show the last delivered round
        with label_col:
            rnd_num = rounds[viewed_idx].round_num if rounds else 0
            st.metric("Round", f"{rnd_num} / {n_rounds}")

    # ── Investor Activity panel (single round, refreshes in place) ─────────
    st.markdown("---")
    _render_investor_activity(rounds[viewed_idx])

    # ── Replay pump ────────────────────────────────────────────────────────
    # Delivers one new round per Streamlit rerun; the activity panel then
    # shows that round's data.  After all rounds are delivered the slider
    # becomes interactive.
    if st.session_state.replay_active:
        idx = st.session_state.replay_index
        if idx < n_rounds:
            st.session_state.replay_index = idx + 1
            st.session_state.viewed_round_idx = idx
            time.sleep(0.10)
            st.rerun()
        else:
            st.session_state.replay_active = False
            st.session_state.simulation_running = False
            st.session_state.simulation_completed = True
            st.session_state.viewed_round_idx = n_rounds - 1
            _sys_notice("All rounds loaded from saved experiment.", "success")
            st.rerun()


# ---------------------------------------------------------------------------
# Investor Activity panel
# ---------------------------------------------------------------------------


def _render_investor_activity(round_data):
    """Render the single-round Investor Activity panel.

    Displays market state (price, return, prev price) as metric cards then
    all agent actions as compact colour-coded cards in a two-column grid.
    This panel replaces itself on every rerun — no history accumulates.

    Args:
        round_data: RoundData from data_loader for the round to display.
    """
    rnd = round_data.round_num
    st.subheader(f"📈 Investor Activity — Round {rnd}")

    # Market state metrics
    mb = round_data.market_broadcast
    if mb is not None and mb.stock_price is not None:
        price = mb.stock_price
        ret = mb.stock_return
        prev = mb.prev_stock_price

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Stock Price", f"{price:.4f}")
        with m2:
            if ret is not None:
                pct = ret * 100
                st.metric("Return", f"{pct:+.4f}%", delta=f"{pct:+.4f}%")
        with m3:
            if prev is not None:
                st.metric("Prev Price", f"{prev:.4f}")
        st.markdown("")

    # Agent action cards in a 2-column grid
    actions = round_data.agent_actions
    if not actions:
        st.info("No agent actions recorded for this round.")
        return

    cols = st.columns(2)
    for i, act in enumerate(actions):
        with cols[i % 2]:
            _render_action_card(act)


def _render_action_card(act):
    """Render a compact dark-themed action card for one agent.

    Args:
        act: AgentAction dataclass from data_loader.
    """
    action_str = act.action_str
    qty = act.quantity
    price = act.price
    strategy = act.strategy
    agent_id = act.agent_id

    color_map = {"BUY": "#28a745", "SELL": "#dc3545", "HOLD": "#6c757d"}
    color = color_map.get(action_str, "#6c757d")
    qty_str = f"+{qty:.1f}" if qty > 0 else f"{qty:.1f}"
    price_str = f"${price:.4f}" if price else "—"
    strategy_html = (
        f"<div style='font-size:11px;color:#6c7a8c;margin-top:3px;'>{strategy}</div>"
        if strategy
        else ""
    )

    st.markdown(
        f"""
<div style="
    background:#1e2533;
    border-left:4px solid {color};
    border-radius:6px;
    padding:10px 14px;
    margin-bottom:8px;
">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-weight:700;font-size:13px;color:#e0e6f0;">{agent_id}</span>
    <span style="
      background:{color};color:#fff;
      padding:2px 10px;border-radius:10px;
      font-size:11px;font-weight:700;
    ">{action_str}</span>
  </div>
  <div style="margin-top:6px;font-size:12px;color:#9ba8bb;">
    Qty: <b style='color:#e0e6f0;'>{qty_str}</b>
    &nbsp;&nbsp;Price: <b style='color:#e0e6f0;'>{price_str}</b>
  </div>
  {strategy_html}
</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# System notice helpers
# ---------------------------------------------------------------------------


def _sys_notice(message: str, level: str = "info"):
    """Append a system notice to the persistent notice list.

    Args:
        message: Human-readable message.
        level: 'info' | 'success' | 'warning' | 'error'
    """
    from datetime import datetime

    st.session_state.sys_messages.append(
        {
            "message": message,
            "level": level,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
    )
    # Keep only the last 5 notices so the bar stays compact
    if len(st.session_state.sys_messages) > 5:
        st.session_state.sys_messages = st.session_state.sys_messages[-5:]


def _render_sys_notice(notice: dict):
    """Render a single system notice banner.

    Args:
        notice: Dict with 'message', 'level', 'timestamp'.
    """
    level = notice.get("level", "info")
    msg = notice.get("message", "")
    ts = notice.get("timestamp", "")
    styles = {
        "info": ("#1a2744", "#4a90d9", "ℹ️"),
        "success": ("#162a1e", "#28a745", "✅"),
        "warning": ("#2a2210", "#f0a500", "⚠️"),
        "error": ("#2a1212", "#dc3545", "❌"),
    }
    bg, border, icon = styles.get(level, styles["info"])
    st.markdown(
        f"""<div style="background:{bg};border-left:4px solid {border};
        border-radius:6px;padding:8px 14px;margin:4px 0;font-size:13px;">
        {icon} {msg}
        <span style="float:right;font-size:11px;color:#888;">{ts}</span>
        </div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Action buttons
# ---------------------------------------------------------------------------


def _render_action_buttons(scenario_name: str):
    """Render Start / Load / View Analysis / Reset buttons.

    Args:
        scenario_name: Currently selected scenario.
    """
    info = get_scenario_info(scenario_name)
    data_exists = has_experiment_data(scenario_name)

    if st.session_state.simulation_running:
        if st.button("⏹ Stop", type="secondary", use_container_width=True):
            _stop_simulation()

    elif st.session_state.simulation_completed:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📊 View Analysis", type="primary", use_container_width=True):
                st.session_state.current_page = "Analysis"
                st.rerun()
        with c2:
            if st.button("🔄 Reset", use_container_width=True):
                _reset_simulation()

    elif data_exists:
        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "📂 Load Results",
                type="primary",
                use_container_width=True,
                help="Replay saved experiment data without re-running the simulation",
            ):
                _start_replay(scenario_name, info)
        with c2:
            if st.button(
                "▶ Re-run",
                use_container_width=True,
                help="Start a fresh simulation (overwrites existing data)",
            ):
                _start_simulation(scenario_name, info)

    else:
        if st.button("▶ Start Simulation", type="primary", use_container_width=True):
            _start_simulation(scenario_name, info)


# ---------------------------------------------------------------------------
# Replay lifecycle
# ---------------------------------------------------------------------------


def _start_replay(scenario_name: str, info: dict):  # noqa: ARG001
    """Load saved rounds and begin animated replay.

    Args:
        scenario_name: Scenario to load.
        info: Scenario info dict (unused; kept for call-site symmetry).
    """
    with st.spinner("Loading experiment data…"):
        rounds = load_rounds(scenario_name)

    if not rounds:
        st.warning("No round data found in saved experiment.")
        return

    st.session_state.simulation_running = True
    st.session_state.simulation_completed = False
    st.session_state.sys_messages = []
    st.session_state.replay_rounds = rounds
    st.session_state.replay_index = 0
    st.session_state.viewed_round_idx = 0
    st.session_state.replay_active = True

    _sys_notice(f"Loading {len(rounds)} saved rounds for {scenario_name}…", "info")
    st.rerun()


# ---------------------------------------------------------------------------
# Live simulation lifecycle
# ---------------------------------------------------------------------------


def _start_simulation(scenario_name: str, info: dict):
    """Initialise and run the simulation."""
    st.session_state.simulation_running = True
    st.session_state.simulation_completed = False
    st.session_state.sys_messages = []
    st.session_state.replay_rounds = []
    st.session_state.replay_index = 0
    st.session_state.viewed_round_idx = 0
    st.session_state.replay_active = False

    config_path = info.get("config_path", f"configs/{scenario_name}/simulation.yml")

    if st.session_state.use_mock:
        st.session_state.runner = MockSimulationRunner(config_path)
    else:
        st.session_state.runner = SimulationRunner(config_path)

    _sys_notice(f"Starting simulation: {scenario_name}", "info")
    _sys_notice(f"Total rounds: {info.get('total_rounds', 'unknown')}", "info")

    try:
        asyncio.run(_run_simulation_async())
    except Exception as e:
        _sys_notice(f"Error: {str(e)}", "error")
        st.session_state.simulation_running = False

    st.rerun()


async def _run_simulation_async():
    """Run simulation asynchronously and collect rounds into replay_rounds."""
    from masim.interface.data_loader import AgentAction as DLAction
    from masim.interface.data_loader import MarketBroadcast, RoundData

    runner = st.session_state.runner
    if not runner:
        return

    if not await runner.setup():
        _sys_notice(f"Setup failed: {runner.status.error}", "error")
        st.session_state.simulation_running = False
        return

    rounds = []
    try:
        async for update in runner.run():
            if update.round_num > 0:
                actions = [
                    DLAction(
                        round_num=update.round_num,
                        agent_id=a.get("agent_id", ""),
                        content={
                            "stock_qty": a.get("quantity", 0),
                            "bid_price": a.get("bid_price", 0),
                            "strategy": a.get("agent_name", ""),
                        },
                    )
                    for a in update.agent_actions
                ]
                mb = None
                if update.market_data:
                    mb = MarketBroadcast(
                        round_num=update.round_num,
                        stock_price=update.market_data.get("price"),
                    )
                rounds.append(
                    RoundData(
                        round_num=update.round_num,
                        market_broadcast=mb,
                        agent_actions=actions,
                    )
                )

        st.session_state.replay_rounds = rounds
        st.session_state.replay_index = len(rounds)
        st.session_state.viewed_round_idx = max(0, len(rounds) - 1)
        st.session_state.simulation_completed = True
        _sys_notice("Simulation completed successfully!", "success")

    except Exception as e:
        _sys_notice(f"Simulation error: {str(e)}", "error")

    finally:
        await runner.shutdown()
        st.session_state.simulation_running = False


def _stop_simulation():
    """Stop the running simulation or replay."""
    if st.session_state.get("replay_active"):
        st.session_state.replay_active = False
        st.session_state.simulation_running = False
        st.session_state.simulation_completed = True
        n = st.session_state.replay_index
        if n > 0:
            st.session_state.viewed_round_idx = n - 1
        _sys_notice("Replay stopped by user.", "warning")
    else:
        if st.session_state.runner:
            st.session_state.runner.stop()
        st.session_state.simulation_running = False
        _sys_notice("Simulation stopped by user.", "warning")
    st.rerun()


def _reset_simulation():
    """Reset simulation state to idle."""
    st.session_state.simulation_running = False
    st.session_state.simulation_completed = False
    st.session_state.sys_messages = []
    st.session_state.replay_rounds = []
    st.session_state.replay_index = 0
    st.session_state.viewed_round_idx = 0
    st.session_state.replay_active = False
    st.session_state.runner = None
    st.session_state.current_page = "Simulation"
    st.rerun()


if __name__ == "__main__":
    main()
