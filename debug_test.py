#!/usr/bin/env python3
"""
Debug script to test HIA components individually
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    
    try:
        from src.api.gemini_client import GeminiClient
        print("✅ GeminiClient imported successfully")
    except Exception as e:
        print(f"❌ GeminiClient import failed: {e}")
    
    try:
        from src.agent.planner import HealthAgentPlanner
        print("✅ HealthAgentPlanner imported successfully")
    except Exception as e:
        print(f"❌ HealthAgentPlanner import failed: {e}")
    
    try:
        from src.agent.executor import HealthTaskExecutor
        print("✅ HealthTaskExecutor imported successfully")
    except Exception as e:
        print(f"❌ HealthTaskExecutor import failed: {e}")
    
    try:
        from src.agent.memory import HealthMemoryStore
        print("✅ HealthMemoryStore imported successfully")
    except Exception as e:
        print(f"❌ HealthMemoryStore import failed: {e}")
    
    try:
        from src.utils.document_parser import DocumentParser
        print("✅ DocumentParser imported successfully")
    except Exception as e:
        print(f"❌ DocumentParser import failed: {e}")
    
    print("\n")

async def test_document_parser():
    """Test document parser functionality"""
    print("Testing DocumentParser...")
    
    try:
        from src.utils.document_parser import DocumentParser
        parser = DocumentParser()
        
        # Test with sample text file
        test_file = Path("test_document.txt")
        if test_file.exists():
            result = await parser.parse_document(test_file)
            print(f"✅ Document parsed successfully")
            print(f"   - File type: {result.get('file_type')}")
            print(f"   - Metadata: {result.get('metadata')}")
            print(f"   - Extracted values: {len(result.get('extracted_values', []))} metrics found")
            if result.get('extracted_values'):
                for val in result['extracted_values'][:3]:  # Show first 3
                    print(f"     • {val['test_name']}: {val['value']} {val.get('unit', '')}")
        else:
            print("❌ test_document.txt not found")
    except Exception as e:
        print(f"❌ DocumentParser test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")

async def test_gemini_client():
    """Test Gemini API client"""
    print("Testing GeminiClient...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not set in environment")
        return
    
    try:
        from src.api.gemini_client import GeminiClient
        client = GeminiClient(api_key)
        
        # Test simple text generation
        response = await client.generate_text("What is cholesterol and why is it important for health? (Answer in 2 sentences)")
        print(f"✅ Gemini text generation working")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ GeminiClient test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")

async def test_memory_store():
    """Test memory store functionality"""
    print("Testing HealthMemoryStore...")
    
    try:
        from src.agent.memory import HealthMemoryStore
        memory = HealthMemoryStore()
        
        # Test storing metrics
        test_metrics = {
            "glucose": {"value": "95", "unit": "mg/dL"},
            "cholesterol": {"value": "180", "unit": "mg/dL"}
        }
        
        await memory.store_health_metrics(test_metrics, source="test")
        print("✅ Metrics stored successfully")
        
        # Test retrieving metrics
        recent = await memory.get_recent_metrics(days=1)
        print(f"✅ Retrieved {len(recent)} recent metrics")
        
    except Exception as e:
        print(f"❌ HealthMemoryStore test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")

def test_streamlit_app():
    """Test if Streamlit app can be imported"""
    print("Testing Streamlit app...")
    
    try:
        from src.ui.streamlit_app import HIAStreamlitApp
        print("✅ HIAStreamlitApp imported successfully")
    except Exception as e:
        print(f"❌ HIAStreamlitApp import failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")

async def main():
    """Run all tests"""
    print("=== HIA Debug Test Script ===\n")
    
    # Test imports
    test_imports()
    
    # Test components
    await test_document_parser()
    await test_gemini_client()
    await test_memory_store()
    test_streamlit_app()
    
    print("=== Tests Complete ===")

if __name__ == "__main__":
    asyncio.run(main())