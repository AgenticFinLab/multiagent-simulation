$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = if ($env:MASIM_PYTHON) { $env:MASIM_PYTHON } else { "D:\Anaconda\envs\masim_env\python.exe" }
$port = if ($env:MASIM_PORT) { [int]$env:MASIM_PORT } else { 8501 }
$address = if ($env:MASIM_ADDRESS) { $env:MASIM_ADDRESS } else { "127.0.0.1" }
$restart = if ($env:MASIM_RESTART) { $env:MASIM_RESTART -eq "1" } else { $true }
$appPath = Join-Path $projectRoot "masim\interface\app.py"
$url = "http://${address}:${port}"
$healthUrl = "${url}/_stcore/health"

function Test-MASimInterface {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $healthUrl -TimeoutSec 1
        return $response.StatusCode -eq 200 -and $response.Content.Trim() -eq "ok"
    }
    catch {
        return $false
    }
}

if (-not (Test-Path -LiteralPath $pythonPath)) {
    $pathPython = Get-Command python -ErrorAction SilentlyContinue
    if ($pathPython) {
        $pythonPath = $pathPython.Source
        Write-Host "MASIM_PYTHON was not found; falling back to PATH python: $pythonPath"
    }
    else {
        Write-Error "Python environment not found: $pythonPath. Set MASIM_PYTHON to a Python executable with streamlit installed."
        exit 1
    }
}

if ($restart) {
    $escapedAppPath = [regex]::Escape($appPath)
    $escapedPortArg = [regex]::Escape("--server.port=$port")
    $existing = Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -match "streamlit" -and
        $_.CommandLine -match $escapedAppPath -and
        $_.CommandLine -match $escapedPortArg
    }
    foreach ($process in $existing) {
        Write-Host "Stopping existing MASim interface process: $($process.ProcessId)"
        Stop-Process -Id $process.ProcessId -Force
    }
    if ($existing) {
        Start-Sleep -Seconds 1
    }
}

if (-not (Test-MASimInterface)) {
    $arguments = @(
        "-m",
        "streamlit",
        "run",
        $appPath,
        "--server.address=$address",
        "--server.port=$port",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    )

    Start-Process `
        -FilePath $pythonPath `
        -ArgumentList $arguments `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden | Out-Null

    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Seconds 1
        if (Test-MASimInterface) {
            $ready = $true
            break
        }
    }

    if (-not $ready) {
        Write-Error "Streamlit did not become ready at $url within 30 seconds."
        exit 1
    }
}

Start-Process $url
Write-Host "MASim interface opened: $url"
