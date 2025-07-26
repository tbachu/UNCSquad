#!/usr/bin/env python3
"""
HIA - Health Insights Agent
Main entry point - Version 2 with better Q&A
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and run the v2 app with better Q&A functionality
from src.app_v2 import *

# The app_v2.py handles everything with document-aware Q&A