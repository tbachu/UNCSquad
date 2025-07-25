import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    DOCUMENT_ANALYSIS = "document_analysis"
    HEALTH_QUERY = "health_query"
    TREND_ANALYSIS = "trend_analysis"
    MEDICATION_CHECK = "medication_check"
    REPORT_GENERATION = "report_generation"
    DATA_VISUALIZATION = "data_visualization"


@dataclass
class Task:
    id: str
    type: TaskType
    description: str
    parameters: Dict[str, Any]
    priority: int = 1
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class HealthAgentPlanner:
    """
    Plans and decomposes user requests into actionable tasks for the HIA agent.
    Uses a ReAct-style approach to break down complex health queries.
    """
    
    def __init__(self):
        self.task_counter = 0
        self.task_queue: List[Task] = []
        
    def plan(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> List[Task]:
        """
        Analyzes user input and creates a task plan.
        
        Args:
            user_input: The user's request or question
            context: Optional context including user history, preferences, etc.
            
        Returns:
            List of tasks to be executed
        """
        logger.info(f"Planning tasks for input: {user_input[:100]}...")
        
        tasks = []
        
        # Analyze input to determine task types needed
        if self._contains_document_reference(user_input):
            tasks.append(self._create_document_task(user_input))
            
        if self._is_health_question(user_input):
            tasks.append(self._create_query_task(user_input))
            
        if self._requires_trend_analysis(user_input, context):
            doc_task_id = tasks[0].id if tasks else None
            tasks.append(self._create_trend_task(user_input, doc_task_id))
            
        if self._mentions_medication(user_input):
            tasks.append(self._create_medication_task(user_input))
            
        if self._needs_report(user_input):
            dependency_ids = [t.id for t in tasks]
            tasks.append(self._create_report_task(dependency_ids))
            
        # If no specific tasks identified, create a general health query task
        if not tasks:
            tasks.append(self._create_query_task(user_input))
            
        logger.info(f"Created {len(tasks)} tasks")
        return tasks
    
    def _create_task(self, task_type: TaskType, description: str, 
                     parameters: Dict[str, Any], dependencies: List[str] = None) -> Task:
        """Creates a new task with unique ID."""
        self.task_counter += 1
        task = Task(
            id=f"task_{self.task_counter}",
            type=task_type,
            description=description,
            parameters=parameters,
            dependencies=dependencies or []
        )
        return task
    
    def _contains_document_reference(self, text: str) -> bool:
        """Checks if the input references a medical document."""
        doc_keywords = ['report', 'lab result', 'test result', 'prescription', 
                       'doctor note', 'medical record', 'pdf', 'image', 'file']
        return any(keyword in text.lower() for keyword in doc_keywords)
    
    def _is_health_question(self, text: str) -> bool:
        """Checks if the input is a health-related question."""
        question_words = ['what', 'why', 'how', 'when', 'should', 'is', 'can', 'does']
        health_terms = ['health', 'medical', 'symptom', 'condition', 'diagnosis', 
                       'treatment', 'medicine', 'doctor', 'test', 'result']
        
        has_question = any(word in text.lower() for word in question_words)
        has_health = any(term in text.lower() for term in health_terms)
        
        return has_question or has_health
    
    def _requires_trend_analysis(self, text: str, context: Optional[Dict[str, Any]]) -> bool:
        """Checks if trend analysis is needed."""
        trend_keywords = ['trend', 'history', 'change', 'progress', 'over time', 
                         'improvement', 'deterioration', 'tracking']
        has_history = context and context.get('has_historical_data', False)
        
        return any(keyword in text.lower() for keyword in trend_keywords) or has_history
    
    def _mentions_medication(self, text: str) -> bool:
        """Checks if the input mentions medications."""
        med_keywords = ['medication', 'medicine', 'drug', 'prescription', 'pill', 
                       'dose', 'interaction', 'side effect']
        return any(keyword in text.lower() for keyword in med_keywords)
    
    def _needs_report(self, text: str) -> bool:
        """Checks if a report generation is needed."""
        report_keywords = ['report', 'summary', 'doctor visit', 'appointment', 
                          'prepare', 'print', 'share']
        return any(keyword in text.lower() for keyword in report_keywords)
    
    def _create_document_task(self, user_input: str) -> Task:
        """Creates a document analysis task."""
        return self._create_task(
            TaskType.DOCUMENT_ANALYSIS,
            "Analyze uploaded medical document",
            {
                "input": user_input,
                "extract_metrics": True,
                "explain_jargon": True
            }
        )
    
    def _create_query_task(self, user_input: str) -> Task:
        """Creates a health query task."""
        return self._create_task(
            TaskType.HEALTH_QUERY,
            "Answer health-related question",
            {
                "query": user_input,
                "provide_sources": True
            }
        )
    
    def _create_trend_task(self, user_input: str, dependency: Optional[str]) -> Task:
        """Creates a trend analysis task."""
        dependencies = [dependency] if dependency else []
        return self._create_task(
            TaskType.TREND_ANALYSIS,
            "Analyze health trends over time",
            {
                "metrics": ["all"],  # Will be refined based on available data
                "time_period": "all",
                "generate_insights": True
            },
            dependencies
        )
    
    def _create_medication_task(self, user_input: str) -> Task:
        """Creates a medication check task."""
        return self._create_task(
            TaskType.MEDICATION_CHECK,
            "Check medication interactions and information",
            {
                "input": user_input,
                "check_interactions": True,
                "provide_info": True
            }
        )
    
    def _create_report_task(self, dependencies: List[str]) -> Task:
        """Creates a report generation task."""
        return self._create_task(
            TaskType.REPORT_GENERATION,
            "Generate comprehensive health report",
            {
                "include_trends": True,
                "include_recommendations": True,
                "format": "printable"
            },
            dependencies
        )