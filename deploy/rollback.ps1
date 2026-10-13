# BIM Nexus production rollback script (lives in the repo at deploy\rollback.ps1).
# Stops the service, shows recent commits and DB backups side by side, lets
# you pick a commit to check out and/or a backup to restore, then restarts.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
. (Join-Path $PSScriptRoot "common.ps1")

$DbFile    = Join-Path $RepoRoot "db_prod.sqlite3"
$BackupDir = Join-Path $RepoRoot "backend\backups"

Set-Location $RepoRoot

Write-Host "--- stopping $ServiceName service ---"
if (-not (Invoke-BimService -Action Stop)) {
    Write-Host "Could not stop the service - stopping here so nothing changes while it is still running." -ForegroundColor Red
    exit 1
}
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "=== Recent commits ===" -ForegroundColor Cyan
$commitLines = @(git log --oneline -20)

Write-Host "=== Recent DB backups ===" -ForegroundColor Cyan
$backupFiles = @(Get-ChildItem $BackupDir -Filter "db_prod_*.sqlite3" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 20)

$maxRows = [Math]::Max($commitLines.Count, $backupFiles.Count)
Write-Host ""
Write-Host ("{0,-3} {1,-50} {2,-30}" -f "#", "COMMIT", "BACKUP")
Write-Host ("{0,-3} {1,-50} {2,-30}" -f "-", ("-" * 50), ("-" * 25))
for ($i = 0; $i -lt $maxRows; $i++) {
    $c = if ($i -lt $commitLines.Count) { $commitLines[$i] } else { "" }
    $b = if ($i -lt $backupFiles.Count) { $backupFiles[$i].Name } else { "" }
    Write-Host ("{0,-3} {1,-50} {2,-30}" -f $i, $c, $b)
}

Write-Host ""
$commitHash   = Read-Host "Enter commit hash to check out (blank = skip code rollback)"
$backupChoice = Read-Host "Enter backup filename to restore (blank = skip DB restore)"

if ($commitHash) {
    Write-Host "`n--- git checkout $commitHash ---"
    git checkout $commitHash
    if ($LASTEXITCODE -ne 0) {
        Write-Host "git checkout failed - not restarting service" -ForegroundColor Red
        exit 1
    }
    Write-Host "Note: repo is now in a detached HEAD state at $commitHash." -ForegroundColor Yellow
    Write-Host "Before the next deploy.ps1 run, check out 'main' again (git checkout main) or deploy.ps1's 'git pull' will fail." -ForegroundColor Yellow
}

if ($backupChoice) {
    $backupPath = Join-Path $BackupDir $backupChoice
    if (-not (Test-Path $backupPath)) {
        Write-Host "Backup file not found: $backupPath - not restarting service" -ForegroundColor Red
        exit 1
    }
    Write-Host "`n--- restoring DB from $backupChoice ---"
    Copy-Item $backupPath $DbFile -Force
    Write-Host "Restored: $DbFile"
}

Write-Host "`n--- starting $ServiceName service ---"
if (-not (Invoke-BimService -Action Start)) {
    Write-Host "Could not start the service - start it from an Administrator window." -ForegroundColor Red
    exit 1
}
Start-Sleep -Seconds 2
$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($null -eq $svc -or $svc.Status -ne "Running") {
    Write-Host "WARNING: service is not in Running state after start (status: $($svc.Status))" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "ROLLBACK COMPLETE" -ForegroundColor Green
