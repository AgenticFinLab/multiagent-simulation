$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = "D:\Anaconda\envs\masim_env\python.exe"
$port = 8501
$address = "127.0.0.1"
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
    Write-Error "Python environment not found: $pythonPath"
    exit 1
}

if (-not (Test-MASimInterface)) {
    $appPath = Join-Path $projectRoot "masim\interface\app.py"
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
