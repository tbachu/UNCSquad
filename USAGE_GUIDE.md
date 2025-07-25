# 🏥 HIA - Health Insights Agent Usage Guide

## Quick Start

1. **Launch the app:**
   ```bash
   python src/main.py web
   ```

2. **Access the app:** Open http://localhost:8501 in your browser

3. **Login:** Click "Try Demo" to start using the app immediately

## 📄 Document Analysis

### Supported File Types
- **PDF files** (.pdf) - Lab reports, prescriptions, medical records
- **Images** (.png, .jpg, .jpeg, .tiff, .bmp) - Scanned documents, photos of reports
- **Word documents** (.docx) - Digital medical records
- **Text files** (.txt) - Plain text medical reports

### How to Upload and Analyze

1. **Go to the "Document Analysis" tab**
2. **Upload your medical document** using the file uploader
3. **Click "🔍 Analyze Document"**
4. **View results** - The app will extract:
   - Medical values (blood pressure, glucose, cholesterol, etc.)
   - Patient information (name, dates, doctor)
   - Document sections (lab results, medications, etc.)
   - AI-powered analysis and recommendations

### ✅ What Works Best

- **High-quality scans** - Clear, well-lit images work better
- **Standard medical formats** - Lab reports, prescriptions, discharge summaries
- **Text-based PDFs** - Digital documents are processed faster than scanned ones

### ⚠️ Troubleshooting

If document analysis fails:

1. **Check file format** - Make sure it's a supported type
2. **Try better quality** - Re-scan blurry or low-quality images
3. **Check file size** - Very large files may take longer to process
4. **Look at debugging info** - Click the 🔧 Debugging Information section for system status

## 💬 Health Q&A

Ask questions about your health data:
- "What do my recent lab results mean?"
- "Are my cholesterol levels normal?"
- "Show me my blood pressure trends"
- "What medications am I taking?"

## 📊 Dashboard

View your health overview:
- Key metrics at a glance
- Health scores and trends
- Recent insights and recommendations
- Upcoming appointments and reminders

## 🔧 System Requirements

### Required Dependencies (Auto-installed)
- Python 3.8+
- Streamlit
- Google Gemini API
- PyPDF2, Pillow, python-docx

### System Dependencies
- **Tesseract OCR** - For reading images and scanned documents
  ```bash
  # macOS
  brew install tesseract
  
  # Linux
  sudo apt-get install tesseract-ocr
  ```

## 🔑 API Setup

1. **Get a Gemini API key** from Google AI Studio
2. **Set it in the login screen** or as an environment variable:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```

## 📋 Tips for Best Results

1. **Scan documents clearly** - Good lighting, no shadows
2. **Keep originals upright** - Don't rotate or skew documents
3. **Use high resolution** - At least 300 DPI for scanned images
4. **Name files descriptively** - "Lab_Results_2024_01_15.pdf"
5. **Upload recent reports first** - The app learns from your data

## 🆘 Getting Help

If you encounter issues:

1. **Check the debugging panel** in the Document Analysis tab
2. **Look at system dependencies** - Make sure Tesseract is installed
3. **Try different file formats** - Convert images to PDF if needed
4. **Refresh the page** after installing dependencies

## 🔒 Privacy & Security

- Your documents are processed locally when possible
- API calls to Gemini are made over secure connections
- No health data is permanently stored without your consent
- Always review AI-generated insights with your healthcare provider

---

**Remember:** This app is a tool to help you understand your health data. Always consult with healthcare professionals for medical decisions. 