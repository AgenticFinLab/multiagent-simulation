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
from masim.interface.simulation_runner import SimulationRunner
from masim.interface.components.sidebar import render_sidebar
from masim.interface.components.analysis_view import render_analysis_page
from masim.interface.components.docs_view import render_docs_page
from masim.interface.components.agent_market import (
    render_back_to_stage1_bar,
    render_customize,
    render_scenario_setup,
    render_selected_market_strip,
    render_variant_choice,
)
from masim.interface.components.welcome import render_welcome
from masim.interface.locale import t

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
    st.session_state.workflow_stage = "welcome"

if "mode" not in st.session_state:
    st.session_state.mode = ""  # "experience" | "project" | "competition"

if "project_name" not in st.session_state:
    st.session_state.project_name = ""

if "project_dir" not in st.session_state:
    st.session_state.project_dir = ""

if "selected_market_agents" not in st.session_state:
    st.session_state.selected_market_agents = []


def main():
    """Main application entry point."""
    workflow_stage = st.session_state.workflow_stage
    if workflow_stage == "welcome":
        render_welcome()
        return
    if workflow_stage == "scenario_setup":
        render_scenario_setup()
        return
    if workflow_stage == "variant_choice":
        render_variant_choice()
        return
    if workflow_stage == "customize":
        render_customize()
        return
    if workflow_stage != "workspace":
        st.error(
            f"Unknown workflow stage: '{workflow_stage}'. "
            "Resetting to welcome page."
        )
        st.session_state.workflow_stage = "welcome"
        st.rerun()
        return

    selected_scenario = render_sidebar()

    # Sub-pages (Analysis / Docs) render their own single "← Back" button that
    # returns to the Simulation page, so the workspace-level stage-1 back bar
    # is shown ONLY on the Simulation page — otherwise those pages would show
    # two back buttons.
    if st.session_state.current_page == "Analysis":
        render_analysis_page(selected_scenario)
    elif st.session_state.current_page == "Docs":
        render_docs_page(selected_scenario)
    else:
        render_back_to_stage1_bar(
            key_suffix="workspace",
            reset_runtime=True,
            target_stage="variant_choice",
        )
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
    st.title("Simulation Platform")
    # Action controls sit in a full-width toolbar row directly below the title
    # (rather than crammed into a narrow side column), so each button gets a
    # consistent, comfortable width.
    _render_action_buttons(scenario_name)

    info = get_scenario_info(scenario_name)

    # Deferred start / replay — launched here, ABOVE the divider, so the running
    # spinner status ("Running … computing N rounds…") renders full-width in the
    # header zone. Everything below the divider stays dedicated to the
    # simulation flow / progress display.
    pending = st.session_state.get("pending_action")
    if pending and info.get("exists"):
        st.session_state.pending_action = None
        if pending == "start":
            _start_simulation(scenario_name, info)
        elif pending == "replay":
            _start_replay(scenario_name, info)

    st.markdown("")
    st.divider()

    render_selected_market_strip()

    if not info.get("exists"):
        st.error(f"Scenario configuration not found: {scenario_name}")
        return

    rounds = st.session_state.replay_rounds
    n_rounds = len(rounds)
    is_running = st.session_state.simulation_running
    is_completed = st.session_state.simulation_completed

    # ── System notices ─────────────────────────────────────────────────────
    # Only surface warnings / errors; routine info (ℹ️) and success (✅) notices
    # are suppressed — the progress bar / slider already conveys run state.
    for notice in st.session_state.sys_messages:
        if notice.get("level") in ("warning", "error"):
            _render_sys_notice(notice)

    if not (is_running or is_completed) or n_rounds == 0:
        return

    # ── Progress slider / bar ──────────────────────────────────────────────
    replay_idx = st.session_state.replay_index  # rounds delivered so far
    progress_frac = (replay_idx / n_rounds) if n_rounds else 0.0

    st.markdown("")

    if is_completed and n_rounds > 1:
        # Completed → interactive slider to browse any recorded round.
        prog_col, label_col = st.columns([5, 1])
        with prog_col:
            slider_val = st.slider(
                "Round",
                min_value=1,
                max_value=n_rounds,
                value=min(st.session_state.viewed_round_idx + 1, n_rounds),
                step=1,
                label_visibility="collapsed",
                key="round_slider",
            )
        viewed_idx = slider_val - 1
        st.session_state.viewed_round_idx = viewed_idx
        with label_col:
            st.metric("Round", f"{rounds[viewed_idx].round_num} / {n_rounds}")
    else:
        # Running → animated progress bar with a live round counter.
        cur_round = replay_idx if replay_idx > 0 else 0
        pct = int(round(progress_frac * 100))
        st.progress(
            progress_frac,
            text=f"Round {cur_round} / {n_rounds}  ·  {pct}% complete",
        )
        viewed_idx = max(0, replay_idx - 1)  # show the last delivered round

    # ── Price ticker + expandable chart dialog ────────────────────────────
    # Show a compact price-metrics row so agents stay visible. The full
    # interactive Plotly chart lives in a dialog opened on demand.
    _render_price_ticker_bar(rounds, viewed_idx)

    # ── Investor Activity panel (single round, refreshes in place) ─────────
    st.markdown("---")
    _render_investor_activity(rounds[viewed_idx], scenario_name)

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


