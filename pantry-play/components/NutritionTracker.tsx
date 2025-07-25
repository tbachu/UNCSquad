'use client';

import { useState, useEffect } from 'react';
import { PantryPlayAgent } from '@/lib/agent';
import { Recipe, NutritionInfo } from '@/lib/agent/types';

interface NutritionTrackerProps {
  agent: PantryPlayAgent | null;
  recipes: Recipe[];
}

interface DailyNutrition {
  date: Date;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  meals: Recipe[];
}

interface NutritionGoals {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
}

export default function NutritionTracker({ agent, recipes }: NutritionTrackerProps) {
  const [dailyNutrition, setDailyNutrition] = useState<DailyNutrition>({
    date: new Date(),
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    fiber: 0,
    meals: [],
  });
  
  const [weeklyData, setWeeklyData] = useState<DailyNutrition[]>([]);
  const [goals, setGoals] = useState<NutritionGoals>({
    calories: 2000,
    protein: 50,
    carbs: 250,
    fat: 65,
    fiber: 25,
  });
  
  const [showGoalEditor, setShowGoalEditor] = useState(false);
  const [activeTab, setActiveTab] = useState<'today' | 'weekly' | 'insights'>('today');

  useEffect(() => {
    // Calculate today's nutrition from recipes
    const todaysMeals = recipes.filter(r => r.nutrition);
    const totals = todaysMeals.reduce((acc, meal) => {
      if (meal.nutrition) {
        acc.calories += meal.nutrition.calories;
        acc.protein += meal.nutrition.protein;
        acc.carbs += meal.nutrition.carbs;
        acc.fat += meal.nutrition.fat;
        acc.fiber += meal.nutrition.fiber || 0;
      }
      return acc;
    }, {
      calories: 0,
      protein: 0,
      carbs: 0,
      fat: 0,
      fiber: 0,
    });

    setDailyNutrition({
      date: new Date(),
      ...totals,
      meals: todaysMeals,
    });

    // Generate mock weekly data
    generateWeeklyData();
  }, [recipes]);

  const generateWeeklyData = () => {
    const data: DailyNutrition[] = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      data.push({
        date,
        calories: 1800 + Math.random() * 400,
        protein: 45 + Math.random() * 20,
        carbs: 200 + Math.random() * 100,
        fat: 50 + Math.random() * 30,
        fiber: 20 + Math.random() * 10,
        meals: [],
      });
    }
    setWeeklyData(data);
  };

  const getPercentage = (current: number, goal: number) => {
    return Math.min(Math.round((current / goal) * 100), 100);
  };

  const getProgressColor = (percentage: number) => {
    if (percentage < 60) return 'bg-yellow-500';
    if (percentage < 90) return 'bg-green-500';
    if (percentage <= 110) return 'bg-green-600';
    return 'bg-red-500';
  };

  const nutrients = [
    { key: 'calories', label: 'Calories', unit: 'kcal', icon: '🔥' },
    { key: 'protein', label: 'Protein', unit: 'g', icon: '💪' },
    { key: 'carbs', label: 'Carbs', unit: 'g', icon: '🌾' },
    { key: 'fat', label: 'Fat', unit: 'g', icon: '🥑' },
    { key: 'fiber', label: 'Fiber', unit: 'g', icon: '🥬' },
  ];

  const getDietaryLabels = () => {
    const labels = [];
    const avgProtein = weeklyData.reduce((sum, day) => sum + day.protein, 0) / 7;
    const avgCarbs = weeklyData.reduce((sum, day) => sum + day.carbs, 0) / 7;
    
    if (avgProtein > 100) labels.push({ name: 'High Protein', color: 'bg-purple-100 text-purple-700' });
    if (avgCarbs < 100) labels.push({ name: 'Low Carb', color: 'bg-orange-100 text-orange-700' });
    if (dailyNutrition.fiber > 25) labels.push({ name: 'High Fiber', color: 'bg-green-100 text-green-700' });
    
    return labels;
  };

  const getInsights = () => {
    const insights = [];
    
    if (dailyNutrition.protein < goals.protein * 0.8) {
      insights.push({
        type: 'warning',
        message: 'Your protein intake is below target. Consider adding lean meats, legumes, or dairy.',
      });
    }
    
    if (dailyNutrition.fiber < goals.fiber * 0.7) {
      insights.push({
        type: 'tip',
        message: 'Increase fiber intake with whole grains, fruits, and vegetables for better digestion.',
      });
    }
    
    if (dailyNutrition.calories > goals.calories * 1.1) {
      insights.push({
        type: 'info',
        message: 'Calorie intake is above your goal. Consider portion control or lighter meal options.',
      });
    }
    
    return insights;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800 flex items-center">
          <span className="mr-2">📊</span> Nutrition Tracker
        </h2>
        <button
          onClick={() => setShowGoalEditor(!showGoalEditor)}
          className="text-sm text-blue-600 hover:text-blue-700"
        >
          Edit Goals
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('today')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            activeTab === 'today'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Today
        </button>
        <button
          onClick={() => setActiveTab('weekly')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            activeTab === 'weekly'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Weekly View
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            activeTab === 'insights'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Insights
        </button>
      </div>

      {/* Today Tab */}
      {activeTab === 'today' && (
        <div className="space-y-4">
          {/* Nutrition Progress */}
          <div className="space-y-3">
            {nutrients.map((nutrient) => {
              const current = dailyNutrition[nutrient.key as keyof DailyNutrition] as number;
              const goal = goals[nutrient.key as keyof NutritionGoals];
              const percentage = getPercentage(current, goal);
              
              return (
                <div key={nutrient.key}>
                  <div className="flex justify-between items-center mb-1">
                    <div className="flex items-center gap-2">
                      <span>{nutrient.icon}</span>
                      <span className="font-medium text-gray-700">{nutrient.label}</span>
                    </div>
                    <span className="text-sm text-gray-600">
                      {current.toFixed(0)} / {goal} {nutrient.unit}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${getProgressColor(percentage)}`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Today's Meals */}
          {dailyNutrition.meals.length > 0 && (
            <div>
              <h3 className="font-medium text-gray-700 mb-2">Today's Meals</h3>
              <div className="space-y-2">
                {dailyNutrition.meals.map((meal, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium text-gray-800">{meal.name}</p>
                    <p className="text-sm text-gray-600">
                      {meal.nutrition?.calories} cal • {meal.nutrition?.protein}g protein
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dietary Labels */}
          <div className="flex gap-2 flex-wrap">
            {getDietaryLabels().map((label, index) => (
              <span key={index} className={`px-3 py-1 rounded-full text-sm ${label.color}`}>
                {label.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Weekly View Tab */}
      {activeTab === 'weekly' && (
        <div className="space-y-4">
          <div className="grid grid-cols-7 gap-2">
            {weeklyData.map((day, index) => (
              <div key={index} className="text-center">
                <p className="text-xs text-gray-600 mb-1">
                  {day.date.toLocaleDateString('en', { weekday: 'short' })}
                </p>
                <div className="bg-gray-100 rounded-lg p-2">
                  <p className="font-bold text-lg">{Math.round(day.calories)}</p>
                  <p className="text-xs text-gray-600">cal</p>
                </div>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <h3 className="font-medium text-gray-700">Weekly Averages</h3>
            {nutrients.map((nutrient) => {
              const avg = weeklyData.reduce((sum, day) => 
                sum + (day[nutrient.key as keyof DailyNutrition] as number), 0
              ) / 7;
              
              return (
                <div key={nutrient.key} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <span className="flex items-center gap-2">
                    <span>{nutrient.icon}</span>
                    <span className="text-sm">{nutrient.label}</span>
                  </span>
                  <span className="font-medium">
                    {avg.toFixed(0)} {nutrient.unit}/day
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Insights Tab */}
      {activeTab === 'insights' && (
        <div className="space-y-4">
          {getInsights().map((insight, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg ${
                insight.type === 'warning' ? 'bg-yellow-50' :
                insight.type === 'tip' ? 'bg-blue-50' : 'bg-gray-50'
              }`}
            >
              <p className={`text-sm ${
                insight.type === 'warning' ? 'text-yellow-800' :
                insight.type === 'tip' ? 'text-blue-800' : 'text-gray-800'
              }`}>
                {insight.message}
              </p>
            </div>
          ))}

          <div className="p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-800 mb-2">Your Progress</h4>
            <p className="text-sm text-green-700">
              You're maintaining a balanced diet! Keep focusing on whole foods and variety.
            </p>
          </div>

          <div>
            <h4 className="font-medium text-gray-700 mb-2">Recommendations</h4>
            <ul className="space-y-2">
              <li className="flex items-start gap-2">
                <span className="text-green-600">•</span>
                <span className="text-sm text-gray-700">Add more colorful vegetables for antioxidants</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600">•</span>
                <span className="text-sm text-gray-700">Include omega-3 rich foods like salmon or walnuts</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600">•</span>
                <span className="text-sm text-gray-700">Stay hydrated with 8-10 glasses of water daily</span>
              </li>
            </ul>
          </div>
        </div>
      )}

      {/* Goal Editor Modal */}
      {showGoalEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="font-bold text-gray-800 mb-4">Edit Nutrition Goals</h3>
            <div className="space-y-3">
              {nutrients.map((nutrient) => (
                <div key={nutrient.key}>
                  <label className="text-sm text-gray-600">{nutrient.label} ({nutrient.unit})</label>
                  <input
                    type="number"
                    value={goals[nutrient.key as keyof NutritionGoals]}
                    onChange={(e) => setGoals(prev => ({
                      ...prev,
                      [nutrient.key]: Number(e.target.value)
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  />
                </div>
              ))}
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={() => setShowGoalEditor(false)}
                className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
              >
                Save Goals
              </button>
              <button
                onClick={() => setShowGoalEditor(false)}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300 transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}