@echo off
title Universal Laptop Fan Control Matrix Dashboard
color 0B
echo ========================================================
echo     STARTING UNIVERSAL LAPTOP FAN CONTROL DASHBOARD
echo ========================================================
echo.
echo Detecting laptop hardware and opening http://localhost:8990...
echo Keep this window open while using the dashboard.
echo.
python "%~dp0server.py"
pause
