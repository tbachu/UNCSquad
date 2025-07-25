import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

from .planner import Task, TaskType
from .memory import HealthMemoryStore
from src.api.gemini_client import GeminiClient
from src.api.health_apis import HealthAPIClient
from src.utils.document_parser import DocumentParser
from src.utils.visualizations import HealthVisualizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    task_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthAgentExecutor:
    """
    Executes tasks planned by the HealthAgentPlanner.
    Integrates with Gemini API and other tools to process health data.
    """
    
    def __init__(self, gemini_api_key: str, memory_store: HealthMemoryStore):
        self.gemini_client = GeminiClient(api_key=gemini_api_key)
        self.memory_store = memory_store
        self.health_api = HealthAPIClient()
        self.doc_parser = DocumentParser()
        self.visualizer = HealthVisualizer()
        self.task_results: Dict[str, TaskResult] = {}
        
    async def execute_tasks(self, tasks: List[Task]) -> List[TaskResult]:
        """
        Executes a list of tasks, respecting dependencies.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            List of task results
        """
        results = []
        
        # Sort tasks by dependencies
        sorted_tasks = self._sort_by_dependencies(tasks)
        
        for task in sorted_tasks:
            # Wait for dependencies
            await self._wait_for_dependencies(task)
            
            # Execute task
            logger.info(f"Executing task {task.id}: {task.description}")
            result = await self._execute_single_task(task)
            
            self.task_results[task.id] = result
            results.append(result)
            
            # Store result in memory if successful
            if result.success and result.result:
                await self.memory_store.store_task_result(task, result)
                
        return results
    
    async def _execute_single_task(self, task: Task) -> TaskResult:
        """Executes a single task based on its type."""
        try:
            if task.type == TaskType.DOCUMENT_ANALYSIS:
                result = await self._execute_document_analysis(task)
            elif task.type == TaskType.HEALTH_QUERY:
                result = await self._execute_health_query(task)
            elif task.type == TaskType.TREND_ANALYSIS:
                result = await self._execute_trend_analysis(task)
            elif task.type == TaskType.MEDICATION_CHECK:
                result = await self._execute_medication_check(task)
            elif task.type == TaskType.REPORT_GENERATION:
                result = await self._execute_report_generation(task)
            elif task.type == TaskType.DATA_VISUALIZATION:
                result = await self._execute_visualization(task)
            else:
                raise ValueError(f"Unknown task type: {task.type}")
                
            return TaskResult(
                task_id=task.id,
                success=True,
                result=result,
                metadata={"task_type": task.type.value}
            )
            
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {str(e)}")
            return TaskResult(
                task_id=task.id,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def _execute_document_analysis(self, task: Task) -> Dict[str, Any]:
        """Analyzes medical documents using Gemini's multimodal capabilities."""
        params = task.parameters
        file_path = params.get('file_path')
        
        if not file_path:
            raise ValueError("No file path provided for document analysis")
        
        logger.info(f"Starting document analysis for: {file_path}")
        
        # Parse document (PDF or image)
        document_content = await self.doc_parser.parse_document(file_path)
        
        logger.info(f"Document parsed successfully. Text length: {len(document_content.get('cleaned_text', ''))}")
        
        # Check if we got meaningful content
        cleaned_text = document_content.get('cleaned_text', '')
        if len(cleaned_text.strip()) < 10:
            logger.warning("Very little text extracted from document")
            return {
                "analysis": "Unable to extract sufficient text from document for analysis",
                "metrics": {},
                "document_type": "unknown",
                "parsing_notes": document_content.get('parsing_notes', [])
            }
        
        # Use the already extracted values from document parser
        extracted_values = document_content.get('extracted_values', [])
        
        # Convert to metrics format - handle duplicates by using unique keys
        metrics = {}
        seen_tests = {}  # Track how many times we've seen each test
        
        for value in extracted_values:
            test_name = value.get('test_name', '').strip()
            if not test_name:
                continue
                
            # Create unique key for metrics
            base_key = test_name.lower().replace(' ', '_').replace('-', '_')
            
            # Handle duplicates by adding a counter
            if base_key in seen_tests:
                seen_tests[base_key] += 1
                unique_key = f"{base_key}_{seen_tests[base_key]}"
            else:
                seen_tests[base_key] = 0
                unique_key = base_key
            
            metrics[unique_key] = {
                'value': value.get('value'),
                'unit': value.get('unit', ''),
                'name': test_name
            }
        
        logger.info(f"Extracted {len(metrics)} metrics from document parser")
        
        # Use Gemini to analyze the document content
        prompt = f"""
        Analyze this medical document and provide:
        1. A clear summary of key findings
        2. Explanation of any medical terms in simple language
        3. Identification of concerning values or findings
        4. General health insights based on the data
        
        Document content:
        Raw text: {cleaned_text[:2000]}...
        
        Already extracted metrics: {extracted_values}
        
        Provide a comprehensive but concise analysis.
        """
        
        try:
            analysis = await self.gemini_client.analyze_text(prompt)
            logger.info("Gemini analysis completed successfully")
        except Exception as e:
            logger.error(f"Gemini analysis failed: {str(e)}")
            analysis = f"AI analysis unavailable: {str(e)}. However, basic metrics were extracted from the document."
        
        # Also try to extract additional metrics from Gemini's analysis
        gemini_metrics = self._extract_health_metrics(analysis)
        logger.info(f"Extracted {len(gemini_metrics)} additional metrics from Gemini analysis")
        
        # Merge metrics from document parser and Gemini
        all_metrics = {**metrics, **gemini_metrics}
        
        # Store metrics in memory
        if all_metrics:
            try:
                await self.memory_store.store_health_metrics(all_metrics)
                logger.info(f"Stored {len(all_metrics)} metrics in memory")
            except Exception as e:
                logger.error(f"Failed to store metrics: {str(e)}")
        
        return {
            "analysis": analysis,
            "metrics": all_metrics,
            "document_type": self._identify_document_type(cleaned_text),
            "parsing_notes": document_content.get('parsing_notes', []),
            "raw_metrics_count": len(extracted_values),
            "gemini_metrics_count": len(gemini_metrics)
        }
    
    async def _execute_health_query(self, task: Task) -> Dict[str, Any]:
        """Answers health-related questions using Gemini and stored data."""
        query = task.parameters.get('query')
        
        # Get relevant context from memory
        context = await self.memory_store.get_relevant_context(query)
        
        # Construct prompt with context
        prompt = f"""
        Answer this health question based on the user's medical history and general medical knowledge.
        Always provide accurate, helpful information while reminding users to consult healthcare professionals.
        
        User's health context:
        {json.dumps(context, indent=2)}
        
        Question: {query}
        
        Provide:
        1. Direct answer to the question
        2. Relevant context from user's health data
        3. General medical information
        4. Recommendations or next steps
        5. Sources or references when applicable
        """
        
        response = await self.gemini_client.analyze_text(prompt)
        
        return {
            "answer": response,
            "context_used": context,
            "query": query
        }
    
    async def _execute_trend_analysis(self, task: Task) -> Dict[str, Any]:
        """Analyzes health trends over time."""
        # Get historical data from memory
        metrics = task.parameters.get('metrics', ['all'])
        time_period = task.parameters.get('time_period', 'all')
        
        historical_data = await self.memory_store.get_historical_metrics(
            metrics=metrics,
            time_period=time_period
        )
        
        if not historical_data:
            return {
                "trends": [],
                "insights": "No historical data available for trend analysis."
            }
        
        # Generate visualizations
        charts = self.visualizer.create_trend_charts(historical_data)
        
        # Use Gemini to generate insights
        prompt = f"""
        Analyze these health metrics trends and provide insights:
        
        Historical data:
        {json.dumps(historical_data, indent=2)}
        
        Provide:
        1. Key trends identified (improving, declining, stable)
        2. Significant changes or patterns
        3. Health implications of these trends
        4. Recommendations based on trends
        5. Areas that need attention
        """
        
        insights = await self.gemini_client.analyze_text(prompt)
        
        return {
            "trends": historical_data,
            "insights": insights,
            "visualizations": charts
        }
    
    async def _execute_medication_check(self, task: Task) -> Dict[str, Any]:
        """Checks medication interactions and provides information."""
        input_text = task.parameters.get('input')
        
        # Extract medication names
        medications = await self._extract_medications(input_text)
        
        # Check for interactions
        interactions = await self.health_api.check_drug_interactions(medications)
        
        # Get medication information
        med_info = await self.health_api.get_medication_info(medications)
        
        # Use Gemini to provide comprehensive analysis
        prompt = f"""
        Provide a comprehensive analysis of these medications:
        
        Medications: {', '.join(medications)}
        Interactions found: {json.dumps(interactions, indent=2)}
        Medication info: {json.dumps(med_info, indent=2)}
        
        Include:
        1. Summary of each medication's purpose
        2. Important interactions and warnings
        3. Common side effects
        4. Best practices for taking these medications
        5. Questions to ask the doctor
        """
        
        analysis = await self.gemini_client.analyze_text(prompt)
        
        return {
            "medications": medications,
            "interactions": interactions,
            "information": med_info,
            "analysis": analysis
        }
    
    async def _execute_report_generation(self, task: Task) -> Dict[str, Any]:
        """Generates a comprehensive health report."""
        # Gather all relevant data
        recent_results = {}
        for dep_id in task.dependencies:
            if dep_id in self.task_results:
                recent_results[dep_id] = self.task_results[dep_id].result
        
        # Get user's health summary from memory
        health_summary = await self.memory_store.get_health_summary()
        
        # Generate report using Gemini
        prompt = f"""
        Generate a comprehensive health report for a doctor's visit based on:
        
        Recent analysis results:
        {json.dumps(recent_results, indent=2)}
        
        Health summary:
        {json.dumps(health_summary, indent=2)}
        
        Create a professional report including:
        1. Current health status summary
        2. Recent test results and their implications
        3. Medication list and compliance
        4. Health trends and changes
        5. Questions and concerns for the doctor
        6. Recommended follow-ups or tests
        
        Format this for easy printing and sharing.
        """
        
        report = await self.gemini_client.analyze_text(prompt)
        
        # Generate PDF version
        pdf_path = await self.visualizer.generate_report_pdf(report, health_summary)
        
        return {
            "report": report,
            "pdf_path": pdf_path,
            "summary": health_summary
        }
    
    async def _execute_visualization(self, task: Task) -> Dict[str, Any]:
        """Creates health data visualizations."""
        data_type = task.parameters.get('data_type')
        time_range = task.parameters.get('time_range', 'all')
        
        # Get data from memory
        data = await self.memory_store.get_metrics_for_visualization(
            data_type=data_type,
            time_range=time_range
        )
        
        # Create visualizations
        charts = self.visualizer.create_health_dashboard(data)
        
        return {
            "charts": charts,
            "data": data
        }
    
    def _sort_by_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Sorts tasks based on their dependencies."""
        sorted_tasks = []
        remaining = tasks.copy()
        
        while remaining:
            # Find tasks with no dependencies or dependencies already satisfied
            ready = [t for t in remaining if all(
                dep in [st.id for st in sorted_tasks] 
                for dep in t.dependencies
            )]
            
            if not ready:
                # Circular dependency or missing dependency
                logger.warning("Circular or missing dependencies detected")
                sorted_tasks.extend(remaining)
                break
                
            sorted_tasks.extend(ready)
            for t in ready:
                remaining.remove(t)
                
        return sorted_tasks
    
    async def _wait_for_dependencies(self, task: Task):
        """Waits for task dependencies to complete."""
        for dep_id in task.dependencies:
            while dep_id not in self.task_results:
                await asyncio.sleep(0.1)
    
    def _extract_health_metrics(self, analysis: str) -> Dict[str, Any]:
        """Extracts structured health metrics from analysis text."""
        metrics = {}
        
        # Enhanced pattern matching for various metric formats
        metric_patterns = {
            'cholesterol': [
                r'cholesterol[:\s]+(\d+\.?\d*)\s*(mg/dl|mg/dL)?',
                r'total cholesterol[:\s]+(\d+\.?\d*)',
                r'chol[:\s]+(\d+\.?\d*)'
            ],
            'blood_pressure': [
                r'blood pressure[:\s]+(\d+/\d+)\s*(mmHg)?',
                r'bp[:\s]+(\d+/\d+)',
                r'systolic[:\s]+(\d+)[^\d]*diastolic[:\s]+(\d+)',
                r'(\d+/\d+)\s*mmHg'
            ],
            'glucose': [
                r'glucose[:\s]+(\d+\.?\d*)\s*(mg/dl|mg/dL)?',
                r'blood glucose[:\s]+(\d+\.?\d*)',
                r'sugar[:\s]+(\d+\.?\d*)',
                r'fasting glucose[:\s]+(\d+\.?\d*)'
            ],
            'hemoglobin': [
                r'hemoglobin[:\s]+(\d+\.?\d*)\s*(g/dl|g/dL)?',
                r'hgb[:\s]+(\d+\.?\d*)',
                r'hb[:\s]+(\d+\.?\d*)'
            ],
            'hba1c': [
                r'hba1c[:\s]+(\d+\.?\d*)\s*%?',
                r'a1c[:\s]+(\d+\.?\d*)',
                r'glycated hemoglobin[:\s]+(\d+\.?\d*)'
            ],
            'ldl': [
                r'ldl[:\s]+(\d+\.?\d*)\s*(mg/dl|mg/dL)?',
                r'ldl cholesterol[:\s]+(\d+\.?\d*)'
            ],
            'hdl': [
                r'hdl[:\s]+(\d+\.?\d*)\s*(mg/dl|mg/dL)?',
                r'hdl cholesterol[:\s]+(\d+\.?\d*)'
            ],
            'triglycerides': [
                r'triglycerides?[:\s]+(\d+\.?\d*)\s*(mg/dl|mg/dL)?',
                r'trig[:\s]+(\d+\.?\d*)'
            ],
            'white_blood_cells': [
                r'wbc[:\s]+(\d+\.?\d*)\s*(k/ul|K/uL)?',
                r'white blood cells?[:\s]+(\d+\.?\d*)'
            ],
            'red_blood_cells': [
                r'rbc[:\s]+(\d+\.?\d*)\s*(m/ul|M/uL)?',
                r'red blood cells?[:\s]+(\d+\.?\d*)'
            ],
            'platelets': [
                r'platelets?[:\s]+(\d+\.?\d*)\s*(k/ul|K/uL)?',
                r'plt[:\s]+(\d+\.?\d*)'
            ]
        }
        
        import re
        
        for metric_name, patterns in metric_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, analysis, re.IGNORECASE)
                for match in matches:
                    value = match.group(1)
                    unit = match.group(2) if match.lastindex >= 2 else ''
                    
                    # Handle special case for blood pressure (systolic/diastolic)
                    if metric_name == 'blood_pressure' and '/' in value:
                        metrics[metric_name] = {
                            'value': value,
                            'unit': unit or 'mmHg',
                            'name': 'Blood Pressure'
                        }
                    else:
                        metrics[metric_name] = {
                            'value': value,
                            'unit': unit,
                            'name': metric_name.replace('_', ' ').title()
                        }
                    break  # Use first match for each metric
                
                if metric_name in metrics:
                    break  # Found a match, move to next metric
        
        return metrics
    
    def _identify_document_type(self, content: str) -> str:
        """Identifies the type of medical document."""
        doc_types = {
            'lab_report': ['lab', 'blood', 'urine', 'test results'],
            'prescription': ['prescription', 'medication', 'rx'],
            'radiology': ['x-ray', 'mri', 'ct scan', 'ultrasound'],
            'doctor_note': ['diagnosis', 'treatment plan', 'consultation']
        }
        
        content_lower = content.lower()
        for doc_type, keywords in doc_types.items():
            if any(keyword in content_lower for keyword in keywords):
                return doc_type
                
        return 'general_medical'
    
    async def _extract_medications(self, text: str) -> List[str]:
        """Extracts medication names from text."""
        prompt = f"""
        Extract all medication names from this text:
        {text}
        
        Return only the medication names as a comma-separated list.
        """
        
        response = await self.gemini_client.analyze_text(prompt)
        medications = [med.strip() for med in response.split(',')]
        
        return medications