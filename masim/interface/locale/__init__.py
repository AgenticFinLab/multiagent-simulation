"""Locale module for MASIM Web UI internationalization.

Provides the t() function for translating UI strings. All UI text should
use t("key.path") instead of hardcoded strings.

Locale files are stored in masim/interface/locale/{locale}.yml

Usage:
    from masim.interface.locale import t

    st.title(t("sidebar.title"))  # Returns "MASIM 仿真器" for zh_CN
    st.button(t("simulation.start"))  # Returns "▶ 开始仿真" for zh_CN

Locale Selection:
    1. MASIM_LOCALE environment variable
    2. Streamlit session_state.locale
    3. Default: en_US
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# Cache for loaded locales
_locales: Dict[str, Dict[str, Any]] = {}
_current_locale: str = "en_US"

LOCALE_DIR = Path(__file__).parent


def _load_locale(locale_name: str) -> Dict[str, Any]:
    """Load a locale file from disk.

    Args:
        locale_name: Locale name (e.g., "zh_CN", "en_US")

    Returns:
        Locale dictionary, or empty dict if not found
    """
    locale_path = LOCALE_DIR / f"{locale_name}.yml"
    if not locale_path.exists():
        return {}
    try:
        with open(locale_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def get_locale() -> str:
    """Get the current locale name.

    Priority:
        1. MASIM_LOCALE environment variable
        2. Streamlit session_state.locale (if available)
        3. Default: en_US

    Returns:
        Current locale name (e.g., "zh_CN", "en_US")
    """
    global _current_locale

    # Check environment variable first
    env_locale = os.environ.get("MASIM_LOCALE")
    if env_locale:
        return env_locale

    # Try to get from Streamlit session state
    try:
        import streamlit as st

        if "locale" in st.session_state:
            return st.session_state.locale
    except Exception:
        pass

    return _current_locale


def set_locale(locale_name: str) -> None:
    """Set the current locale.

    Only writes to session_state (per-session) to avoid leaking locale
    changes to other concurrent sessions sharing the same Streamlit process.

    Args:
        locale_name: Locale name (e.g., "zh_CN", "en_US")
    """
    # Store in Streamlit session state (per-session, no cross-session leakage).
    try:
        import streamlit as st

        st.session_state.locale = locale_name
    except Exception:
        # Fallback for non-Streamlit callers (CLI, tests).
        global _current_locale
        _current_locale = locale_name


def _get_nested(data: Dict[str, Any], key: str, default: str = "") -> str:
    """Get a nested value from a dictionary using dot notation.

    Args:
        data: Dictionary to search
        key: Dot-separated key (e.g., "sidebar.title")
        default: Default value if key not found

    Returns:
        Value at key path, or default if not found
    """
    keys = key.split(".")
    value = data
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return str(value) if not isinstance(value, dict) else default


def t(key: str, default: Optional[str] = None, **kwargs) -> str:
    """Translate a UI string by key.

    Looks up the key in the current locale file and returns the translated
    string. If the key is not found, returns the default or the key itself.

    Args:
        key: Dot-separated key path (e.g., "sidebar.title")
        default: Default value if key not found (default: key itself)
        **kwargs: Format variables for string interpolation

    Returns:
        Translated string

    Example:
        >>> t("sidebar.title")
        'MASIM 仿真器'
        >>> t("simulation.loading_rounds", count=10, scenario="AssetBubble")
        '正在加载 10 个已保存回合，场景：AssetBubble…'
    """
    locale_name = get_locale()

    # Load locale if not cached
    if locale_name not in _locales:
        _locales[locale_name] = _load_locale(locale_name)

    locale_data = _locales[locale_name]

    # Try to get the translation
    result = _get_nested(locale_data, key)

    # If not found, try fallback to en_US
    if not result and locale_name != "en_US":
        if "en_US" not in _locales:
            _locales["en_US"] = _load_locale("en_US")
        result = _get_nested(_locales["en_US"], key)

    # If still not found, use default or key
    if not result:
        result = default if default is not None else key

    # Format with kwargs if provided
    if kwargs and result:
        try:
            result = result.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return result


def get_available_locales() -> list:
    """Get list of available locales.

    Returns:
        List of locale names (e.g., ["en_US", "zh_CN"])
    """
    locales = []
    for f in LOCALE_DIR.glob("*.yml"):
        locales.append(f.stem)
    return sorted(locales)
