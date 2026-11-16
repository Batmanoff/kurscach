@echo off
chcp 65001 >nul
cd /d "%~dp0"
title ATELIER — запуск
echo.
echo  Запуск ATELIER (курсовая)...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
if errorlevel 1 pause