def _render_investor_activity(round_data, scenario_name: str):
    """Render the single-round Investor Activity panel.

    Displays market state (price, return, prev price) as metric cards then
    every configured investor as a compact colour-coded card in a two-column
    grid. Agents that placed no order this round are shown as HOLD, so the
    panel always reflects the full roster from the sidebar (not just the
    agents that traded). This panel replaces itself on every rerun.

    Args:
        round_data: RoundData from data_loader for the round to display.
        scenario_name: Active scenario key (to resolve the full roster).
    """
    from masim.interface.config_loader import get_agent_roster
    from masim.interface.data_loader import ReplayAgentAction

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
                st.metric("Price Change", f"{pct:+.4f}%", delta=f"{pct:+.4f}%")
        with m3:
            if prev is not None:
                st.metric("Prev Price", f"{prev:.4f}")
        st.markdown("")

    # Build the full roster and merge in this round's actual actions; agents
    # with no recorded order are rendered as synthetic HOLD cards.
    action_by_id = {a.agent_id: a for a in round_data.agent_actions}
    roster = get_agent_roster(scenario_name)
    roster_ids = {m["id"] for m in roster}

    display_actions = []
    for member in roster:
        act = action_by_id.get(member["id"])
        if act is None:
            act = ReplayAgentAction(round_num=rnd, agent_id=member["id"], content={})
        display_actions.append(act)
    # Safety: include any traded agent not present in the config roster.
    for a in round_data.agent_actions:
        if a.agent_id not in roster_ids:
            display_actions.append(a)

    if not display_actions:
        st.info("No agents configured for this scenario.")
        return

    cols = st.columns(2)
    for i, act in enumerate(display_actions):
        with cols[i % 2]:
            _render_action_card(act)


# ---------------------------------------------------------------------------
# Price dynamics chart
# ---------------------------------------------------------------------------


