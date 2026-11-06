#!/usr/bin/env bash
# ====================================================================
# FigCraft to Bootstrap 5 + FontAwesome - Direct Exporter Runner
# Author: uzielweb (https://github.com/uzielweb)
# ====================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "===================================================================="
echo " FigCraft to Bootstrap 5 + FontAwesome Exporter Engine"
echo "===================================================================="
echo ""

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERRO] Python 3 não foi encontrado no PATH."
    echo "Por favor instale o Python 3.10+."
    exit 1
fi

if [ -z "$1" ]; then
    echo "[Modo Automático] Detectando documento ativo no FigCraft..."
    python3 "$SCRIPT_DIR/exporter.py"
else
    echo "[Modo Direto] Exportando arquivo fornecido: $@"
    python3 "$SCRIPT_DIR/exporter.py" "$@"
fi

echo ""
