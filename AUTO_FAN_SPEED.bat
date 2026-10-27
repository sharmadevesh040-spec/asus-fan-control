@echo off
title Universal Laptop - Normal Auto Fan Speed
color 0A
echo ========================================================
echo        RESTORING FACTORY AUTO FAN CONTROL
echo        UNIVERSAL AUTO-DETECTING LAPTOP CONTROLLER
echo ========================================================
echo.
python "%~dp0main.py" auto
echo.
echo ========================================================
echo  Fans restored to standard BIOS automatic control.
echo ========================================================
echo.
pause
