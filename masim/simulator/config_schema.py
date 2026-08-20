"""Pydantic v2 boundary schema for simulation.yml validation.

Design rationale
----------------

The runtime :class:`~masim.simulator.base.SimulationConfig` is a plain
``@dataclass`` that wraps seven top-level dicts (``setting``, ``ray``,
``players``, ``topology``, ``environment``, ``communication``,
``knowledge``).  Downstream code (Simulator/Persona/Player) reaches into
those dicts with untyped ``.get(...)`` / ``[key]`` accesses everywhere,
so tightening the dataclass fields into structured types would ripple
into hundreds of call sites.

This module keeps the runtime dataclass unchanged and instead validates
the raw YAML **at the boundary** — the moment we cross from the
external world (a YAML file, a Streamlit form submission, a customized
bundle writer) into the simulation core.  Validation catches
misconfigurations *before* Ray actors spin up (where errors are hard to
attribute) and provides one authoritative schema definition that
documents the config format for humans.

Usage
-----

>>> from masim.utils.config import load_config
>>> from masim.simulator.config_schema import validate_simulation_config
>>> cfg = load_config("configs/Demo/simulation.yml")
>>> validate_simulation_config(cfg)   # raises pydantic.ValidationError on bad shape
>>> sim_config = SimulationConfig(**cfg)

Or use the convenience helper that combines load + validate:

>>> from masim.simulator.config_schema import load_and_validate_config
>>> sim_config = load_and_validate_config("configs/Demo/simulation.yml")

Contract
--------

* **Non-invasive**: the validator only *inspects* the dict; it does not
  mutate or coerce fields.  The dict passed to :class:`SimulationConfig`
  is the same one the user wrote.
* **Extra keys allowed**: shipped scenarios sprinkle scenario-specific
  keys throughout ``setting`` / ``environment`` / player ``config``
  blocks.  We validate the *required* structure and permit unknown
  keys so scenario authors keep their extension freedom.
* **Fail-loud**: missing required fields, wrong types, and empty
  ``players`` / ``topology`` raise :class:`pydantic.ValidationError`
  with a full field-path traceback.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Sub-schemas
# ---------------------------------------------------------------------------


class SettingSchema(BaseModel):
    """``setting:`` block — top-level simulation metadata.

    Required fields are enforced by the ``BaseSimulator`` constructor
    (it dereferences ``config.setting['record_path']`` and
    ``['round_history_limit']`` at wire time) so pre-validating them
    here surfaces the KeyError as a structured ValidationError
    instead of a Ray-actor traceback.
    """

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Human-readable simulation name.")
    record_path: str = Field(
        ...,
        description="Filesystem path where round history + turn blocks are persisted.",
    )
    round_history_limit: int = Field(
        ...,
        ge=1,
        description="Hot-memory ring size for HistoryBuffer; overflow spills to disk.",
    )
    total_rounds: int = Field(
        ..., ge=1, description="Number of simulation rounds to execute."
    )
    description: Optional[str] = None
    save_diagram_interval: Optional[int] = Field(default=None, ge=0)


class TopologySchema(BaseModel):
    """``topology:`` block — graph structure driving execution order."""

    model_config = ConfigDict(extra="allow")

    type: str = Field(
        ...,
        description="Topology kind, e.g. 'directed', 'star', 'mesh'.",
    )
    sources: List[str] = Field(
        ...,
        description="Level-0 sources (executed first each round, e.g. coordinators).",
    )
    connections: Dict[str, List[str]] = Field(
        ...,
        description="Adjacency map: sender_key -> [target_key, ...].",
    )

    @field_validator("sources")
    @classmethod
    def _sources_nonempty(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError(
                "topology.sources must be non-empty — at least one level-0 "
                "source (typically a coordinator) is required."
            )
        return value


class CommunicationSchema(BaseModel):
    """``communication:`` block — channel + message persistence config."""

    model_config = ConfigDict(extra="allow")

    storage_path: str = Field(
        ...,
        description="Filesystem path for message block persistence.",
    )
    record_messages: bool = Field(
        default=True,
        description="Whether to persist Message envelopes for post-hoc analysis.",
    )
    message_block_size: int = Field(
        default=500,
        ge=1,
        description="Number of messages per persisted block file.",
    )


class PlayerBlockSchema(BaseModel):
    """One player entry inside the ``players:`` dict.

    Enforces only the fields the framework itself reads
    (``expand_player_instances`` in :mod:`masim.utils.config`, the
    Persona/Player construction path, and the customized-bundle writer).
    Scenario-specific fields under ``config:`` and ``persona:`` are
    left free-form.
    """

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Human-readable player display name.")
    num_instances: int = Field(
        ...,
        ge=1,
        description="Number of instances to spawn from this template. "
        "1 keeps the key unchanged; >1 expands to name_1, name_2, ...",
    )
    # Python 'class' is a reserved keyword; pydantic v2 supports aliases.
    class_: str = Field(
        ...,
        alias="class",
        description="Dotted import path 'package.module:ClassName' for the player.",
    )
    config: Dict[str, Any] = Field(default_factory=dict)
    persona: Dict[str, Any] = Field(default_factory=dict)


class RaySchema(BaseModel):
    """``ray:`` block — Ray cluster + actor options.

    Pass-through container — Ray itself validates these; we only ensure
    the block is a dict so ``ray.init(**config.ray)`` doesn't ``TypeError``.
    """

    model_config = ConfigDict(extra="allow")


class EnvironmentSchema(BaseModel):
    """``environment:`` block — dotenv path + workspace hints."""

    model_config = ConfigDict(extra="allow")

    dotenv_path: Optional[str] = None
    workspace: Optional[str] = None


class KnowledgeSchema(BaseModel):
    """``knowledge:`` block — RAG / knowledge-store configuration.

    Optional overall; when present the RAG-store bootstrap in
    :mod:`masim.knowledge.resource` validates the inner shape.
    """

    model_config = ConfigDict(extra="allow")


# ---------------------------------------------------------------------------
# Root schema
# ---------------------------------------------------------------------------


class SimulationConfigSchema(BaseModel):
    """Root schema validating the seven top-level simulation.yml blocks.

    Matches field-for-field with
    :class:`~masim.simulator.base.SimulationConfig`.  Extra top-level
    keys are forbidden so typos like ``knowlege:`` (missing d) surface
    as a validation error instead of silently disappearing into a
    dataclass field the framework never reads.
    """

    model_config = ConfigDict(extra="forbid")

    setting: SettingSchema
    topology: TopologySchema
    communication: CommunicationSchema
    players: Dict[str, PlayerBlockSchema] = Field(default_factory=dict)
    ray: RaySchema = Field(default_factory=RaySchema)
    environment: EnvironmentSchema = Field(default_factory=EnvironmentSchema)
    knowledge: KnowledgeSchema = Field(default_factory=KnowledgeSchema)
    simulation_id: Optional[str] = None

    @field_validator("players")
    @classmethod
    def _players_nonempty(
        cls, value: Dict[str, PlayerBlockSchema]
    ) -> Dict[str, PlayerBlockSchema]:
        if not value:
            raise ValueError(
                "players must be non-empty — at least one player template "
                "is required (coordinator + regular player at minimum)."
            )
        return value

    @model_validator(mode="after")
    def _cross_check_topology_players(self) -> "SimulationConfigSchema":
        """Every topology source/connection key must map to a real player.

        Runs after ``expand_player_instances`` has rewritten ``sources`` and
        ``connections`` to use fully-expanded instance keys, so keys must
        appear verbatim in ``players``.  Missing references are the single
        largest source of "actor not found" failures at runtime; catching
        them here saves a Ray actor spin-up cycle per bad config.
        """
        player_keys = set(self.players.keys())
        missing: List[str] = []

        for source in self.topology.sources:
            if source not in player_keys:
                missing.append(f"topology.sources[{source}]")

        for sender, targets in self.topology.connections.items():
            if sender not in player_keys:
                missing.append(f"topology.connections[{sender!r}] (sender)")
            for target in targets:
                if target not in player_keys:
                    missing.append(
                        f"topology.connections[{sender!r}] -> {target!r} (target)"
                    )

        if missing:
            raise ValueError(
                "Topology references player keys that do not exist in "
                "players:\n  - " + "\n  - ".join(missing)
            )
        return self


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------


def validate_simulation_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a raw simulation.yml dict against the boundary schema.

    Parameters
    ----------
    config
        The dict produced by :func:`masim.utils.config.load_config`
        (after ``!include`` resolution and ``expand_player_instances``).

    Returns
    -------
    dict
        The same dict, unchanged.  Passed through for convenience so
        callers can chain ``SimulationConfig(**validate_simulation_config(cfg))``.

    Raises
    ------
    pydantic.ValidationError
        On any shape / type / cross-field violation with a full
        field-path traceback.
    """
    SimulationConfigSchema.model_validate(config)
    return config


