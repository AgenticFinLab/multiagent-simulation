"""Strict local JSON and path handling for H2EPR execution releases."""

from __future__ import annotations

from enum import Enum
import json
from pathlib import Path
from typing import Any


class ExecutionIOCode(str, Enum):
    SOURCE_NOT_FOUND = "H2EPR_EXECUTION_SOURCE_NOT_FOUND"
    PATH_UNSAFE = "H2EPR_EXECUTION_PATH_UNSAFE"
    JSON_INVALID = "H2EPR_EXECUTION_JSON_INVALID"
    JSON_DUPLICATE_KEY = "H2EPR_EXECUTION_JSON_DUPLICATE_KEY"


class ExecutionIOError(ValueError):
    """One typed fail-closed input rejection."""

    def __init__(
        self,
        code: ExecutionIOCode,
        *,
        pointer: str = "",
        detail: str = "",
    ) -> None:
        self.code = code
        self.pointer = pointer
        self.detail = detail
        parts = [code.value]
        if pointer:
            parts.append(pointer)
        if detail:
            parts.append(detail)
        super().__init__(":".join(parts))


class _DuplicateKey(ValueError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(value)


def path_within(root: str | Path, path: str | Path, *, pointer: str) -> Path:
    """Resolve a path and reject any escape from its declared root."""

    resolved_root = Path(root).resolve()
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ExecutionIOError(
            ExecutionIOCode.PATH_UNSAFE,
            pointer=pointer,
            detail=Path(path).as_posix(),
        ) from exc
    return resolved


def read_json_object(path: str | Path, *, pointer: str) -> tuple[dict[str, Any], bytes]:
    """Read one UTF-8 JSON object while rejecting duplicate keys and constants."""

    source = Path(path)
    if not source.is_file():
        raise ExecutionIOError(
            ExecutionIOCode.SOURCE_NOT_FOUND,
            pointer=pointer,
            detail=source.as_posix(),
        )
    raw = source.read_bytes()
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except _DuplicateKey as exc:
        raise ExecutionIOError(
            ExecutionIOCode.JSON_DUPLICATE_KEY,
            pointer=pointer,
            detail=str(exc),
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ExecutionIOError(
            ExecutionIOCode.JSON_INVALID,
            pointer=pointer,
            detail=type(exc).__name__,
        ) from exc
    if not isinstance(value, dict):
        raise ExecutionIOError(ExecutionIOCode.JSON_INVALID, pointer=pointer)
    return value, raw


__all__ = [
    "ExecutionIOCode",
    "ExecutionIOError",
    "path_within",
    "read_json_object",
]
