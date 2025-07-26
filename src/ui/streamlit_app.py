import streamlit as st
import asyncio
from datetime import datetime
import os
from pathlib import Path
import pandas as pd
import base64
import logging
from typing import Dict, Any, List, Optional

# Import HIA components
from src.agent.planner import HealthAgentPlanner
from src.agent.executor import HealthTaskExecutor
from src.agent.memory import HealthMemoryStore
from src.utils import SecurityManager
from src.api import GeminiClient

logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="HIA - Health Insights Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS is now injected via inject_custom_css() method to prevent caching issues


class HIAStreamlitApp:
    """Main Streamlit application for HIA."""
    
    def __init__(self):
        self.initialize_session_state()
        self.setup_components()
    
    def initialize_session_state(self):
        """Initialize session state variables."""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.authenticated = False
            st.session_state.session_token = None
            st.session_state.chat_history = []
            st.session_state.uploaded_files = []
            st.session_state.current_metrics = {}
            st.session_state.analysis_results = []
            st.session_state.css_loaded = False  # Track CSS loading
    
    def inject_custom_css(self):
        """Inject custom CSS with cache busting and persistent loading."""
        # Force reload CSS on every run by using timestamp
        cache_buster = datetime.now().timestamp()
        st.markdown(f"""
        <style id="hia-custom-styles-{cache_buster}">
            /* HIA Custom Styles - Cache buster: {cache_buster} */
            /* If styles revert after reload, press Ctrl+F5 (Windows) or Cmd+Shift+R (Mac) to hard refresh */
            
            /* Import modern fonts with cache busting */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap&v={cache_buster}');
                
                /* Root variables for consistent theming */
                :root {{
                    --primary-color: #2c5aa0;
                    --primary-light: #4a90e2;
                    --primary-dark: #1e3d73;
                    --secondary-color: #00b894;
                    --secondary-light: #26d0ce;
                    --warning-color: #fd79a8;
                    --danger-color: #e17055;
                    --success-color: #00b894;
                    --info-color: #74b9ff;
                    --light-bg: #f8fafe;
                    --card-bg: #ffffff;
                    --text-primary: #2d3436;
                    --text-secondary: #636e72;
                    --text-light: #b2bec3;
                    --border-color: #ddd;
                    --shadow-light: 0 2px 10px rgba(44, 90, 160, 0.08);
                    --shadow-medium: 0 4px 20px rgba(44, 90, 160, 0.12);
                    --shadow-heavy: 0 8px 30px rgba(44, 90, 160, 0.15);
                    --border-radius: 12px;
                    --border-radius-lg: 16px;
                }}
                
                /* Force override Streamlit defaults */
                .main .block-container {{
                    padding-top: 2rem !important;
                    padding-bottom: 2rem !important;
                    max-width: 1400px !important;
                }}
                
                /* Hide Streamlit elements */
                #MainMenu {{visibility: hidden !important;}}
                footer {{visibility: hidden !important;}}
                header {{visibility: hidden !important;}}
                .stDeployButton {{display: none !important;}}
                
                /* Main header styling */
                .main-header {{
                    font-family: 'Poppins', sans-serif !important;
                    font-size: 3.5rem !important;
                    font-weight: 700 !important;
                    background: linear-gradient(135deg, var(--primary-color), var(--primary-light)) !important;
                    -webkit-background-clip: text !important;
                    -webkit-text-fill-color: transparent !important;
                    background-clip: text !important;
                    text-align: center !important;
                    margin-bottom: 3rem !important;
                    letter-spacing: -0.02em !important;
                }}
                
                /* Enhanced metric cards */
                .metric-card {{
                    background: linear-gradient(145deg, #ffffff, #f8fafe) !important;
                    padding: 2rem !important;
                    border-radius: var(--border-radius-lg) !important;
                    box-shadow: var(--shadow-medium) !important;
                    margin-bottom: 1.5rem !important;
                    border: 1px solid rgba(44, 90, 160, 0.08) !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    position: relative !important;
                    overflow: hidden !important;
                }}
                
                .metric-card::before {{
                    content: '' !important;
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                    right: 0 !important;
                    height: 4px !important;
                    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)) !important;
                }}
                
                .metric-card:hover {{
                    transform: translateY(-4px) !important;
                    box-shadow: var(--shadow-heavy) !important;
                }}
                
                .metric-card h4 {{
                    font-family: 'Inter', sans-serif !important;
                    font-size: 0.9rem !important;
                    font-weight: 600 !important;
                    color: var(--text-secondary) !important;
                    margin-bottom: 1rem !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.05em !important;
                }}
                
                .metric-card .metric-value {{
                    font-family: 'Poppins', sans-serif !important;
                    font-size: 2.2rem !important;
                    font-weight: 700 !important;
                    margin-bottom: 0.5rem !important;
                    line-height: 1 !important;
                }}
                
                /* Health score colors */
                .health-score-excellent {{ color: var(--success-color) !important; }}
                .health-score-good {{ color: var(--info-color) !important; }}
                .health-score-warning {{ color: var(--warning-color) !important; }}
                .health-score-critical {{ color: var(--danger-color) !important; }}
                .health-score-unknown {{ color: var(--text-light) !important; }}
                
                /* Enhanced buttons */
                .stButton > button {{
                    font-family: 'Inter', sans-serif !important;
                    font-weight: 500 !important;
                    border-radius: var(--border-radius) !important;
                    border: none !important;
                    padding: 0.75rem 2rem !important;
                    transition: all 0.3s ease !important;
                    box-shadow: var(--shadow-light) !important;
                }}
                
                .stButton > button:hover {{
                    transform: translateY(-1px) !important;
                    box-shadow: var(--shadow-medium) !important;
                }}
                
                .stButton > button[kind="primary"], .stButton > button[type="primary"] {{
                    background: linear-gradient(135deg, var(--primary-color), var(--primary-light)) !important;
                    color: white !important;
                }}
                
                /* Form styling */
                .stTextInput > div > div > input,
                .stTextArea > div > div > textarea,
                .stSelectbox > div > div > select {{
                    border-radius: var(--border-radius) !important;
                    border: 2px solid var(--border-color) !important;
                    padding: 0.75rem !important;
                    font-family: 'Inter', sans-serif !important;
                    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
                    background-color: white !important;
                }}
                
                .stTextInput > div > div > input:focus,
                .stTextArea > div > div > textarea:focus,
                .stSelectbox > div > div > select:focus {{
                    border-color: var(--primary-color) !important;
                    box-shadow: 0 0 0 3px rgba(44, 90, 160, 0.1) !important;
                    outline: none !important;
                }}
                
                /* Tab styling */
                .stTabs [data-baseweb="tab-list"] {{
                    gap: 1rem !important;
                    background-color: transparent !important;
                    border-bottom: 2px solid var(--border-color) !important;
                }}
                
                .stTabs [data-baseweb="tab"] {{
                    height: 3rem !important;
                    padding: 0 1.5rem !important;
                    border-radius: var(--border-radius) var(--border-radius) 0 0 !important;
                    font-family: 'Inter', sans-serif !important;
                    font-weight: 500 !important;
                    color: var(--text-secondary) !important;
                    background-color: transparent !important;
                    border: none !important;
                    transition: all 0.3s ease !important;
                }}
                
                .stTabs [aria-selected="true"] {{
                    background-color: var(--primary-color) !important;
                    color: white !important;
                    box-shadow: var(--shadow-light) !important;
                }}
                
                /* Sidebar styling */
                .css-1d391kg {{
                    background: linear-gradient(180deg, var(--light-bg), #ffffff) !important;
                    border-right: 1px solid var(--border-color) !important;
                }}
                
                /* Info cards */
                .info-card {{
                    background: linear-gradient(145deg, #ffffff, #f8fafe) !important;
                    border: 1px solid rgba(44, 90, 160, 0.08) !important;
                    border-left: 4px solid var(--info-color) !important;
                    border-radius: var(--border-radius) !important;
                    padding: 1.5rem !important;
                    margin-bottom: 1.5rem !important;
                    box-shadow: var(--shadow-light) !important;
                    transition: all 0.3s ease !important;
                }}
                
                .info-card:hover {{ box-shadow: var(--shadow-medium) !important; }}
                .warning-card {{ border-left-color: var(--warning-color) !important; background: linear-gradient(145deg, #fff8f0, #ffffff) !important; }}
                .success-card {{ border-left-color: var(--success-color) !important; background: linear-gradient(145deg, #f0fff8, #ffffff) !important; }}
                .error-card {{ border-left-color: var(--danger-color) !important; background: linear-gradient(145deg, #fff0f0, #ffffff) !important; }}
                
                /* Progress bars */
                .stProgress > div > div > div > div {{
                    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)) !important;
                    border-radius: 10px !important;
                }}
                
                /* File uploader styling */
                .stFileUploader {{
                    background-color: var(--light-bg) !important;
                    border: 2px dashed var(--border-color) !important;
                    border-radius: var(--border-radius-lg) !important;
                    padding: 2rem !important;
                    transition: all 0.3s ease !important;
                }}
                
                .stFileUploader:hover {{
                    border-color: var(--primary-color) !important;
                    background-color: rgba(44, 90, 160, 0.02) !important;
                }}
                
                /* Section headers */
                .section-header {{
                    font-family: 'Poppins', sans-serif !important;
                    font-size: 1.8rem !important;
                    font-weight: 600 !important;
                    color: var(--text-primary) !important;
                    margin-bottom: 2rem !important;
                    padding-bottom: 0.5rem !important;
                    border-bottom: 2px solid var(--border-color) !important;
                    position: relative !important;
                }}
                
                .section-header::after {{
                    content: '' !important;
                    position: absolute !important;
                    bottom: -2px !important;
                    left: 0 !important;
                    width: 60px !important;
                    height: 2px !important;
                    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)) !important;
                }}
                
                /* Animation classes */
                .fade-in-up {{
                    animation: fadeInUp 0.6s ease-out !important;
                }}
                
                @keyframes fadeInUp {{
                    from {{
                        opacity: 0;
                        transform: translateY(20px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                
                /* Typography improvements */
                h1, h2, h3, h4, h5, h6 {{
                    font-family: 'Poppins', sans-serif !important;
                    color: var(--text-primary) !important;
                    font-weight: 600 !important;
                }}
                
                p, li, span, div {{
                    font-family: 'Inter', sans-serif !important;
                    color: var(--text-primary) !important;
                    line-height: 1.6 !important;
                }}
                
                /* Responsive design */
                @media (max-width: 768px) {{
                    .main-header {{ font-size: 2.5rem !important; }}
                    .metric-card {{ margin-bottom: 1rem !important; }}
                }}
        </style>
        """, unsafe_allow_html=True)
        
        # Also inject a small script to force style refresh
        st.markdown(f"""
        <script>
            // Force refresh styles - cache buster: {cache_buster}
            if (typeof window.hia_styles_loaded === 'undefined') {{
                window.hia_styles_loaded = true;
                console.log('HIA Custom Styles Loaded - Version: {cache_buster}');
            }}
        </script>
        """, unsafe_allow_html=True)
    
    def setup_components(self):
        """Setup HIA components."""
        # Get API key from environment or user input
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Initialize components
        try:
            self.security_manager = SecurityManager()
            self.memory_store = HealthMemoryStore()
            self.planner = HealthAgentPlanner()
            
            if self.gemini_api_key:
                self.executor = HealthTaskExecutor(gemini_api_key=self.gemini_api_key)
            else:
                self.executor = None
        except Exception as e:
            logger.error(f"Error setting up components: {str(e)}")
            self.executor = None
    
    def run(self):
        """Main application entry point."""
        # Inject custom CSS first to ensure consistent styling
        self.inject_custom_css()
        
        # Header
        st.markdown('<h1 class="main-header">🏥 HIA - Health Insights Agent</h1>', 
                   unsafe_allow_html=True)
        
        # Authentication check
        if not st.session_state.authenticated:
            self.show_login()
        else:
            self.show_main_app()
    
    def show_login(self):
        """Show login/authentication screen."""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Modern welcome section with enhanced styling
            st.markdown("""
            <div style="
                text-align: center;
                padding: 3rem 2rem;
                background: linear-gradient(145deg, #ffffff, #f8fafe);
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(44, 90, 160, 0.15);
                margin-bottom: 2rem;
                border: 1px solid rgba(44, 90, 160, 0.08);
            ">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🏥</div>
                <h2 style="
                    font-family: 'Poppins', sans-serif;
                    font-weight: 700;
                    font-size: 2.2rem;
                    background: linear-gradient(135deg, #2c5aa0, #4a90e2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 0.5rem;
                ">
                    Welcome to HIA
                </h2>
                <p style="
                    font-family: 'Inter', sans-serif;
                    font-size: 1.1rem;
                    color: #636e72;
                    margin-bottom: 0;
                ">
                    Your personal AI health analyst
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced login form container
            st.markdown("""
            <div style="
                background: linear-gradient(145deg, #ffffff, #f8fafe);
                border-radius: 16px;
                padding: 2.5rem;
                box-shadow: 0 4px 20px rgba(44, 90, 160, 0.12);
                border: 1px solid rgba(44, 90, 160, 0.08);
                margin-bottom: 2rem;
            ">
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <style>
                .login-form .stTextInput > div > div > input {
                    border-radius: 12px !important;
                    border: 2px solid #ddd !important;
                    padding: 0.75rem !important;
                    font-family: 'Inter', sans-serif !important;
                    transition: all 0.3s ease !important;
                    background-color: #ffffff !important;
                }
                .login-form .stTextInput > div > div > input:focus {
                    border-color: #2c5aa0 !important;
                    box-shadow: 0 0 0 3px rgba(44, 90, 160, 0.1) !important;
                }
                .login-form .stButton > button {
                    border-radius: 12px !important;
                    padding: 0.75rem 2rem !important;
                    font-family: 'Inter', sans-serif !important;
                    font-weight: 500 !important;
                    transition: all 0.3s ease !important;
                    border: none !important;
                    box-shadow: 0 2px 10px rgba(44, 90, 160, 0.08) !important;
                }
                .login-form .stButton > button:hover {
                    transform: translateY(-1px) !important;
                    box-shadow: 0 4px 20px rgba(44, 90, 160, 0.15) !important;
                }
                .login-form .stButton > button[kind="primary"] {
                    background: linear-gradient(135deg, #2c5aa0, #4a90e2) !important;
                    color: white !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Simple authentication (in production, use proper auth)
            with st.form("login_form", clear_on_submit=False):
                st.markdown('<div class="login-form">', unsafe_allow_html=True)
                
                st.markdown("""
                <h3 style="
                    font-family: 'Poppins', sans-serif;
                    font-weight: 600;
                    color: #2c5aa0;
                    text-align: center;
                    margin-bottom: 1.5rem;
                    font-size: 1.3rem;
                ">
                    🔐 Sign In to Continue
                </h3>
                """, unsafe_allow_html=True)
                
                username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
                password = st.text_input("🔒 Password", type="password", 
                                       placeholder="Enter your password", key="login_password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    login_button = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
                with col2:
                    demo_button = st.form_submit_button("🎯 Try Demo", use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if login_button:
                    # Validate credentials (simplified for demo)
                    if username and password:
                        st.session_state.authenticated = True
                        st.session_state.session_token = self.security_manager.create_session(username)
                        st.rerun()
                    else:
                        st.error("Please enter both username and password")
                
                if demo_button:
                    st.session_state.authenticated = True
                    st.session_state.session_token = self.security_manager.create_session("demo_user")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close login form container
            
            # Enhanced API Key setup
            st.markdown("""
            <div style="
                background: linear-gradient(145deg, #f8fafe, #ffffff);
                border: 1px solid rgba(116, 185, 255, 0.2);
                border-radius: 16px;
                padding: 2rem;
                margin-top: 1.5rem;
                box-shadow: 0 2px 10px rgba(116, 185, 255, 0.08);
            ">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.5rem; margin-right: 0.75rem;">🔑</div>
                    <h4 style="
                        font-family: 'Poppins', sans-serif;
                        font-weight: 600;
                        color: #74b9ff;
                        margin: 0;
                        font-size: 1.1rem;
                    ">
                        Setup Gemini API Key
                    </h4>
                </div>
                <p style="
                    font-family: 'Inter', sans-serif;
                    color: #636e72;
                    font-size: 0.9rem;
                    margin-bottom: 1.5rem;
                    line-height: 1.5;
                ">
                    To use the AI analysis features, please provide your Google Gemini API key.
                    <a href="https://makersuite.google.com/app/apikey" target="_blank" style="color: #74b9ff; text-decoration: none;">
                        Get your API key here →
                    </a>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🔑 Configure API Key", expanded=False):
                st.markdown("""
                <style>
                    .api-form .stTextInput > div > div > input {
                        border-radius: 8px !important;
                        border: 1px solid #ddd !important;
                        font-family: 'Inter', sans-serif !important;
                    }
                    .api-form .stButton > button {
                        background: linear-gradient(135deg, #74b9ff, #4a90e2) !important;
                        color: white !important;
                        border-radius: 8px !important;
                        border: none !important;
                        font-family: 'Inter', sans-serif !important;
                        font-weight: 500 !important;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="api-form">', unsafe_allow_html=True)
                api_key = st.text_input("🔐 Gemini API Key", type="password",
                                      help="Enter your Google Gemini API key", 
                                      placeholder="Enter your API key...")
                if st.button("💾 Save API Key", use_container_width=True):
                    if api_key:
                        os.environ['GEMINI_API_KEY'] = api_key
                        st.session_state.api_key_updated = True
                        st.success("✅ API Key saved! Please click 'Try Demo' to continue.")
                        # Reinitialize components with new API key
                        self.gemini_api_key = api_key
                        self.setup_components()
                    else:
                        st.error("❌ Please enter a valid API key")
                st.markdown('</div>', unsafe_allow_html=True)
    
    def show_main_app(self):
        """Show main application interface."""
        # Sidebar
        with st.sidebar:
            self.show_sidebar()
        
        # Main content area with tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard", 
            "📄 Document Analysis", 
            "💬 Health Q&A", 
            "📈 Trends & Insights",
            "⚕️ Reports"
        ])
        
        with tab1:
            self.show_dashboard()
        
        with tab2:
            self.show_document_analysis()
        
        with tab3:
            self.show_health_qa()
        
        with tab4:
            self.show_trends()
        
        with tab5:
            self.show_reports()
    
    def show_sidebar(self):
        """Show sidebar with user info and settings."""
        # User profile section with modern styling
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
            color: white;
            padding: 1.5rem;
            border-radius: var(--border-radius-lg);
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: var(--shadow-medium);
        ">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">👤</div>
            <div style="font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem;">
                Health Dashboard
            </div>
            <div style="font-size: 0.9rem; opacity: 0.9; font-family: 'Inter', sans-serif;">
                Session Active
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown('<div class="section-header" style="font-size: 1.1rem; margin-bottom: 1.5rem;">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        # Quick upload section
        st.markdown("#### Quick Upload")
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'txt'],
            key="sidebar_upload"
        )
        
        if uploaded_file:
            if st.button("🔍 Analyze", use_container_width=True):
                # Save to session state to process in main area
                st.session_state.pending_file = uploaded_file
                st.info("Switch to Document Analysis tab to see results")
        
        # Recent activities
        st.markdown('<div class="section-header" style="font-size: 1.1rem; margin: 2rem 0 1.5rem 0;">📋 Recent Activities</div>', unsafe_allow_html=True)
        activities = st.session_state.get('recent_activities', [
            "Document analyzed - Lab Report.pdf",
            "Health score updated - 85/100",
            "Recommendation generated",
            "Metrics synchronized",
            "Report generated"
        ])
        
        for i, activity in enumerate(activities[-5:]):
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                padding: 0.75rem;
                background-color: var(--light-bg);
                border-radius: var(--border-radius);
                margin-bottom: 0.5rem;
                border-left: 3px solid var(--primary-color);
                transition: all 0.3s ease;
            " onmouseover="this.style.backgroundColor='rgba(44, 90, 160, 0.05)'"
               onmouseout="this.style.backgroundColor='var(--light-bg)'">
                <div style="
                    width: 8px;
                    height: 8px;
                    background-color: var(--secondary-color);
                    border-radius: 50%;
                    margin-right: 0.75rem;
                "></div>
                <div style="
                    font-family: 'Inter', sans-serif;
                    font-size: 0.85rem;
                    color: var(--text-primary);
                ">
                    {activity}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Settings
        with st.expander("⚙️ Settings"):
            st.selectbox("Language", ["English", "Spanish", "French", "Chinese"])
            st.selectbox("Units", ["Metric", "Imperial"])
            st.checkbox("Enable notifications")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.session_token = None
            st.rerun()
    
    def show_dashboard(self):
        """Show main dashboard with health overview."""
        st.markdown('<div class="section-header">🩺 Health Overview</div>', unsafe_allow_html=True)
        
        # Fetch recent metrics
        asyncio.run(self._update_dashboard_metrics())
        
        # Display metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = st.session_state.current_metrics
        
        with col1:
            self._show_metric_card("Blood Pressure", 
                                 metrics.get('blood_pressure', {}).get('value', 'N/A'),
                                 metrics.get('blood_pressure', {}).get('status', 'unknown'))
        
        with col2:
            self._show_metric_card("Glucose", 
                                 metrics.get('glucose', {}).get('value', 'N/A'),
                                 metrics.get('glucose', {}).get('status', 'unknown'))
        
        with col3:
            self._show_metric_card("Cholesterol", 
                                 metrics.get('cholesterol', {}).get('value', 'N/A'),
                                 metrics.get('cholesterol', {}).get('status', 'unknown'))
        
        with col4:
            self._show_metric_card("BMI", 
                                 metrics.get('bmi', {}).get('value', 'N/A'),
                                 metrics.get('bmi', {}).get('status', 'unknown'))
        
        # Health insights
        st.markdown('<div class="section-header" style="font-size: 1.4rem; margin-top: 3rem;">💡 Recent Insights</div>', unsafe_allow_html=True)
        
        insights = st.session_state.get('recent_insights', [
            {
                "text": "Your blood pressure has been stable over the past month",
                "type": "success",
                "icon": "✅"
            },
            {
                "text": "Cholesterol levels show improvement since last quarter", 
                "type": "success",
                "icon": "📈"
            },
            {
                "text": "Consider discussing vitamin D supplementation with your doctor",
                "type": "info", 
                "icon": "💊"
            }
        ])
        
        for insight in insights:
            insight_type = insight.get('type', 'info')
            card_class = f"{insight_type}-card" if insight_type in ['success', 'warning', 'error'] else "info-card"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; align-items: flex-start; gap: 1rem;">
                    <div style="font-size: 1.5rem; flex-shrink: 0;">{insight['icon']}</div>
                    <div style="flex: 1;">
                        <p style="margin: 0; line-height: 1.6; font-family: 'Inter', sans-serif; font-size: 0.95rem;">
                            {insight['text']}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header" style="font-size: 1.2rem;">📊 Health Score</div>', unsafe_allow_html=True)
            health_score = st.session_state.get('health_score', 75)
            st.progress(health_score / 100)
            
            # Enhanced health score display
            score_color = "var(--success-color)" if health_score >= 80 else "var(--warning-color)" if health_score >= 60 else "var(--danger-color)"
            st.markdown(f"""
            <div style="text-align: center; margin-top: 1rem;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {score_color}; font-family: 'Poppins', sans-serif;">
                    {health_score}/100
                </div>
                <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                    Overall Health Score
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-header" style="font-size: 1.2rem;">📅 Upcoming</div>', unsafe_allow_html=True)
            upcoming_items = [
                {"icon": "🗓️", "text": "Annual check-up", "date": "Feb 15"},
                {"icon": "💉", "text": "Flu vaccine", "date": "Oct 1"},
                {"icon": "🦷", "text": "Dental cleaning", "date": "Mar 20"}
            ]
            
            for item in upcoming_items:
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 0.75rem; background-color: var(--light-bg); 
                           border-radius: var(--border-radius); margin-bottom: 0.5rem; transition: all 0.3s ease;">
                    <span style="font-size: 1.2rem; margin-right: 1rem;">{item['icon']}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 500; color: var(--text-primary);">{item['text']}</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">{item['date']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def show_document_analysis(self):
        """Show document upload and analysis interface."""
        st.markdown('<div class="section-header">📄 Document Analysis</div>', unsafe_allow_html=True)
        
        # Check for pending file from sidebar
        pending_file = st.session_state.get('pending_file', None)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload medical document",
            type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'txt'],
            help="Upload lab reports, prescriptions, or medical records",
            key="main_upload"
        )
        
        # Use pending file if available
        file_to_process = pending_file or uploaded_file
        
        if file_to_process:
            # Save uploaded file temporarily
            temp_path = Path("temp") / file_to_process.name
            temp_path.parent.mkdir(exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(file_to_process.getbuffer())
            
            # Show file info
            st.success(f"📄 Loaded: {file_to_process.name}")
            st.info(f"File type: {file_to_process.type} | Size: {file_to_process.size:,} bytes")
            
            # Analyze button
            if st.button("🔍 Analyze Document", type="primary", use_container_width=True):
                with st.spinner("Analyzing document..."):
                    asyncio.run(self._analyze_document(temp_path))
                    
            # Clear pending file after processing
            if pending_file:
                st.session_state.pending_file = None
        
        # Show analysis results
        if st.session_state.analysis_results:
            st.markdown('<div class="section-header" style="font-size: 1.4rem; margin-top: 3rem;">📊 Analysis Results</div>', unsafe_allow_html=True)
            
            for result in st.session_state.analysis_results:
                with st.expander(f"📄 {result['filename']} - {result['date']}"):
                    st.markdown("**Summary:**")
                    st.write(result.get('summary', 'No summary available'))
                    
                    st.markdown("**Extracted Values:**")
                    values_df = pd.DataFrame(result.get('values', []))
                    if not values_df.empty:
                        st.dataframe(values_df)
                    
                    st.markdown("**Recommendations:**")
                    for rec in result.get('recommendations', []):
                        st.markdown(f"- {rec}")
    
    def show_health_qa(self):
        """Show health Q&A chat interface."""
        st.markdown('<div class="section-header">💬 Health Q&A</div>', unsafe_allow_html=True)
        
        # Chat interface
        chat_container = st.container()
        
        # Input area
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area("Ask me anything about your health:", 
                                    placeholder="E.g., What do my recent lab results mean?")
            col1, col2 = st.columns([5, 1])
            
            with col2:
                submit = st.form_submit_button("Send", use_container_width=True)
            
            if submit and user_input:
                # Add to chat history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now()
                })
                
                # Get response
                with st.spinner("Thinking..."):
                    response = asyncio.run(self._get_chat_response(user_input))
                
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now()
                })
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**HIA:** {message['content']}")
                st.caption(message['timestamp'].strftime("%I:%M %p"))
                st.divider()
    
    def show_trends(self):
        """Show health trends and analytics."""
        st.markdown('<div class="section-header">📈 Health Trends & Analytics</div>', unsafe_allow_html=True)
        
        # Time range selector
        col1, col2 = st.columns([3, 1])
        with col1:
            time_range = st.selectbox(
                "Select time range",
                ["Last Week", "Last Month", "Last Quarter", "Last Year", "All Time"]
            )
        
        # Metric selector
        selected_metrics = st.multiselect(
            "Select metrics to view",
            ["Blood Pressure", "Glucose", "Cholesterol", "Weight", "Heart Rate"],
            default=["Blood Pressure", "Glucose"]
        )
        
        if selected_metrics:
            # Generate and display charts
            for metric in selected_metrics:
                st.markdown(f"### {metric} Trend")
                
                # Placeholder for actual chart
                chart_placeholder = st.empty()
                
                # In real implementation, this would fetch data and create chart
                # For now, show a placeholder
                chart_placeholder.info(f"Chart for {metric} would be displayed here")
        
        # Insights section
        st.markdown('<div class="section-header" style="font-size: 1.4rem; margin-top: 3rem;">🔍 Key Insights</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Average Blood Pressure", "118/78", "-2%", 
                     help="Compared to last month")
            st.metric("Average Glucose", "95 mg/dL", "+1%",
                     help="Compared to last month")
        
        with col2:
            st.metric("Weight Change", "-3 lbs", "-1.5%",
                     help="Over the past month")
            st.metric("Exercise Days", "18/30", "+20%",
                     help="Compared to last month")
    
    def show_reports(self):
        """Show report generation and history."""
        st.markdown('<div class="section-header">⚕️ Health Reports</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Generate New Report")
            
            report_type = st.selectbox(
                "Report Type",
                ["Comprehensive Health Summary", "Doctor Visit Prep", 
                 "Medication Review", "Lab Results Summary"]
            )
            
            include_options = st.multiselect(
                "Include in report",
                ["Recent Lab Results", "Medication List", "Health Trends", 
                 "Recommendations", "Questions for Doctor"],
                default=["Recent Lab Results", "Medication List"]
            )
            
            if st.button("📄 Generate Report", use_container_width=True):
                with st.spinner("Generating report..."):
                    # Generate report
                    report_path = asyncio.run(self._generate_report(
                        report_type, include_options
                    ))
                    
                    if report_path:
                        st.success("Report generated successfully!")
                        
                        # Provide download link
                        with open(report_path, "rb") as f:
                            st.download_button(
                                "📥 Download Report",
                                f.read(),
                                file_name=f"health_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
        
        with col2:
            st.markdown("### Recent Reports")
            
            # List recent reports
            recent_reports = [
                {"date": "2024-01-15", "type": "Annual Summary", "id": "rep_001"},
                {"date": "2024-01-08", "type": "Lab Results", "id": "rep_002"},
                {"date": "2023-12-20", "type": "Doctor Visit", "id": "rep_003"}
            ]
            
            for report in recent_reports:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{report['type']}**")
                    st.caption(report['date'])
                with col2:
                    st.button("View", key=f"view_{report['id']}")
                with col3:
                    st.button("Share", key=f"share_{report['id']}")
                st.divider()
    
    # Helper methods
    def _show_metric_card(self, name: str, value: str, status: str):
        """Display an enhanced metric card with modern styling."""
        # Map status to appropriate classes and icons
        status_mapping = {
            'normal': {'class': 'health-score-excellent', 'icon': '✅', 'label': 'Normal'},
            'good': {'class': 'health-score-good', 'icon': '💙', 'label': 'Good'},
            'warning': {'class': 'health-score-warning', 'icon': '⚠️', 'label': 'Attention'},
            'critical': {'class': 'health-score-critical', 'icon': '🚨', 'label': 'Critical'},
            'unknown': {'class': 'health-score-unknown', 'icon': '❓', 'label': 'No Data'}
        }
        
        status_info = status_mapping.get(status, status_mapping['unknown'])
        
        st.markdown(f"""
        <div class="metric-card fade-in-up">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                <h4>{name}</h4>
                <span style="font-size: 1.2rem;">{status_info['icon']}</span>
            </div>
            <div class="metric-value {status_info['class']}">{value}</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem;">
                Status: {status_info['label']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    async def _update_dashboard_metrics(self):
        """Update dashboard metrics from memory store."""
        try:
            recent_metrics = await self.memory_store.get_recent_metrics()
            st.session_state.current_metrics = recent_metrics
        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")
    
    async def _analyze_document(self, file_path: Path):
        """Analyze uploaded document."""
        if not self.gemini_api_key:
            st.error("⚠️ **Gemini API Key Required**")
            st.info("Please set up your Gemini API key in the login screen first!")
            return
            
        if not self.executor:
            st.error("⚠️ **System Error**")
            st.info("Please refresh the page after setting up your API key.")
            return
        
        try:
            # Import the components we need
            from src.utils.document_parser import DocumentParser
            from src.api.gemini_client import GeminiClient
            
            # Step 1: Parse the document
            st.info("📄 Parsing document...")
            parser = DocumentParser()
            
            # Parse document with detailed error handling
            try:
                document_data = await parser.parse_document(file_path)
                st.success("✅ Document parsed successfully!")
            except RuntimeError as e:
                # OCR/dependency error
                raise e
            except Exception as e:
                st.error(f"Failed to parse document: {str(e)}")
                raise e
            
            # Show parsing notes if any
            if 'parsing_notes' in document_data and document_data['parsing_notes']:
                with st.expander("📝 Parsing Notes", expanded=True):
                    for note in document_data['parsing_notes']:
                        st.write(f"• {note}")
            
            # Step 2: Display extracted content
            with st.expander("📊 Extracted Data", expanded=True):
                # Show metadata
                if document_data.get('metadata'):
                    st.write("**Document Metadata:**")
                    for key, value in document_data['metadata'].items():
                        st.write(f"- {key}: {value}")
                
                # Show extracted values
                if document_data.get('extracted_values'):
                    st.write("\n**Extracted Health Metrics:**")
                    values_df = pd.DataFrame(document_data['extracted_values'])
                    st.dataframe(values_df, use_container_width=True)
                    
                    # Store metrics in memory
                    try:
                        metrics = {}
                        for val in document_data['extracted_values']:
                            metrics[val['test_name']] = {
                                'value': val['value'],
                                'unit': val.get('unit', '')
                            }
                        await self.memory_store.store_health_metrics(
                            metrics, 
                            source=f"document_{file_path.name}"
                        )
                        st.success(f"✅ Stored {len(metrics)} health metrics")
                    except Exception as e:
                        st.warning(f"Could not store metrics: {str(e)}")
                else:
                    st.info("No health metrics found in document")
                
                # Show text preview
                if document_data.get('cleaned_text'):
                    st.write("\n**Document Text Preview:**")
                    text_preview = document_data['cleaned_text'][:500] + "..." if len(document_data['cleaned_text']) > 500 else document_data['cleaned_text']
                    st.text(text_preview)
            
            # Step 3: AI Analysis
            if self.gemini_api_key and document_data.get('cleaned_text'):
                st.info("🤖 Generating AI analysis...")
                
                try:
                    client = GeminiClient(self.gemini_api_key)
                    
                    # Create a comprehensive prompt
                    analysis_prompt = f"""
                    Analyze this medical document and provide a patient-friendly summary.
                    
                    Document Type: {document_data.get('file_type', 'Unknown')}
                    Metadata: {document_data.get('metadata', {})}
                    Extracted Values: {document_data.get('extracted_values', [])[:20]}  # Limit to first 20
                    Document Text (first 1000 chars): {document_data.get('cleaned_text', '')[:1000]}
                    
                    Please provide:
                    1. What type of medical document this is
                    2. Key findings or values that stand out  
                    3. Any values that appear abnormal or concerning
                    4. General health insights based on the data
                    5. Recommendations for the patient
                    
                    Keep the summary concise, clear, and patient-friendly. Avoid medical jargon.
                    """
                    
                    # Get AI analysis
                    ai_summary = await client.generate_text(analysis_prompt)
                    
                    # Display AI summary
                    st.markdown("### 🤖 AI Health Analysis")
                    st.info(ai_summary)
                    
                    # Store the analysis result
                    analysis_result = {
                        'filename': file_path.name,
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'summary': ai_summary,
                        'values': document_data.get('extracted_values', []),
                        'metadata': document_data.get('metadata', {}),
                        'recommendations': [
                            'Review these results with your healthcare provider',
                            'Keep a record of these results for future reference',
                            'Monitor any values flagged as abnormal'
                        ]
                    }
                    
                    st.session_state.analysis_results.append(analysis_result)
                    
                    # Store document in memory
                    try:
                        await self.memory_store.store_document(
                            document_id=f"doc_{datetime.now().timestamp()}",
                            content=document_data.get('cleaned_text', ''),
                            document_type=document_data.get('file_type', 'unknown'),
                            metadata={
                                **document_data.get('metadata', {}),
                                'summary': ai_summary
                            }
                        )
                    except Exception as e:
                        st.warning(f"Could not store document: {str(e)}")
                    
                    st.success("✅ **Analysis complete!**")
                    
                except Exception as e:
                    st.warning(f"⚠️ Could not generate AI summary: {str(e)}")
                    st.info("The document was still parsed successfully. Check the extracted data above.")
            else:
                st.warning("⚠️ AI analysis not available. Set up Gemini API key for AI-powered insights.")
                
                # Still save basic results
                analysis_result = {
                    'filename': file_path.name,
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'summary': 'Document parsed successfully. AI analysis not available.',
                    'values': document_data.get('extracted_values', []),
                    'metadata': document_data.get('metadata', {}),
                    'recommendations': ['Review with healthcare provider']
                }
                st.session_state.analysis_results.append(analysis_result)
            
        except RuntimeError as e:
            # Handle system dependency errors (like missing Tesseract)
            error_msg = str(e)
            st.error("🚫 **System Dependency Missing**")
            st.markdown(f"**Error:** {error_msg}")
            
            if "Tesseract" in error_msg:
                st.info("**To fix this issue:**")
                st.code("brew install tesseract", language="bash")
                st.markdown("After installation, refresh this page and try again.")
            
        except FileNotFoundError as e:
            st.error("📄 **File Not Found**")
            st.markdown(f"The uploaded file could not be found: {str(e)}")
            st.info("Please try uploading the file again.")
            
        except ValueError as e:
            st.error("📋 **Unsupported File Format**")
            st.markdown(f"**Error:** {str(e)}")
            st.info("**Supported formats:** PDF, PNG, JPG, JPEG, DOCX, TXT")
            
        except Exception as e:
            logger.error(f"Error in document analysis: {str(e)}")
            st.error("❌ **Analysis Failed**")
            st.markdown(f"**Error:** {str(e)}")
            
            # Provide helpful debugging information
            with st.expander("🔧 Debugging Information"):
                st.markdown(f"**File:** {file_path}")
                st.markdown(f"**File exists:** {file_path.exists()}")
                st.markdown(f"**File size:** {file_path.stat().st_size if file_path.exists() else 'N/A'} bytes")
                st.markdown(f"**Error type:** {type(e).__name__}")
                
                # Check system dependencies
                st.markdown("**System Dependencies:**")
                try:
                    import pytesseract
                    tesseract_version = pytesseract.get_tesseract_version()
                    st.success(f"✅ Tesseract OCR: {tesseract_version}")
                except:
                    st.error("❌ Tesseract OCR: Not available")
                
                try:
                    import PyPDF2
                    st.success("✅ PyPDF2: Available")
                except:
                    st.error("❌ PyPDF2: Not available")
                
                try:
                    from PIL import Image
                    st.success("✅ PIL (Image processing): Available")
                except:
                    st.error("❌ PIL: Not available")
                
                try:
                    import docx
                    st.success("✅ python-docx: Available")
                except:
                    st.error("❌ python-docx: Not available")
                
                # Show traceback for debugging
                import traceback
                st.code(traceback.format_exc())
    
    async def _get_chat_response(self, user_input: str) -> str:
        """Get response from health agent."""
        if not self.gemini_api_key:
            return "Please set up your Gemini API key in the login screen to use the chat feature."
        
        try:
            # Get relevant context from memory
            context = await self.memory_store.get_relevant_context(user_input)
            
            # Use Gemini directly for Q&A
            from src.api.gemini_client import GeminiClient
            gemini = GeminiClient(self.gemini_api_key)
            
            # Build context string
            context_str = ""
            if context.get('recent_metrics'):
                context_str += "\nRecent Health Metrics:\n"
                for metric, data in context['recent_metrics'].items():
                    context_str += f"- {metric}: {data.get('value')} {data.get('unit', '')}\n"
            
            if context.get('documents'):
                context_str += "\nRecent Documents:\n"
                for doc in context['documents'][:3]:  # Limit to 3 most relevant
                    context_str += f"- {doc.get('metadata', {}).get('document_type', 'Document')}: {doc.get('content', '')[:200]}...\n"
            
            prompt = f"""
            You are HIA (Health Insights Agent), a knowledgeable and friendly AI health assistant.
            
            User's Health Context:
            {context_str if context_str else "No previous health data available."}
            
            User Question: {user_input}
            
            Please provide a helpful, accurate, and easy-to-understand response. Consider:
            1. Answer the question directly and clearly
            2. If discussing health metrics, explain what normal ranges are
            3. Provide practical advice when appropriate
            4. Always remind users to consult healthcare providers for medical decisions
            5. Be empathetic and supportive
            
            If you don't have enough information to answer fully, acknowledge this and suggest what information would be helpful.
            """
            
            response = await gemini.generate_text(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error in chat response: {str(e)}")
            
            # More specific error messages
            if "API key not valid" in str(e):
                return "❌ Your Gemini API key appears to be invalid. Please check your API key in the settings."
            elif "quota" in str(e).lower():
                return "⚠️ API quota exceeded. Please try again later or check your Gemini API usage limits."
            elif "timeout" in str(e).lower():
                return "⏱️ Request timed out. Please try again with a shorter question."
            else:
                return f"😔 I encountered an error while processing your question. Error: {str(e)}\n\nPlease try again or rephrase your question."
    
    async def _generate_report(self, report_type: str, 
                              include_options: List[str]) -> Optional[str]:
        """Generate health report."""
        try:
            # This would use the executor to generate report
            # For now, return a placeholder
            return "reports/sample_report.pdf"
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            return None


def run_app():
    """Entry point for the Streamlit app."""
    app = HIAStreamlitApp()
    app.run()


if __name__ == "__main__":
    run_app()