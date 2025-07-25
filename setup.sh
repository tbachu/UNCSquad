#!/bin/bash

# Setup script for HIA - Health Insights Agent

echo "🏥 Setting up HIA - Health Insights Agent..."
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p data temp reports logs data/health_memory data/security

# Check for system dependencies
echo ""
echo "⚠️  System Dependencies Check:"
echo "--------------------------------"

# Check for Tesseract (for OCR)
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR is installed"
else
    echo "❌ Tesseract OCR is NOT installed"
    echo "   For macOS: brew install tesseract"
    echo "   For Ubuntu: sudo apt-get install tesseract-ocr"
fi

# Check for poppler (for PDF to image conversion)
if command -v pdfinfo &> /dev/null; then
    echo "✅ Poppler is installed"
else
    echo "❌ Poppler is NOT installed"
    echo "   For macOS: brew install poppler"
    echo "   For Ubuntu: sudo apt-get install poppler-utils"
fi

echo ""
echo "🔑 API Key Setup:"
echo "-----------------"
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY is not set"
    echo "   Please set it with: export GEMINI_API_KEY=your_api_key_here"
else
    echo "✅ GEMINI_API_KEY is set"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run HIA:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set your Gemini API key: export GEMINI_API_KEY=your_api_key_here"
echo "3. Run the app: python src/main.py web"
echo ""
echo "The app will be available at http://localhost:8501"