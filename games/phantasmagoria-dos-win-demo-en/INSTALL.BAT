@echo off
cls
mode co80

:INSTALL
cd \install
call install.exe -f

IF NOT EXIST RESOURCE.CFG  GOTO end
IF NOT EXIST INSTALL.EXE   GOTO end
IF NOT EXIST CPUID.EXE     GOTO end
IF NOT EXIST HDDTEC.EXE    GOTO end
IF NOT EXIST WHAT.EXE      GOTO end


cls
@echo The Sierra Install Program is about to perform a 
@echo hardware test.  The results of these tests are used
@echo to determine optimal program performance settings.
@echo.
@echo If you are running the install program for the 
@echo first time, you must select Y for proper gameplay
@echo performance.
@echo.
@echo This Hardware test may lock your computer system.
@echo Select N if you have experienced a lock-up 
@echo previously when performing this test.  
@echo.
what C "Do you want to perform hardware tests? (Y/N) " yn
cls

if not %what%.==Y. goto skipTests

@echo.        
	cpuid
@echo.        
	dos4gw hddtec
@echo.

:skipTests


:end

