"""Pytest configuration for the offline H2EPR contract suite."""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True
TEST_ROOT = Path(__file__).resolve().parent
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

PROJECT_SRC = TEST_ROOT.parent / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

PROJECT_ROOT = TEST_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(1, str(PROJECT_ROOT))
