# 🏥 HIA Quick Start Guide

## Step 1: Get Gemini API Key (Required)

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with "AIza...")

## Step 2: Start the App

```bash
# In terminal:
cd UNCSquad
source venv/bin/activate
streamlit run src/main.py
```

Or use the simple version directly:
```bash
streamlit run src/simple_app.py
```

## Step 3: Configure API Key

In the app:
1. Look at the **left sidebar**
2. Find "Gemini API Key" field
3. Paste your API key
4. You should see "✅ API Key configured"

## Step 4: Test Document Analysis

1. Click on **"📄 Document Analysis"** tab
2. Click **"Browse files"** button
3. Select **test_document.txt** from your folder
4. Click **"🔍 Analyze Document"** button
5. Wait for results!

## What Should Happen:

✅ You'll see extracted metrics:
- Glucose: 95
- Cholesterol: 180
- Blood Pressure: 120/80
- Hemoglobin: 14.5

✅ You'll see AI analysis explaining the document

## Step 5: Test Q&A Chat

1. Click on **"💬 Q&A Chat"** tab
2. Type a question like: "What is a normal glucose level?"
3. Press Enter
4. Get AI-powered answer!

## If Nothing Works:

### Check #1: API Key
- Make sure you entered the API key in sidebar
- Make sure it's the complete key (40+ characters)
- Try generating a new key if needed

### Check #2: Dependencies
Run this test:
```bash
python test_simple.py
```

All items should show ✅

### Check #3: Try Direct Test
```python
# In Python:
import google.generativeai as genai

genai.configure(api_key='YOUR_API_KEY_HERE')
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Hello")
print(response.text)
```

This should print a response.

## Still Not Working?

1. **Clear everything and restart:**
```bash
# Kill any running streamlit
pkill -f streamlit

# Clear cache
rm -rf ~/.streamlit/cache

# Restart
streamlit run src/simple_app.py
```

2. **Check browser console:**
- Press F12 in browser
- Look for red errors
- Try different browser

3. **Use simple test:**
```bash
# This opens a minimal working version
streamlit run src/simple_app.py
```

## Working Features:

The app now has these working features:
1. ✅ Document upload (PDF, images, text)
2. ✅ Text extraction from documents
3. ✅ Health metric extraction (glucose, cholesterol, etc.)
4. ✅ AI-powered document analysis
5. ✅ Q&A chat for health questions
6. ✅ Analysis history

## Important Notes:

- **API Key Required**: Nothing works without a valid Gemini API key
- **Internet Required**: For AI features
- **OCR Optional**: For image files, install Tesseract if needed

---

**The app is now simplified and should work!** Just follow steps 1-4 above.