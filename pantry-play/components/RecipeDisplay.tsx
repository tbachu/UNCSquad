'use client';

import { Recipe } from '@/lib/agent/types';

interface RecipeDisplayProps {
  recipe: Recipe;
}

export default function RecipeDisplay({ recipe }: RecipeDisplayProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">{recipe.name}</h2>
        <p className="text-gray-600">{recipe.description}</p>
        
        <div className="flex gap-4 mt-3 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <span>⏱</span> Prep: {recipe.prepTime} min
          </span>
          <span className="flex items-center gap-1">
            <span>🔥</span> Cook: {recipe.cookTime} min
          </span>
          <span className="flex items-center gap-1">
            <span>🍽</span> Servings: {recipe.servings}
          </span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            recipe.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
            recipe.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
            'bg-red-100 text-red-700'
          }`}>
            {recipe.difficulty}
          </span>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
            <span className="mr-2">🥘</span> Ingredients
          </h3>
          <ul className="space-y-2">
            {recipe.ingredients.map((ingredient, index) => (
              <li key={index} className="flex items-start">
                <span className="text-green-600 mr-2">•</span>
                <span>
                  {ingredient.amount} {ingredient.unit} {ingredient.name}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
            <span className="mr-2">📝</span> Instructions
          </h3>
          <ol className="space-y-3">
            {recipe.instructions.map((instruction, index) => (
              <li key={index} className="flex">
                <span className="font-bold text-green-600 mr-2">{index + 1}.</span>
                <span>{instruction}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {recipe.nutrition && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
            <span className="mr-2">📊</span> Nutrition Per Serving
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-800">{recipe.nutrition.calories}</p>
              <p className="text-sm text-gray-600">Calories</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-800">{recipe.nutrition.protein}g</p>
              <p className="text-sm text-gray-600">Protein</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-800">{recipe.nutrition.carbs}g</p>
              <p className="text-sm text-gray-600">Carbs</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-800">{recipe.nutrition.fat}g</p>
              <p className="text-sm text-gray-600">Fat</p>
            </div>
          </div>
        </div>
      )}

      {recipe.tags && recipe.tags.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {recipe.tags.map((tag, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}