@echo off
title vLoon Auto Portfolio Updater — Install Schedule
echo ============================================
echo  vLoon Auto Portfolio Updater
echo  Installing scheduled task...
echo ============================================
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script must be run as Administrator.
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Get the absolute path
set SCRIPT_DIR=%~dp0
set PS_PATH=%SCRIPT_DIR%auto-update.ps1

:: Create the daily scheduled task (runs at 9:00 AM)
schtasks /Create /SC DAILY /TN "vLoon\AutoPortfolioUpdater" /TR "powershell.exe -File \"%PS_PATH%\"" /ST 09:00 /RL HIGHEST /F

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task created!
    echo.
    echo   Task Name:  vLoon\AutoPortfolioUpdater
    echo   Schedule:   Daily at 9:00 AM
    echo   Script:     %PS_PATH%
    echo   Logs:       %SCRIPT_DIR%logs\
    echo.
    echo To run it right now, open Task Scheduler and right-click ^> Run.
    echo Or run: schtasks /Run /TN "vLoon\AutoPortfolioUpdater"
) else (
    echo.
    echo [FAILED] Could not create the task. See error above.
)

echo.
pause
