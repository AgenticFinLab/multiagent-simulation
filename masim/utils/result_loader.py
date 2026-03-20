"""Simulation Result Loader

Lazy, on-demand accessor for simulation records written by StorageProxy.

Design principle
----------------
Nothing is read from disk until explicitly requested.  The entry point
``SimulationResults`` reflects the directory structure verbatim:

    SimulationResults
    └── PlayerResults          (one per player directory)
        ├── TurnStore          (turns/ sub-directory)
        ├── MessageStore       (messages/ sub-directory)
        └── BatchStore         (any other sub-directory with batch_block_*.json)

All classes are thin wrappers that remember paths and scan / read files only
when a query method is called.  No domain assumptions (market, investor, price,
trade …) appear anywhere in this module.

On-disk layout written by StorageProxy / BlockBasedStoreManager
---------------------------------------------------------------
{record_path}/
  {player_id}/
    turns/
      turn-store-information.json     – index (optional, not required for reading)
      turn_block_N.json               – { turn_rXXXXXX_MMDDHHMMSS :
                                           { round_num   : int,
                                             timestamp   : str,
                                             turn_result : {
                                               step_results : [
                                                 { decision_payload : {...},
                                                   action           : {...},
                                                   tick_step_count  : int,
                                                   tick_step_duration_ms : float }
                                               ],
                                               final_action              : {...},
                                               tick_turn_count           : int,
                                               tick_turn_duration_ms     : float,
                                               tick_turn_total_duration_ms: float,
                                               tick_step_count           : int }}}
    messages/
      msg-store-information.json      – index (optional)
      msg_block_N.json                – { msg_rXXXXXX_MMDDHHMMSS :
                                           { round_num  : int,
                                             direction  : str ("received"|"sent"),
                                             timestamp  : str,
                                             message    : {
                                               message_type : str,
                                               sender_id    : str,
                                               recipient_id : str,
                                               payload      : { content : {...}, ... },
                                               timestamp    : str, ... }}}
    {store_name}/                     – one dir per named batch time-series
      batch-store-information.json    – index (optional)
      batch_block_N.json              – { batch_XXXXX_XXXXX : [value, ...] }

Usage
-----
    from masim.utils import load_config, load_results

    config  = load_config("configs/AssetBubble/simulation.yml")
    results = load_results(config)          # nothing read yet

    # Iterate players
    for pid, player in results.players.items():
        print(pid, player.role)

    # Query one player's turns – full range
    player = results.player("market")
    all_turns = player.turns.all()          # {round_num: full turn record}
    payload   = player.turns.payload(round_num=5)      # decision_payload dict
    payloads  = player.turns.payloads()    # {round_num: decision_payload}
    payloads  = player.turns.payloads(rounds=range(1, 10))

    # Single field across all rounds
    field_vals = player.turns.field("price")           # {round_num: value}

    # Messages
    msgs      = player.messages.all()                  # [{round_num, direction, message}]
    received  = player.messages.by_direction("received")
    round_msg = player.messages.at_round(5)

    # Batch time-series
    store_names = player.batch_store_names             # list of store dirs
    series      = player.batch("price").all()          # [float, ...]
    window      = player.batch("price").range(0, 50)   # first 50 values

    # Topology
    conns = results.topology.connections("market")     # ["player_A", ...]
    peers = results.topology.peers("player_A")         # all nodes that player_A connects to
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

# ---------------------------------------------------------------------------
# Internal: block-file readers (shared by all store types)
# ---------------------------------------------------------------------------

_SKIP_NAMES = {
    "turn-store-information.json",
    "msg-store-information.json",
    "batch-store-information.json",
}


def _iter_turn_blocks(turns_dir: Path) -> Iterator[Dict[str, Any]]:
    """Yield each raw record dict from turn_block_*.json files, sorted."""
    for bf in sorted(turns_dir.glob("turn_block_*.json")):
        try:
            with open(bf, encoding="utf-8") as f:
                block: Dict[str, Any] = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for record in block.values():
            if isinstance(record, dict) and "round_num" in record:
                yield record


def _iter_msg_blocks(msg_dir: Path) -> Iterator[Dict[str, Any]]:
    """Yield each raw message record dict from msg_block_*.json files, sorted."""
    for bf in sorted(msg_dir.glob("msg_block_*.json")):
        try:
            with open(bf, encoding="utf-8") as f:
                block: Dict[str, Any] = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for record in block.values():
            if isinstance(record, dict) and "round_num" in record:
                yield record


def _read_batch_blocks(store_dir: Path) -> List[Any]:
    """Concatenate all batch_block_*.json value lists, sorted by file name."""
    combined: List[Any] = []
    for bf in sorted(store_dir.glob("batch_block_*.json")):
        try:
            with open(bf, encoding="utf-8") as f:
                block: Dict[str, Any] = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for values in block.values():
            if isinstance(values, list):
                combined.extend(values)
    return combined


# ---------------------------------------------------------------------------
# TurnStore – accessor for one player's turns/ directory
# ---------------------------------------------------------------------------


class TurnStore:
    """Lazy accessor for a player's turn records.

    All methods read from disk on each call; nothing is cached.
    """

    def __init__(self, turns_dir: Path) -> None:
        self._dir = turns_dir

    @property
    def exists(self) -> bool:
        return self._dir.exists()

    # ------------------------------------------------------------------
    # Full-record accessors
    # ------------------------------------------------------------------

    def all(self) -> Dict[int, Dict[str, Any]]:
        """Return all turn records as {round_num: full_turn_record}.

        Each value is the complete on-disk record:
            { round_num, timestamp, turn_result: { step_results, final_action,
              tick_turn_count, tick_turn_duration_ms, ... } }
        """
        result: Dict[int, Dict[str, Any]] = {}
        if not self._dir.exists():
            return result
        for record in _iter_turn_blocks(self._dir):
            result[int(record["round_num"])] = record
        return result

    def at_round(self, round_num: int) -> Optional[Dict[str, Any]]:
        """Return the full turn record for a specific round, or None."""
        if not self._dir.exists():
            return None
        target = int(round_num)
        for record in _iter_turn_blocks(self._dir):
            if int(record["round_num"]) == target:
                return record
        return None

    def rounds(self) -> List[int]:
        """Return sorted list of all recorded round numbers."""
        if not self._dir.exists():
            return []
        return sorted(int(r["round_num"]) for r in _iter_turn_blocks(self._dir))

    # ------------------------------------------------------------------
    # decision_payload accessors
    # ------------------------------------------------------------------

    def payload(self, round_num: int) -> Optional[Dict[str, Any]]:
        """Return the decision_payload for a specific round, or None.

        Reads from the first non-empty step_result of that round's turn_result.
        """
        record = self.at_round(round_num)
        if record is None:
            return None
        return _extract_payload(record)

    def payloads(
        self,
        rounds: Optional[Iterable[int]] = None,
    ) -> Dict[int, Dict[str, Any]]:
        """Return {round_num: decision_payload} for all (or selected) rounds.

        Args:
            rounds: Optional iterable of round numbers to restrict the result.
                    When None, all recorded rounds are returned.
        """
        if not self._dir.exists():
            return {}
        wanted = set(int(r) for r in rounds) if rounds is not None else None
        result: Dict[int, Dict[str, Any]] = {}
        for record in _iter_turn_blocks(self._dir):
            rn = int(record["round_num"])
            if wanted is not None and rn not in wanted:
                continue
            payload = _extract_payload(record)
            if payload is not None:
                result[rn] = payload
        return result

    def field(
        self,
        field_name: str,
        rounds: Optional[Iterable[int]] = None,
    ) -> Dict[int, Any]:
        """Return {round_num: value} for a single named field in decision_payload.

        Rounds where the field is absent are omitted.

        Args:
            field_name: Key to extract from each round's decision_payload.
            rounds:     Optional round filter (same semantics as payloads()).
        """
        result: Dict[int, Any] = {}
        for rn, payload in self.payloads(rounds=rounds).items():
            if field_name in payload:
                result[rn] = payload[field_name]
        return result

    def fields(
        self,
        field_names: Iterable[str],
        rounds: Optional[Iterable[int]] = None,
    ) -> Dict[int, Dict[str, Any]]:
        """Return {round_num: {field: value, ...}} for multiple named fields.

        Only rounds where at least one of the fields is present are included.
        """
        names = list(field_names)
        result: Dict[int, Dict[str, Any]] = {}
        for rn, payload in self.payloads(rounds=rounds).items():
            row = {k: payload[k] for k in names if k in payload}
            if row:
                result[rn] = row
        return result

    # ------------------------------------------------------------------
    # full turn_result accessors (step timing, action, etc.)
    # ------------------------------------------------------------------

    def turn_result(self, round_num: int) -> Optional[Dict[str, Any]]:
        """Return the full turn_result dict for a specific round, or None."""
        record = self.at_round(round_num)
        if record is None:
            return None
        return record.get("turn_result")

    def __repr__(self) -> str:
        n = len(self.rounds()) if self._dir.exists() else 0
        return f"TurnStore(dir={self._dir}, rounds={n})"


def _extract_payload(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract decision_payload from the first non-empty step_result."""
    step_results = record.get("turn_result", {}).get("step_results", [])
    for step in step_results:
        payload = step.get("decision_payload")
        if payload:
            return payload
    return None


