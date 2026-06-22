#!/usr/bin/env bash
# macOS / Linux launcher for the MASim Streamlit interface.
# Mirrors scripts/start_interface.ps1 (Windows).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Allow override: MASIM_PYTHON=/path/to/python ./scripts/start_interface.sh
PYTHON_BIN="${MASIM_PYTHON:-python3}"
PORT="${MASIM_PORT:-8501}"
ADDRESS="${MASIM_ADDRESS:-127.0.0.1}"
URL="http://${ADDRESS}:${PORT}"
HEALTH_URL="${URL}/_stcore/health"
APP_PATH="${PROJECT_ROOT}/masim/interface/app.py"
LOG_FILE="${PROJECT_ROOT}/.streamlit_interface.log"

is_ready() {
    # Returns 0 when Streamlit health endpoint replies "ok".
    curl --silent --max-time 1 --fail "${HEALTH_URL}" 2>/dev/null | grep -q '^ok$'
}

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "Python interpreter not found: ${PYTHON_BIN}" >&2
    echo "Set MASIM_PYTHON to override (e.g. MASIM_PYTHON=/path/to/conda/env/bin/python)." >&2
    exit 1
fi

if ! is_ready; then
    cd "${PROJECT_ROOT}"
    nohup "${PYTHON_BIN}" -m streamlit run "${APP_PATH}" \
        --server.address="${ADDRESS}" \
        --server.port="${PORT}" \
        --server.headless=true \
        --browser.gatherUsageStats=false \
        >"${LOG_FILE}" 2>&1 &
    disown $! 2>/dev/null || true

    ready=false
    for _ in $(seq 1 30); do
        sleep 1
        if is_ready; then
            ready=true
            break
        fi
    done

    if [ "${ready}" != "true" ]; then
        echo "Streamlit did not become ready at ${URL} within 30 seconds." >&2
        echo "See log: ${LOG_FILE}" >&2
        exit 1
    fi
fi

# Open the URL in the user's default browser.
if command -v open >/dev/null 2>&1; then
    open "${URL}"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${URL}" >/dev/null 2>&1 || true
fi

echo "MASim interface opened: ${URL}"
