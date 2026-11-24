@echo off
chcp 65001 >nul
cd /d "%~dp0"
title BAST — остановка
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop.ps1"
pause