# ---------------------------------------------------------------------------
# MessageStore – accessor for one player's messages/ directory
# ---------------------------------------------------------------------------


class MessageStore:
    """Lazy accessor for a player's message records.

    Each message record on disk has the shape:
        { round_num, direction, timestamp,
          message: { message_type, sender_id, recipient_id,
                     payload: { content: {...}, content_type, extras },
                     timestamp, priority, extras } }
    """

    def __init__(self, msg_dir: Path) -> None:
        self._dir = msg_dir

    @property
    def exists(self) -> bool:
        return self._dir.exists()

    def all(self) -> List[Dict[str, Any]]:
        """Return all message records as a list (unsorted by default).

        Each element is the full on-disk record dict.
        """
        if not self._dir.exists():
            return []
        return list(_iter_msg_blocks(self._dir))

    def at_round(self, round_num: int) -> List[Dict[str, Any]]:
        """Return all message records for a specific round number."""
        if not self._dir.exists():
            return []
        target = int(round_num)
        return [r for r in _iter_msg_blocks(self._dir) if int(r["round_num"]) == target]

    def by_direction(self, direction: str) -> List[Dict[str, Any]]:
        """Return all message records matching a direction string.

        Args:
            direction: Typically "received" or "sent".
        """
        if not self._dir.exists():
            return []
        return [
            r for r in _iter_msg_blocks(self._dir) if r.get("direction") == direction
        ]

    def by_sender(self, sender_id: str) -> List[Dict[str, Any]]:
        """Return all message records where message.sender_id matches."""
        if not self._dir.exists():
            return []
        return [
            r
            for r in _iter_msg_blocks(self._dir)
            if r.get("message", {}).get("sender_id") == sender_id
        ]

    def rounds(self) -> List[int]:
        """Return sorted list of round numbers that have at least one message."""
        if not self._dir.exists():
            return []
        return sorted({int(r["round_num"]) for r in _iter_msg_blocks(self._dir)})

    def __repr__(self) -> str:
        n = len(self.all()) if self._dir.exists() else 0
        return f"MessageStore(dir={self._dir}, records={n})"


