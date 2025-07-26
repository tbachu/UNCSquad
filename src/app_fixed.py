import streamlit as st
import os
import google.generativeai as genai
from pathlib import Path
import PyPDF2
from PIL import Image
import pytesseract
import re
from datetime import datetime

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="HIA - Health Insights Agent",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state properly
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.api_key = os.getenv('GEMINI_API_KEY', '')
    st.session_state.api_key_set = False
    st.session_state.analysis_results = []

# Title
st.title("🏥 HIA - Health Insights Agent")
st.markdown("Your AI-powered health document analyzer")

# API Key Section - Using form to prevent rerun on enter
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Use a form to prevent page reload on enter
    with st.form("api_key_form"):
        api_key = st.text_input(
            "Gemini API Key",
            value=st.session_state.api_key,
            type="password",
            help="Get your API key from https://makersuite.google.com/app/apikey"
        )
        submit_button = st.form_submit_button("Set API Key")
        
        if submit_button and api_key:
            st.session_state.api_key = api_key
            st.session_state.api_key_set = True
            try:
                genai.configure(api_key=api_key)
                st.success("✅ API Key configured successfully!")
            except Exception as e:
                st.error(f"❌ Invalid API key: {str(e)}")
                st.session_state.api_key_set = False
    
    # Show status
    if st.session_state.api_key_set:
        st.success("✅ API Key is active")
    else:
        st.warning("⚠️ Please enter your Gemini API key above")
    
    st.markdown("---")
    st.markdown("### 📚 How to use:")
    st.markdown("1. Enter your Gemini API key above")
    st.markdown("2. Click 'Set API Key' button")
    st.markdown("3. Upload a medical document")
    st.markdown("4. Get instant AI analysis!")

# Configure Gemini if we have a key
if st.session_state.api_key and st.session_state.api_key_set:
    try:
        genai.configure(api_key=st.session_state.api_key)
    except:
        pass

# Main area tabs
tab1, tab2, tab3 = st.tabs(["📄 Document Analysis", "💬 Q&A Chat", "📊 Results History"])

