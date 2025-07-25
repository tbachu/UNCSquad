import { GoogleGenerativeAI } from '@google/generative-ai';
import { Task, TaskType, PantryItem, Recipe } from './types';

export class Executor {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor(apiKey: string) {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-pro' });
  }

  async execute(task: Task): Promise<any> {
    switch (task.taskType) {
      case TaskType.ANALYZE_PANTRY:
        return await this.analyzePantry(task.context);
      
      case TaskType.GENERATE_RECIPE:
        return await this.generateRecipe(task.context);
      
      case TaskType.CHECK_NUTRITION:
        return await this.checkNutrition(task.context);
      
      case TaskType.SUGGEST_SUBSTITUTIONS:
        return await this.suggestSubstitutions(task.context);
      
      case TaskType.CREATE_SHOPPING_LIST:
        return await this.createShoppingList(task.context);
      
      case TaskType.TRACK_WASTE:
        return await this.trackWaste(task.context);
      
      case TaskType.MOOD_WEATHER_RECOMMEND:
        return await this.moodWeatherRecommend(task.context);
      
      default:
        throw new Error(`Unknown task type: ${task.taskType}`);
    }
  }

  private async analyzePantry(context: any): Promise<any> {
    const prompt = `Analyze these pantry items and categorize them: ${JSON.stringify(context.items || [])}
    
    Return a JSON response with:
    {
      "ingredients": [
        {
          "name": "item name",
          "quantity": "amount",
          "category": "vegetables/proteins/dairy/grains/etc",
          "daysUntilExpiry": number,
          "freshnessScore": 1-10
        }
      ],
      "expiringGoon": ["items expiring in next 3 days"],
      "wellStocked": ["categories with good variety"],
      "needsRestocking": ["categories running low"]
    }`;

    const result = await this.model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    try {
      return JSON.parse(text);
    } catch {
      return { rawResponse: text };
    }
  }

  private async generateRecipe(context: any): Promise<Recipe> {
    const prompt = `Create a creative, delicious recipe using ONLY these ingredients: ${JSON.stringify(context.ingredients)}
    Dietary preferences: ${JSON.stringify(context.preferences)}
    Servings: ${context.servings || 2}
    
    Return a JSON response with this exact structure:
    {
      "id": "unique-id",
      "name": "Creative Recipe Name",
      "description": "Brief exciting description",
      "prepTime": minutes as number,
      "cookTime": minutes as number,
      "servings": number,
      "ingredients": [
        {
          "name": "ingredient",
          "amount": "quantity",
          "unit": "unit of measurement"
        }
      ],
      "instructions": ["Step 1", "Step 2", ...],
      "nutrition": {
        "calories": number,
        "protein": grams,
        "carbs": grams,
        "fat": grams,
        "fiber": grams
      },
      "tags": ["cuisine type", "meal type", "dietary tags"],
      "difficulty": "easy|medium|hard",
      "funFact": "Interesting fact about the dish",
      "substitutions": ["possible swaps"],
      "leftoverIdeas": ["what to do with leftovers"]
    }`;

    const result = await this.model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    try {
      return JSON.parse(text);
    } catch {
      // Fallback recipe if parsing fails
      return {
        id: 'fallback-1',
        name: 'Creative Pantry Surprise',
        description: text.substring(0, 100),
        prepTime: 15,
        cookTime: 30,
        servings: context.servings || 2,
        ingredients: [],
        instructions: [text],
        tags: ['pantry-meal'],
        difficulty: 'medium',
      };
    }
  }

  private async checkNutrition(context: any): Promise<any> {
    const prompt = `Calculate detailed nutritional information for this recipe: ${JSON.stringify(context.recipe)}
    
    Provide comprehensive nutrition data including:
    - Calories per serving
    - Macronutrients (protein, carbs, fat in grams)
    - Key vitamins and minerals with % daily values
    - Dietary labels (vegan, gluten-free, keto-friendly, etc.)
    - Health benefits of key ingredients
    - Nutritional score (1-10) with explanation`;

    const result = await this.model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  }

  private async suggestSubstitutions(context: any): Promise<any> {
    const prompt = `Suggest creative substitutions for these missing ingredients: ${JSON.stringify(context.missingIngredients)}
    Available ingredients: ${JSON.stringify(context.availableIngredients)}
    
    For each substitution provide:
    - What to use instead
    - Ratio/amount conversion
    - How it affects taste/texture
    - Any cooking adjustments needed
    - Why it works (food science explanation)`;

    const result = await this.model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  }

  private async createShoppingList(context: any): Promise<any> {
    const prompt = `Create an optimized shopping list for this meal plan: ${JSON.stringify(context.mealPlan)}
    Current pantry: ${JSON.stringify(context.currentPantry)}
    
    Organize the list by:
    - Store sections (produce, dairy, meat, etc.)
    - Priority (essential vs nice-to-have)
    - Budget-friendly alternatives
    - Seasonal recommendations
    - Quantity estimates with prices
    - Storage tips for each item
    
    Also include total estimated cost and money-saving tips.`;

    const result = await this.model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  }

  private async trackWaste(context: any): Promise<any> {
    const prompt = `Transform these leftovers into exciting new dishes: ${JSON.stringify(context.leftovers)}
    
    Provide:
    - 3-5 creative transformation recipes
    - Zero-waste tips for each ingredient
    - Storage recommendations with shelf life
    - Meal prep suggestions
    - Cost savings estimate
    - Environmental impact (CO2 saved, water saved)
    - Fun challenge ideas for leftover transformations`;

    const result = await this.model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  }

  private async moodWeatherRecommend(context: any): Promise<any> {
    const prompt = `Suggest perfect meals for:
    Mood: ${context.mood}
    Weather: ${JSON.stringify(context.weather)}
    Time of day: ${context.timeOfDay}
    
    Provide:
    - 3 meal suggestions with detailed reasoning
    - Comfort factor explanation (why it matches the mood)
    - Cooking playlist recommendations (5-7 songs)
    - Ambiance tips (lighting, table setting)
    - Ingredient mood boosters (foods that enhance the mood)
    - Seasonal touches to add
    - Beverage pairings`;

    const result = await this.model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  }
}