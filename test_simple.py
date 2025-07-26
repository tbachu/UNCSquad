#!/usr/bin/env python3
"""Test script for simple HIA app"""

import os
import sys

print("🏥 Testing HIA Simple App Setup\n")

# Test imports
print("1. Testing imports...")
try:
    import streamlit
    print("✅ Streamlit imported")
except:
    print("❌ Streamlit not installed - run: pip install streamlit")

try:
    import google.generativeai as genai
    print("✅ Google Generative AI imported")
except:
    print("❌ Google Generative AI not installed - run: pip install google-generativeai")

try:
    import PyPDF2
    print("✅ PyPDF2 imported")
except:
    print("❌ PyPDF2 not installed - run: pip install PyPDF2")

try:
    from PIL import Image
    print("✅ PIL imported")
except:
    print("❌ PIL not installed - run: pip install pillow")

try:
    import pytesseract
    print("✅ Pytesseract imported")
    # Test if tesseract binary is available
    try:
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR binary found")
    except:
        print("⚠️  Tesseract OCR binary not found - install with: brew install tesseract")
except:
    print("❌ Pytesseract not installed - run: pip install pytesseract")

# Test API key
print("\n2. Testing API Key...")
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print("✅ GEMINI_API_KEY found in environment")
    # Test if key works
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'API working' in 3 words")
        print("✅ API Key is valid and working!")
    except Exception as e:
        print(f"❌ API Key error: {str(e)}")
else:
    print("⚠️  GEMINI_API_KEY not set")
    print("   Set it with: export GEMINI_API_KEY='your-key'")
    print("   Or enter it in the app interface")

# Test file
print("\n3. Testing sample file...")
if os.path.exists("test_document.txt"):
    print("✅ test_document.txt found")
else:
    print("⚠️  test_document.txt not found")

print("\n✨ Setup test complete!")
print("\nTo run the simple app:")
print("streamlit run src/simple_app.py")