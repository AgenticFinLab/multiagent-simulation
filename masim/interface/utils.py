"""Utility functions for MASIM Web Interface."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent.parent


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if not.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_number(value: float, decimals: int = 2) -> str:
    """Format a number for display.

    Args:
        value: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a value as percentage.

    Args:
        value: Value to format (0.5 = 50%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    return f"{value * 100:.{decimals}f}%"


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate a string to max length.

    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


def safe_get(d: Dict, key: str, default: Any = None) -> Any:
    """Safely get a value from a dict.

    Args:
        d: Dictionary
        key: Key to get
        default: Default value if key not found

    Returns:
        Value or default
    """
    try:
        return d.get(key, default)
    except (AttributeError, TypeError):
        return default


def class_name_to_display(class_name: str) -> str:
    """Convert a class name to display format.

    Args:
        class_name: Full class name (e.g., "examples.AssetBubble.players:MomentumSpeculator")

    Returns:
        Display name (e.g., "Momentum Speculator")
    """
    # Extract class name from module path
    if ":" in class_name:
        class_name = class_name.split(":")[-1]

    # Convert CamelCase to spaces
    result = []
    for i, char in enumerate(class_name):
        if i > 0 and char.isupper():
            result.append(" ")
        result.append(char)

    return "".join(result)


def get_scenario_color(scenario_name: str) -> str:
    """Get a color for a scenario type.

    Args:
        scenario_name: Scenario name

    Returns:
        Hex color code
    """
    colors = {
        "AssetBubble": "#FF6B6B",
        "MarketCrash": "#4ECDC4",
        "HerdEffect": "#45B7D1",
        "MomentumEffect": "#96CEB4",
        "ReversalEffect": "#FFEAA7",
        "FlashCrash": "#DDA0DD",
        "VolatilityClustering": "#98D8C8",
        "EquityPremium": "#F7DC6F",
        "DispositionEffect": "#BB8FCE",
        "LiquidityDryup": "#85C1E9",
        "ShortSqueeze": "#F8C471",
    }

    # Remove LLM suffix for color lookup
    base_name = scenario_name.replace("LLM", "")
    return colors.get(base_name, "#95A5A6")


def is_running_in_streamlit() -> bool:
    """Check if code is running inside Streamlit.

    Returns:
        True if running in Streamlit
    """
    try:
        import streamlit as st

        # This will raise an error if not in Streamlit context
        _ = st.session_state
        return True
    except Exception:
        return False


def setup_logging():
    """Setup logging for the interface."""
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage statistics.

    Returns:
        Dict with memory usage info
    """
    try:
        import psutil

        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()

        return {
            "rss_mb": mem_info.rss / 1024 / 1024,
            "vms_mb": mem_info.vms / 1024 / 1024,
            "percent": process.memory_percent(),
        }
    except ImportError:
        return {"error": "psutil not installed"}


def validate_config_path(path: str) -> bool:
    """Validate that a config path exists and is readable.

    Args:
        path: Path to validate

    Returns:
        True if valid
    """
    try:
        p = Path(path)
        return p.exists() and p.is_file() and p.suffix in (".yml", ".yaml")
    except Exception:
        return False


def get_file_size(path: Path) -> str:
    """Get human-readable file size.

    Args:
        path: File path

    Returns:
        Human-readable size string
    """
    try:
        size = path.stat().st_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except Exception:
        return "Unknown"


def count_lines_in_file(path: Path) -> int:
    """Count lines in a text file.

    Args:
        path: File path

    Returns:
        Line count
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0
