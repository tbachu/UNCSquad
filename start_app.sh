#!/bin/bash

# Health Insights Agent (HIA) Startup Script

echo "🏥 Starting Health Insights Agent (HIA)..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Gemini API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "⚠️  GEMINI_API_KEY not set in environment"
    echo ""
    echo "You can:"
    echo "1. Set it now: export GEMINI_API_KEY='your-api-key'"
    echo "2. Or enter it in the app's login screen"
    echo ""
else
    echo "✅ GEMINI_API_KEY is configured"
fi

# Run the app
echo ""
echo "🚀 Launching HIA..."
echo "----------------------------------------"
echo "Access the app at: http://localhost:8501"
echo "Press Ctrl+C to stop"
echo "----------------------------------------"
echo ""

streamlit run src/main.py