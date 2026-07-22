@echo off
setlocal
title MASim Interface Launcher
cd /d "%~dp0"

if not defined MASIM_PORT set "MASIM_PORT=8501"
if not defined MASIM_ADDRESS set "MASIM_ADDRESS=127.0.0.1"
if not defined MASIM_PYTHON set "MASIM_PYTHON=python"

echo Starting MASim interface...
echo URL: http://%MASIM_ADDRESS%:%MASIM_PORT%
echo Log: .streamlit_interface.log
echo.

start "" "%MASIM_PYTHON%" -m streamlit run masim\interface\app.py ^
    --server.address %MASIM_ADDRESS% ^
    --server.port %MASIM_PORT% ^
    --server.headless true

if errorlevel 1 (
    echo.
    echo Failed to start the MASim interface.
    pause
    exit /b 1
)

start "" "http://%MASIM_ADDRESS%:%MASIM_PORT%"

echo.
echo MASim interface is opening in your browser.
endlocal
