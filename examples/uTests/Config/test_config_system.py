"""Acceptance tests for the Config part (YAML composition and validation).

``load_config`` resolves ``!include`` relative to the including file,
interpolates ``${VAR}`` / ``${VAR:-default}`` and expands ``num_instances``;
the pydantic boundary then rejects a malformed config (e.g. empty ``players``)
with a ``ValidationError``.
"""

from __future__ import annotations

import os
import unittest

from examples.uTests._helpers import PROJECT_ROOT, TempDirTestCase, write_text

from pydantic import ValidationError

from masim.simulator.base import SimulationConfig
from masim.simulator.config_schema import (
    load_and_validate_config,
    validate_simulation_config,
)
from masim.utils.config import expand_player_instances, load_config, validate_config

_DEMO_CONFIG = PROJECT_ROOT / "configs" / "Demo" / "simulation.yml"

# Two templates: one single-instance and one that expands into spoke_1/spoke_2.
_PLAYERS_TWO = """\
players:
  hub:
    name: "Hub"
    class: "examples.Demo.players:SimpleCoordinator"
    num_instances: 1
    config:
      identity: "hub"
      role: "coordinator"
  spoke:
    name: "Spoke"
    class: "examples.Demo.players:SimplePlayer"
    num_instances: 2
    config:
      identity: "spoke"
      role: "player"
"""

_PLAYERS_EMPTY = "players: {}\n"


class _ConfigFixture(TempDirTestCase):
    """Base case that can materialise YAML configs inside its temp dir."""

    def write_config(
        self,
        name: str = "tmp_simulation",
        players_block: str = _PLAYERS_TWO,
        sources: str = "[hub]",
    ) -> str:
        """Write a self-contained simulation.yml and return its path."""
        body = (
            "setting:\n"
            f'  name: "{name}"\n'
            f'  record_path: "{self.tmp_path("records")}"\n'
            "  round_history_limit: 3\n"
            "  total_rounds: 2\n"
            f"{players_block}"
            "topology:\n"
            '  type: "star"\n'
            f"  sources: {sources}\n"
            "  connections:\n"
            "    hub: [spoke]\n"
            "    spoke: [hub]\n"
            "communication:\n"
            f'  storage_path: "{self.tmp_path("communication")}"\n'
            "  record_messages: false\n"
            "  message_block_size: 500\n"
        )
        return write_text(self.tmp_path("simulation.yml"), body)


class TestIncludeResolution(_ConfigFixture):
    """``!include`` is resolved relative to the including file."""

    def test_include_pulls_a_sibling_file_into_the_document(self) -> None:
        write_text(
            self.tmp_path("main.yml"),
            """\
setting:
  name: "include_test"
  record_path: "/tmp/records"
  round_history_limit: 3
  total_rounds: 1
players: !include players.yml
topology: !include topology.yml
""",
        )
        write_text(
            self.tmp_path("players.yml"),
            """\
hub:
  name: "Hub"
  class: "examples.Demo.players:SimpleCoordinator"
  num_instances: 1
  config:
    identity: "hub"
    role: "coordinator"
""",
        )
        write_text(
            self.tmp_path("topology.yml"),
            'type: "star"\nsources: [hub]\nconnections:\n  hub: [hub]\n',
        )
        config = load_config(self.tmp_path("main.yml"))
        self.assertEqual(config["players"]["hub"]["name"], "Hub")
        self.assertEqual(config["topology"]["type"], "star")

    def test_include_of_a_missing_file_raises_file_not_found(self) -> None:
        path = write_text(
            self.tmp_path("main.yml"),
            "players: !include nope.yml\ntopology: !include also-nope.yml\n",
        )
        with self.assertRaises(FileNotFoundError):
            load_config(path)

    def test_the_shipped_demo_config_resolves_its_includes(self) -> None:
        config = load_config(str(_DEMO_CONFIG))
        self.assertEqual(config["setting"]["name"], "demo_simulation")
        self.assertIn("coordinator", config["players"])
        self.assertEqual(config["topology"]["type"], "star")


class TestEnvInterpolation(_ConfigFixture):
    """``${VAR}`` is required; ``${VAR:-default}`` falls back."""

    def test_a_set_variable_is_substituted(self) -> None:
        os.environ["MASIM_UTEST_NAME"] = "from_env"
        self.addCleanup(os.environ.pop, "MASIM_UTEST_NAME", None)
        path = self.write_config(name="${MASIM_UTEST_NAME}")
        self.assertEqual(load_config(path)["setting"]["name"], "from_env")

    def test_the_documented_default_is_used_when_the_variable_is_absent(
        self,
    ) -> None:
        os.environ.pop("MASIM_UTEST_ABSENT", None)
        path = self.write_config(name="${MASIM_UTEST_ABSENT:-fallback_name}")
        self.assertEqual(load_config(path)["setting"]["name"], "fallback_name")

    def test_a_missing_variable_without_a_default_is_a_hard_error(self) -> None:
        os.environ.pop("MASIM_UTEST_MISSING", None)
        path = self.write_config(name="${MASIM_UTEST_MISSING}")
        with self.assertRaises(ValueError):
            load_config(path)

    def test_interpolation_can_be_disabled(self) -> None:
        os.environ["MASIM_UTEST_NAME"] = "from_env"
        self.addCleanup(os.environ.pop, "MASIM_UTEST_NAME", None)
        path = self.write_config(name="${MASIM_UTEST_NAME}")
        config = load_config(path, env_interpolate=False)
        self.assertEqual(config["setting"]["name"], "${MASIM_UTEST_NAME}")