def load_and_validate_config(
    config_path: Union[str, Path],
    env_interpolate: bool = True,
) -> "SimulationConfig":
    """Load + validate + wrap in the runtime :class:`SimulationConfig`.

    Convenience wrapper that combines :func:`load_config`,
    :func:`validate_simulation_config`, and the ``SimulationConfig(**cfg)``
    construction step used at every CLI / interface entry point.

    Parameters
    ----------
    config_path
        Path to the simulation.yml file.
    env_interpolate
        Forwarded to :func:`load_config`.

    Returns
    -------
    SimulationConfig
        Ready to hand to :class:`~masim.simulator.general.GeneralSimulator`.
    """
    # Local imports to avoid module-load-time cycles: this module lives
    # at masim/simulator/config_schema.py and load_config imports from
    # masim.utils.config; SimulationConfig lives in masim/simulator/base.py.
    from masim.simulator.base import SimulationConfig
    from masim.utils.config import load_config

    raw = load_config(config_path, env_interpolate=env_interpolate)
    validate_simulation_config(raw)
    return SimulationConfig(**raw)


__all__ = [
    "CommunicationSchema",
    "EnvironmentSchema",
    "KnowledgeSchema",
    "PlayerBlockSchema",
    "RaySchema",
    "SettingSchema",
    "SimulationConfigSchema",
    "TopologySchema",
    "load_and_validate_config",
    "validate_simulation_config",
]
