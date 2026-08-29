"""Static implementation identities available to the Panic policy loader."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping


_IMPLEMENTATION_VERSIONS: Mapping[str, str] = MappingProxyType({})


def implementation_versions() -> Mapping[str, str]:
    """Return the closed registry without importing code from document fields."""

    return _IMPLEMENTATION_VERSIONS


__all__ = ["implementation_versions"]
