#!/usr/bin/env python3
"""
Quick fix script for common HIA issues
"""

import os
import sys
import shutil
from pathlib import Path

def fix_imports():
    """Fix import issues by updating sys.path"""
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    print("✅ Fixed import paths")

def clear_cache():
    """Clear Streamlit cache and temporary files"""
    # Clear temp files
    temp_files = list(Path('.').glob('temp_*'))
    for f in temp_files:
        try:
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                shutil.rmtree(f)
        except:
            pass
    
    # Clear ChromaDB if it exists
    chroma_path = Path('data/health_memory/chroma')
    if chroma_path.exists():
        try:
            shutil.rmtree(chroma_path)
            print("✅ Cleared ChromaDB cache")
        except:
            print("⚠️  Could not clear ChromaDB cache")
    
    print("✅ Cleared temporary files")

def check_dependencies():
    """Check and install missing dependencies"""
    required = [
        'streamlit',
        'google-generativeai',
        'chromadb',
        'PyPDF2',
        'pillow',
        'pytesseract',
        'python-docx',
        'plotly',
        'pandas'
    ]
    
    print("Checking dependencies...")
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install " + ' '.join(missing))
    else:
        print("✅ All dependencies installed")

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    if shutil.which('tesseract'):
        print("✅ Tesseract OCR is installed")
    else:
        print("⚠️  Tesseract OCR not found")
        print("   Install with:")
        print("   - macOS: brew install tesseract")
        print("   - Linux: sudo apt-get install tesseract-ocr")

def check_api_key():
    """Check if Gemini API key is set"""
    if os.getenv('GEMINI_API_KEY'):
        print("✅ GEMINI_API_KEY is set in environment")
    else:
        print("⚠️  GEMINI_API_KEY not set")
        print("   Set it with: export GEMINI_API_KEY='your-key'")
        print("   Or enter it in the app's login screen")

def create_directories():
    """Ensure all required directories exist"""
    dirs = [
        'data',
        'data/health_memory',
        'temp',
        'reports'
    ]
    
    for d in dirs:
        Path(d).mkdir(exist_ok=True, parents=True)
    
    print("✅ Created required directories")

def main():
    print("🏥 HIA Quick Fix Script\n")
    
    # Run all fixes
    fix_imports()
    clear_cache()
    create_directories()
    check_dependencies()
    check_tesseract()
    check_api_key()
    
    print("\n✨ Fixes applied!")
    print("\nNext steps:")
    print("1. Make sure you have a Gemini API key")
    print("2. Run: ./start_app.sh")
    print("3. Upload test_document.txt to test")
    
if __name__ == "__main__":
    main()