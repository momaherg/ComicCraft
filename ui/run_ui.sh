#!/bin/bash
# Launcher script for ComicCraft AI Testing UI

echo "========================================"
echo "ComicCraft AI - Testing Interface"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env with GEMINI_API_KEY=your_key"
    exit 1
fi

# Run the UI
echo "Starting Gradio interface..."
echo "Access at: http://localhost:7860"
echo ""
python ui/gradio_app.py
