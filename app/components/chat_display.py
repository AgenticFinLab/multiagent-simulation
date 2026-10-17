"""Chat/activity display component for real-time simulation updates.

Note (2026-07-24): The UI-side ``ChatUiAgentAction`` and ``ChatUiMarketUpdate``
dataclasses defined here are *presentation view-models*, not runtime format
contracts. They exist purely to feed the Streamlit ChatDisplay widget. The
authoritative runtime structures live in :mod:`masim.format` — see
:class:`masim.format.InvestorOrder` and :class:`masim.format.MarketBroadcast`.
The view-models were renamed with ``ChatUi`` prefixes on 2026-07-24 to
eliminate the previous name collision with ``masim.format.MarketBroadcast``
and to signal that lowercase ``buy`` / ``sell`` / ``hold`` (the canonical
enum from :data:`masim.format.INVESTOR_ORDER_ACTION_VALUES`) is expected here.
"""

import streamlit as st
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

from masim.format import BUY, SELL, HOLD, INVESTOR_ORDER_ACTION_VALUES


@dataclass
class ChatUiAgentAction:
    """Presentation view-model for a single agent action in a round.

    ``action`` MUST be one of :data:`masim.format.INVESTOR_ORDER_ACTION_VALUES`
    (``"buy"`` / ``"sell"`` / ``"hold"``). Construction fails loudly for any
    other value; silently coercing an unknown value to ``hold`` would mask
    upstream bugs in the log-parser.
    """

    round_num: int
    agent_name: str
    agent_id: str
    bid_price: float
    quantity: float
    action: str
    timestamp: Optional[str] = None

    def __post_init__(self) -> None:
        if self.action not in INVESTOR_ORDER_ACTION_VALUES:
            raise ValueError(
                f"ChatUiAgentAction.action must be one of "
                f"{sorted(INVESTOR_ORDER_ACTION_VALUES)}, "
                f"got {self.action!r}. Silent coercion would mask "
                f"upstream log-parser bugs."
            )


@dataclass
class ChatUiMarketUpdate:
    """Presentation view-model for a market state update.

    Mirrors a subset of :class:`masim.format.MarketBroadcast` payload keys for
    display purposes. NOT to be used as a runtime broadcast — coordinators
    MUST emit through :class:`masim.format.MarketBroadcast`.
    """

    round_num: int
    price: float
    volume: float
    fundamental: Optional[float] = None


