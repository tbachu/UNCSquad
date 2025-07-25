import { Planner } from './planner';
import { Executor } from './executor';
import { Memory, MemoryType } from './memory';
import { Task } from './types';

export class PantryPlayAgent {
  private planner: Planner;
  private executor: Executor;
  private memory: Memory;

  constructor(apiKey: string) {
    this.planner = new Planner();
    this.executor = new Executor(apiKey);
    this.memory = new Memory();
  }

  async processUserInput(input: string, context: Record<string, any> = {}): Promise<any> {
    // Step 1: Retrieve relevant memory
    const userPreferences = this.memory.getUserPreferences();
    const recentRecipes = this.memory.getRecentRecipes();
    const patterns = this.memory.analyzePatterns();

    // Enhance context with memory
    const enhancedContext = {
      ...context,
      userPreferences,
      recentRecipes,
      patterns,
      timestamp: new Date(),
    };

    // Step 2: Plan sub-tasks
    const tasks = await this.planner.plan(input, enhancedContext);

    // Step 3: Execute tasks
    const results: Record<string, any> = {};
    
    for (const task of tasks) {
      try {
        // Execute the task
        const result = await this.executor.execute({
          ...task,
          context: {
            ...task.context,
            previousResults: results,
          },
        });

        // Mark task as complete
        this.planner.markTaskComplete(task.id, result);
        results[task.taskType] = result;

        // Store relevant memories
        this.storeTaskMemory(task, result);
      } catch (error) {
        console.error(`Error executing task ${task.id}:`, error);
        results[task.taskType] = { error: error.message };
      }
    }

    // Step 4: Generate final response
    const response = this.generateResponse(input, tasks, results);

    // Store interaction in memory
    this.memory.store(MemoryType.USER_PREFERENCE, {
      interaction: {
        input,
        response,
        timestamp: new Date(),
      },
    });

    return response;
  }

  private storeTaskMemory(task: Task, result: any): void {
    switch (task.taskType) {
      case 'generate_recipe':
        if (result && result.id) {
          this.memory.store(MemoryType.RECIPE_HISTORY, result);
        }
        break;
      
      case 'analyze_pantry':
        if (result && result.ingredients) {
          this.memory.store(MemoryType.PANTRY_SNAPSHOT, result);
        }
        break;
      
      case 'track_waste':
        if (result) {
          this.memory.store(MemoryType.WASTE_TRACKING, result);
        }
        break;
    }
  }

  private generateResponse(input: string, tasks: Task[], results: Record<string, any>): any {
    // Compile results into a cohesive response
    const completedTasks = this.planner.getCompletedTasks();
    
    return {
      success: completedTasks.length === tasks.length,
      tasksCompleted: completedTasks.length,
      totalTasks: tasks.length,
      results,
      summary: this.generateSummary(input, results),
      nextSteps: this.suggestNextSteps(results),
    };
  }

  private generateSummary(input: string, results: Record<string, any>): string {
    // Generate a natural language summary of what was accomplished
    const summaryParts: string[] = [];

    if (results.analyze_pantry) {
      summaryParts.push('Analyzed your pantry ingredients');
    }

    if (results.generate_recipe) {
      const recipe = results.generate_recipe;
      summaryParts.push(`Created a recipe for ${recipe.name || 'a delicious meal'}`);
    }

    if (results.create_shopping_list) {
      summaryParts.push('Generated an optimized shopping list');
    }

    if (results.track_waste) {
      summaryParts.push('Provided leftover transformation ideas');
    }

    return summaryParts.join(', ') || 'Processed your request';
  }

  private suggestNextSteps(results: Record<string, any>): string[] {
    const suggestions: string[] = [];

    if (results.generate_recipe) {
      suggestions.push('Start cooking and track your progress');
      suggestions.push('Share the recipe with friends');
      suggestions.push('Rate the recipe after cooking');
    }

    if (results.analyze_pantry?.expiringGoon?.length > 0) {
      suggestions.push('Use expiring ingredients first');
    }

    if (results.create_shopping_list) {
      suggestions.push('Order groceries online or visit the store');
    }

    return suggestions;
  }

  // Additional utility methods
  getUserStats() {
    return this.memory.getUserStats();
  }

  getAchievements() {
    return this.memory.getAchievements();
  }

  updatePreferences(preferences: Partial<any>) {
    this.memory.store(MemoryType.USER_PREFERENCE, preferences);
  }
}