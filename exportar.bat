@echo off
chcp 65001 > nul
title FigCraft - Exportador Bootstrap 5 & FontAwesome
echo ====================================================================
echo  FigCraft to Bootstrap 5 + FontAwesome Exporter Engine
echo ====================================================================
echo.
echo [1/2] Conectando ao FigCraft ativo (porta 7987)...
echo [2/2] Abrindo navegador de arquivos para escolher a pasta de destino...
echo.
python "%~dp0exporter.py" --browse
echo.
pause