class TestInstanceExpansion(_ConfigFixture):
    """``num_instances`` is required and rewrites topology references."""

    def test_num_instances_expands_templates_and_rewrites_topology(self) -> None:
        config = load_config(self.write_config())
        self.assertEqual(sorted(config["players"]), ["hub", "spoke_1", "spoke_2"])
        self.assertEqual(config["topology"]["sources"], ["hub"])
        self.assertEqual(
            sorted(config["topology"]["connections"]), ["hub", "spoke_1", "spoke_2"]
        )
        self.assertEqual(
            config["topology"]["connections"]["hub"], ["spoke_1", "spoke_2"]
        )
        self.assertEqual(config["topology"]["connections"]["spoke_1"], ["hub"])

    def test_expanded_instances_get_their_own_identity_and_display_name(self) -> None:
        config = load_config(self.write_config())
        self.assertEqual(config["players"]["spoke_2"]["config"]["identity"], "spoke_2")
        self.assertEqual(config["players"]["spoke_2"]["name"], "Spoke 2")

    def test_a_single_instance_keeps_the_original_key(self) -> None:
        config = load_config(self.write_config())
        self.assertEqual(config["players"]["hub"]["config"]["identity"], "hub")
        self.assertEqual(config["players"]["hub"]["name"], "Hub")

    def test_a_missing_num_instances_is_a_hard_error(self) -> None:
        config = load_config(self.write_config())
        del config["players"]["hub"]["num_instances"]
        with self.assertRaises(KeyError):
            expand_player_instances(config)

    def test_a_non_positive_num_instances_is_rejected(self) -> None:
        config = load_config(self.write_config())
        config["players"]["hub"]["num_instances"] = 0
        with self.assertRaises(ValueError):
            expand_player_instances(config)


class TestBoundaryValidation(_ConfigFixture):
    """The pydantic schema is the fail-loud boundary into the simulation core."""

    def test_a_real_shipped_config_passes_the_boundary(self) -> None:
        config = load_config(str(_DEMO_CONFIG))
        self.assertIs(validate_simulation_config(config), config)

    def test_a_generated_config_passes_the_boundary(self) -> None:
        validate_simulation_config(load_config(self.write_config()))

    def test_empty_players_is_rejected_with_a_validation_error(self) -> None:
        path = self.write_config(players_block=_PLAYERS_EMPTY)
        with self.assertRaises(ValidationError) as caught:
            validate_simulation_config(load_config(path))
        self.assertIn("players", str(caught.exception))

    def test_an_unknown_topology_reference_is_rejected(self) -> None:
        path = self.write_config(sources="[ghost]")
        with self.assertRaises(ValidationError):
            validate_simulation_config(load_config(path))

    def test_an_unknown_top_level_key_is_forbidden(self) -> None:
        config = load_config(self.write_config())
        config["knowlege"] = {}
        with self.assertRaises(ValidationError):
            validate_simulation_config(config)

    def test_a_missing_required_setting_field_is_rejected(self) -> None:
        config = load_config(self.write_config())
        del config["setting"]["record_path"]
        with self.assertRaises(ValidationError):
            validate_simulation_config(config)

    def test_an_empty_topology_sources_list_is_rejected(self) -> None:
        path = self.write_config(sources="[]")
        with self.assertRaises(ValidationError):
            validate_simulation_config(load_config(path))

    def test_validation_does_not_mutate_the_config(self) -> None:
        config = load_config(self.write_config())
        before = repr(config)
        validate_simulation_config(config)
        self.assertEqual(repr(config), before)

    def test_load_and_validate_config_returns_a_runtime_dataclass(self) -> None:
        sim_config = load_and_validate_config(str(_DEMO_CONFIG))
        self.assertIsInstance(sim_config, SimulationConfig)
        self.assertEqual(sim_config.setting["name"], "demo_simulation")
        self.assertTrue(sim_config.simulation_id)


class TestLegacyValidator(_ConfigFixture):
    """``validate_config`` remains the lightweight pre-schema check."""

    def test_a_generated_config_validates(self) -> None:
        validate_config(load_config(self.write_config()))

    def test_empty_players_is_rejected(self) -> None:
        config = load_config(self.write_config())
        config["players"] = {}
        with self.assertRaises(ValueError):
            validate_config(config)

    def test_a_player_without_a_class_is_rejected(self) -> None:
        config = load_config(self.write_config())
        del config["players"]["hub"]["class"]
        with self.assertRaises(ValueError):
            validate_config(config)
