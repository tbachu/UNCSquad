# HIA (Health Insights Agent) 🏥

## Description

HIA is your personal AI health analyst. It securely analyzes your medical documents—lab results, doctor's notes, prescriptions, and more—then delivers clear, actionable insights, tracks your health trends, and empowers you to make better health decisions every day.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))
- (Optional) Tesseract OCR for image processing

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd UNCSquad
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies

Core dependencies include:
- `streamlit>=1.28.0` - Web interface
- `google-generativeai>=0.8.0` - Gemini AI integration
- `PyPDF2>=3.0.0` - PDF processing
- `pillow>=10.0.0` - Image processing
- `pytesseract>=0.3.10` - OCR capabilities
- `chromadb>=0.4.0` - Vector storage
- `python-docx>=0.8.11` - Word document processing
- `plotly>=5.17.0` - Data visualization
- `pandas>=2.0.0` - Data manipulation
- `cryptography>=41.0.0` - Security features

Full list in `requirements.txt`

### How to Run

1. **Quick Start:**
   ```bash
   ./run_hia.sh
   ```

2. **Manual Start:**
   ```bash
   source venv/bin/activate
   streamlit run src/main.py
   ```
   
   This runs the latest version (v2) with full document-aware Q&A functionality.

3. **Access the app:**
   - Open browser to `http://localhost:8501`
   - Enter your Gemini API key in the sidebar
   - Upload medical documents
   - Get AI-powered analysis!

### Optional: Install OCR Support

For analyzing scanned documents and images:

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

## Key Features

### 1. Multi-Format Medical Report Analysis 📄
- Upload PDFs, images, or text from lab reports, prescriptions, radiology summaries, or visit notes.
- Gemini reads, extracts, and explains complex medical jargon in plain language.

### 2. Personalized Health Insights & Trends 📈
- Tracks your key health metrics over time (cholesterol, blood pressure, glucose, etc.).
- Visualizes trends and flags significant changes or out-of-range results.
- Offers contextual explanations: "Your cholesterol improved by 15% since last year. Here's what it means."

### 3. Proactive Health Reminders & Suggestions 💡
- Suggests follow-up questions for your doctor based on new test results or changes.
- Notifies you if a medication interaction or missing vaccination is detected (using public drug/safety databases).

### 4. Privacy-First & Secure 🔒
- All data is encrypted and analyzed locally or with strong privacy guarantees.
- No data is shared without explicit user consent.

### 5. "Ask Anything" Health Q&A 💬
- Natural language chat to ask, "Is this test result serious?" or "What lifestyle changes can help with my diagnosis?"
- Gemini provides reliable, referenced information and guides you to trusted sources.

### 6. Doctor Visit Prep & Summaries ⚕️
- Generates a printable or shareable summary of recent health trends, medications, and questions for your next appointment.

### 7. Multi-Language Support 🌍
- Instantly translates medical explanations into the user's preferred language.

## Getting Started

### Prerequisites
- Python 3.8+
- Google Gemini API key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))
- Tesseract OCR (optional, for image text extraction)

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd UNCSquad
```

2. Set up virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. Run the application:
```bash
# Easy way
./start_app.sh

# Or manually
streamlit run src/main.py
```

4. Access the app at `http://localhost:8501`

5. In the app:
   - Click "Try Demo" to start
   - Go to Document Analysis tab
   - Upload a medical document (PDF, image, or text file)
   - Get instant AI-powered analysis!

### Setting Up Gemini API Key

**Option 1: In the app (Recommended)**
1. On the login screen, expand "🔑 Configure API Key"
2. Enter your Gemini API key
3. Click "Save API Key"

**Option 2: Environment variable**
```bash
export GEMINI_API_KEY='your-api-key-here'
```

### Installing OCR Support (Optional)

For analyzing scanned documents and images:

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

## Usage Guide

