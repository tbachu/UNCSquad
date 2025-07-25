'use client';

import { useState, useEffect } from 'react';
import { PantryPlayAgent } from '@/lib/agent';
import { PantryItem } from '@/lib/agent/types';

interface WasteTrackerProps {
  agent: PantryPlayAgent | null;
  pantryItems: PantryItem[];
}

interface ExpiringItem extends PantryItem {
  daysUntilExpiry: number;
  urgencyLevel: 'critical' | 'warning' | 'ok';
}

export default function WasteTracker({ agent, pantryItems }: WasteTrackerProps) {
  const [expiringItems, setExpiringItems] = useState<ExpiringItem[]>([]);
  const [leftoverIdeas, setLeftoverIdeas] = useState<string[]>([]);
  const [wasteStats, setWasteStats] = useState({
    saved: 0,
    moneySaved: 0,
    co2Saved: 0,
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    analyzeExpiration();
  }, [pantryItems]);

  const analyzeExpiration = () => {
    const itemsWithExpiry: ExpiringItem[] = pantryItems.map(item => {
      // Simulate expiry analysis (in real app, would use actual dates)
      const daysUntilExpiry = Math.floor(Math.random() * 14) + 1;
      const urgencyLevel = 
        daysUntilExpiry <= 3 ? 'critical' : 
        daysUntilExpiry <= 7 ? 'warning' : 'ok';
      
      return {
        ...item,
        daysUntilExpiry,
        urgencyLevel,
      };
    });

    // Sort by urgency
    itemsWithExpiry.sort((a, b) => a.daysUntilExpiry - b.daysUntilExpiry);
    setExpiringItems(itemsWithExpiry.filter(item => item.daysUntilExpiry <= 7));
  };

  const getLeftoverIdeas = async () => {
    if (!agent || expiringItems.length === 0) return;
    
    setIsLoading(true);
    try {
      const itemNames = expiringItems.map(item => item.name).join(', ');
      const response = await agent.processUserInput(
        `Give me creative ideas to use these items before they expire: ${itemNames}`,
        { leftovers: expiringItems }
      );

      if (response.results?.track_waste) {
        // Extract ideas from response
        const ideas = response.results.track_waste.split('\n')
          .filter((line: string) => line.trim().startsWith('-') || line.trim().startsWith('•'))
          .map((line: string) => line.trim().substring(1).trim());
        setLeftoverIdeas(ideas);
      }
    } catch (error) {
      console.error('Error getting leftover ideas:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const markAsSaved = (item: ExpiringItem) => {
    // Update stats
    setWasteStats(prev => ({
      saved: prev.saved + 1,
      moneySaved: prev.moneySaved + (Math.random() * 5 + 1), // Simulate money saved
      co2Saved: prev.co2Saved + (Math.random() * 0.5 + 0.1), // Simulate CO2 saved
    }));

    // Remove from expiring items
    setExpiringItems(prev => prev.filter(i => i.name !== item.name));

    // Store in memory
    if (agent) {
      agent.updatePreferences({
        wasteReduced: 1,
        moneySaved: Math.random() * 5 + 1,
      });
    }
  };

  const getUrgencyColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-700 border-red-300';
      case 'warning': return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      default: return 'bg-green-100 text-green-700 border-green-300';
    }
  };

  const getUrgencyIcon = (level: string) => {
    switch (level) {
      case 'critical': return '🚨';
      case 'warning': return '⚠️';
      default: return '✅';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800 flex items-center">
          <span className="mr-2">♻️</span> Zero-Waste Tracker
        </h2>
        <div className="flex gap-4 text-sm">
          <div className="text-center">
            <p className="font-bold text-green-600">{wasteStats.saved}</p>
            <p className="text-gray-500">Items Saved</p>
          </div>
          <div className="text-center">
            <p className="font-bold text-green-600">${wasteStats.moneySaved.toFixed(2)}</p>
            <p className="text-gray-500">Money Saved</p>
          </div>
          <div className="text-center">
            <p className="font-bold text-green-600">{wasteStats.co2Saved.toFixed(2)}kg</p>
            <p className="text-gray-500">CO2 Saved</p>
          </div>
        </div>
      </div>

      {expiringItems.length > 0 ? (
        <>
          <div className="mb-4">
            <h3 className="font-medium text-gray-700 mb-2">Items Expiring Soon</h3>
            <div className="space-y-2">
              {expiringItems.map((item, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-3 rounded-lg border ${getUrgencyColor(item.urgencyLevel)}`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{getUrgencyIcon(item.urgencyLevel)}</span>
                    <div>
                      <p className="font-medium">{item.name}</p>
                      <p className="text-sm opacity-75">
                        {item.quantity} • Expires in {item.daysUntilExpiry} day{item.daysUntilExpiry !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => markAsSaved(item)}
                    className="text-sm bg-white px-3 py-1 rounded-lg hover:bg-gray-50 transition"
                  >
                    Mark as Used
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t pt-4">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-medium text-gray-700">Leftover Transformation Ideas</h3>
              <button
                onClick={getLeftoverIdeas}
                disabled={isLoading}
                className="text-sm bg-green-600 text-white px-3 py-1 rounded-lg hover:bg-green-700 transition disabled:bg-gray-300"
              >
                {isLoading ? 'Getting Ideas...' : 'Get Ideas'}
              </button>
            </div>

            {leftoverIdeas.length > 0 && (
              <div className="space-y-2">
                {leftoverIdeas.map((idea, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <span className="text-green-600 mt-1">💡</span>
                    <p className="text-sm text-gray-700">{idea}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">🎉</div>
          <p>Great job! No items expiring soon.</p>
          <p className="text-sm mt-1">Keep up the zero-waste cooking!</p>
        </div>
      )}

      <div className="mt-4 p-3 bg-green-50 rounded-lg">
        <p className="text-sm text-green-800">
          <span className="font-medium">Pro Tip:</span> Plan meals using items that expire first to minimize waste and save money!
        </p>
      </div>
    </div>
  );
}