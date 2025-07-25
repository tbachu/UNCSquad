"""
Planner module for Pantry Play
Breaks down user goals into sub-tasks using ReAct pattern
"""

import json
from typing import List, Dict, Any
from enum import Enum

class TaskType(Enum):
    ANALYZE_PANTRY = "analyze_pantry"
    GENERATE_RECIPE = "generate_recipe"
    CHECK_NUTRITION = "check_nutrition"
    SUGGEST_SUBSTITUTIONS = "suggest_substitutions"
    CREATE_SHOPPING_LIST = "create_shopping_list"
    TRACK_WASTE = "track_waste"
    MOOD_WEATHER_RECOMMEND = "mood_weather_recommend"

class TaskPriority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class Task:
    def __init__(self, task_type: TaskType, description: str, priority: TaskPriority, context: Dict[str, Any]):
        self.task_type = task_type
        self.description = description
        self.priority = priority
        self.context = context
        self.completed = False
        self.result = None

class Planner:
    def __init__(self):
        self.tasks = []
        
    def plan(self, user_input: str, context: Dict[str, Any]) -> List[Task]:
        """
        Break down user goals into sub-tasks using ReAct pattern
        """
        tasks = []
        
        # Analyze user intent
        if "recipe" in user_input.lower() or "cook" in user_input.lower():
            # First analyze what's available
            tasks.append(Task(
                TaskType.ANALYZE_PANTRY,
                "Analyze available ingredients in pantry",
                TaskPriority.HIGH,
                {"user_input": user_input}
            ))
            
            # Then generate recipe
            tasks.append(Task(
                TaskType.GENERATE_RECIPE,
                "Generate creative recipe based on available ingredients",
                TaskPriority.HIGH,
                {"preferences": context.get("dietary_preferences", [])}
            ))
            
            # Check nutrition if needed
            if context.get("track_nutrition", False):
                tasks.append(Task(
                    TaskType.CHECK_NUTRITION,
                    "Calculate nutritional information",
                    TaskPriority.MEDIUM,
                    {}
                ))
        
        elif "shopping" in user_input.lower() or "grocery" in user_input.lower():
            tasks.append(Task(
                TaskType.CREATE_SHOPPING_LIST,
                "Generate optimized shopping list",
                TaskPriority.HIGH,
                {"meal_plan": context.get("meal_plan", [])}
            ))
            
        elif "mood" in user_input.lower() or "weather" in user_input.lower():
            tasks.append(Task(
                TaskType.MOOD_WEATHER_RECOMMEND,
                "Suggest meals based on mood and weather",
                TaskPriority.HIGH,
                {"mood": context.get("mood"), "weather": context.get("weather")}
            ))
            
        elif "waste" in user_input.lower() or "leftover" in user_input.lower():
            tasks.append(Task(
                TaskType.TRACK_WASTE,
                "Analyze food waste and suggest leftover transformations",
                TaskPriority.HIGH,
                {"leftovers": context.get("leftovers", [])}
            ))
        
        # Sort by priority
        tasks.sort(key=lambda x: x.priority.value)
        self.tasks = tasks
        return tasks
    
    def get_next_task(self) -> Task:
        """Get the next uncompleted task"""
        for task in self.tasks:
            if not task.completed:
                return task
        return None
    
    def mark_task_complete(self, task: Task, result: Any):
        """Mark a task as complete with its result"""
        task.completed = True
        task.result = result