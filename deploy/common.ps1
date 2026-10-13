# Shared helpers for deploy.ps1 and rollback.ps1 (dot-sourced, not run directly).

$ServiceName = "BIMNexus"
$NssmPath    = "C:\nssm-2.24\win64\nssm.exe"

# Start / stop / restart the BIMNexus service. Uses the normal Windows service
# controls first (works without an elevated prompt once
# deploy\grant-restart-permission.ps1 has been run as Administrator), then falls
# back to nssm (works when this script is run as Administrator).
function Invoke-BimService {
    param([Parameter(Mandatory)][ValidateSet("Restart", "Stop", "Start")][string]$Action)

    try {
        switch ($Action) {
            "Restart" { Restart-Service -Name $ServiceName -Force -ErrorAction Stop }
            "Stop"    { Stop-Service -Name $ServiceName -Force -ErrorAction Stop }
            "Start"   { Start-Service -Name $ServiceName -ErrorAction Stop }
        }
        return $true
    } catch {
        Write-Host "Windows service $Action failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    if (Test-Path $NssmPath) {
        Write-Host "Trying nssm $Action ..." -ForegroundColor Yellow
        & $NssmPath $Action.ToLower() $ServiceName
        return ($LASTEXITCODE -eq 0)
    }
    return $false
}

function Get-EnvValue {
    param([string]$File, [string]$Key)
    if (-not (Test-Path $File)) { return $null }
    $line = Get-Content $File | Where-Object { $_ -match "^\s*$Key\s*=" } | Select-Object -First 1
    if (-not $line) { return $null }
    return (($line -split "=", 2)[1]).Trim().Trim('"').Trim("'")
}

# After a restart: wait for the site to answer and confirm it serves the frontend
# build that was just made (not a stale one). Returns $true/$false.
function Test-BimSite {
    param([Parameter(Mandatory)][string]$RepoRoot, [int]$TimeoutSeconds = 45)

    $envFile    = Join-Path $RepoRoot "backend\.env.production"
    $hosts      = Get-EnvValue $envFile "DJANGO_ALLOWED_HOSTS"
    $hostHeader = if ($hosts) { ($hosts -split ",")[0].Trim() } else { "localhost" }
    $port       = Get-EnvValue $envFile "WAITRESS_PORT"
    if (-not $port) { $port = "8000" }

    $manifestPath = Join-Path $RepoRoot "backend\static\frontend\manifest.json"
    $expectedBase = $null
    if (Test-Path $manifestPath) {
        $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
        $entry = $manifest.PSObject.Properties | Where-Object { $_.Value.isEntry } | Select-Object -First 1
        if ($entry) { $expectedBase = [IO.Path]::GetFileNameWithoutExtension($entry.Value.file) }
    }

    $url      = "http://127.0.0.1:$port/accounts/login/"
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastError = ""
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $url -Headers @{ Host = $hostHeader } -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                if (-not $expectedBase) { return $true }
                if ($response.Content -match ("assets/" + [regex]::Escape($expectedBase) + "\.")) {
                    Write-Host "Site is up and serving frontend build $expectedBase"
                    return $true
                }
                $lastError = "site is up but is not serving build $expectedBase"
            } else {
                $lastError = "HTTP $($response.StatusCode)"
            }
        } catch {
            $lastError = $_.Exception.Message
        }
        Start-Sleep -Seconds 2
    }
    Write-Host "Health check failed: $lastError" -ForegroundColor Red
    return $false
}
