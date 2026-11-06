@echo off
setlocal
chcp 65001 > nul
title FigCraft - Exportador Bootstrap 5 e FontAwesome

echo ====================================================================
echo  FigCraft to Bootstrap 5 e FontAwesome Exporter Engine
echo ====================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Python nao foi encontrado no seu PATH.
    echo Por favor instale o Python 3.10+ e marque 'Add python.exe to PATH'.
    echo.
    pause
    exit /b 1
)

if "%~1"=="" (
    python "%~dp0exporter.py"
) else (
    python "%~dp0exporter.py" "%~1"
)
