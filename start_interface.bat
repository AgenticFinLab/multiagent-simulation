@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_interface.ps1"
if errorlevel 1 (
    echo.
    echo Failed to start the MASim interface.
    pause
)

endlocal