def _render_price_chart(rounds: list, viewed_idx: int):
    """Render a composite price-dynamics chart that grows up to the current round.

    Two vertically-stacked, x-aligned panels are drawn for rounds 0..*viewed_idx*:
      1. Price panel — dashed grey fundamental line, solid gold market
         clearing price, and a semi-transparent scatter of every investor's
         bid price each round (coloured by side, sized by order quantity).
      2. Volume panel — per-round trading-volume distribution as buy (up,
         green) / sell (down, red) bars.

    Args:
        rounds: Full list of RoundData objects.
        viewed_idx: 0-based index of the round being displayed.
    """
    if viewed_idx < 0 or not rounds:
        return

    import pandas as pd

    # ── Collect per-round series and distributions ──────────────────────────────────
    round_nums: list = []
    market_prices: list = []
    fundamentals: list = []
    bid_stat_rows: list = []
    vol_stat_rows: list = []

    for i in range(viewed_idx + 1):
        rd = rounds[i]
        rn = rd.round_num
        round_nums.append(rn)
        mb = rd.market_broadcast
        mp = float(mb.stock_price) if mb and mb.stock_price is not None else None
        fv = float(mb.fundamental) if mb and mb.fundamental is not None else None
        market_prices.append(mp)
        fundamentals.append(fv)

        bids: list = []
        buys: list = []
        sells: list = []
        for act in rd.agent_actions:
            price = act.price
            qty = act.quantity
            if price is not None:
                bids.append(float(price))
            if qty > 0:
                buys.append(float(qty))
            elif qty < 0:
                sells.append(float(-qty))

        # Per-round bid-price spread (whisker-style, not a box): min / IQR /
        # median / max, drawn slightly left of the round tick on the price axis.
        if bids:
            s = pd.Series(bids)
            bid_stat_rows.append(
                {
                    "Round": rn,
                    "X": rn - 0.14,
                    "lo": float(s.min()),
                    "q1": float(s.quantile(0.25)),
                    "med": float(s.median()),
                    "q3": float(s.quantile(0.75)),
                    "hi": float(s.max()),
                }
            )
        # Per-round order-size spread on the right (volume) axis: buys up (+),
        # sells down (-), each a min→max range line with a median tick.
        if buys:
            b = pd.Series(buys)
            vol_stat_rows.append(
                {
                    "Round": rn,
                    "X": rn + 0.14,
                    "Side": "Buy",
                    "lo": float(b.min()),
                    "med": float(b.median()),
                    "hi": float(b.max()),
                }
            )
        if sells:
            se = pd.Series(sells)
            vol_stat_rows.append(
                {
                    "Round": rn,
                    "X": rn + 0.14,
                    "Side": "Sell",
                    "lo": -float(se.max()),
                    "med": -float(se.median()),
                    "hi": -float(se.min()),
                }
            )

    has_market = any(p is not None for p in market_prices)
    has_fundamental = any(f is not None for f in fundamentals)
    if not has_market and not has_fundamental and not bid_stat_rows:
        return

    # Price reference lines in long form so one colour scale drives the legend.
    line_rows: list = []
    for rn, mp, fv in zip(round_nums, market_prices, fundamentals):
        if fv is not None:
            line_rows.append(
                {"Round": rn, "X": rn, "Value": fv, "Series": "Fundamental"}
            )
        if mp is not None:
            line_rows.append(
                {"Round": rn, "X": rn, "Value": mp, "Series": "Market Price"}
            )

    # ── Build composite chart (Altair) ────────────────────────────────────────────
    try:
        import altair as alt
    except ImportError:
        _render_price_chart_fallback(round_nums, market_prices, fundamentals)
        return

    x_enc = alt.X(
        "X:Q",
        title="Round",
        scale=alt.Scale(domainMin=0.3, domainMax=round_nums[-1] + 0.7, nice=False),
    )

    # ---- Left axis: price (reference lines + investor bid spread) ----
    price_marks: list = []
    if line_rows:
        line_df = pd.DataFrame(line_rows)
        price_marks.append(
            alt.Chart(line_df)
            .mark_line(size=2.5)
            .encode(
                x=x_enc,
                y=alt.Y("Value:Q", title="Price"),
                color=alt.Color(
                    "Series:N",
                    scale=alt.Scale(
                        domain=["Fundamental", "Market Price"],
                        range=["#9ba8bb", "#f0a500"],
                    ),
                    legend=alt.Legend(title="Price lines"),
                ),
                strokeDash=alt.StrokeDash(
                    "Series:N",
                    scale=alt.Scale(
                        domain=["Fundamental", "Market Price"],
                        range=[[5, 4], [1, 0]],
                    ),
                    legend=None,
                ),
                tooltip=["Round", "Series", "Value"],
            )
        )
    if bid_stat_rows:
        bid_df = pd.DataFrame(bid_stat_rows)
        base_bid = alt.Chart(bid_df)
        # min→max whisker (thin), IQR band (thick), median tick.
        price_marks.append(
            base_bid.mark_rule(color="#4cc9c0", size=1.5, opacity=0.55).encode(
                x=x_enc,
                y=alt.Y("lo:Q", title="Price"),
                y2="hi:Q",
                tooltip=["Round", "lo", "q1", "med", "q3", "hi"],
            )
        )
        price_marks.append(
            base_bid.mark_rule(color="#4cc9c0", size=5, opacity=0.9).encode(
                x=x_enc, y="q1:Q", y2="q3:Q"
            )
        )
        price_marks.append(
            base_bid.mark_tick(color="#e0fbfc", thickness=2, size=13).encode(
                x=x_enc, y="med:Q"
            )
        )

    price_layer = alt.layer(*price_marks)

    # ---- Right axis: volume (buy/sell order-size spread) ----
    if vol_stat_rows:
        vol_df = pd.DataFrame(vol_stat_rows)
        vol_color = alt.Color(
            "Side:N",
            scale=alt.Scale(domain=["Buy", "Sell"], range=["#06d6a0", "#ef476f"]),
            legend=alt.Legend(title="Volume"),
        )
        base_vol = alt.Chart(vol_df)
        vol_layer = alt.layer(
            base_vol.mark_rule(size=5, opacity=0.85).encode(
                x=x_enc,
                y=alt.Y(
                    "lo:Q",
                    title="Quantity (Buy +, Sell -)",
                    axis=alt.Axis(orient="right"),
                ),
                y2="hi:Q",
                color=vol_color,
                tooltip=["Round", "Side", "lo", "med", "hi"],
            ),
            base_vol.mark_tick(thickness=2, size=13).encode(
                x=x_enc,
                y=alt.Y("med:Q", axis=alt.Axis(orient="right")),
                color=vol_color,
            ),
        )
        chart = alt.layer(price_layer, vol_layer).resolve_scale(
            y="independent", color="independent"
        )
    else:
        chart = price_layer

    chart = chart.properties(
        height=460, title="Price & Volume Distribution per Round"
    ).configure_view(strokeWidth=0)
    st.altair_chart(chart, width="stretch", key="price_dynamics")


