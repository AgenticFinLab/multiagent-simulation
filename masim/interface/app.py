"""Main Streamlit application for MASIM Web Interface."""
# D:\Anaconda\envs\masim_env\python.exe -m streamlit run "masim\interface\app.py" --server.port=8502
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
    _configs_path,
)
from masim.interface.data_loader import has_experiment_data, load_rounds
from masim.interface.simulation_runner import (
    MockSimulationRunner,
    SimulationRunner,
)
from masim.interface.components.sidebar import render_sidebar
from masim.interface.components.analysis_view import render_analysis_page
from masim.interface.components.docs_view import render_docs_page
from masim.interface.components.agent_market import (
    render_agent_market,
    render_entry_choice,
    render_back_to_start_bar,
    render_selected_portfolio_strip,
    render_simulation_setup,
)

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

if "workflow_stage" not in st.session_state:
    st.session_state.workflow_stage = "entry"

if "selected_market_agents" not in st.session_state:
    st.session_state.selected_market_agents = []


def _requested_agent_from_url() -> str:
    """Return the agent profile requested through the URL, if any."""
    if hasattr(st, "query_params"):
        value = st.query_params.get("agent", "")
        return value[0] if isinstance(value, list) else value
    values = st.experimental_get_query_params()
    return values.get("agent", [""])[0]


if _requested_agent_from_url():
    st.session_state.workflow_stage = "agents"


def main():
    """Main application entry point."""
    workflow_stage = st.session_state.workflow_stage
    if workflow_stage == "entry":
        render_entry_choice()
        return
    if workflow_stage == "agents":
        render_agent_market()
        return
    if workflow_stage == "setup":
        render_simulation_setup()
        return

    selected_scenario = render_sidebar()

    render_back_to_start_bar(key_suffix="workspace", reset_runtime=True)

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
    render_selected_portfolio_strip()
    st.divider()

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

    # ── Price dynamics chart ───────────────────────────────────────────────
    _render_price_chart(rounds, viewed_idx)

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
            time.sleep(0.05)
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


# ---------------------------------------------------------------------------
# Price dynamics chart
# ---------------------------------------------------------------------------


