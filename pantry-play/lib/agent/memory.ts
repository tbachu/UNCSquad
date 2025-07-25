import { UserPreferences, Recipe, Achievement, PantryItem } from './types';

export enum MemoryType {
  USER_PREFERENCE = 'user_preference',
  RECIPE_HISTORY = 'recipe_history',
  PANTRY_SNAPSHOT = 'pantry_snapshot',
  WASTE_TRACKING = 'waste_tracking',
  ACHIEVEMENT = 'achievement',
  SHOPPING_HISTORY = 'shopping_history',
}

interface MemoryEntry {
  id: string;
  type: MemoryType;
  timestamp: Date;
  content: any;
}

interface UserProfile {
  preferences: UserPreferences;
  achievements: Achievement[];
  stats: {
    recipesCooked: number;
    wasteReducedKg: number;
    moneySaved: number;
    challengesCompleted: number;
  };
}

export class Memory {
  private shortTermMemory: MemoryEntry[] = [];
  private userProfile: UserProfile;

  constructor() {
    this.userProfile = this.loadUserProfile();
  }

  private loadUserProfile(): UserProfile {
    // In a real app, this would load from a database
    const stored = localStorage.getItem('userProfile');
    if (stored) {
      return JSON.parse(stored);
    }

    return {
      preferences: {
        dietaryRestrictions: [],
        favoriteCuisines: [],
        dislikedIngredients: [],
        cookingSkillLevel: 'intermediate',
        servingSize: 2,
      },
      achievements: [],
      stats: {
        recipesCooked: 0,
        wasteReducedKg: 0,
        moneySaved: 0,
        challengesCompleted: 0,
      },
    };
  }

  store(memoryType: MemoryType, content: any): void {
    const entry: MemoryEntry = {
      id: Date.now().toString(),
      type: memoryType,
      timestamp: new Date(),
      content,
    };

    // Add to short-term memory
    this.shortTermMemory.push(entry);
    if (this.shortTermMemory.length > 100) {
      this.shortTermMemory = this.shortTermMemory.slice(-100);
    }

    // Persist to localStorage
    this.persistMemory(memoryType, entry);

    // Update user profile
    this.updateProfile(memoryType, content);
  }

  private persistMemory(memoryType: MemoryType, entry: MemoryEntry): void {
    const key = `memory_${memoryType}`;
    const existing = localStorage.getItem(key);
    const entries = existing ? JSON.parse(existing) : [];
    
    entries.push(entry);
    
    // Keep only last 1000 entries
    if (entries.length > 1000) {
      entries.splice(0, entries.length - 1000);
    }
    
    localStorage.setItem(key, JSON.stringify(entries));
  }

  private updateProfile(memoryType: MemoryType, content: any): void {
    switch (memoryType) {
      case MemoryType.USER_PREFERENCE:
        Object.assign(this.userProfile.preferences, content);
        break;
      
      case MemoryType.RECIPE_HISTORY:
        this.userProfile.stats.recipesCooked++;
        break;
      
      case MemoryType.WASTE_TRACKING:
        if (content.wasteReduced) {
          this.userProfile.stats.wasteReducedKg += content.wasteReduced;
        }
        if (content.moneySaved) {
          this.userProfile.stats.moneySaved += content.moneySaved;
        }
        break;
      
      case MemoryType.ACHIEVEMENT:
        this.userProfile.achievements.push({
          ...content,
          earnedAt: new Date(),
        });
        if (content.isChallenge) {
          this.userProfile.stats.challengesCompleted++;
        }
        break;
    }

    this.saveUserProfile();
  }

  private saveUserProfile(): void {
    localStorage.setItem('userProfile', JSON.stringify(this.userProfile));
  }

  retrieve(memoryType: MemoryType, limit: number = 10): MemoryEntry[] {
    const key = `memory_${memoryType}`;
    const stored = localStorage.getItem(key);
    
    if (!stored) return [];
    
    const entries = JSON.parse(stored);
    return entries.slice(-limit);
  }

  getUserPreferences(): UserPreferences {
    return this.userProfile.preferences;
  }

  getUserStats() {
    return this.userProfile.stats;
  }

  getAchievements(): Achievement[] {
    return this.userProfile.achievements;
  }

  getRecentRecipes(limit: number = 5): Recipe[] {
    const entries = this.retrieve(MemoryType.RECIPE_HISTORY, limit);
    return entries.map(entry => entry.content);
  }

  analyzePatterns() {
    const recipes = this.getRecentRecipes(20);
    const ingredientFreq: Record<string, number> = {};
    const cuisineFreq: Record<string, number> = {};

    recipes.forEach(recipe => {
      recipe.ingredients?.forEach(ing => {
        ingredientFreq[ing.name] = (ingredientFreq[ing.name] || 0) + 1;
      });
      
      recipe.tags?.forEach(tag => {
        if (tag.includes('cuisine')) {
          cuisineFreq[tag] = (cuisineFreq[tag] || 0) + 1;
        }
      });
    });

    const favoriteIngredients = Object.entries(ingredientFreq)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10);
    
    const favoriteCuisines = Object.entries(cuisineFreq)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5);

    return {
      favoriteIngredients,
      favoriteCuisines,
      cookingFrequency: recipes.length / 20,
      wasteReductionTrend: this.calculateWasteTrend(),
    };
  }

  private calculateWasteTrend(): string {
    const wasteLogs = this.retrieve(MemoryType.WASTE_TRACKING, 30);
    if (wasteLogs.length < 2) return 'insufficient_data';

    const mid = Math.floor(wasteLogs.length / 2);
    const firstHalf = wasteLogs.slice(0, mid);
    const secondHalf = wasteLogs.slice(mid);

    const firstHalfWaste = firstHalf.reduce((sum, log) => 
      sum + (log.content.wasteAmount || 0), 0);
    const secondHalfWaste = secondHalf.reduce((sum, log) => 
      sum + (log.content.wasteAmount || 0), 0);

    if (secondHalfWaste < firstHalfWaste) return 'improving';
    if (secondHalfWaste > firstHalfWaste) return 'needs_attention';
    return 'stable';
  }
}