def _render_price_chart_fallback(round_nums, market_prices, fundamentals):
    """Minimal fallback chart using st.line_chart when plotly is unavailable."""
    import pandas as pd

    # Only include series that actually have data — an all-None column becomes
    # an object dtype that st.line_chart rejects ("mixed types"). Coerce the
    # rest to numeric so partially-missing series render as gaps, not errors.
    data = {}
    if any(p is not None for p in market_prices):
        data["Market Price"] = market_prices
    if any(f is not None for f in fundamentals):
        data["Fundamental"] = fundamentals
    if not data:
        return
    df = pd.DataFrame(data, index=round_nums).apply(pd.to_numeric, errors="coerce")
    df.index.name = "Round"
    st.line_chart(df, height=480)


# ---------------------------------------------------------------------------
# Price ticker bar + dialog
# ---------------------------------------------------------------------------


def _render_price_ticker_bar(rounds: list, viewed_idx: int):
    """Compact inline price metrics bar with an expand button.

    Displays the current round's price, return %, and fundamental value
    as a narrow row of metrics so the Investor Activity panel remains
    above the fold. An \u201cExpand chart\u201d button opens the full Plotly
    price-dynamics chart in a modal dialog.
    """
    rd = rounds[viewed_idx]
    mb = rd.market_broadcast

    price_str = ""
    ret_str = ""
    fundamental_str = ""
    delta_str = ""
    if mb is not None:
        if mb.stock_price is not None:
            price_str = f"{mb.stock_price:.4f}"
        if mb.stock_return is not None:
            pct = mb.stock_return * 100
            ret_str = f"{pct:+.3f}%"
            delta_str = f"{pct:+.3f}%"
        if mb.fundamental is not None:
            fundamental_str = f"{mb.fundamental:.4f}"

    # Inject scoped button style: compact, dark-themed, matching the sim page.
    st.markdown(
        "<style>"
        '[class*="st-key-open_price_dialog"] button{'
        'background:#1a2744 !important;'
        'border:1px solid #2a5fa6 !important;'
        'color:#7baed4 !important;'
        'font-weight:700 !important;'
        'font-size:0.78rem !important;'
        'padding:4px 12px !important;'
        'min-height:0 !important;height:auto !important;'
        'border-radius:6px !important;'
        '}'
        '[class*="st-key-open_price_dialog"] button:hover{'
        'background:#223356 !important;'
        'border-color:#4a90d9 !important;'
        'color:#b8d8f8 !important;'
        '}'
        "</style>",
        unsafe_allow_html=True,
    )

    # Layout: price | return | fundamental | expand button
    cols = st.columns([2, 2, 2, 1.5])
    with cols[0]:
        st.metric(
            "\U0001f4b0 Price",
            price_str or "—",
            help="The market clearing price at which trades settle this round — "
            "the price the market's supply and demand agreed on.",
        )
    with cols[1]:
        st.metric(
            "\U0001f4c8 Price Change",
            ret_str or "—",
            delta=delta_str or None,
            help="Round-over-round price change: (price − previous price) / "
            "previous price. Positive means the price rose versus last round.",
        )
    with cols[2]:
        st.metric(
            "\U0001f3af Fundamental",
            fundamental_str or "—",
            help="The asset's intrinsic (fair) value benchmark. Gaps between "
            "price and fundamental signal over-/under-valuation — e.g. a "
            "bubble when price sits well above fundamental.",
        )
    with cols[3]:
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        with st.container(key="open_price_dialog"):
            if st.button(
                "\U0001f4c8 Price chart \u2922",
                key=f"btn_price_dialog_{viewed_idx}",
                help="Open the full price dynamics chart in an overlay",
            ):
                _show_price_chart_dialog(rounds, viewed_idx)


