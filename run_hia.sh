#!/bin/bash

echo "🏥 Starting HIA - Health Insights Agent"
echo "======================================"
echo ""

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating one now..."
    python -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check dependencies
echo "🔍 Checking dependencies..."
python -c "import streamlit" 2>/dev/null || pip install streamlit
python -c "import google.generativeai" 2>/dev/null || pip install google-generativeai
python -c "import PyPDF2" 2>/dev/null || pip install PyPDF2
python -c "import PIL" 2>/dev/null || pip install pillow

echo ""
echo "✅ Dependencies ready!"
echo ""

# Clear any cache issues
echo "🧹 Clearing cache..."
rm -rf ~/.streamlit/cache 2>/dev/null
rm -rf temp_* 2>/dev/null

# Instructions
echo "📋 IMPORTANT INSTRUCTIONS:"
echo "=========================="
echo ""
echo "1. The app will open in your browser"
echo "2. Look for the LEFT SIDEBAR"
echo "3. Enter your Gemini API key there"
echo "4. Click 'Set API Key' button"
echo "5. Upload test_document.txt to test"
echo ""
echo "🔑 No API key? Get one free at:"
echo "   https://makersuite.google.com/app/apikey"
echo ""
echo "Starting app in 3 seconds..."
sleep 3

# Run the fixed app
streamlit run src/app_fixed.py