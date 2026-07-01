@echo off
title vLoon Auto Portfolio Updater — Remove Schedule
echo ============================================
echo  vLoon Auto Portfolio Updater
echo  Removing scheduled task...
echo ============================================
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script must be run as Administrator.
    echo.
    pause
    exit /b 1
)

schtasks /Delete /TN "vLoon\AutoPortfolioUpdater" /F

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task removed!
) else (
    echo.
    echo [INFO] Task may not exist or could not be removed.
)

echo.
pause
