@echo off
cls
echo Please put the Phantasmagoria CD into your CD-Rom and then
pause
if not "%0"=="CheckCD" goto Abort
if "%1"=="" goto Abort
echo Checking for Phantasmagoria CD in drive %1:
if exist %1:phcheck.bat goto Exit
cls
echo Please put the Phantasmagoria CD into your CD-Rom and then
pause

:LoopCheck
if exist %1:\phcheck.bat goto Exit
echo.
echo Unable to detect the Phantasmagoria CD in drive %1:.
echo You may abort this looping test by pressing Ctrl-C or
echo insert the CD into your CD-ROM and then
pause
goto LoopCheck

:Abort
echo.
echo This batch file is used automatically by
echo Phantasmagoria. Please do not run it from
echo the DOS command line.
echo.

:Exit 