### 1. Document Analysis 📄
- **Upload** any medical document (lab reports, prescriptions, etc.)
- **Supported formats**: PDF, PNG, JPG, DOCX, TXT
- **What it does**:
  - Extracts health metrics (glucose, cholesterol, etc.)
  - Identifies patient information
  - Provides AI-powered summary
  - Explains medical terms in simple language

### 2. Health Q&A 💬
- **Ask** questions about your health
- **Examples**:
  - "What does my cholesterol level mean?"
  - "Should I be concerned about these results?"
  - "What lifestyle changes can improve my health?"
- **Note**: Requires Gemini API key for AI responses

### 3. Dashboard Overview 📊
- **View** your health metrics at a glance
- **Track** recent uploads and analyses
- **Monitor** health score and insights

### 4. Trends & Analytics 📈
- **Visualize** health metrics over time
- **Identify** patterns and improvements
- **Compare** results across different periods

### 5. Health Reports ⚕️
- **Generate** comprehensive health summaries
- **Prepare** for doctor visits
- **Export** reports as PDF

## Troubleshooting

Having issues? Check our [Troubleshooting Guide](TROUBLESHOOTING.md) for solutions to common problems.

### Quick Fixes:
- **"Nothing works"** → Make sure you have a Gemini API key
- **Upload fails** → Check file format and size (<10MB)
- **OCR error** → Install Tesseract for image processing
- **No AI responses** → Verify API key is valid

## Security & Privacy 🔐

- ✅ **Local Processing**: All data stays on your device
- ✅ **Encryption**: Documents encrypted at rest
- ✅ **Privacy First**: Only document text sent to Gemini for AI analysis
- ✅ **Session Security**: Secure session management
- ✅ **No Data Retention**: Gemini API doesn't store your health data

## Demo & Testing

Try the app with the included test document:

1. Start the app
2. Click "Try Demo"
3. Go to Document Analysis
4. Upload `test_document.txt`
5. See extracted health metrics!

## Requirements

Minimum system requirements:
- Python 3.8+
- 2GB RAM
- 500MB disk space
- Modern web browser
- Internet connection (for AI features)

## Project Structure

```
UNCSquad/
├── src/
│   ├── agent/           # Core agent logic (planner, executor, memory)
│   │   ├── planner.py   # Task planning with ReAct pattern
│   │   ├── executor.py  # Task execution engine
│   │   └── memory.py    # Health data persistence
│   ├── api/            # External API integrations
│   │   ├── gemini_client.py  # Google Gemini integration
│   │   └── health_apis.py    # Health data APIs
│   ├── ui/             # User interface
│   │   ├── streamlit_app.py  # Main app interface
│   │   └── components.py     # Reusable UI components
│   └── utils/          # Helper utilities
│       ├── document_parser.py # Multi-format document processing
│       ├── security.py        # Encryption and security
│       └── visualizations.py  # Health data charts
├── data/               # Local encrypted storage
├── .streamlit/         # Streamlit configuration
├── requirements.txt    # Python dependencies
├── run_hia.sh         # Quick start script
├── test_document.txt  # Sample medical document
├── ARCHITECTURE.md    # System design documentation
└── EXPLANATION.md     # Agent reasoning documentation
```

## Testing

1. **Test basic setup:**
   ```bash
   python test_simple.py
   ```

2. **Test Gemini API:**
   ```bash
   python test_gemini.py
   ```

3. **Debug components:**
   ```bash
   python debug_test.py
   ```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

Quick fixes:
- **API Key Issues**: Make sure to click "Set API Key" button after entering it
- **Black Screen**: Already fixed in the current version
- **Q&A Not Working**: Upload documents first, then ask specific questions
- **OCR Errors**: Install Tesseract for image processing

## Contributing

We welcome contributions! Please see our contributing guidelines for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for AI capabilities
- Streamlit for the web interface
- Open source community for various libraries
- Google Agentic AI Hackathon for inspiration

---

**Note**: HIA is not a replacement for professional medical advice. Always consult with qualified healthcare providers for medical decisions.