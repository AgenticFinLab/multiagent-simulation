"""Shared fixtures and builders for the per-part acceptance suite.

Every module under ``examples/uTests/<Part>/`` asserts the documented contract
of one platform part; the reusable pieces live here so those modules stay
readable.  Framework objects are imported *inside* the builder functions, so
``unittest discover`` never pays for a heavy import it does not need and
import order cannot matter.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

# <repo root>: examples/uTests/_helpers.py -> uTests -> examples -> repo root.
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

# The acceptance suite asserts behaviour, not log output; the framework is
# deliberately chatty (resume warnings, audit trails), so silence it globally.
logging.disable(logging.CRITICAL)

# Canonical record-key shapes written by the wire channel and the storage proxy.
WIRE_KEY_RE = re.compile(r"^msg_r\d{6}_\d{6}$")
TURN_KEY_RE = re.compile(r"^turn_r\d{6}_\d{6}$")


def lmbase_available() -> bool:
    """True when the optional ``lmbase`` record-store backend is installed."""
    try:
        from lmbase.utils.tools import BlockBasedStoreManager  # noqa: F401
    except Exception:
        return False
    return True


LMBAVAILABLE: bool = lmbase_available()
# Persisting any record goes through the lmbase block store. Tests that only
# build objects, parse config or assert source text must run without it.
STORE_REQUIRED = unittest.skipUnless(
    LMBAVAILABLE, "optional lmbase record-store backend not installed"
)


class TempDirTestCase(unittest.TestCase):
    """Base case owning one temporary directory per test method.

    Every filesystem write the suite performs happens under ``self.tmp`` and is
    removed in ``tearDown`` — the repository itself is never written to.
    """

    tmp: str

    def setUp(self) -> None:
        super().setUp()
        self.tmp = tempfile.mkdtemp(prefix="masim-utest-")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)
        super().tearDown()

    def tmp_path(self, *parts: str) -> str:
        """Return an absolute path inside this test's temporary directory."""
        return os.path.join(self.tmp, *parts)


def write_text(path: str, text: str) -> str:
    """Write ``text`` to ``path``, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def write_json(path: str, payload: Any) -> str:
    """Write ``payload`` as JSON, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)
    return path


def read_block_records(folder: str) -> Dict[str, Any]:
    """Merge every ``*_block_*.json`` record block under ``folder``.

    Returns the persisted ``{record_key: record}`` mapping exactly as written
    by ``BlockBasedStoreManager``; the keys are the contract under test.
    """
    merged: Dict[str, Any] = {}
    for name in sorted(os.listdir(folder)):
        if "_block_" not in name or not name.endswith(".json"):
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as handle:
            merged.update(json.load(handle))
    return merged


def read_batch_values(folder: str) -> List[Any]:
    """Concatenate every ``batch_block_*.json`` value list under ``folder``."""
    values: List[Any] = []
    for name in sorted(os.listdir(folder)):
        if not (name.startswith("batch_block_") and name.endswith(".json")):
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as handle:
            block = json.load(handle)
        for entries in block.values():
            if isinstance(entries, list):
                values.extend(entries)
    return values


def make_player_config(
    identity: str = "probe",
    seed: Optional[int] = None,
    **extras: Any,
):
    """Build a :class:`~masim.player.base.PlayerConfig` for a probe agent."""
    from masim.player.base import PlayerConfig

    merged: Dict[str, Any] = dict(extras)
    if seed is not None:
        merged["seed"] = seed
    return PlayerConfig(name=identity, identity=identity, extras=merged)


def make_rule_agent(
    identity: str = "probe",
    seed: Optional[int] = None,
    cash: float = 1000.0,
    position: float = 0.0,
    **extras: Any,
):
    """Build a bare ``CanonicalRulePlayer`` with portfolio state primed.

    ``CanonicalRulePlayer`` is concrete (only ``decide_order`` raises, and only
    when called), so it can be exercised directly for the ``act`` / RNG /
    lifecycle contract tests.
    """
    from masim.agents._base import CanonicalRulePlayer

    agent = CanonicalRulePlayer(make_player_config(identity, seed, **extras))
    agent.state.custom_state["cash"] = float(cash)
    agent.state.custom_state["position"] = float(position)
    return agent


def channel_config(storage_path: str, record_messages: bool = True) -> Dict[str, Any]:
    """Config dict accepted by :class:`GeneralCommunicationChannel`."""
    return {
        "storage_path": storage_path,
        "record_messages": record_messages,
        "message_block_size": 500,
    }


def make_channel(storage_path: str, record_messages: bool = True):
    """Build a :class:`GeneralCommunicationChannel` rooted at ``storage_path``."""
    from masim.communication.general import GeneralCommunicationChannel

    return GeneralCommunicationChannel(channel_config(storage_path, record_messages))
