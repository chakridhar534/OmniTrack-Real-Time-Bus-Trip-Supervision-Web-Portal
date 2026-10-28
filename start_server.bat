@echo off
title OmniTrack Local Server
echo ========================================================
echo  Starting OmniTrack Local Server...
echo  KEEP THIS WINDOW OPEN! Closing it will stop the site.
echo ========================================================
echo.
timeout /t 2 /nobreak >nul
start http://localhost:8000/index.html
python server.py
if errorlevel 1 (
    echo.
    echo Server stopped or encountered an error.
    pause
)
