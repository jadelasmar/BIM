# ONE-TIME SETUP - run this in an Administrator PowerShell on the production server.
#
# Lets one Windows account start, stop and restart the BIMNexus service without an
# elevated prompt, so deploy\deploy.ps1 can finish on its own. It adds a single
# access rule to that one service (the same rights the SYSTEM account already has:
# query, start, stop, pause). It does not give the account any other rights on the
# service (it cannot change its configuration or delete it) and touches nothing else.
#
# Usage (Administrator PowerShell):
#   .\deploy\grant-restart-permission.ps1                  # grants the current user
#   .\deploy\grant-restart-permission.ps1 -UserName "PC\jad"
#
# To undo it, run:  sc.exe sdshow BIMNexus   then remove the "(A;;CCLCSWRPWPDTLOCRRC;;;<that user's SID>)"
# entry and apply the result with  sc.exe sdset BIMNexus "<edited string>".

param([string]$UserName = "$env:USERDOMAIN\$env:USERNAME")

$ServiceName = "BIMNexus"

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "This must be run from an Administrator PowerShell window." -ForegroundColor Red
    exit 1
}

try {
    $sid = (New-Object Security.Principal.NTAccount($UserName)).Translate([Security.Principal.SecurityIdentifier]).Value
} catch {
    Write-Host "Could not find the account '$UserName'." -ForegroundColor Red
    exit 1
}

$current = ((& sc.exe sdshow $ServiceName) | Where-Object { $_ -match "^D:" }) -join ""
if (-not $current) {
    Write-Host "Could not read the permissions of service $ServiceName." -ForegroundColor Red
    exit 1
}
if ($current -match [regex]::Escape($sid)) {
    Write-Host "$UserName already has access to $ServiceName. Nothing to do." -ForegroundColor Green
    exit 0
}

$ace = "(A;;CCLCSWRPWPDTLOCRRC;;;$sid)"
$updated = $current -replace "^D:", ("D:" + $ace)
Write-Host "Granting $UserName ($sid) start/stop on $ServiceName ..."
& sc.exe sdset $ServiceName $updated
if ($LASTEXITCODE -ne 0) {
    Write-Host "sc.exe sdset failed." -ForegroundColor Red
    exit 1
}

$check = ((& sc.exe sdshow $ServiceName) | Where-Object { $_ -match "^D:" }) -join ""
if ($check -match [regex]::Escape($sid)) {
    Write-Host "Done. $UserName can now restart $ServiceName without an Administrator prompt." -ForegroundColor Green
} else {
    Write-Host "The change did not stick - check the service permissions manually." -ForegroundColor Red
    exit 1
}
