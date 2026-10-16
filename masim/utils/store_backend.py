"""Lazy handle for the ``lmbase`` block-store backend.

``BlockBasedStoreManager`` comes from ``lmbase`` — a sibling project that is
**not published on PyPI**. Importing it at module scope made ``import masim``
fail outright on any environment without lmbase, even for code paths that never
touch disk storage (unit tests, contract audits, config validation, pure-Rule
runs with message recording disabled, and the whole ``masim/platform`` contract
layer).

``BlockBasedStoreManager`` below is therefore a thin lazy proxy. It is a real
class object, so runtime type annotations such as
``Dict[str, BlockBasedStoreManager]`` keep working, but its ``__new__``
resolves the genuine ``lmbase`` class on first instantiation and delegates to
it. A missing lmbase then surfaces as a single actionable error at the point of
use instead of an opaque ``ModuleNotFoundError`` at import time.

Notes
-----
* The proxy is not meant to be subclassed or used with ``isinstance`` — the
  framework only ever instantiates the store, so those operations are not
  supported and would misbehave.
* ``masim/agents/_base.py`` and ``masim/utils/llm_utils.py`` import lmbase's
  *inference* classes inside functions already; only the block store needed a
  top-level shim.
"""

from typing import Any

_INSTALL_HINT = (
    "The MASim record store requires the 'lmbase' package "
    "(https://github.com/AgenticFinLab/lmbase), which is not published on "
    "PyPI. Install it from source before recording a run:\n"
    "    git clone https://github.com/AgenticFinLab/lmbase.git /opt/lmbase\n"
    "    pip install -e /opt/lmbase"
)


def load_block_store_manager() -> Any:
    """Return the real ``BlockBasedStoreManager`` class.

    Raises:
        ImportError: when ``lmbase`` is not installed, with an install hint.
    """
    try:
        from lmbase.utils.tools import BlockBasedStoreManager as _real
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise ImportError(_INSTALL_HINT) from exc
    return _real


class BlockBasedStoreManager:
    """Lazy stand-in for ``lmbase.utils.tools.BlockBasedStoreManager``.

    Instantiation resolves and constructs the genuine class, so callers can
    treat this exactly like the real store.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        return load_block_store_manager()(*args, **kwargs)
