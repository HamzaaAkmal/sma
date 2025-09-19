@echo off
title NSFW Video Filter - Web App Launcher

echo.
echo ================================
echo   NSFW Video Filter Web App
echo ================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found! Starting launcher...
echo.

python launch_webapp.py

echo.
echo Press any key to exit...
pause >nul
