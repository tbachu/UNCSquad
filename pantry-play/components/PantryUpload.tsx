'use client';

import { useState, useRef, useEffect } from 'react';
import { PantryPlayAgent } from '@/lib/agent';
import { PantryItem } from '@/lib/agent/types';

interface PantryUploadProps {
  agent: PantryPlayAgent | null;
  onPantryUpdate?: (items: PantryItem[]) => void;
}

export default function PantryUpload({ agent, onPantryUpdate }: PantryUploadProps) {
  const [pantryItems, setPantryItems] = useState<PantryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (onPantryUpdate) {
      onPantryUpdate(pantryItems);
    }
  }, [pantryItems, onPantryUpdate]);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !agent) return;

    setIsLoading(true);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    try {
      // Convert image to base64
      const base64 = await fileToBase64(file);
      
      // Process with agent
      const result = await agent.processUserInput('analyze my pantry items from this image', {
        image_data: base64,
      });

      if (result.results?.analyze_pantry?.ingredients) {
        setPantryItems(result.results.analyze_pantry.ingredients);
      }
    } catch (error) {
      console.error('Error processing image:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  };

  const addManualItem = () => {
    const newItem: PantryItem = {
      name: '',
      quantity: '',
      category: 'other',
    };
    setPantryItems([...pantryItems, newItem]);
  };

  const updateItem = (index: number, field: keyof PantryItem, value: string) => {
    const updated = [...pantryItems];
    updated[index] = { ...updated[index], [field]: value };
    setPantryItems(updated);
  };

  const removeItem = (index: number) => {
    setPantryItems(pantryItems.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">📸</span> Your Pantry
      </h2>

      <div className="space-y-4">
        {/* Image Upload */}
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-green-500 transition"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
          
          {imagePreview ? (
            <div className="space-y-2">
              <img 
                src={imagePreview} 
                alt="Pantry preview" 
                className="max-h-48 mx-auto rounded-lg"
              />
              <p className="text-sm text-gray-600">Click to upload a new image</p>
            </div>
          ) : (
            <>
              <div className="text-4xl mb-2">📷</div>
              <p className="text-gray-600">Click to upload a photo of your pantry</p>
              <p className="text-sm text-gray-500">Or add items manually below</p>
            </>
          )}
        </div>

        {isLoading && (
          <div className="text-center py-4">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
            <p className="text-sm text-gray-600 mt-2">Analyzing your pantry...</p>
          </div>
        )}

        {/* Manual Item Entry */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="font-medium text-gray-700">Pantry Items</h3>
            <button
              onClick={addManualItem}
              className="text-sm bg-green-600 text-white px-3 py-1 rounded-lg hover:bg-green-700 transition"
            >
              + Add Item
            </button>
          </div>

          {pantryItems.map((item, index) => (
            <div key={index} className="flex gap-2 items-center">
              <input
                type="text"
                value={item.name}
                onChange={(e) => updateItem(index, 'name', e.target.value)}
                placeholder="Item name"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <input
                type="text"
                value={item.quantity}
                onChange={(e) => updateItem(index, 'quantity', e.target.value)}
                placeholder="Quantity"
                className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <select
                value={item.category}
                onChange={(e) => updateItem(index, 'category', e.target.value)}
                className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                <option value="vegetables">Vegetables</option>
                <option value="fruits">Fruits</option>
                <option value="proteins">Proteins</option>
                <option value="dairy">Dairy</option>
                <option value="grains">Grains</option>
                <option value="spices">Spices</option>
                <option value="other">Other</option>
              </select>
              <button
                onClick={() => removeItem(index)}
                className="text-red-600 hover:text-red-700"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        {pantryItems.length > 0 && (
          <div className="pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              <p className="font-medium mb-1">Pantry Summary:</p>
              <p>Total items: {pantryItems.length}</p>
              <p>Categories: {new Set(pantryItems.map(item => item.category)).size}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}