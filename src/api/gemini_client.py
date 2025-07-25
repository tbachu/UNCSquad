import logging
import os
from typing import Dict, Any, List, Optional, Union
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import asyncio
import base64
from PIL import Image
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client for interacting with Google's Gemini API.
    Handles text analysis, multimodal inputs, and health-specific prompting.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize models - using current model names
        self.text_model = genai.GenerativeModel('gemini-1.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')  # Flash now supports vision
        
        # Safety settings for medical content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # System prompt for health context
        self.system_prompt = """You are HIA (Health Insights Agent), an AI health analyst assistant.
        Your role is to:
        1. Analyze medical documents and explain them in simple terms
        2. Track health metrics and identify trends
        3. Provide evidence-based health information
        4. Always remind users to consult healthcare professionals for medical decisions
        5. Maintain user privacy and confidentiality
        
        Important guidelines:
        - Be accurate and cite sources when possible
        - Explain medical terms in layman's language
        - Flag concerning values or trends
        - Never diagnose conditions or prescribe treatments
        - Always emphasize the importance of professional medical advice
        """
    
    async def analyze_text(self, prompt: str, context: str = None) -> str:
        """
        Analyzes text using Gemini Pro.
        
        Args:
            prompt: The analysis prompt
            context: Optional context to prepend
            
        Returns:
            Analysis response from Gemini
        """
        try:
            full_prompt = self.system_prompt + "\n\n"
            if context:
                full_prompt += f"Context:\n{context}\n\n"
            full_prompt += prompt
            
            response = await asyncio.to_thread(
                self.text_model.generate_content,
                full_prompt,
                safety_settings=self.safety_settings
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in Gemini text analysis: {str(e)}")
            raise
    
    async def analyze_image(self, image_path: str, prompt: str) -> str:
        """
        Analyzes medical images or documents using Gemini Pro Vision.
        
        Args:
            image_path: Path to the image file
            prompt: Analysis prompt
            
        Returns:
            Analysis response from Gemini
        """
        try:
            # Open and prepare image
            image = Image.open(image_path)
            
            full_prompt = self.system_prompt + "\n\n" + prompt
            
            response = await asyncio.to_thread(
                self.vision_model.generate_content,
                [full_prompt, image],
                safety_settings=self.safety_settings
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in Gemini image analysis: {str(e)}")
            raise
    
    async def analyze_multimodal(self, inputs: List[Union[str, Image.Image]], 
                                prompt: str) -> str:
        """
        Analyzes multiple inputs (text and images) together.
        
        Args:
            inputs: List of text strings or PIL Image objects
            prompt: Analysis prompt
            
        Returns:
            Analysis response from Gemini
        """
        try:
            full_inputs = [self.system_prompt + "\n\n" + prompt] + inputs
            
            response = await asyncio.to_thread(
                self.vision_model.generate_content,
                full_inputs,
                safety_settings=self.safety_settings
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in Gemini multimodal analysis: {str(e)}")
            raise
    
    async def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts structured data from text according to a schema.
        
        Args:
            text: Input text to extract from
            schema: Expected output schema
            
        Returns:
            Structured data matching the schema
        """
        prompt = f"""
        Extract structured data from the following text according to this schema:
        {schema}
        
        Text:
        {text}
        
        Return the data in JSON format matching the schema exactly.
        Include only fields that have clear values in the text.
        """
        
        response = await self.analyze_text(prompt)
        
        # Parse JSON from response
        try:
            import json
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in response")
                return {}
        except Exception as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return {}
    
    async def medical_document_qa(self, document_content: str, question: str) -> str:
        """
        Answers questions about medical documents.
        
        Args:
            document_content: The medical document text
            question: User's question about the document
            
        Returns:
            Answer to the question
        """
        prompt = f"""
        Based on this medical document, answer the following question.
        Provide a clear, accurate answer and explain any medical terms used.
        
        Document:
        {document_content}
        
        Question: {question}
        
        Answer:
        """
        
        return await self.analyze_text(prompt)
    
    async def explain_medical_term(self, term: str, context: str = None) -> str:
        """
        Explains a medical term in simple language.
        
        Args:
            term: Medical term to explain
            context: Optional context where the term was used
            
        Returns:
            Simple explanation of the term
        """
        prompt = f"""
        Explain the medical term "{term}" in simple, easy-to-understand language.
        Include:
        1. What it means
        2. Why it's important
        3. What normal/abnormal values might indicate (if applicable)
        """
        
        if context:
            prompt += f"\n\nContext where this term appeared:\n{context}"
        
        return await self.analyze_text(prompt)
    
    async def generate_health_insights(self, health_data: Dict[str, Any]) -> str:
        """
        Generates personalized health insights from user data.
        
        Args:
            health_data: Dictionary containing health metrics, history, etc.
            
        Returns:
            Personalized health insights and recommendations
        """
        prompt = f"""
        Analyze this health data and provide personalized insights:
        
        {health_data}
        
        Provide:
        1. Overall health assessment
        2. Key trends or changes noted
        3. Areas doing well
        4. Areas that need attention
        5. Practical recommendations
        6. Questions to discuss with healthcare provider
        
        Be encouraging but honest about areas needing improvement.
        """
        
        return await self.analyze_text(prompt)
    
    async def translate_medical_content(self, content: str, target_language: str) -> str:
        """
        Translates medical content to another language.
        
        Args:
            content: Medical content to translate
            target_language: Target language
            
        Returns:
            Translated content
        """
        prompt = f"""
        Translate the following medical content to {target_language}.
        Maintain accuracy and use appropriate medical terminology in the target language.
        
        Content:
        {content}
        
        Translation:
        """
        
        return await self.analyze_text(prompt)
    
    async def summarize_for_doctor(self, health_history: Dict[str, Any]) -> str:
        """
        Creates a summary suitable for sharing with healthcare providers.
        
        Args:
            health_history: User's health history and recent data
            
        Returns:
            Professional summary for healthcare providers
        """
        prompt = f"""
        Create a concise, professional health summary suitable for a doctor's review:
        
        {health_history}
        
        Include:
        1. Chief concerns or reasons for visit
        2. Recent test results with dates
        3. Current medications
        4. Relevant medical history
        5. Symptoms or changes noted
        6. Questions from the patient
        
        Format this professionally as a medical summary.
        """
        
        return await self.analyze_text(prompt)
    
    async def check_symptom_severity(self, symptoms: List[str]) -> Dict[str, Any]:
        """
        Assesses symptom severity and urgency.
        
        Args:
            symptoms: List of reported symptoms
            
        Returns:
            Severity assessment and recommendations
        """
        prompt = f"""
        Assess these symptoms for severity and urgency:
        {', '.join(symptoms)}
        
        Provide:
        1. Severity level (low/moderate/high/emergency)
        2. Possible causes (common conditions only)
        3. Recommended actions
        4. When to seek immediate medical care
        
        Be cautious and recommend medical consultation when appropriate.
        Format response as JSON with keys: severity, possible_causes, actions, seek_care_if
        """
        
        response = await self.analyze_text(prompt)
        
        # Parse response
        try:
            import json
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            return {
                "severity": "unknown",
                "assessment": response,
                "recommendation": "Please consult a healthcare provider"
            }