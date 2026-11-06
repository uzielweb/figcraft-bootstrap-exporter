@echo off
setlocal EnableDelayedExpansion
chcp 65001 > nul
title FigCraft Exporter - Instalador Oficial (Windows)

echo ====================================================================
echo  FigCraft to Bootstrap 5 + FontAwesome - Instalador Poka-Yoke
echo ====================================================================
echo.

set "TARGET_DIR=%APPDATA%\FigCraft\plugins\figcraft-bootstrap-exporter"

echo [1/5] Preparando diretorio seguro de plugins...
if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
)

echo [2/5] Copiando modulo nativo Rust/WASM e manifestos...
copy /Y "%~dp0plugin.wasm" "%TARGET_DIR%\" > nul
copy /Y "%~dp0figcraft-plugin.json" "%TARGET_DIR%\" > nul
copy /Y "%~dp0exporter.py" "%TARGET_DIR%\" > nul
copy /Y "%~dp0exportar.bat" "%TARGET_DIR%\" > nul
copy /Y "%~dp0README.md" "%TARGET_DIR%\" > nul

echo [3/5] Habilitando conexao permanente do FigCraft (Porta 7987)...
setx FIGCRAFT_CONTROL_PORT 7987 > nul

echo [4/5] Registrando plugin nativo WASM no state.json do FigCraft...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$statePath = Join-Path $env:APPDATA 'FigCraft\state.json'; $manifestPath = Join-Path $env:APPDATA 'FigCraft\plugins\figcraft-bootstrap-exporter\figcraft-plugin.json'; if (Test-Path $statePath) { try { $json = Get-Content $statePath -Raw -Encoding UTF8 | ConvertFrom-Json; if ($null -eq $json.prefs.plugins) { $json.prefs | Add-Member -MemberType NoteProperty -Name 'plugins' -Value @() -Force }; $exists = $json.prefs.plugins | Where-Object { $_.manifest.id -eq 'io.github.uzielweb.bootstrap-exporter' }; $manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json; $entry = [PSCustomObject]@{ manifest = $manifest; path = $manifestPath }; if (-not $exists) { $json.prefs.plugins += $entry; } else { for ($i = 0; $i -lt $json.prefs.plugins.Count; $i++) { if ($json.prefs.plugins[$i].manifest.id -eq 'io.github.uzielweb.bootstrap-exporter') { $json.prefs.plugins[$i] = $entry } } }; $utf8NoBom = [System.Text.UTF8Encoding]::new($false); [System.IO.File]::WriteAllText($statePath, ($json | ConvertTo-Json -Depth 20), $utf8NoBom); } catch {} }"

echo [5/5] Criando atalho auxiliar do Python na Area de Trabalho...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$py = (Get-Command python.exe -ErrorAction SilentlyContinue).Source; if (-not $py) { $py = 'python.exe' }; $script = Join-Path $env:APPDATA 'FigCraft\plugins\figcraft-bootstrap-exporter\exporter.py'; $figExe = 'C:\Program Files\FigCraft\figcraft.exe'; $ws = New-Object -ComObject WScript.Shell; $desktop = [Environment]::GetFolderPath('Desktop'); $shortcut = $ws.CreateShortcut((Join-Path $desktop 'Exportar FigCraft para Bootstrap.lnk')); $shortcut.TargetPath = $py; $shortcut.Arguments = '\"' + $script + '\"'; $shortcut.WorkingDirectory = Join-Path $env:APPDATA 'FigCraft\plugins\figcraft-bootstrap-exporter'; if (Test-Path $figExe) { $shortcut.IconLocation = $figExe + ',0' }; $shortcut.Description = 'Exportador Oficial Bootstrap 5 & FontAwesome para FigCraft'; $shortcut.Save();"

echo.
echo ====================================================================
echo  OK: INSTALACAO CONCLUIDA COM SUCESSO!
echo ====================================================================
echo.
echo O plugin nativo Rust/WASM foi registrado diretamente no seu FigCraft!
echo.
echo Como usar diretamente dentro do FigCraft:
echo   1. Abra qualquer projeto no FigCraft.
echo   2. Clique no menu 'Plugins' -> 'Bootstrap 5 & FontAwesome Exporter'
echo      -> 'Exportar para Bootstrap 5 & FontAwesome...'.
echo   3. A janela nativa de Salvar Arquivo abrira para voce salvar o
echo      'index.html' gerado com todas as classes CSS, Bootstrap 5 e icones!
echo.
