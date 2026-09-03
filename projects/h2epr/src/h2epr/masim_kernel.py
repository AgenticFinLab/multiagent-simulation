"""Dependency-light access to MASim's event-process kernel.

MASim's top-level package imports the complete distributed and model stack.
The benchmark Rule baseline needs only the repository's public event-process
implementation. This loader executes that unchanged subpackage under a private
module name, so missing Ray, psutil, or model dependencies cannot alter the
scientific runtime.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from h2epr.canonical import file_sha256


_PRIVATE_PACKAGE = "_h2epr_masim_event_process"
_SOURCE_NAMES = (
    "__init__.py",
    "model.py",
    "reducer.py",
    "seals.py",
    "trace.py",
    "transport.py",
)


def _source_root() -> Path:
    return Path(__file__).resolve().parents[4] / "masim" / "integrations" / "event_process"


def _load() -> ModuleType:
    existing = sys.modules.get(_PRIVATE_PACKAGE)
    if existing is not None:
        return existing
    root = _source_root()
    complete_environment = all(
        importlib.util.find_spec(name) is not None
        for name in ("masim", "psutil", "ray", "lmbase")
    )
    if complete_environment:
        return importlib.import_module("masim.integrations.event_process")
    init_path = root / "__init__.py"
    if any(not (root / name).is_file() for name in _SOURCE_NAMES):
        raise ImportError("masim_event_process_kernel_incomplete")
    spec = importlib.util.spec_from_file_location(
        _PRIVATE_PACKAGE,
        init_path,
        submodule_search_locations=[str(root)],
    )
    if spec is None or spec.loader is None:
        raise ImportError("masim_event_process_kernel_spec_failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[_PRIVATE_PACKAGE] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(_PRIVATE_PACKAGE, None)
        raise
    return module


def source_inventory() -> list[dict[str, Any]]:
    root = _source_root()
    return [
        {
            "relative_path": (
                Path("masim") / "integrations" / "event_process" / name
            ).as_posix(),
            "sha256": file_sha256(root / name),
        }
        for name in _SOURCE_NAMES
    ]


_kernel = _load()

ActionDisposition = _kernel.ActionDisposition
ActionIntent = _kernel.ActionIntent
AppendOnlyTransport = _kernel.AppendOnlyTransport
AuthoritativeReducer = _kernel.AuthoritativeReducer
MessageDisposition = _kernel.MessageDisposition
MessageIntent = _kernel.MessageIntent
ObservationEnvelope = _kernel.ObservationEnvelope
ReducerResult = _kernel.ReducerResult
RunSeal = _kernel.RunSeal
StateDelta = _kernel.StateDelta
TickSeal = _kernel.TickSeal
TraceWriter = _kernel.TraceWriter
canonical_bytes = _kernel.canonical_bytes
canonical_sha256 = _kernel.canonical_sha256
replay_trace = _kernel.replay_trace
validate_trace = _kernel.validate_trace

__all__ = [
    "ActionDisposition",
    "ActionIntent",
    "AppendOnlyTransport",
    "AuthoritativeReducer",
    "MessageDisposition",
    "MessageIntent",
    "ObservationEnvelope",
    "ReducerResult",
    "RunSeal",
    "StateDelta",
    "TickSeal",
    "TraceWriter",
    "canonical_bytes",
    "canonical_sha256",
    "replay_trace",
    "source_inventory",
    "validate_trace",
]
