"""Resume-scanning utilities for the MASim framework.

Pure disk-inspection helpers that determine where to resume a simulation
after an interruption. Kept in a dedicated module so that GeneralSimulator
can stay focused on round orchestration; these functions have no runtime
dependency on Ray, config schemas, or player personas.

Public API
----------
detect_resume_round(record_path) -> int
    Return the highest completed round number found under ``record_path``.
    Consults, in order:
        1. ``.masim-progress.json``                  — atomic progress marker
        2. ``environment/messages/msg_block_*.json`` — EchoChamber compatibility
        3. ``market/turns/turn_block_*.json``        — coordinator turn blocks
        4. ``market/<store>/batch_block_*.json``     — HistoryBuffer cold storage

max_persisted_message_round(messages_path) -> int
    Return the largest ``round_num`` stored in ``msg_block_*.json`` files
    under ``messages_path``. Zero if the directory is missing or empty.

write_resume_checkpoint(record_path, round_num) -> None
    Atomically persist ``round_num`` as the latest fully-completed round
    into ``<record_path>/.masim-progress.json`` using an fsync + rename
    to survive crashes and interrupts without leaving a partial marker.

Design notes
------------
* All three helpers are ``@staticmethod``-style free functions — they do
  not touch simulator state, so re-hosting them at module scope keeps the
  simulator class smaller without complicating the call sites.
* File-scanning failures are swallowed intentionally: a corrupted block or
  a partially-written file must never abort a resume; the worst outcome is
  falling back to an earlier checkpoint.
* Keep this module dependency-light (stdlib only) so it can be imported
  from tools, CLIs, and tests without pulling Ray into the process.
"""

from __future__ import annotations

import json
import logging
import os
import re
import tempfile

logger = logging.getLogger("masim.simulator.resume_scanner")


def detect_resume_round(record_path: str) -> int:
    """Scan ``record_path`` for the highest completed round number.

    Consultation order (see module docstring for details):
        1. Atomic progress marker file.
        2. EchoChamber environment/messages fallback.
        3. Coordinator turns/ directory (``turn_block_*.json``).
        4. HistoryBuffer / block-based cold storage (``batch_*.json``).

    Returns 0 when no data is found.
    """
    checkpoint_path = os.path.join(record_path, ".masim-progress.json")
    try:
        with open(checkpoint_path, encoding="utf-8") as checkpoint_file:
            checkpoint = json.load(checkpoint_file)
        completed_round = int(checkpoint["completed_round"])
        if completed_round >= 0:
            return completed_round
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        pass

    # Compatibility recovery for EchoChamber runs created before the
    # progress marker existed.  The environment receives the final-level
    # actions; the largest persisted round is therefore the last round
    # that made it through the simulation pipeline.
    environment_messages = os.path.join(record_path, "environment", "messages")
    recovered_round = max_persisted_message_round(environment_messages)
    if recovered_round:
        logger.info(
            "    Recovered completed round %d from environment messages",
            recovered_round,
        )
        return recovered_round

    market_path = os.path.join(record_path, "market")
    if not os.path.isdir(market_path):
        return 0

    # Primary: read turn_block_*.json files in market/turns/
    turns_path = os.path.join(market_path, "turns")
    if os.path.isdir(turns_path):
        max_round = 0
        for fname in os.listdir(turns_path):
            if not (fname.startswith("turn_block_") and fname.endswith(".json")):
                continue
            try:
                with open(os.path.join(turns_path, fname)) as f:
                    block = json.load(f)
                for record in block.values():
                    rn = (
                        record.get("round_num")
                        if isinstance(record, dict)
                        else None
                    )
                    if rn is not None:
                        max_round = max(max_round, int(rn))
            except Exception:
                pass
        if max_round > 0:
            return max_round

    # Fallback: count entries in HistoryBuffer cold files under market/*/
    # File naming: batch_block_N.json (BlockBasedStoreManager, the only
    # cold-storage filename ever written; the older ``batch_{start:08d}_
    # {end:08d}.json`` shape is a *JSON key* inside these block files, not
    # a standalone filename — no support needed).
    max_round = 0
    for store_name in os.listdir(market_path):
        store_path = os.path.join(market_path, store_name)
        if not os.path.isdir(store_path) or store_name in ("turns", "messages"):
            continue
        total = 0
        for fname in os.listdir(store_path):
            m2 = re.match(r"batch_block_(\d+)\.json", fname)
            if m2:
                try:
                    with open(os.path.join(store_path, fname)) as f:
                        entries = json.load(f)
                    block_idx = int(m2.group(1))
                    block_size = 50
                    total = max(total, block_idx * block_size + len(entries))
                except Exception:
                    pass
        max_round = max(max_round, total)
    return max_round


def max_persisted_message_round(messages_path: str) -> int:
    """Return the largest round in persisted ``msg_block_*.json`` files."""
    if not os.path.isdir(messages_path):
        return 0
    max_round = 0
    for fname in os.listdir(messages_path):
        if not (fname.startswith("msg_block_") and fname.endswith(".json")):
            continue
        try:
            with open(
                os.path.join(messages_path, fname), encoding="utf-8"
            ) as message_file:
                block = json.load(message_file)
            for record in block.values():
                if isinstance(record, dict) and record.get("round_num") is not None:
                    max_round = max(max_round, int(record["round_num"]))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
    return max_round


def write_resume_checkpoint(record_path: str, round_num: int) -> None:
    """Atomically persist the latest fully-completed round.

    Uses fsync + os.replace so an interrupted write can never leave a
    partial ``.masim-progress.json`` behind.
    """
    os.makedirs(record_path, exist_ok=True)
    checkpoint_path = os.path.join(record_path, ".masim-progress.json")
    fd, temporary_path = tempfile.mkstemp(
        prefix=".masim-progress-", suffix=".tmp", dir=record_path
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as checkpoint_file:
            json.dump({"completed_round": int(round_num)}, checkpoint_file)
            checkpoint_file.flush()
            os.fsync(checkpoint_file.fileno())
        os.replace(temporary_path, checkpoint_path)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)
