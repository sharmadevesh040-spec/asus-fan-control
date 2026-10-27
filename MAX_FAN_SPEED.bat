@echo off
title ASUS TUF - Maximum Fan Speed (Highest RPM)
color 0C
echo ===================================================
echo     ACTIVATING MAXIMUM HIGHEST FAN SPEED (100%%)
echo           ASUS TUF GAMING LAPTOP
echo ===================================================
echo.
python "%~dp0asus_fan_controller.py" max
echo.
echo ===================================================
echo  Fans are now running at MAX HIGHEST RPM!
echo  To reset to normal auto mode, run AUTO_FAN_SPEED.bat
echo ===================================================
echo.
pause
