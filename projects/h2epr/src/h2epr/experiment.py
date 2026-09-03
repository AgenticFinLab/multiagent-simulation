"""Experiment-plan admission against current event packages."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from h2epr.benchmark.package import EventPackageError, load_event_package
from h2epr._experiment_core import (
    _ExperimentAdmissionCoreError,
    _admit_experiment_plan,
    _load_and_admit_experiment_plan,
)


ExperimentAdmissionError = _ExperimentAdmissionCoreError


def admit_experiment_plan(
    *,
    project_root: Path,
    data_root: Path,
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Admit the experiment-plan contract against current package identities."""

    return _admit_experiment_plan(
        project_root=project_root,
        data_root=data_root,
        plan=plan,
        _package_loader=load_event_package,
        _package_error=EventPackageError,
    )


def load_and_admit_experiment_plan(
    *,
    project_root: Path,
    data_root: Path,
    plan_path: Path,
) -> dict[str, Any]:
    """Read and admit one plan without launching a run."""

    return _load_and_admit_experiment_plan(
        project_root=project_root,
        data_root=data_root,
        plan_path=plan_path,
        _package_loader=load_event_package,
        _package_error=EventPackageError,
    )


__all__ = [
    "ExperimentAdmissionError",
    "admit_experiment_plan",
    "load_and_admit_experiment_plan",
]
