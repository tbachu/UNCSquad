'use client';

import { useState } from 'react';
import PantryUpload from '@/components/PantryUpload';
import RecipeDisplay from '@/components/RecipeDisplay';
import ChatInterface from '@/components/ChatInterface';
import StatsDisplay from '@/components/StatsDisplay';
import WasteTracker from '@/components/WasteTracker';
import MoodWeatherRecommender from '@/components/MoodWeatherRecommender';
import Gamification from '@/components/Gamification';
import ShoppingAssistant from '@/components/ShoppingAssistant';
import CollaborativeCooking from '@/components/CollaborativeCooking';
import NutritionTracker from '@/components/NutritionTracker';
import { PantryPlayAgent } from '@/lib/agent';
import { PantryItem, Recipe } from '@/lib/agent/types';

export default function Home() {
  const [agent, setAgent] = useState<PantryPlayAgent | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [isInitialized, setIsInitialized] = useState(false);
  const [currentRecipe, setCurrentRecipe] = useState<Recipe | null>(null);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [pantryItems, setPantryItems] = useState<PantryItem[]>([]);
  const [activeTab, setActiveTab] = useState<'pantry' | 'waste' | 'mood' | 'challenges' | 'shopping' | 'collab' | 'nutrition'>('pantry');

  const initializeAgent = () => {
    if (apiKey) {
      const newAgent = new PantryPlayAgent(apiKey);
      setAgent(newAgent);
      setIsInitialized(true);
    }
  };

  const handleRecipeGenerated = (recipe: Recipe) => {
    setCurrentRecipe(recipe);
    setRecipes(prev => [...prev, recipe]);
  };

  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome to Pantry Play!</h1>
          <p className="text-gray-600 mb-6">Your AI-powered culinary adventure companion</p>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
                Enter your Gemini API Key
              </label>
              <input
                type="password"
                id="apiKey"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                placeholder="Your API key"
              />
              <p className="mt-2 text-xs text-gray-500">
                Get your key from{' '}
                <a
                  href="https://makersuite.google.com/app/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  Google AI Studio
                </a>
              </p>
            </div>
            
            <button
              onClick={initializeAgent}
              disabled={!apiKey}
              className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Start Your Culinary Adventure
            </button>
          </div>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'pantry', label: 'Pantry', icon: '📸' },
    { id: 'waste', label: 'Zero Waste', icon: '♻️' },
    { id: 'mood', label: 'Mood Meals', icon: '🌈' },
    { id: 'challenges', label: 'Challenges', icon: '🏆' },
    { id: 'shopping', label: 'Shopping', icon: '🛒' },
    { id: 'collab', label: 'Cook Together', icon: '👥' },
    { id: 'nutrition', label: 'Nutrition', icon: '📊' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-3xl">🍳</span>
              <h1 className="text-2xl font-bold text-gray-800">Pantry Play</h1>
            </div>
            <StatsDisplay agent={agent} />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-6 overflow-x-auto">
          <div className="flex gap-2 min-w-max">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 rounded-lg font-medium transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-green-600 text-white'
                    : 'bg-white hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            {/* Dynamic Content Based on Active Tab */}
            {activeTab === 'pantry' && <PantryUpload agent={agent} onPantryUpdate={setPantryItems} />}
            {activeTab === 'waste' && <WasteTracker agent={agent} pantryItems={pantryItems} />}
            {activeTab === 'mood' && <MoodWeatherRecommender agent={agent} onRecipeSelect={handleRecipeGenerated} />}
            {activeTab === 'challenges' && <Gamification agent={agent} />}
            {activeTab === 'shopping' && <ShoppingAssistant agent={agent} recipes={recipes} pantryItems={pantryItems} />}
            {activeTab === 'collab' && <CollaborativeCooking agent={agent} currentRecipe={currentRecipe} />}
            {activeTab === 'nutrition' && <NutritionTracker agent={agent} recipes={recipes} />}
            
            {/* Always show current recipe if available */}
            {currentRecipe && <RecipeDisplay recipe={currentRecipe} />}
          </div>
          
          <div className="lg:col-span-1">
            <ChatInterface 
              agent={agent} 
              onRecipeGenerated={handleRecipeGenerated}
            />
          </div>
        </div>
      </main>
    </div>
  );
}