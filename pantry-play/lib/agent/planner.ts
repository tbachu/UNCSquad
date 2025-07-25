import { Task, TaskType, TaskPriority } from './types';
import { v4 as uuidv4 } from 'uuid';

export class Planner {
  private tasks: Task[] = [];

  async plan(userInput: string, context: Record<string, any>): Promise<Task[]> {
    const tasks: Task[] = [];
    const input = userInput.toLowerCase();

    // Analyze user intent and create tasks
    if (input.includes('recipe') || input.includes('cook') || input.includes('make')) {
      // First analyze pantry
      tasks.push({
        id: uuidv4(),
        taskType: TaskType.ANALYZE_PANTRY,
        description: 'Analyze available ingredients in pantry',
        priority: TaskPriority.HIGH,
        context: { userInput },
        completed: false,
      });

      // Generate recipe
      tasks.push({
        id: uuidv4(),
        taskType: TaskType.GENERATE_RECIPE,
        description: 'Generate creative recipe based on available ingredients',
        priority: TaskPriority.HIGH,
        context: { 
          preferences: context.dietary_preferences || [],
          servings: context.servings || 2,
        },
        completed: false,
      });

      // Check nutrition if tracking
      if (context.trackNutrition) {
        tasks.push({
          id: uuidv4(),
          taskType: TaskType.CHECK_NUTRITION,
          description: 'Calculate nutritional information',
          priority: TaskPriority.MEDIUM,
          context: {},
          completed: false,
        });
      }
    }

    if (input.includes('shopping') || input.includes('grocery') || input.includes('buy')) {
      tasks.push({
        id: uuidv4(),
        taskType: TaskType.CREATE_SHOPPING_LIST,
        description: 'Generate optimized shopping list',
        priority: TaskPriority.HIGH,
        context: { mealPlan: context.mealPlan || [] },
        completed: false,
      });
    }

    if (input.includes('mood') || input.includes('weather') || input.includes('feeling')) {
      tasks.push({
        id: uuidv4(),
        taskType: TaskType.MOOD_WEATHER_RECOMMEND,
        description: 'Suggest meals based on mood and weather',
        priority: TaskPriority.HIGH,
        context: { 
          mood: context.mood,
          weather: context.weather,
        },
        completed: false,
      });
    }

    if (input.includes('waste') || input.includes('leftover') || input.includes('save')) {
      tasks.push({
        id: uuidv4(),
        taskType: TaskType.TRACK_WASTE,
        description: 'Analyze food waste and suggest leftover transformations',
        priority: TaskPriority.HIGH,
        context: { leftovers: context.leftovers || [] },
        completed: false,
      });
    }

    // Sort by priority
    tasks.sort((a, b) => a.priority - b.priority);
    this.tasks = tasks;
    return tasks;
  }

  getNextTask(): Task | null {
    return this.tasks.find(task => !task.completed) || null;
  }

  markTaskComplete(taskId: string, result: any): void {
    const task = this.tasks.find(t => t.id === taskId);
    if (task) {
      task.completed = true;
      task.result = result;
    }
  }

  getAllTasks(): Task[] {
    return this.tasks;
  }

  getCompletedTasks(): Task[] {
    return this.tasks.filter(task => task.completed);
  }

  getPendingTasks(): Task[] {
    return this.tasks.filter(task => !task.completed);
  }
}