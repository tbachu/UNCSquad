export enum TaskType {
  ANALYZE_PANTRY = 'analyze_pantry',
  GENERATE_RECIPE = 'generate_recipe',
  CHECK_NUTRITION = 'check_nutrition',
  SUGGEST_SUBSTITUTIONS = 'suggest_substitutions',
  CREATE_SHOPPING_LIST = 'create_shopping_list',
  TRACK_WASTE = 'track_waste',
  MOOD_WEATHER_RECOMMEND = 'mood_weather_recommend',
}

export enum TaskPriority {
  HIGH = 1,
  MEDIUM = 2,
  LOW = 3,
}

export interface Task {
  id: string;
  taskType: TaskType;
  description: string;
  priority: TaskPriority;
  context: Record<string, any>;
  completed: boolean;
  result?: any;
}

export interface PantryItem {
  name: string;
  quantity: string;
  unit?: string;
  expiryDate?: Date;
  category: string;
}

export interface Recipe {
  id: string;
  name: string;
  description: string;
  prepTime: number;
  cookTime: number;
  servings: number;
  ingredients: Array<{
    name: string;
    amount: string;
    unit: string;
  }>;
  instructions: string[];
  nutrition?: NutritionInfo;
  tags: string[];
  difficulty: 'easy' | 'medium' | 'hard';
  imageUrl?: string;
}

export interface NutritionInfo {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  vitamins?: Record<string, number>;
}

export interface UserPreferences {
  dietaryRestrictions: string[];
  favoriteCuisines: string[];
  dislikedIngredients: string[];
  cookingSkillLevel: 'beginner' | 'intermediate' | 'advanced';
  servingSize: number;
}

export interface MealPlan {
  id: string;
  date: Date;
  meals: {
    breakfast?: Recipe;
    lunch?: Recipe;
    dinner?: Recipe;
    snacks?: Recipe[];
  };
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  earnedAt?: Date;
  progress?: number;
  maxProgress?: number;
}