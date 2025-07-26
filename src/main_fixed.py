import streamlit as st
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page config
st.set_page_config(
    page_title="HIA - Health Insights Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import the simple app
from src.simple_app import *

# The simple app handles everything