"""Domain-neutral event-process runtime contracts."""

from .model import (
    ActionDisposition,
    ActionIntent,
    MessageDisposition,
    MessageIntent,
    ObservationEnvelope,
    StateDelta,
)
from .reducer import AuthoritativeReducer, ReducerResult
from .seals import RunSeal, TickSeal, canonical_bytes, canonical_sha256
from .trace import TraceWriter, replay_trace, validate_trace
from .transport import AppendOnlyTransport

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
    "validate_trace",
]
