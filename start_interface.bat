@echo off
setlocal EnableExtensions
title MASim Interface Launcher
cd /d "%~dp0"

rem ---------------------------------------------------------------------------
rem Configuration. Values supplied by the caller always take precedence.
rem ---------------------------------------------------------------------------
if not defined MASIM_PORT set "MASIM_PORT=8501"
if not defined MASIM_ADDRESS set "MASIM_ADDRESS=127.0.0.1"

rem Prefer the project's known Conda environment when it is available.
if not defined MASIM_PYTHON (
    if exist "D:\Anaconda\envs\masim_env\python.exe" (
        set "MASIM_PYTHON=D:\Anaconda\envs\masim_env\python.exe"
    ) else (
        set "MASIM_PYTHON=python"
    )
)

set "MASIM_URL=http://%MASIM_ADDRESS%:%MASIM_PORT%"
set "MASIM_HEALTH_URL=%MASIM_URL%/_stcore/health"
set "MASIM_ROOT=%~dp0"
set "MASIM_LOG=%~dp0.streamlit_interface.log"
set "MASIM_OUT_LOG=%~dp0.streamlit_interface.stdout.log"
set "MASIM_PID_FILE=%~dp0.streamlit_interface.pid"

echo MASim Interface Launcher
echo URL:    %MASIM_URL%
echo Python: %MASIM_PYTHON%
echo Error log: %MASIM_LOG%
echo Output log: %MASIM_OUT_LOG%
echo.

rem Reuse an already-running interface instead of starting a duplicate process.
powershell -NoProfile -Command ^
    "try { $r = Invoke-WebRequest -UseBasicParsing -Uri $env:MASIM_HEALTH_URL -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; exit 1"
if not errorlevel 1 (
    echo The interface is already running. Opening it in your browser...
    goto open_browser
)

rem Fail early with a useful message if this interpreter cannot run the app.
"%MASIM_PYTHON%" -c "import streamlit, masim" >nul 2>&1
if errorlevel 1 (
    echo ERROR: The selected Python environment cannot import streamlit and masim.
    echo Set MASIM_PYTHON to the correct python.exe and try again.
    goto failed
)

echo Starting the interface...
powershell -NoProfile -Command ^
    "$streamlitArgs = @('-m', 'streamlit', 'run', 'masim\interface\app.py', '--server.address', $env:MASIM_ADDRESS, '--server.port', $env:MASIM_PORT, '--server.headless', 'true'); $process = Start-Process -FilePath $env:MASIM_PYTHON -ArgumentList $streamlitArgs -WorkingDirectory $env:MASIM_ROOT -WindowStyle Hidden -RedirectStandardOutput $env:MASIM_OUT_LOG -RedirectStandardError $env:MASIM_LOG -PassThru; Set-Content -LiteralPath $env:MASIM_PID_FILE -Value $process.Id -Encoding ascii; Start-Sleep -Milliseconds 750; if ($process.HasExited) { exit 1 }"

if errorlevel 1 (
    echo ERROR: Streamlit could not be started.
    goto failed
)

rem Wait up to 45 seconds so the browser never lands on a server that is not ready.
echo Waiting for the interface to become ready...
powershell -NoProfile -Command ^
    "$deadline = (Get-Date).AddSeconds(45); do { try { $r = Invoke-WebRequest -UseBasicParsing -Uri $env:MASIM_HEALTH_URL -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 500 } while ((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 (
    echo ERROR: The interface did not become ready within 45 seconds.
    goto failed
)

:open_browser
start "" "%MASIM_URL%"
echo MASim is ready and has been opened in your browser.
endlocal
exit /b 0

:failed
echo.
echo Check the log for details:
echo %MASIM_LOG%
if exist "%MASIM_LOG%" (
    echo.
    echo Last log lines:
    powershell -NoProfile -Command "Get-Content -LiteralPath $env:MASIM_LOG -Tail 20"
)
if exist "%MASIM_OUT_LOG%" (
    echo.
    echo Last output lines:
    powershell -NoProfile -Command "Get-Content -LiteralPath $env:MASIM_OUT_LOG -Tail 20"
)
echo.
pause
endlocal
exit /b 1
