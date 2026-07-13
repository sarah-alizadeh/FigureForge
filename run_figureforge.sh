#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "Stopping old FigureForge and Streamlit processes..."
pkill -f "streamlit run" 2>/dev/null || true
pkill -f "python.*streamlit" 2>/dev/null || true

sleep 1

echo "Removing Python and Streamlit caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
rm -rf .streamlit/cache 2>/dev/null || true

if grep -q "hero-title" app.py; then
    echo ""
    echo "ERROR: app.py still contains the broken old HTML."
    echo "Remove every occurrence of hero-title before running."
    echo ""
    grep -n "hero-title" app.py
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing required packages..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet streamlit pandas numpy matplotlib scipy

echo "Starting the clean FigureForge app..."
python3 -m streamlit run app.py
