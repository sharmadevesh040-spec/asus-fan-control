@echo off
title ASUS TUF - Normal Auto Fan Speed
color 0A
echo ===================================================
echo        RESTORING FACTORY AUTO FAN CONTROL
echo             ASUS TUF GAMING LAPTOP
echo ===================================================
echo.
python "%~dp0asus_fan_controller.py" auto
echo.
echo ===================================================
echo  Fans restored to standard BIOS automatic control.
echo ===================================================
echo.
pause