class ChatDisplay:
    """Manages the display of simulation activity in a chat-like format."""

    def __init__(self, container):
        """Initialize with a Streamlit container.

        Args:
            container: Streamlit container to render in
        """
        self.container = container
        self.messages: List[dict] = []
        self.max_messages = 100  # Keep last 100 messages
        self._last_price: Optional[float] = None

    def add_round_header(self, round_num: int, total_rounds: int):
        """Add a round header separator.

        Args:
            round_num: Current round number
            total_rounds: Total rounds in simulation
        """
        self.messages.append(
            {
                "type": "round_header",
                "round_num": round_num,
                "total_rounds": total_rounds,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
        self._trim_messages()

    def add_agent_action(self, action: ChatUiAgentAction):
        """Add an agent action message.

        Args:
            action: ChatUiAgentAction to display
        """
        self.messages.append(
            {
                "type": "agent_action",
                "data": action,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
        self._trim_messages()

    def add_market_update(self, update: ChatUiMarketUpdate):
        """Add a market state update.

        Args:
            update: ChatUiMarketUpdate to display
        """
        self.messages.append(
            {
                "type": "market_update",
                "data": update,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
        self._trim_messages()

    def add_system_message(self, message: str, level: str = "info"):
        """Add a system message.

        Args:
            message: Message text
            level: Message level (info, warning, error, success)
        """
        self.messages.append(
            {
                "type": "system",
                "message": message,
                "level": level,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
        self._trim_messages()

    def _trim_messages(self):
        """Trim message history to max size."""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def render(self):
        """Render all messages in the container."""
        with self.container:
            for msg in self.messages:
                self._render_message(msg)

    def _render_message(self, msg: dict):
        """Render a single message.

        Args:
            msg: Message dict to render
        """
        msg_type = msg.get("type")

        if msg_type == "round_header":
            self._render_round_header(msg)
        elif msg_type == "agent_action":
            self._render_agent_action(msg)
        elif msg_type == "market_update":
            self._render_market_update(msg)
        elif msg_type == "system":
            self._render_system_message(msg)

    def _render_round_header(self, msg: dict):
        """Render a round header."""
        round_num = msg["round_num"]
        total_rounds = msg["total_rounds"]
        timestamp = msg.get("timestamp", "")

        st.markdown(
            f"""
        <div style="
            background: linear-gradient(90deg, #1f77b4 0%, #2c3e50 100%);
            padding: 10px 15px;
            border-radius: 8px;
            margin: 15px 0 10px 0;
            color: white;
            font-weight: bold;
            font-size: 16px;
        ">
            Round {round_num} / {total_rounds} <span style="float: right; font-weight: normal; font-size: 12px;">{timestamp}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def _render_agent_action(self, msg: dict):
        """Render an agent action message."""
        action = msg["data"]
        timestamp = msg.get("timestamp", "")

        # Determine action styling (canonical lowercase enum from masim.format)
        action_colors = {
            BUY: "#28a745",   # Green
            SELL: "#dc3545",  # Red
            HOLD: "#6c757d",  # Gray
        }
        action_color = action_colors.get(action.action, "#6c757d")

        # Format quantity with sign
        qty = action.quantity
        qty_str = f"+{qty:.1f}" if qty > 0 else f"{qty:.1f}"

        # Uppercase label is a *display* choice; the canonical enum stays lowercase.
        display_action = action.action.upper()

        st.markdown(
            f"""
        <div style="
            background: #f8f9fa;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 5px 0;
            border-left: 4px solid {action_color};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600;">{action.agent_name}</span>
                <span style="
                    background: {action_color};
                    color: white;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                ">{display_action}</span>
            </div>
            <div style="margin-top: 5px; font-size: 14px; color: #495057;">
                Bid: <b>${action.bid_price:.2f}</b> | Qty: <b>{qty_str}</b>
            </div>
            <div style="font-size: 11px; color: #6c757d; margin-top: 3px;">
                {action.agent_id} | {timestamp}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def _render_market_update(self, msg: dict):
        """Render a market update message."""
        update = msg["data"]
        timestamp = msg.get("timestamp", "")

        # Calculate price change indicator
        price_indicator = ""
        if hasattr(self, "_last_price") and self._last_price:
            change = update.price - self._last_price
            if change > 0:
                price_indicator = "▲"
            elif change < 0:
                price_indicator = "▼"
        self._last_price = update.price

        st.markdown(
            f"""
        <div style="
            background: #fff3cd;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 5px 0;
            border-left: 4px solid #ffc107;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600;">🏦 Market Update</span>
                <span style="font-size: 12px; color: #856404;">{timestamp}</span>
            </div>
            <div style="margin-top: 5px; font-size: 14px;">
                Price: <b>${update.price:.2f}</b> {price_indicator} | 
                Volume: <b>{update.volume:.1f}</b>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def _render_system_message(self, msg: dict):
        """Render a system message."""
        message = msg["message"]
        level = msg.get("level", "info")
        timestamp = msg.get("timestamp", "")

        # Level styling
        level_styles = {
            "info": ("#e3f2fd", "#1976d2", "ℹ️"),
            "warning": ("#fff3e0", "#f57c00", "⚠️"),
            "error": ("#ffebee", "#d32f2f", "❌"),
            "success": ("#e8f5e9", "#388e3c", "✅"),
        }
        bg_color, border_color, icon = level_styles.get(level, level_styles["info"])

        st.markdown(
            f"""
        <div style="
            background: {bg_color};
            padding: 10px 15px;
            border-radius: 8px;
            margin: 5px 0;
            border-left: 4px solid {border_color};
        ">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>{icon}</span>
                <span>{message}</span>
            </div>
            <div style="font-size: 11px; color: #666; margin-top: 3px; margin-left: 26px;">
                {timestamp}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_progress_bar(progress_pct: float, current_round: int, total_rounds: int):
    """Render a progress bar with status.

    Args:
        progress_pct: Progress percentage (0-100)
        current_round: Current round number
        total_rounds: Total rounds
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        st.progress(progress_pct / 100)

    with col2:
        st.metric(
            "Progress", f"{progress_pct:.1f}%", f"Round {current_round}/{total_rounds}"
        )


def render_simulation_controls(
    is_running: bool, on_start: callable, on_stop: callable, disabled: bool = False
):
    """Render simulation control buttons.

    Args:
        is_running: Whether simulation is currently running
        on_start: Callback for start button
        on_stop: Callback for stop button
        disabled: Whether controls should be disabled
    """
    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        if is_running:
            if st.button("⏹️ Stop", type="secondary", disabled=disabled, key="stop_btn"):
                on_stop()
        else:
            if st.button("▶️ Start", type="primary", disabled=disabled, key="start_btn"):
                on_start()

    with col2:
        if st.button("🔄 Reset", disabled=is_running or disabled, key="reset_btn"):
            # Reset simulation state
            st.session_state.simulation_started = False
            st.session_state.simulation_completed = False
            st.rerun()

    with col3:
        if is_running:
            st.spinner("Simulation running...")


def create_chat_container():
    """Create and return a chat display container.

    Returns:
        Tuple of (container, ChatDisplay instance)
    """
    container = st.container()
    chat_display = ChatDisplay(container)
    return container, chat_display