@st.dialog("\U0001f4c8 Price Dynamics", width="large")
def _show_price_chart_dialog(rounds: list, viewed_idx: int):
    """Modal dialog rendering the full interactive Plotly price chart.

    This moves the chart out of the main content flow so the Investor
    Activity panel (agent orders) remains visible without scrolling.
    The dialog shows the same growing-line chart that was previously
    rendered inline.
    """
    n = len(rounds)
    caption = f"Showing rounds 1\u2013{viewed_idx + 1} of {n}"
    st.caption(caption)
    _render_price_chart(rounds, viewed_idx)


def _render_action_card(act):
    """Render a compact dark-themed action card for one agent.

    Args:
        act: ReplayAgentAction dataclass from data_loader.
    """
    action_str = act.action_str  # canonical lowercase from masim.format
    qty = act.quantity
    price = act.price
    strategy = act.strategy
    agent_id = act.agent_id
    analysis = act.analysis
    reasoning = act.reasoning

    # Canonical enum from masim.format is lowercase; keep upper-case display.
    color_map = {"buy": "#28a745", "sell": "#dc3545", "hold": "#6c757d"}
    color = color_map.get(action_str, "#6c757d")
    display_action_str = action_str.upper()
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
    ">{display_action_str}</span>
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


def _render_toolbar(buttons: list, disabled: bool = False):
    """Render a list of action buttons as a left-aligned full-width toolbar.

    Buttons keep a consistent, comfortable width via equal 1-unit columns plus
    a trailing spacer, so they never stretch across the whole page.

    Args:
        buttons: list of (label, type, help_text, callback) tuples.
        disabled: when True, every button is rendered greyed-out and
            non-clickable (used while a run is already queued/starting).
    """
    if not buttons:
        return
    n = len(buttons)
    cols = st.columns([1] * n + [max(1, 6 - n)])
    for i, (label, btn_type, help_text, callback) in enumerate(buttons):
        with cols[i]:
            if st.button(
                label,
                type=btn_type,
                width="stretch",
                help=help_text,
                key=f"action_btn_{i}_{label}",
                disabled=disabled,
            ):
                callback()


