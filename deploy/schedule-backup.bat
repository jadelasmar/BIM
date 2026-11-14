@echo off
rem BIM Nexus - one-time setup of the scheduled daily backup (deploy\schedule-backup.bat).
rem Right-click this file and choose "Run as administrator".
rem
rem Creates two Windows scheduled tasks, "BIM Nexus Backup 1300" and "BIM Nexus Backup 2300",
rem that run deploy\backup.ps1 -KeepDaily 28 every day at 13:00 and 23:00 as the Windows
rem account you type. Windows itself asks for that account's password (once per task) and
rem stores it; this script never sees it. Then it runs the 13:00 task once and prints the
rem last line of backend\backups\backup.log. Safe to run again: existing tasks are replaced.
rem
rem Only if that last line says OK, it then disables (does not delete) the older task
rem "BIMNexus Nightly DB Backup", whose script (backend\backup_db.ps1) prunes every
rem db_prod_*.sqlite3 file and would in time delete the daily and pre-rollback backups.
rem If the line is not OK, the old task is left enabled so there is still a nightly backup.
setlocal

set "SCRIPT=C:\Projects\BIM-Release\deploy\backup.ps1"
set "LOG=C:\Projects\BIM-Release\backend\backups\backup.log"
set "TASK1=BIM Nexus Backup 1300"
set "TASK2=BIM Nexus Backup 2300"
set "OLDTASK=BIMNexus Nightly DB Backup"
rem The whole command is one quoted /TR value. It has no inner quotes because the
rem script path has no spaces; keep it that way if the path ever changes.
set "TR=powershell.exe -NoProfile -ExecutionPolicy Bypass -File %SCRIPT% -KeepDaily 28"

fltmc >nul 2>&1
if errorlevel 1 goto notadmin
if not exist "%SCRIPT%" goto noscript

echo The tasks must run as the Windows account that can write to the backup share.
set "ACCOUNT="
set /p "ACCOUNT=Windows account name (for example PC\jad or DOMAIN\jad): "
if not defined ACCOUNT goto noaccount

echo.
echo Creating "%TASK1%" - Windows will now ask for the password of %ACCOUNT%.
schtasks /Create /F /TN "%TASK1%" /TR "%TR%" /SC DAILY /ST 13:00 /RU "%ACCOUNT%" /RP *
if errorlevel 1 goto createfailed

echo.
echo Creating "%TASK2%" - Windows will ask for the same password again.
schtasks /Create /F /TN "%TASK2%" /TR "%TR%" /SC DAILY /ST 23:00 /RU "%ACCOUNT%" /RP *
if errorlevel 1 goto createfailed

rem Run the 13:00 task once and wait (up to 2 minutes) for a new line in backup.log.
set "BEFORE=0"
if exist "%LOG%" for /f %%n in ('type "%LOG%" ^| find /c /v ""') do set "BEFORE=%%n"
echo.
echo Running "%TASK1%" once to test it ...
schtasks /Run /TN "%TASK1%"
if errorlevel 1 goto runfailed

set /a TRIES=0
:wait
timeout /t 3 /nobreak >nul
set "AFTER=0"
if exist "%LOG%" for /f %%n in ('type "%LOG%" ^| find /c /v ""') do set "AFTER=%%n"
if %AFTER% GTR %BEFORE% goto logged
set /a TRIES+=1
if %TRIES% LSS 40 goto wait
echo.
echo The task did not write a new line to %LOG% within 2 minutes.
echo Open Task Scheduler, select "%TASK1%" and check "Last Run Result".
goto failed

:logged
echo.
echo Last line of %LOG%:
powershell.exe -NoProfile -Command "Get-Content -LiteralPath '%LOG%' -Tail 1"
rem A log line is "yyyy-MM-dd HH:mm:ss LEVEL message": the test passed only if LEVEL is OK.
powershell.exe -NoProfile -Command "$l = Get-Content -LiteralPath '%LOG%' -Tail 1; if ($l -and (($l -split ' ')[2] -ceq 'OK')) { exit 0 } else { exit 1 }"
if errorlevel 1 goto testfailed
echo.
echo That line says OK: the daily backup is scheduled and working.

rem The new backup works, so retire the old nightly task. Disable only, never delete.
schtasks /Query /TN "%OLDTASK%" >nul 2>&1
if errorlevel 1 goto oldmissing
schtasks /Change /TN "%OLDTASK%" /DISABLE >nul
if errorlevel 1 goto olddisablefailed
echo.
echo The old task "%OLDTASK%" was DISABLED. It was not deleted;
echo to turn it back on: schtasks /Change /TN "%OLDTASK%" /ENABLE
pause
exit /b 0

:oldmissing
echo.
echo There is no task named "%OLDTASK%" on this machine, so there was nothing to disable.
pause
exit /b 0

:olddisablefailed
echo.
echo WARNING: the old task "%OLDTASK%" could NOT be disabled and is STILL ENABLED.
echo Disable it by hand in Task Scheduler: its script deletes old db_prod_*.sqlite3
echo files, which in time would include the new daily backups.
goto failed

:testfailed
echo.
echo That line does NOT say OK, so the new backup is not working yet.
echo The old task "%OLDTASK%" was left ENABLED, so the nightly backup still runs.
echo The line above gives the reason; fix it and run this file again.
goto failed

:notadmin
echo This must be run as Administrator: right-click the file and choose "Run as administrator".
goto failed

:noscript
echo %SCRIPT% was not found. Run deploy.bat first so the script exists.
goto failed

:noaccount
echo No account name was entered. Nothing was changed.
goto failed

:createfailed
echo.
echo schtasks could not create the task (wrong account name or password?). Run this file again.
goto failed

:runfailed
echo.
echo The tasks were created but "%TASK1%" could not be started.
goto failed

:failed
pause
exit /b 1
