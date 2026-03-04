#!/bin/bash

echo "🚀 Avvio procedura Setup SquadraCorse..."

# 1. Navigazione e Git
cd ~/SquadraCorse || exit
echo "--- Aggiornamento Git ---"
git pull
git checkout TestCostamagna

# 2. Ambiente Virtuale
if [ ! -d ".venv" ]; then
    echo "--- Creazione ambiente virtuale ---"
    python3 -m venv .venv
fi

echo "--- Attivazione ambiente ---"
source .venv/bin/activate

# 3. Esecuzione
echo "--- Avvio main.py ---"
cd Python/src
python main.py