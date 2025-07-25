# HIA Setup Instructions

Since you don't have conda installed, here are two ways to set up HIA:

## Option 1: Using the Setup Script (Recommended)

```bash
# Run the setup script
./setup.sh

# After setup completes:
source venv/bin/activate
export GEMINI_API_KEY=your_api_key_here
python src/main.py web
```

## Option 2: Manual Setup with pip

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
# venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data temp reports logs

# Set your Gemini API key
export GEMINI_API_KEY=your_api_key_here

# Run the application
python src/main.py web
```

## System Dependencies

You'll also need to install these system dependencies:

### For OCR functionality (optional):
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
```

### For PDF processing (optional):
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

## Quick Start

1. **Clone the repository** (if not already done)
2. **Run setup**: `./setup.sh`
3. **Activate environment**: `source venv/bin/activate`
4. **Set API key**: `export GEMINI_API_KEY=your_key`
5. **Start app**: `python src/main.py web`
6. **Open browser**: http://localhost:8501

## Troubleshooting

- If you get permission errors, try: `chmod +x setup.sh`
- If Python 3 is not found, install it from python.org
- For Windows users, use `python` instead of `python3`

## Demo Mode

You can try the app in demo mode without an API key:
1. Run the app
2. Click "Try Demo" on the login screen
3. Note: Some features will be limited without an API key