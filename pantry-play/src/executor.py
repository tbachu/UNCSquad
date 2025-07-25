"""
Executor module for Pantry Play
Logic for calling Gemini API and executing tools
"""

import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from planner import Task, TaskType

class Executor:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        
    def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a task using appropriate tools and Gemini API"""
        
        if task.task_type == TaskType.ANALYZE_PANTRY:
            return self._analyze_pantry(task.context)
        
        elif task.task_type == TaskType.GENERATE_RECIPE:
            return self._generate_recipe(task.context)
        
        elif task.task_type == TaskType.CHECK_NUTRITION:
            return self._check_nutrition(task.context)
        
        elif task.task_type == TaskType.SUGGEST_SUBSTITUTIONS:
            return self._suggest_substitutions(task.context)
        
        elif task.task_type == TaskType.CREATE_SHOPPING_LIST:
            return self._create_shopping_list(task.context)
        
        elif task.task_type == TaskType.TRACK_WASTE:
            return self._track_waste(task.context)
        
        elif task.task_type == TaskType.MOOD_WEATHER_RECOMMEND:
            return self._mood_weather_recommend(task.context)
        
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
    
    def _analyze_pantry(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pantry items from photo or text input"""
        if context.get("image_data"):
            # Use vision model for image analysis
            prompt = """Analyze this pantry/refrigerator image and list all visible ingredients.
            Format the response as JSON with:
            - ingredients: list of ingredient objects with name, quantity, and estimated expiry
            - categories: group ingredients by type (vegetables, proteins, dairy, etc.)
            - freshness_alerts: items that might expire soon"""
            
            response = self.vision_model.generate_content([prompt, context["image_data"]])
        else:
            # Use text model for text/receipt analysis
            prompt = f"""Analyze these pantry items: {context.get('items', [])}
            Format the response as JSON with:
            - ingredients: list of ingredient objects with name, quantity, and estimated expiry
            - categories: group ingredients by type
            - freshness_alerts: items that might expire soon"""
            
            response = self.model.generate_content(prompt)
        
        return {"pantry_analysis": response.text}
    
    def _generate_recipe(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate creative recipes based on available ingredients"""
        ingredients = context.get("ingredients", [])
        preferences = context.get("preferences", [])
        
        prompt = f"""Create a creative, delicious recipe using ONLY these ingredients: {ingredients}
        Dietary preferences: {preferences}
        
        Response format:
        - recipe_name: creative name for the dish
        - description: brief exciting description
        - prep_time: in minutes
        - cook_time: in minutes
        - servings: number of servings
        - ingredients_used: list of ingredients with quantities
        - instructions: step-by-step cooking instructions
        - nutrition_estimate: basic nutritional info per serving
        - fun_fact: interesting fact about the dish or ingredients
        - substitutions: possible ingredient swaps
        - leftover_ideas: what to do with leftovers"""
        
        response = self.model.generate_content(prompt)
        return {"recipe": response.text}
    
    def _check_nutrition(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate nutritional information for a recipe"""
        recipe = context.get("recipe", {})
        
        prompt = f"""Calculate detailed nutritional information for this recipe: {recipe}
        
        Provide:
        - calories per serving
        - macronutrients (protein, carbs, fat)
        - key vitamins and minerals
        - dietary labels (vegan, gluten-free, etc.)
        - health benefits
        - nutritional score (1-10)"""
        
        response = self.model.generate_content(prompt)
        return {"nutrition": response.text}
    
    def _suggest_substitutions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest ingredient substitutions"""
        missing = context.get("missing_ingredients", [])
        available = context.get("available_ingredients", [])
        
        prompt = f"""Suggest creative substitutions for these missing ingredients: {missing}
        Available ingredients: {available}
        
        For each substitution explain:
        - What to use instead
        - How it affects the dish
        - Any adjustments needed
        - Science behind why it works"""
        
        response = self.model.generate_content(prompt)
        return {"substitutions": response.text}
    
    def _create_shopping_list(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimized shopping list"""
        meal_plan = context.get("meal_plan", [])
        pantry = context.get("current_pantry", [])
        
        prompt = f"""Create an optimized shopping list for this meal plan: {meal_plan}
        Current pantry: {pantry}
        
        Organize by:
        - Store sections (produce, dairy, etc.)
        - Priority items
        - Budget-friendly alternatives
        - Seasonal recommendations
        - Quantity estimates
        - Storage tips"""
        
        response = self.model.generate_content(prompt)
        return {"shopping_list": response.text}
    
    def _track_waste(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Track food waste and suggest leftover transformations"""
        leftovers = context.get("leftovers", [])
        
        prompt = f"""Transform these leftovers into new exciting dishes: {leftovers}
        
        Provide:
        - Creative transformation ideas
        - Zero-waste tips
        - Storage recommendations
        - Meal prep suggestions
        - Cost savings estimate
        - Environmental impact reduction"""
        
        response = self.model.generate_content(prompt)
        return {"waste_reduction": response.text}
    
    def _mood_weather_recommend(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend meals based on mood and weather"""
        mood = context.get("mood", "neutral")
        weather = context.get("weather", {})
        
        prompt = f"""Suggest perfect meals for:
        Mood: {mood}
        Weather: {weather}
        
        Provide:
        - 3 meal suggestions with reasoning
        - Comfort factor explanation
        - Cooking playlist recommendations
        - Ambiance tips
        - Ingredient mood boosters
        - Seasonal touches"""
        
        response = self.model.generate_content(prompt)
        return {"mood_meals": response.text}