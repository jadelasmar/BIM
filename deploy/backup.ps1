# BIM Nexus scheduled backup (lives in the repo at deploy\backup.ps1).
# Meant to be run by Windows Task Scheduler (see docs\Development.md), not only at
# deploy time. It never stops the service and never changes the live database:
#   1. online-backup db_prod.sqlite3 with the project's python, PRAGMA integrity_check the copy
#   2. copy the backup to the share and verify it by hash
#   3. copy backend\media to <share>\media with robocopy /E (never /MIR)
#   4. prune old daily backups, locally and on the share (only files matching its own pattern)
# Backup files are named db_prod_daily_YYYYMMDD_HHMMSS.sqlite3, so deploy.ps1's pruning
# pattern (db_prod_20*.sqlite3) never matches or deletes them, while rollback.ps1 lists
# them (it lists db_prod_*.sqlite3).
# A failed copy is renamed to *.failed, never deleted. Any failure exits non-zero and
# appends a line to <BackupDir>\backup.log; success appends one summary line.
#
# The parameters default to the production locations; pass others to test against a
# throwaway database and temp folders.

param(
    [string]$DbFile    = (Join-Path (Split-Path -Parent $PSScriptRoot) "db_prod.sqlite3"),
    [string]$BackupDir = (Join-Path (Split-Path -Parent $PSScriptRoot) "backend\backups"),
    [string]$ShareDir  = "\\hostserver\Technical Dep\Jad\BIM Nexus",
    [string]$MediaDir  = (Join-Path (Split-Path -Parent $PSScriptRoot) "backend\media"),
    [string]$PythonExe = (Join-Path (Split-Path -Parent $PSScriptRoot) ".venv\Scripts\python.exe"),
    [int]$KeepDaily    = 14
)

$ErrorActionPreference = "Stop"
$Pattern = "db_prod_daily_*.sqlite3"   # this script's own files, and only these are ever pruned
$LogFile = Join-Path $BackupDir "backup.log"

function Write-Log($level, $msg) {
    $line = "{0} {1} {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $level, $msg
    try {
        if (-not (Test-Path -LiteralPath $BackupDir)) { New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null }
        Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
    } catch {
        Write-Host "Could not write to $LogFile : $($_.Exception.Message)" -ForegroundColor Yellow
    }
    Write-Host $line
}

function Fail($msg) {
    Write-Log "FAILED" $msg
    exit 1
}

try {
    # 1. Online backup + integrity check
    if (-not (Test-Path -LiteralPath $PythonExe)) { Fail "python not found at $PythonExe" }
    if (-not (Test-Path -LiteralPath $DbFile)) { Fail "database not found at $DbFile" }
    if (-not (Test-Path -LiteralPath $BackupDir)) { New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null }

    $timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "db_prod_daily_$timestamp.sqlite3"
    $backupFile = Join-Path $BackupDir $backupName
    # SQLite's online backup API is safe while the service is running.
    $backupScript = "import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); d=sqlite3.connect(sys.argv[2]); s.backup(d); r=d.execute('PRAGMA integrity_check').fetchone()[0]; d.close(); s.close(); sys.exit(0 if r == 'ok' else 1)"
    & $PythonExe -c $backupScript $DbFile $backupFile
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $backupFile) -or (Get-Item -LiteralPath $backupFile).Length -eq 0) {
        if (Test-Path -LiteralPath $backupFile) { Move-Item -LiteralPath $backupFile "$backupFile.failed" -Force }
        Fail "could not create a valid backup of $DbFile (kept as $backupName.failed if a file was written)"
    }

    # 2. Copy to the share, verify by hash
    if (-not (Test-Path -LiteralPath $ShareDir)) { Fail "backup share not reachable: $ShareDir (local backup $backupName was kept)" }
    try {
        Copy-Item -LiteralPath $backupFile -Destination $ShareDir -ErrorAction Stop
    } catch {
        $partial = Join-Path $ShareDir $backupName
        if (Test-Path -LiteralPath $partial) { Move-Item -LiteralPath $partial "$partial.failed" -Force -ErrorAction SilentlyContinue }
        Fail "could not copy $backupName to $ShareDir : $($_.Exception.Message) (local backup kept)"
    }
    $shareCopy = Join-Path $ShareDir $backupName
    if (-not (Test-Path -LiteralPath $shareCopy) -or
        (Get-FileHash -LiteralPath $shareCopy).Hash -ne (Get-FileHash -LiteralPath $backupFile).Hash) {
        if (Test-Path -LiteralPath $shareCopy) { Move-Item -LiteralPath $shareCopy "$shareCopy.failed" -Force }
        Fail "the copy of $backupName on $ShareDir does not match the local backup (renamed to .failed on the share)"
    }

    # 3. Media: /E adds and updates, never deletes from the share (not /MIR).
    # Robocopy exit codes 0-7 are success, 8 or more is a failure.
    $mediaNote = "media skipped (no folder)"
    if (Test-Path -LiteralPath $MediaDir) {
        $mediaShare = Join-Path $ShareDir "media"
        robocopy $MediaDir $mediaShare /E /R:2 /W:2 /NFL /NDL /NP /NJH | Out-Null
        $rc = $LASTEXITCODE
        if ($rc -ge 8) { Fail "database backup $backupName is safe on the share, but copying media to $mediaShare failed (robocopy exit code $rc)" }
        $mediaNote = "media copied (robocopy exit $rc)"
    }

    # 4. Retention: only after the database copy is confirmed, only this script's own files
    $pruned = 0
    foreach ($dir in @($BackupDir, $ShareDir)) {
        Get-ChildItem -LiteralPath $dir -Filter $Pattern |
            Where-Object { $_.Name -like "db_prod_daily_*.sqlite3" -and $_.Extension -eq ".sqlite3" } |
            Sort-Object Name -Descending |
            Select-Object -Skip $KeepDaily |
            ForEach-Object {
                Remove-Item -LiteralPath $_.FullName -Force
                $pruned++
            }
    }

    $sizeMb = [math]::Round((Get-Item -LiteralPath $backupFile).Length / 1MB, 2)
    Write-Log "OK" "$backupName ($sizeMb MB) verified locally and on share; pruned $pruned old daily backup(s), keeping $KeepDaily; $mediaNote"
    exit 0
} catch {
    Write-Log "FAILED" "unexpected error: $($_.Exception.Message)"
    exit 1
}
