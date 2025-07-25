'use client';

import { useState } from 'react';
import { PantryPlayAgent } from '@/lib/agent';
import { Recipe } from '@/lib/agent/types';

interface ShoppingAssistantProps {
  agent: PantryPlayAgent | null;
  recipes: Recipe[];
  pantryItems: any[];
}

interface ShoppingItem {
  name: string;
  quantity: string;
  category: string;
  price: number;
  checked: boolean;
  alternatives?: string[];
}

export default function ShoppingAssistant({ agent, recipes, pantryItems }: ShoppingAssistantProps) {
  const [shoppingList, setShoppingList] = useState<ShoppingItem[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [budget, setBudget] = useState<number>(50);
  const [showAlternatives, setShowAlternatives] = useState<string | null>(null);
  const [selectedStore, setSelectedStore] = useState('all');

  const categories = [
    { id: 'produce', name: 'Produce', icon: '🥬' },
    { id: 'dairy', name: 'Dairy', icon: '🥛' },
    { id: 'meat', name: 'Meat & Fish', icon: '🥩' },
    { id: 'grains', name: 'Grains & Pasta', icon: '🌾' },
    { id: 'pantry', name: 'Pantry', icon: '🥫' },
    { id: 'frozen', name: 'Frozen', icon: '❄️' },
  ];

  const stores = [
    { id: 'all', name: 'All Stores' },
    { id: 'walmart', name: 'Walmart' },
    { id: 'wholefoods', name: 'Whole Foods' },
    { id: 'trader-joes', name: "Trader Joe's" },
  ];

  const generateShoppingList = async () => {
    if (!agent || recipes.length === 0) return;

    setIsGenerating(true);
    try {
      const response = await agent.processUserInput(
        'Create an optimized shopping list for my meal plan',
        {
          mealPlan: recipes,
          currentPantry: pantryItems,
          budget: budget,
        }
      );

      if (response.results?.create_shopping_list) {
        // Parse the shopping list (simplified for demo)
        const items: ShoppingItem[] = [
          { name: 'Tomatoes', quantity: '6', category: 'produce', price: 3.99, checked: false, alternatives: ['Cherry tomatoes', 'Canned tomatoes'] },
          { name: 'Chicken Breast', quantity: '2 lbs', category: 'meat', price: 12.99, checked: false, alternatives: ['Chicken thighs', 'Turkey breast'] },
          { name: 'Pasta', quantity: '1 box', category: 'grains', price: 2.49, checked: false, alternatives: ['Rice', 'Quinoa'] },
          { name: 'Mozzarella', quantity: '8 oz', category: 'dairy', price: 4.99, checked: false, alternatives: ['Provolone', 'Cheddar'] },
          { name: 'Basil', quantity: '1 bunch', category: 'produce', price: 2.99, checked: false },
          { name: 'Olive Oil', quantity: '1 bottle', category: 'pantry', price: 8.99, checked: false, alternatives: ['Avocado oil', 'Canola oil'] },
        ];
        setShoppingList(items);
      }
    } catch (error) {
      console.error('Error generating shopping list:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const toggleItem = (index: number) => {
    setShoppingList(prev => prev.map((item, i) => 
      i === index ? { ...item, checked: !item.checked } : item
    ));
  };

  const removeItem = (index: number) => {
    setShoppingList(prev => prev.filter((_, i) => i !== index));
  };

  const addCustomItem = () => {
    const newItem: ShoppingItem = {
      name: '',
      quantity: '',
      category: 'pantry',
      price: 0,
      checked: false,
    };
    setShoppingList(prev => [...prev, newItem]);
  };

  const updateItem = (index: number, field: keyof ShoppingItem, value: any) => {
    setShoppingList(prev => prev.map((item, i) => 
      i === index ? { ...item, [field]: value } : item
    ));
  };

  const getTotalPrice = () => {
    return shoppingList.reduce((sum, item) => sum + (item.checked ? 0 : item.price), 0);
  };

  const getCategoryItems = (categoryId: string) => {
    return shoppingList.filter(item => item.category === categoryId);
  };

  const exportList = () => {
    const text = shoppingList
      .map(item => `${item.checked ? '✓' : '☐'} ${item.name} - ${item.quantity}`)
      .join('\n');
    
    // Create a blob and download
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'shopping-list.txt';
    a.click();
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800 flex items-center">
          <span className="mr-2">🛒</span> Smart Shopping List
        </h2>
        <div className="flex items-center gap-4">
          <div className="text-center">
            <p className="text-sm text-gray-600">Budget</p>
            <input
              type="number"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              className="w-20 text-center font-bold text-green-600 border-b border-gray-300 focus:border-green-500"
            />
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">Total</p>
            <p className="font-bold text-gray-800">${getTotalPrice().toFixed(2)}</p>
          </div>
        </div>
      </div>

      {/* Store Selection */}
      <div className="mb-4 flex gap-2">
        {stores.map((store) => (
          <button
            key={store.id}
            onClick={() => setSelectedStore(store.id)}
            className={`px-3 py-1 rounded-lg text-sm transition ${
              selectedStore === store.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            {store.name}
          </button>
        ))}
      </div>

      {shoppingList.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-4">🛍️</div>
          <p className="text-gray-600 mb-4">No items in your shopping list yet</p>
          <button
            onClick={generateShoppingList}
            disabled={isGenerating}
            className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition disabled:bg-gray-300"
          >
            {isGenerating ? 'Generating List...' : 'Generate Smart Shopping List'}
          </button>
        </div>
      ) : (
        <>
          {/* Shopping List by Category */}
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {categories.map((category) => {
              const items = getCategoryItems(category.id);
              if (items.length === 0) return null;

              return (
                <div key={category.id}>
                  <h3 className="font-medium text-gray-700 mb-2 flex items-center sticky top-0 bg-white py-1">
                    <span className="mr-2">{category.icon}</span>
                    {category.name}
                  </h3>
                  <div className="space-y-2 pl-8">
                    {items.map((item, index) => {
                      const originalIndex = shoppingList.indexOf(item);
                      return (
                        <div
                          key={originalIndex}
                          className={`flex items-center gap-3 p-2 rounded-lg ${
                            item.checked ? 'bg-gray-50 opacity-60' : 'bg-white'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={item.checked}
                            onChange={() => toggleItem(originalIndex)}
                            className="w-5 h-5 text-green-600"
                          />
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className={item.checked ? 'line-through' : ''}>
                                {item.name}
                              </span>
                              <span className="text-sm text-gray-500">
                                {item.quantity}
                              </span>
                              {item.alternatives && (
                                <button
                                  onClick={() => setShowAlternatives(
                                    showAlternatives === item.name ? null : item.name
                                  )}
                                  className="text-xs text-blue-600 hover:text-blue-700"
                                >
                                  alternatives
                                </button>
                              )}
                            </div>
                            {showAlternatives === item.name && item.alternatives && (
                              <div className="mt-1 text-sm text-gray-600">
                                <span className="font-medium">Alternatives:</span>{' '}
                                {item.alternatives.join(', ')}
                              </div>
                            )}
                          </div>
                          <span className="font-medium text-gray-700">
                            ${item.price.toFixed(2)}
                          </span>
                          <button
                            onClick={() => removeItem(originalIndex)}
                            className="text-red-600 hover:text-red-700"
                          >
                            ✕
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Actions */}
          <div className="mt-4 pt-4 border-t flex justify-between">
            <div className="flex gap-2">
              <button
                onClick={addCustomItem}
                className="text-sm bg-gray-100 px-3 py-1 rounded-lg hover:bg-gray-200 transition"
              >
                + Add Item
              </button>
              <button
                onClick={exportList}
                className="text-sm bg-gray-100 px-3 py-1 rounded-lg hover:bg-gray-200 transition"
              >
                Export List
              </button>
            </div>
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Order Online
            </button>
          </div>

          {/* Budget Warning */}
          {getTotalPrice() > budget && (
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
              <p className="text-sm text-yellow-800">
                <span className="font-medium">Over Budget:</span> Consider alternatives or remove items to stay within ${budget}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}