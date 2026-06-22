#!/usr/bin/env bash
# ============================================================================
# MASim Streamlit interface launcher (macOS)
# Counterpart of start_interface.bat on Windows.
# ============================================================================
#
# USAGE
# -----
# 1. Double-click in Finder
#      Locate this file at the project root and double-click it. Terminal
#      opens, Streamlit starts in the background, and your default browser
#      opens at http://127.0.0.1:8501 once the server is ready.
#
# 2. From a terminal
#      cd /path/to/multiagent-simulation
#      ./start_interface.command
#
# 3. Override defaults via environment variables
#      MASIM_PYTHON   : python interpreter to use   (default: python3)
#      MASIM_PORT     : Streamlit port              (default: 8501)
#      MASIM_ADDRESS  : bind address                (default: 127.0.0.1)
#
#    Examples (single-line, do not use backslash continuations):
#      MASIM_PYTHON=/opt/anaconda3/envs/masim_env/bin/python ./start_interface.command
#      MASIM_PORT=8600 ./start_interface.command
#
# BEHAVIOR
# --------
#  - If Streamlit is already running on the configured address/port, only the
#    browser is opened (no duplicate process).
#  - The server runs detached in the background; closing this Terminal window
#    does NOT stop it. To stop it: `lsof -ti:8501 | xargs kill` (replace 8501
#    with MASIM_PORT if overridden).
#  - Server stdout/stderr is written to .streamlit_interface.log at the
#    project root for troubleshooting.
#
# REQUIREMENTS
# ------------
#  - Python 3 with `streamlit` and `masim` importable
#    (verify with: python3 -c "import streamlit, masim")
#  - `curl` available on PATH (preinstalled on macOS)
#
# FIRST-RUN NOTE
# --------------
#    If macOS Gatekeeper blocks the file, right-click → Open the first time,
#    or run once: `xattr -d com.apple.quarantine start_interface.command`.
# ============================================================================
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${PROJECT_ROOT}"

if ! "${PROJECT_ROOT}/scripts/start_interface.sh"; then
    echo
    echo "Failed to start the MASim interface."
    # Keep the Terminal window open when launched from Finder.
    read -r -p "Press Return to close..." _
    exit 1
fi
