"""
Memory module for Pantry Play
Logs and stores user interactions, preferences, and cooking history
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from enum import Enum

class MemoryType(Enum):
    USER_PREFERENCE = "user_preference"
    RECIPE_HISTORY = "recipe_history"
    PANTRY_SNAPSHOT = "pantry_snapshot"
    WASTE_TRACKING = "waste_tracking"
    ACHIEVEMENT = "achievement"
    SHOPPING_HISTORY = "shopping_history"

class Memory:
    def __init__(self, storage_path: str = "./memory_store"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.short_term_memory = []
        self.user_profile = self._load_user_profile()
        
    def _load_user_profile(self) -> Dict[str, Any]:
        """Load user profile from storage"""
        profile_path = os.path.join(self.storage_path, "user_profile.json")
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                return json.load(f)
        return {
            "preferences": {
                "dietary_restrictions": [],
                "favorite_cuisines": [],
                "disliked_ingredients": [],
                "cooking_skill_level": "intermediate"
            },
            "achievements": [],
            "stats": {
                "recipes_cooked": 0,
                "waste_reduced_kg": 0,
                "money_saved": 0,
                "challenges_completed": 0
            }
        }
    
    def store(self, memory_type: MemoryType, content: Dict[str, Any]):
        """Store a memory entry"""
        entry = {
            "type": memory_type.value,
            "timestamp": datetime.now().isoformat(),
            "content": content
        }
        
        # Add to short-term memory
        self.short_term_memory.append(entry)
        
        # Persist to appropriate file
        self._persist_memory(memory_type, entry)
        
        # Update user profile if needed
        self._update_profile(memory_type, content)
    
    def _persist_memory(self, memory_type: MemoryType, entry: Dict[str, Any]):
        """Persist memory to file storage"""
        filename = f"{memory_type.value}_log.json"
        filepath = os.path.join(self.storage_path, filename)
        
        # Load existing entries
        entries = []
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                entries = json.load(f)
        
        # Add new entry
        entries.append(entry)
        
        # Keep only recent entries (last 1000)
        if len(entries) > 1000:
            entries = entries[-1000:]
        
        # Save back
        with open(filepath, 'w') as f:
            json.dump(entries, f, indent=2)
    
    def _update_profile(self, memory_type: MemoryType, content: Dict[str, Any]):
        """Update user profile based on memory"""
        if memory_type == MemoryType.USER_PREFERENCE:
            # Update preferences
            for key, value in content.items():
                if key in self.user_profile["preferences"]:
                    if isinstance(self.user_profile["preferences"][key], list):
                        if value not in self.user_profile["preferences"][key]:
                            self.user_profile["preferences"][key].append(value)
                    else:
                        self.user_profile["preferences"][key] = value
        
        elif memory_type == MemoryType.RECIPE_HISTORY:
            # Update stats
            self.user_profile["stats"]["recipes_cooked"] += 1
        
        elif memory_type == MemoryType.WASTE_TRACKING:
            # Update waste reduction stats
            if "waste_reduced" in content:
                self.user_profile["stats"]["waste_reduced_kg"] += content["waste_reduced"]
            if "money_saved" in content:
                self.user_profile["stats"]["money_saved"] += content["money_saved"]
        
        elif memory_type == MemoryType.ACHIEVEMENT:
            # Add achievement
            self.user_profile["achievements"].append({
                "name": content["name"],
                "description": content["description"],
                "earned_at": datetime.now().isoformat()
            })
            if "challenge" in content:
                self.user_profile["stats"]["challenges_completed"] += 1
        
        # Save updated profile
        self._save_user_profile()
    
    def _save_user_profile(self):
        """Save user profile to storage"""
        profile_path = os.path.join(self.storage_path, "user_profile.json")
        with open(profile_path, 'w') as f:
            json.dump(self.user_profile, f, indent=2)
    
    def retrieve(self, memory_type: MemoryType, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent memories of a specific type"""
        filename = f"{memory_type.value}_log.json"
        filepath = os.path.join(self.storage_path, filename)
        
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r') as f:
            entries = json.load(f)
        
        # Return most recent entries
        return entries[-limit:]
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get current user preferences"""
        return self.user_profile["preferences"]
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        return self.user_profile["stats"]
    
    def get_achievements(self) -> List[Dict[str, Any]]:
        """Get user achievements"""
        return self.user_profile["achievements"]
    
    def get_recent_recipes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recently cooked recipes"""
        recipes = self.retrieve(MemoryType.RECIPE_HISTORY, limit)
        return [r["content"] for r in recipes]
    
    def get_pantry_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get pantry snapshots from the last N days"""
        snapshots = self.retrieve(MemoryType.PANTRY_SNAPSHOT, limit=days * 3)  # Assuming 3 snapshots per day
        return snapshots
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze user patterns for personalization"""
        recipes = self.get_recent_recipes(20)
        
        # Analyze common ingredients
        ingredient_freq = {}
        cuisine_freq = {}
        
        for recipe in recipes:
            if "ingredients" in recipe:
                for ingredient in recipe["ingredients"]:
                    ingredient_freq[ingredient] = ingredient_freq.get(ingredient, 0) + 1
            
            if "cuisine" in recipe:
                cuisine_freq[recipe["cuisine"]] = cuisine_freq.get(recipe["cuisine"], 0) + 1
        
        # Sort by frequency
        favorite_ingredients = sorted(ingredient_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        favorite_cuisines = sorted(cuisine_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "favorite_ingredients": favorite_ingredients,
            "favorite_cuisines": favorite_cuisines,
            "cooking_frequency": len(recipes) / 20,  # Average recipes per period
            "waste_reduction_trend": self._calculate_waste_trend()
        }
    
    def _calculate_waste_trend(self) -> str:
        """Calculate waste reduction trend"""
        waste_logs = self.retrieve(MemoryType.WASTE_TRACKING, 30)
        if len(waste_logs) < 2:
            return "insufficient_data"
        
        # Compare first half vs second half
        mid = len(waste_logs) // 2
        first_half_waste = sum(log["content"].get("waste_amount", 0) for log in waste_logs[:mid])
        second_half_waste = sum(log["content"].get("waste_amount", 0) for log in waste_logs[mid:])
        
        if second_half_waste < first_half_waste:
            return "improving"
        elif second_half_waste > first_half_waste:
            return "needs_attention"
        else:
            return "stable"