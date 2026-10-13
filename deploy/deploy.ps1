# BIM Nexus production deploy script (lives in the repo at deploy\deploy.ps1).
# Backs up db_prod.sqlite3, pulls latest code, rebuilds the frontend, applies
# migrations/static, restarts the BIMNexus service and checks the site is serving
# the new build. Stops on first failure.
#
# Restarting the service needs permission to control it: run
# deploy\grant-restart-permission.ps1 once as Administrator so this works without
# an elevated prompt.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
. (Join-Path $PSScriptRoot "common.ps1")

$DbFile     = Join-Path $RepoRoot "db_prod.sqlite3"
$BackupDir  = Join-Path $RepoRoot "backend\backups"
$MaxBackups = 10
$PythonExe  = Join-Path $RepoRoot ".venv\Scripts\python.exe"

function Fail($msg) {
    Write-Host ""
    Write-Host "DEPLOY FAILED: $msg" -ForegroundColor Red
    exit 1
}

Set-Location $RepoRoot

# 1. Backup DB
if (-not (Test-Path $DbFile)) { Fail "db_prod.sqlite3 not found at $DbFile" }
if (-not (Test-Path $BackupDir)) { New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null }

$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupDir "db_prod_$timestamp.sqlite3"
try {
    Copy-Item $DbFile $backupFile -ErrorAction Stop
} catch {
    Fail "could not create backup: $($_.Exception.Message)"
}
Write-Host "Backup created: $backupFile"

$existingBackups = Get-ChildItem $BackupDir -Filter "db_prod_*.sqlite3" | Sort-Object LastWriteTime -Descending
if ($existingBackups.Count -gt $MaxBackups) {
    $existingBackups | Select-Object -Skip $MaxBackups | ForEach-Object {
        Remove-Item $_.FullName -Force
        Write-Host "Pruned old backup: $($_.Name)"
    }
}

# 2. git pull (fast-forward only: never creates a merge on the server)
Write-Host "`n--- git pull ---"
git pull --ff-only
if ($LASTEXITCODE -ne 0) { Fail "git pull failed" }

# 3. npm install
Write-Host "`n--- npm install ---"
Set-Location (Join-Path $RepoRoot "frontend")
npm install
if ($LASTEXITCODE -ne 0) { Fail "npm install failed" }

# 4. npm run build
Write-Host "`n--- npm run build ---"
npm run build
if ($LASTEXITCODE -ne 0) { Fail "npm run build failed" }

# 5. collectstatic
Write-Host "`n--- collectstatic ---"
Set-Location (Join-Path $RepoRoot "backend")
$env:DJANGO_DB_NAME = "db_prod.sqlite3"
& $PythonExe manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) { Fail "collectstatic failed" }

# 6. migrate
Write-Host "`n--- migrate ---"
& $PythonExe manage.py migrate
if ($LASTEXITCODE -ne 0) { Fail "migrate failed" }

# 7. restart service
Write-Host "`n--- restarting $ServiceName service ---"
if (-not (Invoke-BimService -Action Restart)) {
    Fail ("service restart failed. Code, build and migrations are already applied; only the restart is missing. " +
          "Restart $ServiceName from an Administrator window, and run deploy\grant-restart-permission.ps1 once as Administrator so future deploys can do it themselves.")
}
$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($null -eq $svc -or $svc.Status -ne "Running") {
    Fail "service is not in Running state after restart (status: $($svc.Status))"
}

# 8. health check: the site answers and serves the build we just made
Write-Host "`n--- health check ---"
Set-Location $RepoRoot
if (-not (Test-BimSite -RepoRoot $RepoRoot)) {
    Fail "the service is running but the site did not pass the health check (see message above)"
}

Write-Host ""
Write-Host "DEPLOY SUCCEEDED" -ForegroundColor Green
Write-Host "Backup used: $backupFile"