def _render_price_chart(rounds: list, viewed_idx: int):
    """Render a live price-dynamics chart that extends gradually during replay.

    The chart covers ALL rounds from the start, but only populates data up to
    *viewed_idx*.  This keeps the x-axis range and trace count stable across
    reruns so plotly can update in-place (no flicker).  During rapid replay the
    figure is cached and only rebuilt every few rounds for performance.

    Args:
        rounds: Full list of RoundData objects.
        viewed_idx: 0-based index of the round being displayed.
    """
    if viewed_idx < 0 or not rounds:
        return

    n_rounds = len(rounds)

    # ── Throttle during rapid replay ──────────────────────────────────
    # Rebuilding a plotly figure 20 times/sec causes flicker; cache the
    # figure in session_state and only rebuild every *step* rounds.
    replay_active = st.session_state.get("replay_active", False)
    step = max(1, n_rounds // 60)  # ~60 chart frames total
    last_idx = st.session_state.get("_pc_last_idx", -1)

    if replay_active and 0 <= last_idx < viewed_idx < n_rounds - 1:
        if viewed_idx - last_idx < step:
            cached = st.session_state.get("_pc_fig")
            if cached is not None:
                st.plotly_chart(
                    cached,
                    use_container_width=True,
                    key="price_dynamics",
                )
                return

    # ── Collect market price and fundamental up to viewed_idx ─────────
    round_nums: list = []
    market_prices: list = []
    fundamentals: list = []

    for i, rd in enumerate(rounds):
        round_nums.append(rd.round_num)
        if i <= viewed_idx and rd.market_broadcast is not None:
            mb = rd.market_broadcast
            mp = float(mb.stock_price) if mb.stock_price is not None else None
            fv = float(mb.fundamental) if mb.fundamental is not None else None
            market_prices.append(mp)
            fundamentals.append(fv)
        else:
            market_prices.append(None)
            fundamentals.append(None)

    has_market = any(p is not None for p in market_prices)
    has_fundamental = any(f is not None for f in fundamentals)
    if not has_market and not has_fundamental:
        return

    # ── Build plotly chart ────────────────────────────────────────────
    try:
        import plotly.graph_objects as go
    except ImportError:
        _render_price_chart_fallback(round_nums, market_prices, fundamentals)
        return

    fig = go.Figure()

    # Market clearing price — thick gold reference line
    fig.add_trace(
        go.Scatter(
            x=round_nums,
            y=market_prices,
            mode="lines",
            name="Market Price",
            line=dict(color="#f0a500", width=3),
            connectgaps=False,
            hovertemplate="Round %{x}<br>Price: %{y:.4f}<extra>Market</extra>",
        )
    )

    # Fundamental value — dashed reference line
    if has_fundamental:
        fig.add_trace(
            go.Scatter(
                x=round_nums,
                y=fundamentals,
                mode="lines",
                name="Fundamental",
                line=dict(color="#06d6a0", width=2, dash="dash"),
                connectgaps=False,
                hovertemplate="Round %{x}<br>Fundamental: %{y:.4f}<extra></extra>",
            )
        )

    fig.update_layout(
        title=dict(
            text="\U0001f4c8 Price Dynamics",
            font=dict(size=16, color="#e0e6f0"),
        ),
        xaxis_title="Round",
        yaxis_title="Price",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(14,17,23,1)",
        height=480,
        margin=dict(l=60, r=20, t=50, b=80),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#9ba8bb"),
        ),
        hovermode="x unified",
        uirevision="price_dynamics",
        xaxis=dict(
            range=[0.5, round_nums[-1] + 0.5],
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            dtick=max(1, n_rounds // 10),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            tickformat=".2f",
        ),
    )

    # Cache for throttled replay
    st.session_state["_pc_fig"] = fig
    st.session_state["_pc_last_idx"] = viewed_idx

    st.plotly_chart(fig, use_container_width=True, key="price_dynamics")


def _render_price_chart_fallback(round_nums, market_prices, fundamentals):
    """Minimal fallback chart using st.line_chart when plotly is unavailable."""
    import pandas as pd

    data = {"Market Price": market_prices, "Fundamental": fundamentals}
    df = pd.DataFrame(data, index=round_nums)
    df.index.name = "Round"
    st.line_chart(df, height=480)


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
    analysis = act.analysis
    reasoning = act.reasoning

    color_map = {"BUY": "#28a745", "SELL": "#dc3545", "HOLD": "#6c757d"}
    color = color_map.get(action_str, "#6c757d")
    qty_str = f"+{qty:.1f}" if qty > 0 else f"{qty:.1f}"
    price_str = f"${price:.4f}" if price else "—"
    strategy_html = (
        f"<div style='font-size:11px;color:#6c7a8c;margin-top:3px;'>{strategy}</div>"
        if strategy
        else ""
    )

    # Build tooltip content with analysis and reasoning
    tooltip_content = ""
    if analysis:
        # Escape HTML and format analysis
        analysis_escaped = (
            analysis.replace('"', "&quot;").replace("'", "&#39;").replace("\n", "<br/>")
        )
        tooltip_content += f"<b>🔍 Analysis:</b><br/>{analysis_escaped}"
    if reasoning:
        reasoning_escaped = reasoning.replace('"', "&quot;").replace("'", "&#39;")
        if tooltip_content:
            tooltip_content += f"<br/><br/><b>📋 Reasoning:</b> {reasoning_escaped}"
        else:
            tooltip_content += f"<b>📋 Reasoning:</b> {reasoning_escaped}"

    # Add hover tooltip using CSS
    tooltip_html = ""
    if tooltip_content:
        tooltip_html = f"""
    <div class="tooltip" style="position:relative;display:inline-block;width:100%;">
      <style>
        .tooltip .tooltiptext {{
          visibility: hidden;
          width: 320px;
          background-color: #2d3748;
          color: #e2e8f0;
          text-align: left;
          border-radius: 8px;
          padding: 12px;
          position: absolute;
          z-index: 1000;
          bottom: 125%;
          left: 50%;
          margin-left: -160px;
          opacity: 0;
          transition: opacity 0.3s;
          font-size: 12px;
          line-height: 1.5;
          box-shadow: 0 4px 12px rgba(0,0,0,0.4);
          max-height: 300px;
          overflow-y: auto;
        }}
        .tooltip:hover .tooltiptext {{
          visibility: visible;
          opacity: 1;
        }}
      </style>
      <span class="tooltiptext">{tooltip_content}</span>
    """
        close_div = "</div>"
    else:
        tooltip_html = ""
        close_div = ""

    st.markdown(
        f"""
{tooltip_html}
<div style="
    background:#1e2533;
    border-left:4px solid {color};
    border-radius:6px;
    padding:10px 14px;
    margin-bottom:8px;
    cursor: {'pointer' if tooltip_content else 'default'};
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
</div>
{close_div}""",
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
        # When simulation is running, show Stop and View Analysis (if data exists)
        if data_exists:
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("⏹ Stop", type="secondary", use_container_width=True):
                    _stop_simulation()
            with c2:
                if st.button(
                    "📊 View Analysis",
                    type="primary",
                    use_container_width=True,
                    help="Jump to analysis page while simulation continues",
                ):
                    st.session_state.current_page = "Analysis"
                    st.rerun()
            with c3:
                if st.button("🔄 Reset", use_container_width=True):
                    _stop_simulation()
                    _reset_simulation()
        else:
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
        # When data exists but no simulation running, show Load, View Analysis, and Re-run
        c1, c2, c3 = st.columns(3)
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
                "📊 View Analysis",
                type="secondary",
                use_container_width=True,
                help="Jump directly to analysis page without replay",
            ):
                st.session_state.current_page = "Analysis"
                st.rerun()
        with c3:
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

    config_path = info.get("config_path") or str(
        _configs_path(scenario_name) / "simulation.yml"
    )

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
