@echo off
echo ========================================
echo    Universal Video Downloader Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found. Proceeding with setup...
echo.

REM Install pip if not available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Installing pip...
    python -m ensurepip --upgrade
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python dependencies...
python -m pip install -r requirements.txt

REM Run setup script
echo.
echo Running setup script to download tools...
python setup_tools.py

echo.
echo ========================================
echo           Setup Complete!
echo ========================================
echo.
echo To start downloading videos, run:
echo   python video_downloader.py
echo.
echo For YouTube downloads, you can also use:
echo   python -m yt_dlp [URL]
echo.
pause