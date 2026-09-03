"""Offline H2EPR benchmark runtime with lazy public exports."""

from typing import Any


__all__ = ["BenchmarkRunArtifacts", "BenchmarkRunError", "materialize_run"]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)
    from . import benchmark_runner

    return getattr(benchmark_runner, name)
