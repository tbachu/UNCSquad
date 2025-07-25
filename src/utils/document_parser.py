import logging
import io
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import PyPDF2
import pytesseract
from PIL import Image
import docx
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Parses various medical document formats including PDFs, images, and text files.
    Extracts text and structured information from medical documents.
    """
    
    def __init__(self):
        self.supported_formats = {
            '.pdf': self._parse_pdf,
            '.png': self._parse_image,
            '.jpg': self._parse_image,
            '.jpeg': self._parse_image,
            '.tiff': self._parse_image,
            '.bmp': self._parse_image,
            '.docx': self._parse_docx,
            '.txt': self._parse_text
        }
        
        # Common medical document patterns
        self.patterns = {
            'date': r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
            'patient_name': r'Patient(?:\s+Name)?:\s*([A-Za-z\s]+)',
            'doctor_name': r'(?:Dr\.|Doctor|Physician):\s*([A-Za-z\s]+)',
            'medical_record_number': r'MRN?:\s*(\d+)',
            'lab_result': r'([A-Za-z\s]+):\s*(\d+\.?\d*)\s*([A-Za-z/%]+)?'
        }
    
    async def parse_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parses a medical document and extracts text and structured information.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        logger.info(f"Parsing document: {file_path}")
        
        # Parse the document
        parser_func = self.supported_formats[file_extension]
        raw_text = await parser_func(file_path)
        
        # Extract structured information
        metadata = self._extract_metadata(raw_text)
        
        # Clean and structure the text
        cleaned_text = self._clean_text(raw_text)
        
        return {
            "file_path": str(file_path),
            "file_type": file_extension,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "metadata": metadata,
            "extracted_values": self._extract_medical_values(cleaned_text),
            "sections": self._identify_sections(cleaned_text)
        }
    
    async def _parse_pdf(self, file_path: Path) -> str:
        """Extracts text from PDF files."""
        text_content = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            # Try OCR as fallback
            return await self._parse_pdf_with_ocr(file_path)
    
    async def _parse_pdf_with_ocr(self, file_path: Path) -> str:
        """Fallback OCR for PDFs that can't be parsed normally."""
        try:
            # Convert PDF pages to images and OCR them
            from pdf2image import convert_from_path
            
            images = convert_from_path(file_path)
            text_content = []
            
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                text_content.append(f"--- Page {i + 1} ---\n{text}")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error in PDF OCR: {str(e)}")
            return "Unable to extract text from PDF"
    
    async def _parse_image(self, file_path: Path) -> str:
        """Extracts text from image files using OCR."""
        try:
            image = Image.open(file_path)
            
            # Preprocess image for better OCR
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image, config='--psm 3')
            
            return text
            
        except Exception as e:
            logger.error(f"Error parsing image: {str(e)}")
            return "Unable to extract text from image"
    
    async def _parse_docx(self, file_path: Path) -> str:
        """Extracts text from Word documents."""
        try:
            doc = docx.Document(file_path)
            
            text_content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_content.append(" | ".join(row_text))
            
            return "\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}")
            return "Unable to extract text from document"
    
    async def _parse_text(self, file_path: Path) -> str:
        """Reads plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            return "Unable to read text file"
    
    def _clean_text(self, text: str) -> str:
        """Cleans and normalizes extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep medical symbols
        text = re.sub(r'[^\w\s\-.,/:;()%°]', ' ', text)
        
        # Fix common OCR errors
        ocr_corrections = {
            r'\bl\b': '1',  # lowercase L to 1
            r'\bO\b': '0',  # uppercase O to 0
            r'l\/': '1/',    # l/ to 1/
        }
        
        for pattern, replacement in ocr_corrections.items():
            text = re.sub(pattern, replacement, text)
        
        return text.strip()
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extracts metadata from document text."""
        metadata = {}
        
        # Extract dates
        date_matches = re.findall(self.patterns['date'], text)
        if date_matches:
            metadata['dates'] = date_matches
            # Try to identify report date
            report_date_pattern = r'(?:Report|Test|Lab)\s+Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
            report_date = re.search(report_date_pattern, text, re.IGNORECASE)
            if report_date:
                metadata['report_date'] = report_date.group(1)
        
        # Extract patient name
        patient_match = re.search(self.patterns['patient_name'], text, re.IGNORECASE)
        if patient_match:
            metadata['patient_name'] = patient_match.group(1).strip()
        
        # Extract doctor name
        doctor_match = re.search(self.patterns['doctor_name'], text, re.IGNORECASE)
        if doctor_match:
            metadata['doctor_name'] = doctor_match.group(1).strip()
        
        # Extract MRN
        mrn_match = re.search(self.patterns['medical_record_number'], text, re.IGNORECASE)
        if mrn_match:
            metadata['mrn'] = mrn_match.group(1)
        
        return metadata
    
    def _extract_medical_values(self, text: str) -> List[Dict[str, Any]]:
        """Extracts medical test values from text."""
        values = []
        
        # Common medical test patterns
        test_patterns = [
            # Blood tests
            (r'(?:Hemoglobin|Hgb|HGB)[:\s]+(\d+\.?\d*)\s*(g/dL|g/dl)?', 'Hemoglobin'),
            (r'(?:Glucose|GLU)[:\s]+(\d+)\s*(mg/dL|mg/dl)?', 'Glucose'),
            (r'(?:Total\s+)?Cholesterol[:\s]+(\d+)\s*(mg/dL|mg/dl)?', 'Cholesterol'),
            (r'LDL[:\s]+(\d+)\s*(mg/dL|mg/dl)?', 'LDL'),
            (r'HDL[:\s]+(\d+)\s*(mg/dL|mg/dl)?', 'HDL'),
            (r'Triglycerides[:\s]+(\d+)\s*(mg/dL|mg/dl)?', 'Triglycerides'),
            (r'(?:Blood\s+)?Pressure[:\s]+(\d+/\d+)\s*(mmHg)?', 'Blood Pressure'),
            # Additional tests
            (r'(?:WBC|White\s+Blood\s+Cells?)[:\s]+(\d+\.?\d*)\s*(K/uL|cells/uL)?', 'WBC'),
            (r'(?:RBC|Red\s+Blood\s+Cells?)[:\s]+(\d+\.?\d*)\s*(M/uL)?', 'RBC'),
            (r'Platelets?[:\s]+(\d+)\s*(K/uL)?', 'Platelets'),
            (r'Creatinine[:\s]+(\d+\.?\d*)\s*(mg/dL|mg/dl)?', 'Creatinine'),
            (r'(?:ALT|SGPT)[:\s]+(\d+)\s*(U/L|IU/L)?', 'ALT'),
            (r'(?:AST|SGOT)[:\s]+(\d+)\s*(U/L|IU/L)?', 'AST'),
        ]
        
        for pattern, test_name in test_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value_dict = {
                    'test_name': test_name,
                    'value': match.group(1),
                    'unit': match.group(2) if match.lastindex >= 2 else None,
                    'position': match.start()
                }
                values.append(value_dict)
        
        # Sort by position in document
        values.sort(key=lambda x: x['position'])
        
        # Remove position from final output
        for v in values:
            v.pop('position', None)
        
        return values
    
    def _identify_sections(self, text: str) -> Dict[str, str]:
        """Identifies common sections in medical documents."""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'chief_complaint': r'(?:Chief\s+Complaint|CC|Reason\s+for\s+Visit)[:\s]+(.*?)(?=\n[A-Z]|\n\n|\Z)',
            'history': r'(?:History|HPI|Past\s+Medical\s+History)[:\s]+(.*?)(?=\n[A-Z]|\n\n|\Z)',
            'medications': r'(?:Medications?|Current\s+Medications?|Meds)[:\s]+(.*?)(?=\n[A-Z]|\n\n|\Z)',
            'allergies': r'(?:Allergies|Drug\s+Allergies)[:\s]+(.*?)(?=\n[A-Z]|\n\n|\Z)',
            'assessment': r'(?:Assessment|Impression|Diagnosis)[:\s]+(.*?)(?=\n[A-Z]|\n\n|\Z)',
            'plan': r'(?:Plan|Treatment\s+Plan|Recommendations?)[:\s]+(.*?)(?=\n[A-Z]|\n\n|\Z)',
            'lab_results': r'(?:Lab\s+Results?|Laboratory\s+Results?)[:\s]+(.*?)(?=\n[A-Z]|\n\n|\Z)',
            'vital_signs': r'(?:Vital\s+Signs?|Vitals)[:\s]+(.*?)(?=\n[A-Z]|\n\n|\Z)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                # Limit section length
                if len(content) > 1000:
                    content = content[:997] + "..."
                sections[section_name] = content
        
        return sections
    
    async def extract_medications_from_document(self, file_path: Union[str, Path]) -> List[Dict[str, str]]:
        """
        Specifically extracts medication information from a document.
        
        Returns:
            List of medications with dosage and frequency
        """
        document_data = await self.parse_document(file_path)
        text = document_data['cleaned_text']
        
        medications = []
        
        # Medication patterns
        med_patterns = [
            # Standard format: Drug name dose frequency
            r'([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(\d+\.?\d*\s*(?:mg|mcg|g|ml|units?))\s+([A-Za-z\s]+(?:daily|BID|TID|QID|PRN))',
            # Alternative format
            r'([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+-\s+(\d+\.?\d*\s*(?:mg|mcg|g|ml|units?))',
        ]
        
        for pattern in med_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                med = {
                    'name': match.group(1).strip(),
                    'dosage': match.group(2).strip() if match.lastindex >= 2 else 'Unknown',
                    'frequency': match.group(3).strip() if match.lastindex >= 3 else 'As directed'
                }
                
                # Avoid duplicates
                if not any(m['name'].lower() == med['name'].lower() for m in medications):
                    medications.append(med)
        
        return medications