# ---------------------------------------------------------------------------
# BatchStore – accessor for one named batch time-series directory
# ---------------------------------------------------------------------------


class BatchStore:
    """Lazy accessor for a single named batch time-series store.

    Batch stores are written by the player's HistoryBuffer and contain
    monotonically-indexed lists of scalar or structured values, one entry
    per simulation round.
    """

    def __init__(self, store_dir: Path) -> None:
        self._dir = store_dir

    @property
    def name(self) -> str:
        return self._dir.name

    @property
    def exists(self) -> bool:
        return self._dir.exists()

    def all(self) -> List[Any]:
        """Return the full concatenated time-series as a list (round-ordered)."""
        if not self._dir.exists():
            return []
        return _read_batch_blocks(self._dir)

    def range(self, start: int, stop: int) -> List[Any]:
        """Return values at indices [start, stop) from the full series.

        This still reads all blocks; use for post-load slicing convenience.
        """
        return self.all()[start:stop]

    def at_index(self, index: int) -> Any:
        """Return the value at a specific positional index (0-based)."""
        series = self.all()
        if index < 0 or index >= len(series):
            raise IndexError(
                f"BatchStore '{self.name}': index {index} out of range ({len(series)} values)"
            )
        return series[index]

    def __len__(self) -> int:
        return len(self.all())

    def __repr__(self) -> str:
        n = len(self.all()) if self._dir.exists() else 0
        return f"BatchStore(name={self.name!r}, values={n})"


# ---------------------------------------------------------------------------
# PlayerResults – all stores for one player
# ---------------------------------------------------------------------------


class PlayerResults:
    """All recorded data for a single player.

    Attributes:
        player_id : identity string (matches directory name)
        role      : role string from config (e.g. "coordinator", "player");
                    empty string when inferred from directory layout
        turns     : TurnStore for this player
        messages  : MessageStore for this player
    """

    def __init__(self, player_id: str, player_dir: Path, role: str = "") -> None:
        self._dir = player_dir
        self.player_id: str = player_id
        self.role: str = role
        self.turns: TurnStore = TurnStore(player_dir / "turns")
        self.messages: MessageStore = MessageStore(player_dir / "messages")

    @property
    def batch_store_names(self) -> List[str]:
        """Return the names of all available batch stores for this player."""
        if not self._dir.exists():
            return []
        return sorted(
            sub.name
            for sub in self._dir.iterdir()
            if sub.is_dir()
            and sub.name not in ("turns", "messages")
            and any(sub.glob("batch_block_*.json"))
        )

    def batch(self, store_name: str) -> BatchStore:
        """Return a BatchStore for the named sub-directory.

        Returns a BatchStore whose exists property is False if the store
        does not exist, rather than raising an error.
        """
        return BatchStore(self._dir / store_name)

    def __repr__(self) -> str:
        stores = self.batch_store_names
        return (
            f"PlayerResults(id={self.player_id!r}, role={self.role!r}, "
            f"batch_stores={stores})"
        )


