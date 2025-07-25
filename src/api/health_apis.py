import logging
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthAPIClient:
    """
    Client for interacting with various health-related APIs.
    Provides drug interaction checking, medication information, and health databases.
    """
    
    def __init__(self):
        # API endpoints for health services
        self.drug_interaction_api = "https://rxnav.nlm.nih.gov/REST"
        self.openfda_api = "https://api.fda.gov/drug"
        
        # Cache for API responses
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    async def check_drug_interactions(self, medications: List[str]) -> List[Dict[str, Any]]:
        """
        Checks for drug interactions between medications.
        
        Args:
            medications: List of medication names
            
        Returns:
            List of interaction warnings
        """
        if len(medications) < 2:
            return []
        
        interactions = []
        
        try:
            # Get RxCUI codes for medications
            rxcuis = []
            for med in medications:
                rxcui = await self._get_rxcui(med)
                if rxcui:
                    rxcuis.append((med, rxcui))
            
            # Check interactions between all pairs
            for i in range(len(rxcuis)):
                for j in range(i + 1, len(rxcuis)):
                    med1_name, rxcui1 = rxcuis[i]
                    med2_name, rxcui2 = rxcuis[j]
                    
                    interaction = await self._check_interaction_pair(
                        rxcui1, rxcui2, med1_name, med2_name
                    )
                    if interaction:
                        interactions.extend(interaction)
            
        except Exception as e:
            logger.error(f"Error checking drug interactions: {str(e)}")
            # Return a safe default response
            interactions.append({
                "severity": "unknown",
                "description": "Unable to check interactions. Please consult your pharmacist.",
                "medications": medications
            })
        
        return interactions
    
    async def get_medication_info(self, medications: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Gets detailed information about medications.
        
        Args:
            medications: List of medication names
            
        Returns:
            Dictionary with medication information
        """
        med_info = {}
        
        for medication in medications:
            cache_key = f"med_info_{medication}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_ttl:
                    med_info[medication] = cached_data
                    continue
            
            try:
                # Get basic medication info from OpenFDA
                info = await self._get_openfda_info(medication)
                
                if not info:
                    # Fallback to basic info
                    info = {
                        "name": medication,
                        "description": "Medication information not available",
                        "warnings": ["Always follow your doctor's instructions"],
                        "usage": "Take as directed by your healthcare provider"
                    }
                
                med_info[medication] = info
                self.cache[cache_key] = (info, datetime.now())
                
            except Exception as e:
                logger.error(f"Error getting info for {medication}: {str(e)}")
                med_info[medication] = {
                    "name": medication,
                    "error": "Information temporarily unavailable"
                }
        
        return med_info
    
    async def _get_rxcui(self, medication_name: str) -> Optional[str]:
        """Gets RxCUI code for a medication name."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.drug_interaction_api}/rxcui.json"
                params = {"name": medication_name}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        id_group = data.get('idGroup', {})
                        if 'rxnormId' in id_group:
                            return id_group['rxnormId'][0]
            
        except Exception as e:
            logger.error(f"Error getting RxCUI for {medication_name}: {str(e)}")
        
        return None
    
    async def _check_interaction_pair(self, rxcui1: str, rxcui2: str, 
                                    med1_name: str, med2_name: str) -> List[Dict[str, Any]]:
        """Checks interaction between two medications."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.drug_interaction_api}/interaction/list.json"
                params = {"rxcuis": f"{rxcui1}+{rxcui2}"}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        interactions = []
                        for interaction_group in data.get('fullInteractionTypeGroup', []):
                            for interaction_type in interaction_group.get('fullInteractionType', []):
                                for interaction in interaction_type.get('interactionPair', []):
                                    severity = interaction.get('severity', 'unknown')
                                    description = interaction.get('description', 'Interaction detected')
                                    
                                    interactions.append({
                                        "severity": severity,
                                        "description": description,
                                        "medications": [med1_name, med2_name],
                                        "source": "RxNav"
                                    })
                        
                        return interactions
            
        except Exception as e:
            logger.error(f"Error checking interaction between {med1_name} and {med2_name}: {str(e)}")
        
        return []
    
    async def _get_openfda_info(self, medication_name: str) -> Optional[Dict[str, Any]]:
        """Gets medication information from OpenFDA."""
        try:
            async with aiohttp.ClientSession() as session:
                # Search for drug label information
                url = f"{self.openfda_api}/label.json"
                params = {
                    "search": f'brand_name:"{medication_name}" OR generic_name:"{medication_name}"',
                    "limit": 1
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', [])
                        
                        if results:
                            result = results[0]
                            return {
                                "name": medication_name,
                                "brand_name": result.get('openfda', {}).get('brand_name', [medication_name])[0],
                                "generic_name": result.get('openfda', {}).get('generic_name', [''])[0],
                                "purpose": self._extract_first(result.get('purpose', [])),
                                "warnings": result.get('warnings', [])[:3],  # Top 3 warnings
                                "usage": self._extract_first(result.get('indications_and_usage', [])),
                                "dosage": self._extract_first(result.get('dosage_and_administration', [])),
                                "side_effects": self._extract_first(result.get('adverse_reactions', [])),
                                "manufacturer": result.get('openfda', {}).get('manufacturer_name', ['Unknown'])[0]
                            }
            
        except Exception as e:
            logger.error(f"Error getting OpenFDA info for {medication_name}: {str(e)}")
        
        return None
    
    def _extract_first(self, items: List[str]) -> str:
        """Extracts and cleans the first item from a list."""
        if items and len(items) > 0:
            # Clean up the text
            text = items[0]
            # Limit length
            if len(text) > 500:
                text = text[:497] + "..."
            return text
        return "Information not available"
    
    async def get_vaccine_recommendations(self, age: int, conditions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Gets vaccine recommendations based on age and conditions.
        
        Args:
            age: Patient age
            conditions: List of medical conditions
            
        Returns:
            List of recommended vaccines
        """
        # Basic CDC vaccine schedule (simplified)
        recommendations = []
        
        # Adult vaccines
        if age >= 18:
            recommendations.extend([
                {
                    "vaccine": "Influenza (Flu)",
                    "frequency": "Yearly",
                    "reason": "Annual protection against seasonal flu"
                },
                {
                    "vaccine": "Tdap/Td",
                    "frequency": "Tdap once, then Td every 10 years",
                    "reason": "Protection against tetanus, diphtheria, and pertussis"
                }
            ])
            
            if age >= 50:
                recommendations.append({
                    "vaccine": "Shingles (Zoster)",
                    "frequency": "2 doses",
                    "reason": "Protection against shingles"
                })
            
            if age >= 65:
                recommendations.extend([
                    {
                        "vaccine": "Pneumococcal",
                        "frequency": "1-2 doses",
                        "reason": "Protection against pneumonia"
                    },
                    {
                        "vaccine": "RSV",
                        "frequency": "Single dose",
                        "reason": "Protection against respiratory syncytial virus"
                    }
                ])
        
        # Condition-based recommendations
        if conditions:
            conditions_lower = [c.lower() for c in conditions]
            
            if any('diabetes' in c for c in conditions_lower):
                recommendations.append({
                    "vaccine": "Hepatitis B",
                    "frequency": "3 doses",
                    "reason": "Recommended for adults with diabetes"
                })
            
            if any('asthma' in c or 'copd' in c for c in conditions_lower):
                recommendations.append({
                    "vaccine": "Pneumococcal",
                    "frequency": "May need earlier than 65",
                    "reason": "Recommended for chronic lung conditions"
                })
        
        return recommendations
    
    async def check_lab_reference_ranges(self, lab_name: str, value: float, 
                                       age: int = None, gender: str = None) -> Dict[str, Any]:
        """
        Checks if a lab value is within normal reference range.
        
        Args:
            lab_name: Name of the lab test
            value: Test result value
            age: Patient age (optional)
            gender: Patient gender (optional)
            
        Returns:
            Reference range and interpretation
        """
        # Common reference ranges (simplified)
        reference_ranges = {
            "glucose": {"low": 70, "high": 100, "unit": "mg/dL", "fasting": True},
            "cholesterol": {"low": 0, "high": 200, "unit": "mg/dL"},
            "ldl": {"low": 0, "high": 100, "unit": "mg/dL"},
            "hdl": {
                "male": {"low": 40, "high": float('inf'), "unit": "mg/dL"},
                "female": {"low": 50, "high": float('inf'), "unit": "mg/dL"}
            },
            "triglycerides": {"low": 0, "high": 150, "unit": "mg/dL"},
            "hemoglobin": {
                "male": {"low": 13.5, "high": 17.5, "unit": "g/dL"},
                "female": {"low": 12.0, "high": 15.5, "unit": "g/dL"}
            },
            "blood_pressure_systolic": {"low": 90, "high": 120, "unit": "mmHg"},
            "blood_pressure_diastolic": {"low": 60, "high": 80, "unit": "mmHg"},
            "bmi": {"low": 18.5, "high": 24.9, "unit": "kg/m²"}
        }
        
        lab_lower = lab_name.lower()
        
        if lab_lower in reference_ranges:
            ranges = reference_ranges[lab_lower]
            
            # Handle gender-specific ranges
            if isinstance(ranges, dict) and gender and gender.lower() in ranges:
                ranges = ranges[gender.lower()]
            
            low = ranges.get('low', 0)
            high = ranges.get('high', float('inf'))
            unit = ranges.get('unit', '')
            
            status = "normal"
            if value < low:
                status = "low"
            elif value > high:
                status = "high"
            
            interpretation = {
                "value": value,
                "unit": unit,
                "range": f"{low} - {high}",
                "status": status,
                "interpretation": self._interpret_lab_value(lab_lower, status, value, low, high)
            }
            
            return interpretation
        
        return {
            "value": value,
            "status": "unknown",
            "interpretation": "Reference range not available. Please consult your healthcare provider."
        }
    
    def _interpret_lab_value(self, lab_name: str, status: str, value: float, 
                           low: float, high: float) -> str:
        """Provides interpretation of lab values."""
        if status == "normal":
            return f"Your {lab_name} level is within the normal range."
        
        interpretations = {
            "glucose": {
                "high": "Elevated glucose may indicate diabetes or prediabetes. Follow up with your doctor.",
                "low": "Low glucose levels can be dangerous. If you have symptoms, seek immediate care."
            },
            "cholesterol": {
                "high": "High cholesterol increases cardiovascular risk. Consider dietary changes and consult your doctor.",
                "low": "Low cholesterol is generally not concerning."
            },
            "hemoglobin": {
                "high": "Elevated hemoglobin may indicate dehydration or other conditions.",
                "low": "Low hemoglobin suggests anemia. Further evaluation recommended."
            }
        }
        
        if lab_name in interpretations and status in interpretations[lab_name]:
            return interpretations[lab_name][status]
        
        if status == "high":
            return f"Your {lab_name} level ({value}) is above the normal range ({low}-{high}). Please discuss with your doctor."
        else:
            return f"Your {lab_name} level ({value}) is below the normal range ({low}-{high}). Please discuss with your doctor."