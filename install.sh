#!/usr/bin/env bash
# ====================================================================
# FigCraft to Bootstrap 5 + FontAwesome - Installer (macOS & Linux)
# Methodology: Poka-Yoke (Zero-Configuration / Foolproof)
# Author: uzielweb (https://github.com/uzielweb)
# ====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OS_TYPE="$(uname -s)"

echo "===================================================================="
echo " FigCraft to Bootstrap 5 + FontAwesome - Installer ($OS_TYPE)"
echo "===================================================================="
echo ""

# 1. Detect target plugin folder per OS standard
if [ "$OS_TYPE" = "Darwin" ]; then
    TARGET_DIR="$HOME/Library/Application Support/FigCraft/plugins/figcraft-bootstrap-exporter"
    CONFIG_DIR="$HOME/Library/Application Support/FigCraft"
    DESKTOP_DIR="$HOME/Desktop"
else
    # Linux (XDG Base Directory specification)
    XDG_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
    TARGET_DIR="$XDG_CONFIG/FigCraft/plugins/figcraft-bootstrap-exporter"
    CONFIG_DIR="$XDG_CONFIG/FigCraft"
    DESKTOP_DIR="$HOME/Desktop"
fi

echo "[1/5] Preparando diretório seguro de plugins..."
echo "      Destino: $TARGET_DIR"
mkdir -p "$TARGET_DIR"

echo "[2/5] Copiando arquivos do motor de exportação..."
cp -f "$SCRIPT_DIR/exporter.py" "$TARGET_DIR/"
cp -f "$SCRIPT_DIR/figcraft-plugin.json" "$TARGET_DIR/"
cp -f "$SCRIPT_DIR/plugin.wasm" "$TARGET_DIR/"
cp -f "$SCRIPT_DIR/README.md" "$TARGET_DIR/"
if [ -f "$SCRIPT_DIR/exportar.sh" ]; then
    cp -f "$SCRIPT_DIR/exportar.sh" "$TARGET_DIR/"
    chmod +x "$TARGET_DIR/exportar.sh"
fi

echo "[3/5] Configurando variável de ambiente (Porta 7987)..."
ENV_LINE='export FIGCRAFT_CONTROL_PORT=7987'
for RC_FILE in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile"; do
    if [ -f "$RC_FILE" ]; then
        if ! grep -q "FIGCRAFT_CONTROL_PORT" "$RC_FILE"; then
            echo "" >> "$RC_FILE"
            echo "# FigCraft Control Port" >> "$RC_FILE"
            echo "$ENV_LINE" >> "$RC_FILE"
        fi
    fi
done

echo "[4/5] Registrando extensão no state.json do FigCraft..."
STATE_FILE="$CONFIG_DIR/state.json"
MANIFEST_FILE="$TARGET_DIR/figcraft-plugin.json"
if [ -f "$STATE_FILE" ] && command -v python3 >/dev/null 2>&1; then
    python3 -c "
import json, os
state_path = '$STATE_FILE'
manifest_path = '$MANIFEST_FILE'
try:
    with open(state_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    prefs = data.setdefault('prefs', {})
    plugins = prefs.setdefault('plugins', [])
    if not any(p.get('manifest', {}).get('id') == 'io.github.uzielweb.bootstrap-exporter' for p in plugins):
        with open(manifest_path, 'r', encoding='utf-8') as mf:
            m = json.load(mf)
        plugins.append({'manifest': m, 'path': manifest_path})
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
except Exception:
    pass
" || true
fi

echo "[5/5] Criando atalho de 1 clique na Área de Trabalho..."
if [ "$OS_TYPE" = "Darwin" ]; then
    # macOS Command Launcher on Desktop
    SHORTCUT="$DESKTOP_DIR/Exportar FigCraft para Bootstrap.command"
    cat << 'EOF' > "$SHORTCUT"
#!/usr/bin/env bash
TARGET_DIR="$HOME/Library/Application Support/FigCraft/plugins/figcraft-bootstrap-exporter"
cd "$TARGET_DIR"
python3 "$TARGET_DIR/exporter.py" "$@"
read -p "Pressione ENTER para fechar..."
EOF
    chmod +x "$SHORTCUT"
else
    # Linux Desktop Entry (.desktop)
    if [ -d "$DESKTOP_DIR" ]; then
        SHORTCUT="$DESKTOP_DIR/figcraft-bootstrap-exporter.desktop"
        cat << EOF > "$SHORTCUT"
[Desktop Entry]
Version=1.0
Type=Application
Name=Exportar FigCraft para Bootstrap
Comment=Exporta telas do FigCraft para Bootstrap 5 e FontAwesome
Exec=python3 "$TARGET_DIR/exporter.py" %F
Icon=applications-development
Terminal=true
Categories=Development;Graphics;
EOF
        chmod +x "$SHORTCUT"
    fi
fi

echo ""
echo "===================================================================="
echo " ✓ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "===================================================================="
echo ""
echo "Um atalho foi criado na sua Área de Trabalho ($DESKTOP_DIR)."
echo "Basta abrir o FigCraft com o seu projeto e dar um clique duplo no atalho!"
echo ""
