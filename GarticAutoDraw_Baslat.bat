@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Gartic AutoDraw AI Studio Pro
cd /d "%~dp0"
echo ========================================================
echo   ⚡ GARTIC AUTODRAW AI STUDIO PRO BASLATILIYOR...
echo ========================================================
python main.py
if errorlevel 1 (
    echo.
    echo Bir hata olustu.
    pause
)
