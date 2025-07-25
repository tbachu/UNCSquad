#!/usr/bin/env python3
"""
HIA - Health Insights Agent
Main entry point for the application.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.streamlit_app import run_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for HIA."""
    parser = argparse.ArgumentParser(
        description="HIA - Health Insights Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run the web interface
  python main.py web
  
  # Run in CLI mode (future feature)
  python main.py cli --query "What are my recent glucose levels?"
  
  # Set API key
  export GEMINI_API_KEY=your_api_key_here
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['web', 'cli'],
        default='web',
        nargs='?',
        help='Run mode: web for Streamlit UI, cli for command line'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8501,
        help='Port for web interface (default: 8501)'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='Query for CLI mode'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='File path for document analysis in CLI mode'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        logger.warning("GEMINI_API_KEY not set. Some features will be limited.")
        logger.info("Set it with: export GEMINI_API_KEY=your_api_key_here")
    
    # Create necessary directories
    directories = ['data', 'temp', 'reports', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    if args.mode == 'web':
        logger.info("Starting HIA web interface...")
        logger.info(f"Access the application at http://localhost:{args.port}")
        
        # Run Streamlit app
        os.system(f"streamlit run {__file__} --server.port {args.port}")
        
    elif args.mode == 'cli':
        logger.info("CLI mode not yet implemented")
        # TODO: Implement CLI mode
        print("CLI mode is coming soon!")
        print("For now, please use: python main.py web")
    
    else:
        parser.print_help()


def run_streamlit():
    """Entry point when running as Streamlit app."""
    # Check if this is being run by Streamlit
    if 'streamlit' in sys.modules:
        run_app()


if __name__ == "__main__":
    # Check if running under Streamlit
    if 'streamlit' in sys.modules:
        run_streamlit()
    else:
        main()