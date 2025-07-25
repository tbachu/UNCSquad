'use client';

import { useEffect, useState } from 'react';
import { PantryPlayAgent } from '@/lib/agent';

interface StatsDisplayProps {
  agent: PantryPlayAgent | null;
}

export default function StatsDisplay({ agent }: StatsDisplayProps) {
  const [stats, setStats] = useState({
    recipesCooked: 0,
    wasteReducedKg: 0,
    moneySaved: 0,
    challengesCompleted: 0,
  });

  useEffect(() => {
    if (agent) {
      const userStats = agent.getUserStats();
      setStats(userStats);
    }
  }, [agent]);

  const statItems = [
    { icon: '🍳', value: stats.recipesCooked, label: 'Recipes' },
    { icon: '♻️', value: `${stats.wasteReducedKg.toFixed(1)}kg`, label: 'Waste Saved' },
    { icon: '💰', value: `$${stats.moneySaved.toFixed(0)}`, label: 'Money Saved' },
    { icon: '🏆', value: stats.challengesCompleted, label: 'Challenges' },
  ];

  return (
    <div className="flex items-center space-x-6">
      {statItems.map((stat, index) => (
        <div key={index} className="text-center">
          <div className="flex items-center justify-center space-x-1">
            <span className="text-xl">{stat.icon}</span>
            <span className="font-bold text-lg text-gray-800">{stat.value}</span>
          </div>
          <p className="text-xs text-gray-600">{stat.label}</p>
        </div>
      ))}
    </div>
  );
}