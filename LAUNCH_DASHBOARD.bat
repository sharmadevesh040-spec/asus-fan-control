@echo off
title ASUS TUF Fan Control Matrix Dashboard
color 0B
echo ========================================================
echo       STARTING ASUS TUF FAN CONTROL DASHBOARD
echo ========================================================
echo.
echo Opening browser at http://localhost:8990...
echo Keep this window open while using the dashboard.
echo.
python "%~dp0server.py"
pause