# ---------------------------------------------------------------------------
# TopologyView – read-only view over the topology config section
# ---------------------------------------------------------------------------


class TopologyView:
    """Read-only view over the topology section of the simulation config.

    The topology dict from config has the structure:
        { type        : str,              # e.g. "star", "mesh"
          sources     : [player_id, ...], # broadcast sources
          connections : { player_id: [player_id, ...], ... } }
    """

    def __init__(self, topology: Dict[str, Any]) -> None:
        self._topo = topology

    @property
    def type(self) -> str:
        """Topology type string (e.g. "star")."""
        return self._topo.get("type", "")

    @property
    def sources(self) -> List[str]:
        """Player IDs that act as broadcast sources in the topology."""
        return list(self._topo.get("sources", []))

    @property
    def all_connections(self) -> Dict[str, List[str]]:
        """Full connections dict: {player_id: [neighbor_id, ...]}."""
        return dict(self._topo.get("connections", {}))

    def connections(self, player_id: str) -> List[str]:
        """Return the list of player IDs that player_id sends to."""
        return list(self._topo.get("connections", {}).get(player_id, []))

    def peers(self, player_id: str) -> List[str]:
        """Return all player IDs that player_id is connected to (in either direction)."""
        conns = self._topo.get("connections", {})
        out = set(conns.get(player_id, []))
        for other_id, targets in conns.items():
            if player_id in targets:
                out.add(other_id)
        return sorted(out)

    def __repr__(self) -> str:
        return f"TopologyView(type={self.type!r}, sources={self.sources})"


# ---------------------------------------------------------------------------
# SimulationResults – top-level entry point
# ---------------------------------------------------------------------------


