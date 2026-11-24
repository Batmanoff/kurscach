@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Swaga — запуск
echo.
echo  Запуск Swaga...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
if errorlevel 1 pause
