@echo off
title Universal Laptop - Maximum Fan Speed (Highest RPM)
color 0C
echo ========================================================
echo     ACTIVATING MAXIMUM HIGHEST FAN SPEED (100%%)
echo        UNIVERSAL AUTO-DETECTING LAPTOP CONTROLLER
echo ========================================================
echo.
python "%~dp0main.py" max
echo.
echo ========================================================
echo  Fans commanded to MAX HIGHEST RPM!
echo  To reset to normal auto mode, run AUTO_FAN_SPEED.bat
echo ========================================================
echo.
pause