# Document Analysis Tab
with tab1:
    st.header("Upload Medical Document")
    
    # Check if API key is set
    if not st.session_state.api_key_set:
        st.warning("⚠️ Please set your Gemini API key in the sidebar first!")
        st.stop()
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
        help="Upload lab reports, prescriptions, or medical records"
    )
    
    if uploaded_file:
        # Show file info
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📄 File: {uploaded_file.name}")
        with col2:
            st.info(f"📏 Size: {uploaded_file.size:,} bytes")
        
        if st.button("🔍 Analyze Document", type="primary", use_container_width=True):
            with st.spinner("Analyzing document..."):
                try:
                    # Extract text based on file type
                    text = ""
                    
                    if uploaded_file.type == "application/pdf":
                        # PDF extraction
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                        st.success("✅ PDF text extracted")
                    
                    elif uploaded_file.type.startswith("image"):
                        # Image OCR
                        image = Image.open(uploaded_file)
                        try:
                            text = pytesseract.image_to_string(image)
                            st.success("✅ Image text extracted with OCR")
                        except Exception as e:
                            st.error("⚠️ OCR not available. Please install Tesseract.")
                            st.code("brew install tesseract  # For macOS")
                            st.stop()
                    
                    else:
                        # Text file
                        text = str(uploaded_file.read(), "utf-8")
                        st.success("✅ Text file read")
                    
                    # Show extracted text preview
                    with st.expander("📝 View Extracted Text"):
                        st.text(text[:1000] + "..." if len(text) > 1000 else text)
                    
                    # Extract health metrics using regex
                    st.subheader("📊 Extracted Health Metrics")
                    
                    # Common patterns
                    patterns = {
                        'Glucose': r'(?:Glucose|GLU)[:\s]+([\d.]+)\s*(mg/dL)?',
                        'Cholesterol': r'(?:Cholesterol)[:\s]+([\d.]+)\s*(mg/dL)?',
                        'Blood Pressure': r'(?:Blood Pressure|BP)[:\s]+([\d/]+)\s*(mmHg)?',
                        'Hemoglobin': r'(?:Hemoglobin|Hgb)[:\s]+([\d.]+)\s*(g/dL)?',
                        'LDL': r'(?:LDL)[:\s]+([\d.]+)\s*(mg/dL)?',
                        'HDL': r'(?:HDL)[:\s]+([\d.]+)\s*(mg/dL)?',
                    }
                    
                    metrics = {}
                    for name, pattern in patterns.items():
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            metrics[name] = match.group(1)
                    
                    if metrics:
                        # Display metrics in a nice grid
                        cols = st.columns(min(len(metrics), 3))
                        for i, (name, value) in enumerate(metrics.items()):
                            cols[i % len(cols)].metric(name, value)
                    else:
                        st.info("No standard metrics found. See AI analysis below.")
                    
                    # AI Analysis
                    st.subheader("🤖 AI Analysis")
                    
                    # Initialize Gemini
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Limit text length to avoid token limits
                    text_for_analysis = text[:4000] if len(text) > 4000 else text
                    
                    prompt = f"""
                    Analyze this medical document and provide:
                    1. What type of medical document this is
                    2. Key health metrics and their values
                    3. Whether any values are abnormal (highlight concerns)
                    4. Simple explanation for the patient
                    5. Recommendations for the patient
                    
                    Document text:
                    {text_for_analysis}
                    
                    Provide a clear, patient-friendly summary. Use bullet points where appropriate.
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # Display response in a nice box
                    with st.container():
                        st.markdown(response.text)
                    
                    # Save to history
                    result = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'filename': uploaded_file.name,
                        'metrics': metrics,
                        'analysis': response.text
                    }
                    st.session_state.analysis_results.append(result)
                    
                    st.success("✅ Analysis complete! Check the Results History tab for saved results.")
                    
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.error("Please check your API key and try again.")
                    with st.expander("🐛 Debug Info"):
                        st.code(str(e))

# Q&A Chat Tab
with tab2:
    st.header("Health Q&A Chat")
    
    if st.session_state.api_key_set:
        # Recent context
        if st.session_state.analysis_results:
            with st.expander("📋 Recent Analysis Context"):
                latest = st.session_state.analysis_results[-1]
                st.write(f"From: {latest['filename']} ({latest['timestamp']})")
                if latest['metrics']:
                    st.write("Metrics:", latest['metrics'])
        
        # Chat interface - using form to prevent reload
        with st.form("chat_form", clear_on_submit=True):
            user_question = st.text_input(
                "Ask a health question:", 
                placeholder="e.g., What is a normal glucose level? What do my results mean?"
            )
            ask_button = st.form_submit_button("Ask Question")
            
            if ask_button and user_question:
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
                        
                        Provide a helpful, easy-to-understand answer. Use examples where appropriate.
                        Always remind users to consult healthcare providers for medical decisions.
                        """
                        
                        response = model.generate_content(prompt)
                        
                        # Display response
                        st.markdown("### 💬 Answer:")
                        with st.container():
                            st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Please set your Gemini API key in the sidebar to use the chat feature!")

# Results History Tab
with tab3:
    st.header("Analysis History")
    
    if st.session_state.analysis_results:
        # Add download all button
        if st.button("📥 Clear History"):
            st.session_state.analysis_results = []
            st.rerun()
        
        for i, result in enumerate(reversed(st.session_state.analysis_results)):
            with st.expander(f"📄 {result['filename']} - {result['timestamp']}", expanded=(i==0)):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**Extracted Metrics:**")
                    if result['metrics']:
                        for name, value in result['metrics'].items():
                            st.write(f"• {name}: **{value}**")
                    else:
                        st.write("No metrics extracted")
                
                with col2:
                    st.markdown("**AI Analysis:**")
                    st.markdown(result['analysis'])
    else:
        st.info("No analyses yet. Upload a document in the Document Analysis tab to get started!")

# Footer
st.markdown("---")
st.markdown("⚠️ **Disclaimer**: This app is for informational purposes only. Always consult with healthcare professionals for medical advice.")
st.markdown("🔒 **Privacy**: Your data stays on your device. Only the text is sent to Gemini for analysis.")