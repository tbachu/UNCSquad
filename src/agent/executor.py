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
        
        # Parse document (PDF or image)
        document_content = await self.doc_parser.parse_document(params.get('file_path'))
        
        # Use Gemini to analyze the document
        prompt = f"""
        Analyze this medical document and provide:
        1. Summary of key findings
        2. Extracted health metrics (with values and units)
        3. Medical terms explained in simple language
        4. Any concerning values or findings
        
        Document content:
        {document_content}
        """
        
        analysis = await self.gemini_client.analyze_text(prompt)
        
        # Extract structured data
        metrics = self._extract_health_metrics(analysis)
        
        # Store metrics in memory
        if metrics:
            await self.memory_store.store_health_metrics(metrics)
        
        return {
            "analysis": analysis,
            "metrics": metrics,
            "document_type": self._identify_document_type(document_content)
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
        # This would use more sophisticated NLP in production
        metrics = {}
        
        # Example extraction logic
        metric_patterns = {
            'cholesterol': r'cholesterol[:\s]+(\d+)',
            'blood_pressure': r'blood pressure[:\s]+(\d+/\d+)',
            'glucose': r'glucose[:\s]+(\d+)',
            'hemoglobin': r'hemoglobin[:\s]+(\d+\.?\d*)'
        }
        
        import re
        for metric, pattern in metric_patterns.items():
            match = re.search(pattern, analysis, re.IGNORECASE)
            if match:
                metrics[metric] = match.group(1)
                
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