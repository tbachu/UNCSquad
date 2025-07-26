import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
import PyPDF2
from PIL import Image
import pytesseract
import re
from datetime import datetime

# Page config
st.set_page_config(
    page_title="HIA - Health Insights Agent",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('GEMINI_API_KEY', '')
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []

# Title
st.title("🏥 HIA - Health Insights Agent")
st.markdown("Your AI-powered health document analyzer")

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Settings")
    
    api_key = st.text_input(
        "Gemini API Key",
        value=st.session_state.api_key,
        type="password",
        help="Get your API key from https://makersuite.google.com/app/apikey"
    )
    
    if api_key:
        st.session_state.api_key = api_key
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured")
    else:
        st.warning("⚠️ Please enter your Gemini API key")
    
    st.markdown("---")
    st.markdown("### 📚 How to use:")
    st.markdown("1. Enter your Gemini API key above")
    st.markdown("2. Upload a medical document")
    st.markdown("3. Get instant AI analysis!")

# Main area tabs
tab1, tab2, tab3 = st.tabs(["📄 Document Analysis", "💬 Q&A Chat", "📊 Results History"])

# Document Analysis Tab
with tab1:
    st.header("Upload Medical Document")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
        help="Upload lab reports, prescriptions, or medical records"
    )
    
    if uploaded_file and st.session_state.api_key:
        if st.button("🔍 Analyze Document", type="primary"):
            with st.spinner("Analyzing document..."):
                try:
                    # Extract text based on file type
                    text = ""
                    
                    if uploaded_file.type == "application/pdf":
                        # PDF extraction
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                    
                    elif uploaded_file.type.startswith("image"):
                        # Image OCR
                        image = Image.open(uploaded_file)
                        try:
                            text = pytesseract.image_to_string(image)
                        except:
                            st.error("⚠️ OCR not available. Please install Tesseract.")
                            st.stop()
                    
                    else:
                        # Text file
                        text = str(uploaded_file.read(), "utf-8")
                    
                    # Extract health metrics using regex
                    st.subheader("📊 Extracted Health Metrics")
                    
                    # Common patterns
                    patterns = {
                        'Glucose': r'(?:Glucose|GLU)[:\s]+([\d.]+)\s*(mg/dL)?',
                        'Cholesterol': r'(?:Cholesterol)[:\s]+([\d.]+)\s*(mg/dL)?',
                        'Blood Pressure': r'(?:Blood Pressure|BP)[:\s]+([\d/]+)\s*(mmHg)?',
                        'Hemoglobin': r'(?:Hemoglobin|Hgb)[:\s]+([\d.]+)\s*(g/dL)?',
                    }
                    
                    metrics = {}
                    for name, pattern in patterns.items():
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            metrics[name] = match.group(1)
                    
                    if metrics:
                        # Display metrics
                        cols = st.columns(len(metrics))
                        for i, (name, value) in enumerate(metrics.items()):
                            cols[i].metric(name, value)
                    else:
                        st.info("No standard metrics found. See AI analysis below.")
                    
                    # AI Analysis
                    st.subheader("🤖 AI Analysis")
                    
                    # Initialize Gemini
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Analyze this medical document and provide:
                    1. Document type and purpose
                    2. Key health metrics and their values
                    3. Whether any values are abnormal
                    4. Simple explanation for the patient
                    5. Recommendations
                    
                    Document text:
                    {text[:4000]}  # Limit to avoid token limits
                    
                    Provide a clear, patient-friendly summary.
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # Display response
                    st.markdown(response.text)
                    
                    # Save to history
                    result = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'filename': uploaded_file.name,
                        'metrics': metrics,
                        'analysis': response.text
                    }
                    st.session_state.analysis_results.append(result)
                    
                    st.success("✅ Analysis complete!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.error("Please check your API key and try again.")
    
    elif uploaded_file and not st.session_state.api_key:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar first!")

# Q&A Chat Tab
with tab2:
    st.header("Health Q&A Chat")
    
    if st.session_state.api_key:
        # Chat interface
        user_question = st.text_input("Ask a health question:", placeholder="e.g., What is a normal glucose level?")
        
        if user_question:
            with st.spinner("Thinking..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Add context from previous analyses
                    context = ""
                    if st.session_state.analysis_results:
                        latest = st.session_state.analysis_results[-1]
                        context = f"\nContext from recent analysis: {latest['metrics']}"
                    
                    prompt = f"""
                    You are a helpful health assistant. Answer this question clearly and accurately:
                    
                    Question: {user_question}
                    {context}
                    
                    Provide a helpful, easy-to-understand answer. Always remind users to consult healthcare providers for medical decisions.
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # Display response
                    st.markdown("### Answer:")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar to use the chat feature!")

# Results History Tab
with tab3:
    st.header("Analysis History")
    
    if st.session_state.analysis_results:
        for result in reversed(st.session_state.analysis_results):
            with st.expander(f"📄 {result['filename']} - {result['timestamp']}"):
                st.markdown("**Extracted Metrics:**")
                for name, value in result['metrics'].items():
                    st.write(f"- {name}: {value}")
                
                st.markdown("**AI Analysis:**")
                st.markdown(result['analysis'])
    else:
        st.info("No analyses yet. Upload a document to get started!")

# Footer
st.markdown("---")
st.markdown("⚠️ **Disclaimer**: This app is for informational purposes only. Always consult with healthcare professionals for medical advice.")