class SimulationResults:
    """Top-level lazy accessor for a complete simulation run.

    Nothing is read from disk at construction time.  All data access goes
    through the store accessors (TurnStore, MessageStore, BatchStore) which
    read from disk on demand.

    Attributes:
        record_path : root directory containing per-player subdirectories
        players     : {player_id: PlayerResults} — populated at construction
                      by scanning the record_path directory structure
        topology    : TopologyView over the config topology section
                      (empty if constructed from a path rather than a config)
    """

    def __init__(
        self,
        record_path: Path,
        player_roles: Dict[str, str],
        topology: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.record_path: Path = record_path
        self.topology: TopologyView = TopologyView(topology or {})

        # Build the player registry — no disk I/O beyond directory listing
        self.players: Dict[str, PlayerResults] = {}
        for pid, role in player_roles.items():
            player_dir = record_path / pid
            if player_dir.exists():
                self.players[pid] = PlayerResults(
                    player_id=pid,
                    player_dir=player_dir,
                    role=role,
                )

    # ------------------------------------------------------------------
    # Player access
    # ------------------------------------------------------------------

    def player(self, player_id: str) -> PlayerResults:
        """Return the PlayerResults for a specific player_id.

        Raises KeyError if the player is not found in the record directory.
        """
        if player_id not in self.players:
            raise KeyError(
                f"Player {player_id!r} not found in {self.record_path}. "
                f"Available: {sorted(self.players)}"
            )
        return self.players[player_id]

    def players_by_role(self, role: str) -> Dict[str, PlayerResults]:
        """Return all PlayerResults whose role matches the given string."""
        return {pid: p for pid, p in self.players.items() if p.role == role}

    # ------------------------------------------------------------------
    # Cross-player bulk queries
    # ------------------------------------------------------------------

    def all_payloads(
        self,
        role: Optional[str] = None,
        rounds: Optional[Iterable[int]] = None,
    ) -> Dict[str, Dict[int, Dict[str, Any]]]:
        """Return {player_id: {round_num: decision_payload}} across all (or filtered) players.

        Args:
            role:   When given, restrict to players with this role string.
            rounds: Optional round filter forwarded to each TurnStore.
        """
        source = self.players_by_role(role) if role else self.players
        return {pid: p.turns.payloads(rounds=rounds) for pid, p in source.items()}

    def all_field(
        self,
        field_name: str,
        role: Optional[str] = None,
        rounds: Optional[Iterable[int]] = None,
    ) -> Dict[str, Dict[int, Any]]:
        """Return {player_id: {round_num: value}} for a single payload field.

        Players that never emitted the field are omitted from the result.

        Args:
            field_name: Key to extract from each player's decision_payloads.
            role:       Optional role filter.
            rounds:     Optional round filter.
        """
        source = self.players_by_role(role) if role else self.players
        result: Dict[str, Dict[int, Any]] = {}
        for pid, p in source.items():
            vals = p.turns.field(field_name, rounds=rounds)
            if vals:
                result[pid] = vals
        return result

    def all_messages(
        self,
        role: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Return {player_id: [message_record, ...]} across all (or filtered) players.

        Args:
            role:      Optional role filter.
            direction: When given, restrict to messages with this direction string.
        """
        source = self.players_by_role(role) if role else self.players
        result: Dict[str, List[Dict[str, Any]]] = {}
        for pid, p in source.items():
            msgs = p.messages.by_direction(direction) if direction else p.messages.all()
            if msgs:
                result[pid] = msgs
        return result

    def __repr__(self) -> str:
        roles: Dict[str, int] = {}
        for p in self.players.values():
            roles[p.role] = roles.get(p.role, 0) + 1
        return (
            f"SimulationResults("
            f"record_path={str(self.record_path)!r}, "
            f"players={dict(roles)}, "
            f"topology={self.topology!r})"
        )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def load_results(
    config_or_path: Union[Dict[str, Any], str, Path],
) -> SimulationResults:
    """Create a SimulationResults accessor for a simulation record directory.

    Nothing is read from disk beyond the directory listing needed to discover
    which players are present.  All turn / message / batch data is loaded
    lazily on demand through the returned accessor objects.

    Args:
        config_or_path:
            Either a loaded config dict (from load_config()) **or** a record
            directory path string / Path.

            Config dict → record_path, player roles, and topology are resolved
                          from config["setting"]["record_path"],
                          config["players"][*]["config"]["role"], and
                          config["topology"].
            Path        → all subdirectories containing a turns/ sub-directory
                          are treated as players; the directory named "market"
                          is inferred as role "coordinator", others as "player".

    Returns:
        SimulationResults ready for lazy querying.
    """
    if isinstance(config_or_path, dict):
        record_path, player_roles, topology = _parse_config(config_or_path)
    else:
        record_path = Path(config_or_path)
        player_roles = _infer_roles_from_dir(record_path)
        topology = {}

    return SimulationResults(
        record_path=record_path,
        player_roles=player_roles,
        topology=topology,
    )


# ---------------------------------------------------------------------------
# Backward-compatible alias
# ---------------------------------------------------------------------------


def load_simulation_data(
    config_or_path: Union[Dict[str, Any], str, Path],
    **_kwargs: Any,
) -> "SimulationResults":
    """Deprecated alias for load_results().  Use load_results() in new code."""
    return load_results(config_or_path)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SKIP_DIRS = {"diagrams", "history", "checkpoints", "analysis"}


def _parse_config(config: Dict[str, Any]) -> tuple:
    """Extract (record_path, {player_id: role}, topology_dict) from a loaded config.

    Config structure (post load_config / !include expansion):
        config["setting"]["record_path"]
        config["players"]  → { player_id: { config: { identity, role, ... }, ... } }
        config["topology"] → { type, sources, connections }
    """
    record_path = Path(config["setting"]["record_path"])
    players_cfg: Dict[str, Any] = config.get("players", {})
    topology: Dict[str, Any] = config.get("topology", {})

    player_roles: Dict[str, str] = {}
    for _key, player_cfg in players_cfg.items():
        cfg = player_cfg.get("config", {})
        identity: str = cfg.get("identity", _key)
        role: str = cfg.get("role", "player")
        player_roles[identity] = role

    return record_path, player_roles, topology


def _infer_roles_from_dir(record_path: Path) -> Dict[str, str]:
    """Infer {player_id: role} by scanning sub-directories of record_path.

    Used only when no config is available.  Convention:
        directory "market" → role "coordinator"
        all others         → role "player"
    """
    player_roles: Dict[str, str] = {}
    if not record_path.exists():
        return player_roles
    for subdir in sorted(record_path.iterdir()):
        if not subdir.is_dir() or subdir.name in _SKIP_DIRS:
            continue
        if not (subdir / "turns").exists():
            continue
        role = "coordinator" if subdir.name == "market" else "player"
        player_roles[subdir.name] = role
    return player_roles
