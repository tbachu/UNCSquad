"""
API server for Pantry Play Python agent modules
This server provides endpoints for the Next.js frontend to interact with the Python agent
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import agent modules
from planner import Planner, TaskType
from executor import Executor
from memory import Memory, MemoryType

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize components
planner = Planner()
executor = Executor(os.getenv('GEMINI_API_KEY'))
memory = Memory()

@app.route('/api/agent/process', methods=['POST'])
def process_user_input():
    """Main endpoint for processing user input"""
    try:
        data = request.json
        user_input = data.get('input', '')
        context = data.get('context', {})
        
        # Step 1: Retrieve relevant memory
        user_preferences = memory.get_user_preferences()
        recent_recipes = memory.get_recent_recipes()
        patterns = memory.analyze_patterns()
        
        # Enhance context with memory
        enhanced_context = {
            **context,
            'user_preferences': user_preferences,
            'recent_recipes': recent_recipes,
            'patterns': patterns
        }
        
        # Step 2: Plan sub-tasks
        tasks = planner.plan(user_input, enhanced_context)
        
        # Step 3: Execute tasks
        results = {}
        for task in tasks:
            try:
                # Add previous results to context
                task.context['previous_results'] = results
                
                # Execute task
                result = executor.execute(task)
                
                # Mark complete
                planner.mark_task_complete(task, result)
                results[task.task_type.value] = result
                
                # Store relevant memories
                store_task_memory(task, result)
                
            except Exception as e:
                print(f"Error executing task {task.task_type}: {str(e)}")
                results[task.task_type.value] = {"error": str(e)}
        
        # Step 4: Generate response
        response = {
            'success': len(planner.get_completed_tasks()) == len(tasks),
            'tasks_completed': len(planner.get_completed_tasks()),
            'total_tasks': len(tasks),
            'results': results,
            'summary': generate_summary(user_input, results),
            'next_steps': suggest_next_steps(results)
        }
        
        # Store interaction
        memory.store(MemoryType.USER_PREFERENCE, {
            'interaction': {
                'input': user_input,
                'response': response
            }
        })
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def store_task_memory(task, result):
    """Store task results in memory"""
    if task.task_type == TaskType.GENERATE_RECIPE and result:
        memory.store(MemoryType.RECIPE_HISTORY, result)
    elif task.task_type == TaskType.ANALYZE_PANTRY and result:
        memory.store(MemoryType.PANTRY_SNAPSHOT, result)
    elif task.task_type == TaskType.TRACK_WASTE and result:
        memory.store(MemoryType.WASTE_TRACKING, result)

def generate_summary(user_input, results):
    """Generate a summary of completed tasks"""
    summary_parts = []
    
    if 'analyze_pantry' in results:
        summary_parts.append('Analyzed your pantry ingredients')
    
    if 'generate_recipe' in results:
        recipe = results.get('generate_recipe', {})
        recipe_name = recipe.get('recipe_name', 'a delicious meal')
        summary_parts.append(f'Created a recipe for {recipe_name}')
    
    if 'create_shopping_list' in results:
        summary_parts.append('Generated an optimized shopping list')
    
    if 'track_waste' in results:
        summary_parts.append('Provided leftover transformation ideas')
    
    return ', '.join(summary_parts) if summary_parts else 'Processed your request'

def suggest_next_steps(results):
    """Suggest next steps based on results"""
    suggestions = []
    
    if 'generate_recipe' in results:
        suggestions.extend([
            'Start cooking and track your progress',
            'Share the recipe with friends',
            'Rate the recipe after cooking'
        ])
    
    if 'analyze_pantry' in results:
        pantry = results.get('analyze_pantry', {})
        if pantry.get('expiringGoon', []):
            suggestions.append('Use expiring ingredients first')
    
    if 'create_shopping_list' in results:
        suggestions.append('Order groceries online or visit the store')
    
    return suggestions

@app.route('/api/memory/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    return jsonify(memory.get_user_stats())

@app.route('/api/memory/achievements', methods=['GET'])
def get_achievements():
    """Get user achievements"""
    return jsonify(memory.get_achievements())

@app.route('/api/memory/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    return jsonify(memory.get_user_preferences())

@app.route('/api/memory/preferences', methods=['POST'])
def update_preferences():
    """Update user preferences"""
    data = request.json
    memory.store(MemoryType.USER_PREFERENCE, data)
    return jsonify({'success': True})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'pantry-play-agent'})

if __name__ == '__main__':
    port = int(os.getenv('AGENT_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)