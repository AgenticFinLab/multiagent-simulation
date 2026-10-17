"""Corner badge that shows the current online user count.

Renders a small, fixed-position pill in the top-right corner on every page.
Uses Streamlit's internal Runtime API to count active sessions in this
Streamlit process.  Falls back gracefully if the internal API changes.

The count reflects sessions on the CURRENT Streamlit process only.  In a
multi-instance deployment behind Nginx (ip_hash), each user sees the count
of their own instance — good enough as a load indicator.
"""
from __future__ import annotations

import os

import streamlit as st


def _get_max_users() -> int:
    """Read the server-wide user cap from the environment.

    Set by ``set-max-users.sh`` in ``/opt/masim/masim.env``.  Falls back to
    a sensible default when the variable is missing or malformed.
    """
    raw = os.environ.get("MASIM_MAX_USERS", "").strip()
    try:
        value = int(raw)
        if value >= 1:
            return value
    except (TypeError, ValueError):
        pass
    return 4  # default cap when unspecified


def _get_online_count() -> int:
    """Return the number of active Streamlit sessions on this process.

    Uses Streamlit's internal Runtime API.  This API is private and may
    change between Streamlit releases; we wrap it in try/except and return
    ``0`` (not shown as fatal) on any failure.
    """
    try:
        from streamlit.runtime import Runtime

        runtime = Runtime.instance()
        # Streamlit 1.28+: SessionManager exposes list_active_sessions()
        session_mgr = getattr(runtime, "_session_mgr", None)
        if session_mgr is None:
            return 0
        list_fn = getattr(session_mgr, "list_active_sessions", None)
        if list_fn is None:
            return 0
        sessions = list_fn()
        return len(sessions)
    except Exception:
        return 0


def render_online_badge() -> None:
    """Render a fixed-position "在线: N/M" badge in the top-right corner.

    Safe to call on every page and every rerun; injects a single small HTML
    block via ``st.markdown``.  Does NOT consume layout space (position
    fixed).
    """
    online = _get_online_count()
    limit = _get_max_users()

    # Colour bands: blue when comfortable, amber near capacity, red at cap.
    if online >= limit:
        bg = "#dc2626"  # red
    elif online >= max(1, limit - 1):
        bg = "#f59e0b"  # amber
    else:
        bg = "#0B3D91"  # brand blue

    html = (
        f"<div style='"
        f"position:fixed; top:3.5rem; right:1rem; z-index:9999;"
        f"background:{bg}; color:#ffffff;"
        f"padding:4px 12px; border-radius:12px;"
        f"font-size:0.78rem; font-weight:600;"
        f"font-family:system-ui,-apple-system,\"Segoe UI\",sans-serif;"
        f"box-shadow:0 2px 6px rgba(0,0,0,0.18);"
        f"pointer-events:none; user-select:none;"
        f"'>"
        f"👥 在线 {online}/{limit}"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
