import streamlit as st
import asyncio
from datetime import datetime
import os
from pathlib import Path
import pandas as pd
import base64
from typing import Dict, Any, List, Optional

# Import HIA components
from ..agent import HealthAgentPlanner, HealthAgentExecutor, HealthMemoryStore
from ..utils import SecurityManager
from ..api import GeminiClient

# Page config
st.set_page_config(
    page_title="HIA - Health Insights Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .health-score-good {
        color: #27ae60;
        font-weight: bold;
    }
    .health-score-warning {
        color: #f39c12;
        font-weight: bold;
    }
    .health-score-critical {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


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
    
    def setup_components(self):
        """Setup HIA components."""
        # Get API key from environment or user input
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Initialize components
        self.security_manager = SecurityManager()
        self.memory_store = HealthMemoryStore()
        self.planner = HealthAgentPlanner()
        
        if self.gemini_api_key:
            self.executor = HealthAgentExecutor(
                gemini_api_key=self.gemini_api_key,
                memory_store=self.memory_store
            )
    
    def run(self):
        """Main application entry point."""
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
            st.markdown("### Welcome to HIA")
            st.markdown("Your personal AI health analyst")
            
            # Simple authentication (in production, use proper auth)
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", 
                                       placeholder="Enter your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_button = st.form_submit_button("Login", use_container_width=True)
                with col2:
                    demo_button = st.form_submit_button("Try Demo", use_container_width=True)
                
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
            
            # API Key setup
            with st.expander("Setup Gemini API Key"):
                api_key = st.text_input("Gemini API Key", type="password",
                                      help="Enter your Google Gemini API key")
                if st.button("Save API Key"):
                    if api_key:
                        os.environ['GEMINI_API_KEY'] = api_key
                        st.success("API Key saved!")
                        st.rerun()
    
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
        st.markdown("### User Profile")
        st.markdown(f"**Session:** Active")
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        if st.button("📤 Upload Document", use_container_width=True):
            st.session_state.show_upload = True
        
        if st.button("💊 Check Medications", use_container_width=True):
            st.session_state.show_medications = True
        
        if st.button("📋 Generate Report", use_container_width=True):
            st.session_state.show_report_gen = True
        
        # Recent activities
        st.markdown("### Recent Activities")
        activities = st.session_state.get('recent_activities', [])
        for activity in activities[-5:]:
            st.markdown(f"- {activity}")
        
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
        st.markdown("## Health Overview")
        
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
        st.markdown("### Recent Insights")
        
        insights = st.session_state.get('recent_insights', [
            "Your blood pressure has been stable over the past month",
            "Cholesterol levels show improvement since last quarter",
            "Consider discussing vitamin D supplementation with your doctor"
        ])
        
        for insight in insights:
            st.info(f"💡 {insight}")
        
        # Quick stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Health Score")
            health_score = st.session_state.get('health_score', 75)
            st.progress(health_score / 100)
            st.markdown(f"**Overall Health Score: {health_score}/100**")
        
        with col2:
            st.markdown("### Upcoming")
            st.markdown("- 🗓️ Annual check-up - Feb 15")
            st.markdown("- 💉 Flu vaccine - Oct 1")
            st.markdown("- 🦷 Dental cleaning - Mar 20")
    
    def show_document_analysis(self):
        """Show document upload and analysis interface."""
        st.markdown("## Document Analysis")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload medical document",
            type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'txt'],
            help="Upload lab reports, prescriptions, or medical records"
        )
        
        if uploaded_file:
            # Save uploaded file temporarily
            temp_path = Path("temp") / uploaded_file.name
            temp_path.parent.mkdir(exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Analyze button
            if st.button("🔍 Analyze Document"):
                with st.spinner("Analyzing document..."):
                    asyncio.run(self._analyze_document(temp_path))
        
        # Show analysis results
        if st.session_state.analysis_results:
            st.markdown("### Analysis Results")
            
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
        st.markdown("## Health Q&A")
        
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
        st.markdown("## Health Trends & Analytics")
        
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
        st.markdown("### Key Insights")
        
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
        st.markdown("## Health Reports")
        
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
        """Display a metric card."""
        status_class = {
            'normal': 'health-score-good',
            'warning': 'health-score-warning',
            'critical': 'health-score-critical',
            'unknown': ''
        }.get(status, '')
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>{name}</h4>
            <p class="{status_class}" style="font-size: 1.5rem;">{value}</p>
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
            st.error("Please set up your Gemini API key first!")
            return
        
        try:
            # Create analysis task
            tasks = self.planner.plan(f"Analyze medical document at {file_path}")
            
            # Execute tasks
            results = await self.executor.execute_tasks(tasks)
            
            # Process results
            for result in results:
                if result.success:
                    analysis = {
                        'filename': file_path.name,
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'summary': result.result.get('analysis', ''),
                        'values': result.result.get('metrics', []),
                        'recommendations': ['Schedule follow-up', 'Monitor trends']
                    }
                    st.session_state.analysis_results.append(analysis)
            
            st.success("Document analyzed successfully!")
            
        except Exception as e:
            st.error(f"Error analyzing document: {str(e)}")
    
    async def _get_chat_response(self, user_input: str) -> str:
        """Get response from health agent."""
        if not self.gemini_api_key:
            return "Please set up your Gemini API key to use the chat feature."
        
        try:
            # Plan and execute tasks
            tasks = self.planner.plan(user_input)
            results = await self.executor.execute_tasks(tasks)
            
            # Extract response
            for result in results:
                if result.success and 'answer' in result.result:
                    return result.result['answer']
            
            return "I'm sorry, I couldn't process your question. Please try rephrasing."
            
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
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