@echo off
setlocal
title MASim Interface Launcher
cd /d "%~dp0"

if not defined MASIM_PORT set "MASIM_PORT=8501"
if not defined MASIM_ADDRESS set "MASIM_ADDRESS=127.0.0.1"
if not defined MASIM_PYTHON set "MASIM_PYTHON=D:\Anaconda\envs\masim_env\python.exe"
if not defined MASIM_RESTART set "MASIM_RESTART=1"

echo Starting MASim interface...
echo URL: http://%MASIM_ADDRESS%:%MASIM_PORT%
if "%MASIM_RESTART%"=="1" echo Restart: enabled
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_interface.ps1"
if errorlevel 1 (
    echo.
    echo Failed to start the MASim interface.
    pause
    exit /b 1
)

echo.
echo MASim interface is open in your browser.
endlocal
