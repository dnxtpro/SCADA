#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "=========================================="
echo "  SCADA - Instalacion y Ejecucion Linux"
echo "=========================================="

if [[ ! -f "requirements.txt" ]]; then
  echo "[ERROR] No se encontro requirements.txt en la carpeta actual."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] Python3 no esta instalado o no esta en PATH."
  echo "Instala Python 3.10+ e intenta de nuevo."
  exit 1
fi

echo "[INFO] Usando: $(command -v python3)"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "[INFO] Creando entorno virtual..."
  python3 -m venv .venv
fi

echo "[INFO] Activando entorno virtual..."
# shellcheck disable=SC1091
source .venv/bin/activate

echo "[INFO] Actualizando pip..."
python -m pip install --upgrade pip

echo "[INFO] Instalando dependencias..."
python -m pip install -r requirements.txt

echo "[INFO] Iniciando aplicacion SCADA..."
python main.py
