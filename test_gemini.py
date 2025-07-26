#!/usr/bin/env python3
"""Direct test of Gemini API"""

import google.generativeai as genai

print("🧪 Testing Gemini API directly...\n")

# Get API key
api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()

if not api_key:
    print("\n❌ No API key provided")
    print("Get one from: https://makersuite.google.com/app/apikey")
    exit(1)

try:
    # Configure
    genai.configure(api_key=api_key)
    
    # Test model
    print("\n📡 Connecting to Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Simple test
    print("📝 Sending test prompt...")
    response = model.generate_content("What is 2+2? Answer in exactly 3 words.")
    
    print("\n✅ SUCCESS! Gemini responded:")
    print(f"Response: {response.text}")
    
    # Health test
    print("\n🏥 Testing health analysis...")
    health_prompt = """
    A patient has:
    - Glucose: 95 mg/dL
    - Cholesterol: 180 mg/dL
    
    Are these values normal? Answer in 1 sentence.
    """
    
    response = model.generate_content(health_prompt)
    print(f"Health Response: {response.text}")
    
    print("\n✨ Gemini API is working perfectly!")
    print("\nYou can now use this API key in the HIA app!")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nPossible issues:")
    print("1. Invalid API key")
    print("2. API quota exceeded")
    print("3. Network connection issues")
    print("\nTry getting a new API key from:")
    print("https://makersuite.google.com/app/apikey")