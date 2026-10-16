"""Per-part acceptance tests for the MASim platform.

Each subpackage (``Agent``, ``Time``, ``Communication``, ``Storage``,
``Execution``, ``Observability``, ``World``, ``Config``) asserts the
documented contract of one platform part — not the internals that
``tests/`` already covers at unit level.  Run with::

    PYTHONPATH=. python -m unittest discover -s examples/uTests -t . -v
"""
