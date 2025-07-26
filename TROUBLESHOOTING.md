# HIA Troubleshooting Guide

## Common Issues and Solutions

### 1. "Nothing on this website works"

If you're experiencing issues with the app not functioning properly, follow these steps:

#### Step 1: Check Gemini API Key
- **Problem**: Most features require a valid Gemini API key
- **Solution**: 
  1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
  2. Enter it in the login screen under "Setup Gemini API Key"
  3. Click "Save API Key" then "Try Demo"

#### Step 2: Verify Installation
Run the debug script to check all components:
```bash
source venv/bin/activate
python debug_test.py
```

All items should show ✅. If any show ❌, see specific fixes below.

#### Step 3: Check Browser Console
- Open browser developer tools (F12)
- Check Console tab for errors
- Try hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

### 2. Document Upload Not Working

#### For Images (PNG, JPG, etc):
- **Problem**: "Tesseract OCR is required but not installed"
- **Solution**:
  ```bash
  # macOS
  brew install tesseract
  
  # Ubuntu/Debian
  sudo apt-get install tesseract-ocr
  
  # Windows
  # Download from: https://github.com/UB-Mannheim/tesseract/wiki
  ```

#### For PDFs:
- Try uploading a text-based PDF (not scanned image)
- For scanned PDFs, install Tesseract (see above)

### 3. Chat/Q&A Not Working

#### "Please set up your Gemini API key"
- Enter API key in login screen
- Make sure it's a valid key from Google AI Studio

#### "API key not valid"
- Check your API key is correct
- Ensure you have API access enabled in Google Cloud Console
- Try generating a new key

#### "Quota exceeded"
- Free tier has limits (60 requests per minute)
- Wait a few minutes and try again
- Consider upgrading to paid tier

### 4. App Won't Start

#### "ModuleNotFoundError"
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

#### "Address already in use"
```bash
# Kill existing Streamlit process
pkill -f streamlit
# Or use a different port
streamlit run src/main.py --server.port 8502
```

### 5. Features Not Working as Expected

#### Document Analysis
- **What works**: 
  - Text extraction from PDFs, images, Word docs
  - Basic lab value extraction
  - Metadata extraction (dates, patient names)
  
- **Limitations**:
  - Complex medical forms may not parse perfectly
  - Handwritten text requires good quality images
  - Some medical abbreviations may not be recognized

#### Health Q&A
- **What works**:
  - General health questions
  - Explanations of medical terms
  - Analysis of uploaded documents
  
- **Limitations**:
  - Cannot provide medical diagnoses
  - Limited to general health information
  - Requires context from uploaded documents for specific insights

#### Trends & Analytics
- **Note**: Requires historical data to be meaningful
- Upload multiple documents over time to see trends

### 6. Quick Fixes

#### Reset the app:
```bash
# Clear Streamlit cache
streamlit cache clear

# Remove temporary files
rm -rf temp_*
rm -rf data/health_memory/chroma

# Restart
./start_app.sh
```

#### Test with sample data:
1. Use the provided `test_document.txt`
2. Upload it in Document Analysis tab
3. Should extract glucose, cholesterol, blood pressure values

### 7. Getting Help

If issues persist:
1. Run `python debug_test.py` and share the output
2. Check browser console for errors
3. Try with a different browser
4. Make sure you're using a modern browser (Chrome, Firefox, Safari, Edge)

### 8. Known Limitations

1. **OCR Quality**: Image text extraction depends on image quality
2. **API Limits**: Free Gemini API has rate limits
3. **Browser Compatibility**: Works best in Chrome/Firefox
4. **File Size**: Large files (>10MB) may take time to process
5. **Complex Documents**: Highly formatted medical forms may not parse perfectly

### 9. Performance Tips

1. **Use text PDFs** instead of scanned images when possible
2. **Upload clear, high-resolution** images for OCR
3. **Keep documents under 5MB** for faster processing
4. **Use specific questions** in the Q&A for better responses
5. **Allow time for processing** - document analysis can take 10-30 seconds

### 10. Development Mode

For developers wanting to see more details:
```bash
# Run with debug logging
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run src/main.py
```

---

Still having issues? The app's core functionality includes:
- ✅ Document upload and text extraction
- ✅ Health metric extraction from documents  
- ✅ AI-powered Q&A (with valid API key)
- ✅ Secure local data storage
- ✅ Multi-language support (through Gemini)

Make sure you have a valid Gemini API key for AI features!