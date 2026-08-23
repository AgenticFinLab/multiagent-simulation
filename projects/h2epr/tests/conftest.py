"""Pytest configuration for the offline H2EPR contract suite."""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True
TEST_ROOT = Path(__file__).resolve().parent
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))