def _render_action_buttons(scenario_name: str):
    """Render the state-dependent action toolbar.

    Buttons only appear when their prerequisite data exists:
      * ``Load Results`` / ``Re-run`` require saved experiment (round) data.
      * ``Run Analysis`` appears when data exists but the analysis is missing
        OR stale (older than the newest data file). Clicking it (re)generates
        the charts on the analysis page, then shows them.
      * ``View Analysis`` appears only when the analysis is FRESH (newer than
        all data files), so users never view charts computed from older data.

    Args:
        scenario_name: Currently selected scenario.
    """
    from masim.interface.config_loader import get_analysis_freshness

    info = get_scenario_info(scenario_name)
    data_exists = has_experiment_data(scenario_name)
    # Classify analysis output vs the underlying data so we can offer the right
    # action: view fresh analysis, or (re)run analysis when missing/stale.
    freshness = get_analysis_freshness(scenario_name)
    analysis_fresh = freshness == "fresh"
    analysis_runnable = data_exists and freshness in ("missing", "stale")

    def _go_analysis():
        st.session_state.previous_page = st.session_state.current_page
        st.session_state.current_page = "Analysis"
        st.rerun()

    def _run_analysis():
        # Force the analysis page to (re)generate charts even when stale ones
        # already exist on disk, then land on the fresh results.
        st.session_state.previous_page = st.session_state.current_page
        st.session_state.force_analysis_rerun = True
        st.session_state.current_page = "Analysis"
        st.rerun()

    def _defer(action: str):
        # Record the intent and rerun; the blocking run is launched at full
        # page width in render_simulation_page so its spinner isn't cramped
        # inside this narrow toolbar column.
        st.session_state.pending_action = action
        st.rerun()

    def _analysis_button(style: str, help_key: str = ""):
        """Build a View (fresh) or Run (missing/stale) analysis button spec."""
        if analysis_fresh:
            return (
                t("simulation.view_analysis"),
                style,
                t(help_key) if help_key else t("simulation.view_analysis_help"),
                _go_analysis,
            )
        return (
            t("simulation.run_analysis"),
            style,
            t(help_key) if help_key else t("simulation.run_analysis_help"),
            _run_analysis,
        )

    buttons: list = []

    if st.session_state.simulation_running:
        buttons.append((t("simulation.stop"), "secondary", None, _stop_simulation))
        if analysis_fresh:
            buttons.append((
                t("simulation.view_analysis"),
                "primary",
                t("simulation.view_analysis_running_help"),
                _go_analysis,
            ))
        elif analysis_runnable:
            buttons.append((
                t("simulation.run_analysis"),
                "secondary",
                t("simulation.run_analysis_help"),
                _run_analysis,
            ))
        if data_exists:
            buttons.append((
                t("simulation.reset"),
                "secondary",
                None,
                lambda: (_stop_simulation(), _reset_simulation()),
            ))
    elif st.session_state.simulation_completed:
        if analysis_fresh or analysis_runnable:
            buttons.append(_analysis_button("primary"))
        buttons.append((t("simulation.reset"), "secondary", None, _reset_simulation))

    elif data_exists:
        buttons.append((
            t("simulation.load_results"),
            "primary",
            t("simulation.load_results_help"),
            lambda: _defer("replay"),
        ))
        buttons.append(_analysis_button("secondary"))
        buttons.append((
            t("simulation.rerun"),
            "secondary",
            t("simulation.rerun_help"),
            lambda: _defer("start"),
        ))

    else:
        buttons.append((
            t("simulation.start"),
            "primary",
            None,
            lambda: _defer("start"),
        ))

    # A run is queued (button just clicked, blocking launch happens right after
    # in render_simulation_page). Grey out the whole toolbar so the primary
    # trigger button can't be clicked again while the simulation starts.
    pending = bool(st.session_state.get("pending_action"))
    _render_toolbar(buttons, disabled=pending)


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

    # Always run the real simulation engine. Mock/fake data has been removed
    # deliberately: fabricated prices/bids silently corrupt results, so we
    # prefer a real error over invalid data.
    st.session_state.runner = SimulationRunner(config_path)

    _sys_notice(f"Starting simulation: {scenario_name}", "info")
    _sys_notice(f"Total rounds: {info.get('total_rounds', 'unknown')}", "info")

    try:
        with st.spinner(
            f"⚙️ Running {scenario_name} — computing "
            f"{info.get('total_rounds', 'all')} rounds\u2026"
        ):
            asyncio.run(_run_simulation_async())
    except Exception as e:
        _sys_notice(f"Error: {str(e)}", "error")
        st.session_state.simulation_running = False

    st.rerun()


async def _run_simulation_async():
    """Run simulation asynchronously and collect rounds into replay_rounds."""
    from masim.interface.data_loader import ReplayAgentAction as DLAction
    from masim.interface.data_loader import ReplayMarketBroadcast, RoundData

    runner = st.session_state.runner
    if not runner:
        return

    if not await runner.setup():
        _sys_notice(f"Setup failed: {runner.status.error}", "error")
        st.session_state.simulation_running = False
        return

    rounds = []
    prev_price = None
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
                    price = update.market_data.get("price")
                    # Derive the round-over-round return from the previous
                    # cleared price so the Return metric/chart isn't blank.
                    stock_return = None
                    if price is not None and prev_price not in (None, 0):
                        stock_return = (price - prev_price) / prev_price
                    mb = ReplayMarketBroadcast(
                        round_num=update.round_num,
                        stock_price=price,
                        prev_stock_price=prev_price,
                        stock_return=stock_return,
                        fundamental=update.market_data.get("fundamental"),
                    )
                    if price is not None:
                        prev_price = price
                rounds.append(
                    RoundData(
                        round_num=update.round_num,
                        market_broadcast=mb,
                        agent_actions=actions,
                    )
                )

        st.session_state.replay_rounds = rounds
        if rounds:
            # Animate the freshly computed rounds one-by-one via the shared
            # replay pump, so users see a clear round-by-round progression
            # instead of jumping straight to the final frame.
            st.session_state.replay_index = 0
            st.session_state.viewed_round_idx = 0
            st.session_state.replay_active = True
            st.session_state.simulation_running = True
            st.session_state.simulation_completed = False
            _sys_notice(
                f"Simulation finished — replaying {len(rounds)} rounds\u2026",
                "success",
            )
        else:
            st.session_state.replay_active = False
            st.session_state.simulation_running = False
            st.session_state.simulation_completed = True
            _sys_notice("Simulation produced no rounds.", "warning")

    except Exception as e:
        _sys_notice(f"Simulation error: {str(e)}", "error")
        st.session_state.simulation_running = False

    finally:
        await runner.shutdown()


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
