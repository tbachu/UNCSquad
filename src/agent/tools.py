import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthAnalysisTools:
    """
    Collection of specialized tools for health data analysis.
    These tools are used by the executor to process specific types of health data.
    """
    
    @staticmethod
    def extract_lab_values(text: str) -> Dict[str, Dict[str, Any]]:
        """
        Extracts laboratory values from text.
        
        Returns:
            Dictionary with metric names as keys and value/unit/reference as values
        """
        lab_values = {}
        
        # Common lab test patterns
        patterns = {
            'hemoglobin': {
                'pattern': r'hemoglobin[:\s]+(\d+\.?\d*)\s*(g/dL|g/dl)?',
                'unit': 'g/dL',
                'normal_range': {'male': (13.5, 17.5), 'female': (12.0, 15.5)}
            },
            'glucose': {
                'pattern': r'glucose[:\s]+(\d+)\s*(mg/dL|mg/dl)?',
                'unit': 'mg/dL',
                'normal_range': {'fasting': (70, 100), 'random': (70, 140)}
            },
            'cholesterol': {
                'pattern': r'cholesterol[:\s]+(\d+)\s*(mg/dL|mg/dl)?',
                'unit': 'mg/dL',
                'normal_range': {'total': (0, 200)}
            },
            'ldl': {
                'pattern': r'ldl[:\s]+(\d+)\s*(mg/dL|mg/dl)?',
                'unit': 'mg/dL',
                'normal_range': {'optimal': (0, 100)}
            },
            'hdl': {
                'pattern': r'hdl[:\s]+(\d+)\s*(mg/dL|mg/dl)?',
                'unit': 'mg/dL',
                'normal_range': {'male': (40, float('inf')), 'female': (50, float('inf'))}
            },
            'triglycerides': {
                'pattern': r'triglycerides[:\s]+(\d+)\s*(mg/dL|mg/dl)?',
                'unit': 'mg/dL',
                'normal_range': {'normal': (0, 150)}
            },
            'blood_pressure': {
                'pattern': r'blood pressure[:\s]+(\d+/\d+)\s*(mmHg|mm Hg)?',
                'unit': 'mmHg',
                'normal_range': {'systolic': (90, 120), 'diastolic': (60, 80)}
            }
        }
        
        text_lower = text.lower()
        
        for test_name, config in patterns.items():
            match = re.search(config['pattern'], text_lower, re.IGNORECASE)
            if match:
                value = match.group(1)
                lab_values[test_name] = {
                    'value': value,
                    'unit': config['unit'],
                    'normal_range': config['normal_range'],
                    'timestamp': datetime.now().isoformat()
                }
                
                # Check if value is within normal range
                if test_name == 'blood_pressure':
                    systolic, diastolic = map(int, value.split('/'))
                    lab_values[test_name]['is_normal'] = (
                        config['normal_range']['systolic'][0] <= systolic <= config['normal_range']['systolic'][1] and
                        config['normal_range']['diastolic'][0] <= diastolic <= config['normal_range']['diastolic'][1]
                    )
                else:
                    try:
                        numeric_value = float(value)
                        # Use the first available range
                        range_key = list(config['normal_range'].keys())[0]
                        normal_range = config['normal_range'][range_key]
                        lab_values[test_name]['is_normal'] = (
                            normal_range[0] <= numeric_value <= normal_range[1]
                        )
                    except:
                        lab_values[test_name]['is_normal'] = None
        
        return lab_values
    
    @staticmethod
    def categorize_health_metrics(metrics: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Categorizes health metrics by type.
        
        Returns:
            Dictionary with categories as keys and metric names as values
        """
        categories = {
            'cardiovascular': ['blood_pressure', 'heart_rate', 'cholesterol', 'ldl', 'hdl', 'triglycerides'],
            'metabolic': ['glucose', 'hba1c', 'insulin', 'thyroid'],
            'hematology': ['hemoglobin', 'hematocrit', 'wbc', 'rbc', 'platelets'],
            'renal': ['creatinine', 'bun', 'egfr', 'uric_acid'],
            'hepatic': ['alt', 'ast', 'bilirubin', 'albumin'],
            'vitals': ['weight', 'height', 'bmi', 'temperature', 'oxygen_saturation']
        }
        
        categorized = {cat: [] for cat in categories}
        
        for metric in metrics:
            metric_lower = metric.lower()
            for category, keywords in categories.items():
                if any(keyword in metric_lower for keyword in keywords):
                    categorized[category].append(metric)
                    break
            else:
                # If no category matches, add to 'other'
                if 'other' not in categorized:
                    categorized['other'] = []
                categorized['other'].append(metric)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    @staticmethod
    def calculate_health_scores(metrics: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculates health scores based on metrics.
        
        Returns:
            Dictionary with health aspect scores (0-100)
        """
        scores = {}
        
        # Cardiovascular health score
        cardio_metrics = ['blood_pressure', 'cholesterol', 'ldl', 'hdl']
        cardio_values = [m for m in cardio_metrics if m in metrics and metrics[m].get('is_normal') is not None]
        
        if cardio_values:
            normal_count = sum(1 for m in cardio_values if metrics[m].get('is_normal', False))
            scores['cardiovascular'] = (normal_count / len(cardio_values)) * 100
        
        # Metabolic health score
        metabolic_metrics = ['glucose', 'hba1c']
        metabolic_values = [m for m in metabolic_metrics if m in metrics and metrics[m].get('is_normal') is not None]
        
        if metabolic_values:
            normal_count = sum(1 for m in metabolic_values if metrics[m].get('is_normal', False))
            scores['metabolic'] = (normal_count / len(metabolic_values)) * 100
        
        # Overall health score (average of all scores)
        if scores:
            scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    @staticmethod
    def generate_health_recommendations(metrics: Dict[str, Dict[str, Any]], 
                                      scores: Dict[str, float]) -> List[Dict[str, str]]:
        """
        Generates health recommendations based on metrics and scores.
        
        Returns:
            List of recommendations with priority levels
        """
        recommendations = []
        
        # Check individual metrics
        for metric, data in metrics.items():
            if not data.get('is_normal', True):
                if metric == 'blood_pressure':
                    value = data['value']
                    recommendations.append({
                        'type': 'metric',
                        'metric': metric,
                        'priority': 'high',
                        'recommendation': f"Your blood pressure ({value}) is outside the normal range. Consider lifestyle changes and consult your doctor.",
                        'actions': ['Monitor daily', 'Reduce sodium intake', 'Exercise regularly']
                    })
                elif metric == 'glucose':
                    recommendations.append({
                        'type': 'metric',
                        'metric': metric,
                        'priority': 'high',
                        'recommendation': "Your glucose levels need attention. Monitor your diet and consult your doctor.",
                        'actions': ['Monitor blood sugar', 'Follow diabetic diet', 'Regular check-ups']
                    })
                elif metric in ['cholesterol', 'ldl']:
                    recommendations.append({
                        'type': 'metric',
                        'metric': metric,
                        'priority': 'medium',
                        'recommendation': "Your cholesterol levels could be improved. Consider dietary changes.",
                        'actions': ['Reduce saturated fats', 'Increase fiber intake', 'Exercise regularly']
                    })
        
        # Check scores
        for aspect, score in scores.items():
            if score < 70:
                recommendations.append({
                    'type': 'score',
                    'aspect': aspect,
                    'priority': 'medium' if score >= 50 else 'high',
                    'recommendation': f"Your {aspect} health score ({score:.0f}/100) needs improvement.",
                    'actions': ['Schedule check-up', 'Review lifestyle habits']
                })
        
        return recommendations
    
    @staticmethod
    def identify_health_patterns(historical_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Identifies patterns in historical health data.
        
        Returns:
            Dictionary with identified patterns and insights
        """
        patterns = {
            'trends': {},
            'volatility': {},
            'correlations': []
        }
        
        for metric, history in historical_data.items():
            if len(history) < 3:
                continue
                
            values = []
            for h in history:
                try:
                    # Handle blood pressure specially
                    if '/' in str(h['value']):
                        values.append(float(h['value'].split('/')[0]))
                    else:
                        values.append(float(h['value']))
                except:
                    continue
            
            if len(values) < 3:
                continue
            
            # Trend analysis
            if values[-1] > values[0] * 1.1:
                patterns['trends'][metric] = 'increasing'
            elif values[-1] < values[0] * 0.9:
                patterns['trends'][metric] = 'decreasing'
            else:
                patterns['trends'][metric] = 'stable'
            
            # Volatility analysis
            if len(values) > 1:
                avg = sum(values) / len(values)
                variance = sum((x - avg) ** 2 for x in values) / len(values)
                std_dev = variance ** 0.5
                cv = (std_dev / avg) * 100 if avg != 0 else 0
                
                if cv > 20:
                    patterns['volatility'][metric] = 'high'
                elif cv > 10:
                    patterns['volatility'][metric] = 'moderate'
                else:
                    patterns['volatility'][metric] = 'low'
        
        return patterns
    
    @staticmethod
    def format_health_timeline(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Formats health events into a timeline.
        
        Returns:
            Sorted list of health events with formatted descriptions
        """
        timeline = []
        
        for event in events:
            formatted_event = {
                'timestamp': event.get('timestamp', datetime.now().isoformat()),
                'type': event.get('type', 'unknown'),
                'title': event.get('title', 'Health Event'),
                'description': event.get('description', ''),
                'importance': event.get('importance', 'normal')
            }
            
            # Add icon based on type
            type_icons = {
                'lab_result': '🔬',
                'medication': '💊',
                'appointment': '👩‍⚕️',
                'symptom': '🌡️',
                'measurement': '📊'
            }
            
            formatted_event['icon'] = type_icons.get(
                formatted_event['type'], '📝'
            )
            
            timeline.append(formatted_event)
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return timeline