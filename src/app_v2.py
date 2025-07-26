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
    st.session_state.document_texts = []  # Store full document texts
    st.session_state.chat_history = []

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
    
    # Show loaded documents
    if st.session_state.document_texts:
        st.markdown("---")
        st.markdown("### 📚 Loaded Documents:")
        for i, result in enumerate(st.session_state.analysis_results[-3:]):
            st.markdown(f"• {result['filename']}")
    
    st.markdown("---")
    st.markdown("### 📖 Quick Guide:")
    st.markdown("1. Set your API key above")
    st.markdown("2. Upload documents")
    st.markdown("3. Ask questions about them!")

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
                    
                    # Store the full text for Q&A
                    st.session_state.document_texts.append({
                        'filename': uploaded_file.name,
                        'text': text,
                        'timestamp': datetime.now()
                    })
                    
                    # Show extracted text preview
                    with st.expander("📝 View Extracted Text"):
                        st.text(text[:1000] + "..." if len(text) > 1000 else text)
                    
                    # Extract health metrics using regex
                    st.subheader("📊 Extracted Health Metrics")
                    
                    # Common patterns - expanded list
                    patterns = {
                        'Glucose': r'(?:Glucose|GLU|Blood Sugar)[:\s]+([\d.]+)\s*(mg/dL)?',
                        'Total Cholesterol': r'(?:Total\s+)?Cholesterol[:\s]+([\d.]+)\s*(mg/dL)?',
                        'LDL Cholesterol': r'(?:LDL)[:\s]+([\d.]+)\s*(mg/dL)?',
                        'HDL Cholesterol': r'(?:HDL)[:\s]+([\d.]+)\s*(mg/dL)?',
                        'Triglycerides': r'(?:Triglycerides|TRIG)[:\s]+([\d.]+)\s*(mg/dL)?',
                        'Blood Pressure': r'(?:Blood Pressure|BP)[:\s]+([\d/]+)\s*(mmHg)?',
                        'Hemoglobin': r'(?:Hemoglobin|Hgb|HGB)[:\s]+([\d.]+)\s*(g/dL)?',
                        'Heart Rate': r'(?:Heart Rate|Pulse|HR)[:\s]+([\d]+)\s*(bpm)?',
                        'BMI': r'(?:BMI|Body Mass Index)[:\s]+([\d.]+)',
                        'Weight': r'(?:Weight)[:\s]+([\d.]+)\s*(kg|lbs)?',
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
                    
                    # Save to history with full text
                    result = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'filename': uploaded_file.name,
                        'metrics': metrics,
                        'analysis': response.text,
                        'full_text': text  # Store full text for Q&A
                    }
                    st.session_state.analysis_results.append(result)
                    
                    st.success("✅ Analysis complete! You can now ask questions about this document in the Q&A tab.")
                    
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.error("Please check your API key and try again.")
                    with st.expander("🐛 Debug Info"):
                        st.code(str(e))

# Q&A Chat Tab
with tab2:
    st.header("Health Q&A Chat")
    
    if st.session_state.api_key_set:
        # Show available documents
        if st.session_state.document_texts:
            st.success(f"📚 {len(st.session_state.document_texts)} document(s) loaded for Q&A")
            with st.expander("View loaded documents"):
                for doc in st.session_state.document_texts:
                    st.write(f"• {doc['filename']} (loaded {doc['timestamp'].strftime('%H:%M')})")
        else:
            st.warning("📄 No documents loaded yet. Upload documents in the Document Analysis tab first!")
        
        # Chat history display
        if st.session_state.chat_history:
            st.markdown("### 💬 Chat History")
            for chat in st.session_state.chat_history:
                if chat['role'] == 'user':
                    st.markdown(f"**🧑 You:** {chat['content']}")
                else:
                    with st.container():
                        st.markdown(f"**🤖 HIA:** {chat['content']}")
                st.markdown("---")
        
        # Chat interface - using form to prevent reload
        with st.form("chat_form", clear_on_submit=True):
            user_question = st.text_area(
                "Ask about your health documents:", 
                placeholder="Examples:\n- What were my glucose levels?\n- Are my cholesterol values normal?\n- What did the doctor recommend?\n- Compare my current results to the previous ones",
                height=100
            )
            
            col1, col2 = st.columns([5, 1])
            with col1:
                ask_button = st.form_submit_button("Ask Question", type="primary", use_container_width=True)
            with col2:
                clear_button = st.form_submit_button("Clear Chat")
            
            if clear_button:
                st.session_state.chat_history = []
                st.rerun()
            
            if ask_button and user_question:
                # Add user question to history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_question
                })
                
                with st.spinner("Analyzing your documents and thinking..."):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        # Build context from ALL loaded documents
                        full_context = "=== LOADED MEDICAL DOCUMENTS ===\n\n"
                        
                        for i, doc in enumerate(st.session_state.document_texts):
                            full_context += f"Document {i+1}: {doc['filename']}\n"
                            full_context += f"Content:\n{doc['text'][:2000]}\n\n"  # Include more text
                        
                        # Add analysis results too
                        if st.session_state.analysis_results:
                            full_context += "=== ANALYSIS RESULTS ===\n\n"
                            for result in st.session_state.analysis_results:
                                full_context += f"File: {result['filename']}\n"
                                full_context += f"Metrics: {result['metrics']}\n"
                                full_context += f"Analysis: {result['analysis'][:500]}...\n\n"
                        
                        prompt = f"""
                        You are a helpful health assistant with access to the user's medical documents.
                        
                        {full_context}
                        
                        User Question: {user_question}
                        
                        Instructions:
                        1. Answer based SPECIFICALLY on the documents provided above
                        2. Quote exact values from the documents when relevant
                        3. If the information isn't in the documents, say so clearly
                        4. Provide context about what document the information comes from
                        5. Be accurate and helpful
                        6. Always remind users to consult healthcare providers for medical decisions
                        
                        Answer the question thoroughly based on the documents.
                        """
                        
                        response = model.generate_content(prompt)
                        
                        # Add response to history
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response.text
                        })
                        
                        # Rerun to show the new message
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.error("Please try again with a different question.")
    else:
        st.warning("⚠️ Please set your Gemini API key in the sidebar to use the chat feature!")

# Results History Tab
with tab3:
    st.header("Analysis History")
    
    if st.session_state.analysis_results:
        # Add clear history button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.analysis_results = []
                st.session_state.document_texts = []
                st.session_state.chat_history = []
                st.rerun()
        
        for i, result in enumerate(reversed(st.session_state.analysis_results)):
            with st.expander(f"📄 {result['filename']} - {result['timestamp']}", expanded=(i==0)):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**📊 Extracted Metrics:**")
                    if result['metrics']:
                        for name, value in result['metrics'].items():
                            st.write(f"• {name}: **{value}**")
                    else:
                        st.write("No metrics extracted")
                
                with col2:
                    st.markdown("**🤖 AI Analysis:**")
                    st.markdown(result['analysis'])
                
                # Option to view full text
                if 'full_text' in result:
                    with st.expander("View Full Document Text"):
                        st.text(result['full_text'][:2000] + "..." if len(result['full_text']) > 2000 else result['full_text'])
    else:
        st.info("No analyses yet. Upload a document in the Document Analysis tab to get started!")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("⚠️ **Medical Disclaimer**: Always consult healthcare professionals")
with col2:
    st.markdown("🔒 **Privacy**: Your data stays on your device")
with col3:
    st.markdown("🤖 **Powered by**: Google Gemini AI")