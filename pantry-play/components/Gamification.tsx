'use client';

import { useState, useEffect } from 'react';
import { PantryPlayAgent } from '@/lib/agent';
import { Achievement } from '@/lib/agent/types';

interface GamificationProps {
  agent: PantryPlayAgent | null;
}

interface Challenge {
  id: string;
  title: string;
  description: string;
  icon: string;
  progress: number;
  maxProgress: number;
  reward: string;
  difficulty: 'easy' | 'medium' | 'hard';
  completed: boolean;
}

const dailyChallenges: Challenge[] = [
  {
    id: 'colorful-plate',
    title: 'Rainbow Plate',
    description: 'Cook a meal with at least 5 different colors',
    icon: '🌈',
    progress: 0,
    maxProgress: 5,
    reward: 'Color Master Badge',
    difficulty: 'medium',
    completed: false,
  },
  {
    id: 'zero-waste-hero',
    title: 'Zero Waste Hero',
    description: 'Use all expiring ingredients today',
    icon: '♻️',
    progress: 0,
    maxProgress: 3,
    reward: 'Eco Warrior Badge',
    difficulty: 'easy',
    completed: false,
  },
  {
    id: 'cuisine-explorer',
    title: 'Cuisine Explorer',
    description: 'Cook a dish from a new cuisine',
    icon: '🌍',
    progress: 0,
    maxProgress: 1,
    reward: 'Explorer Badge',
    difficulty: 'easy',
    completed: false,
  },
  {
    id: 'speed-chef',
    title: 'Speed Chef',
    description: 'Prepare a meal in under 20 minutes',
    icon: '⚡',
    progress: 0,
    maxProgress: 1,
    reward: 'Lightning Chef Badge',
    difficulty: 'hard',
    completed: false,
  },
];

const badges = [
  { id: 'novice', name: 'Novice Chef', icon: '👨‍🍳', requirement: 'Cook 5 recipes' },
  { id: 'waste-warrior', name: 'Waste Warrior', icon: '🛡️', requirement: 'Save 10 items from waste' },
  { id: 'flavor-master', name: 'Flavor Master', icon: '🎯', requirement: 'Try 10 cuisines' },
  { id: 'social-chef', name: 'Social Chef', icon: '👥', requirement: 'Share 5 recipes' },
  { id: 'budget-hero', name: 'Budget Hero', icon: '💰', requirement: 'Save $50' },
  { id: 'streak-master', name: 'Streak Master', icon: '🔥', requirement: '7 day cooking streak' },
];

export default function Gamification({ agent }: GamificationProps) {
  const [challenges, setChallenges] = useState<Challenge[]>(dailyChallenges);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [level, setLevel] = useState(1);
  const [xp, setXp] = useState(0);
  const [streak, setStreak] = useState(0);
  const [showReward, setShowReward] = useState<string | null>(null);

  useEffect(() => {
    if (agent) {
      setAchievements(agent.getAchievements());
      const stats = agent.getUserStats();
      // Calculate level based on recipes cooked
      setLevel(Math.floor(stats.recipesCooked / 5) + 1);
      setXp((stats.recipesCooked % 5) * 20);
    }
  }, [agent]);

  const updateChallengeProgress = (challengeId: string, increment: number = 1) => {
    setChallenges(prev => prev.map(challenge => {
      if (challenge.id === challengeId && !challenge.completed) {
        const newProgress = Math.min(challenge.progress + increment, challenge.maxProgress);
        const completed = newProgress === challenge.maxProgress;
        
        if (completed) {
          // Show reward animation
          setShowReward(challenge.reward);
          setTimeout(() => setShowReward(null), 3000);
          
          // Award XP
          const xpReward = challenge.difficulty === 'easy' ? 10 : 
                          challenge.difficulty === 'medium' ? 20 : 30;
          setXp(prev => {
            const newXp = prev + xpReward;
            if (newXp >= 100) {
              setLevel(prev => prev + 1);
              return newXp - 100;
            }
            return newXp;
          });
          
          // Store achievement
          if (agent) {
            agent.updatePreferences({
              achievement: {
                name: challenge.reward,
                description: challenge.description,
                isChallenge: true,
              }
            });
          }
        }
        
        return { ...challenge, progress: newProgress, completed };
      }
      return challenge;
    }));
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-700';
      case 'medium': return 'bg-yellow-100 text-yellow-700';
      case 'hard': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const shareChallenge = (challenge: Challenge) => {
    // Simulate sharing
    alert(`Challenge shared: ${challenge.title}`);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800 flex items-center">
          <span className="mr-2">🏆</span> Challenges & Achievements
        </h2>
        <div className="flex items-center gap-4">
          <div className="text-center">
            <p className="text-sm text-gray-600">Level</p>
            <p className="text-2xl font-bold text-purple-600">{level}</p>
          </div>
          <div className="w-32 bg-gray-200 rounded-full h-3 relative">
            <div 
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${xp}%` }}
            />
            <p className="text-xs text-center mt-1 text-gray-600">{xp}/100 XP</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">Streak</p>
            <p className="text-2xl font-bold text-orange-600 flex items-center">
              {streak} <span className="text-lg ml-1">🔥</span>
            </p>
          </div>
        </div>
      </div>

      {/* Daily Challenges */}
      <div className="mb-6">
        <h3 className="font-medium text-gray-700 mb-3">Today's Challenges</h3>
        <div className="grid gap-3">
          {challenges.map((challenge) => (
            <div
              key={challenge.id}
              className={`border rounded-lg p-4 ${
                challenge.completed ? 'bg-green-50 border-green-300' : 'bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{challenge.icon}</span>
                  <div>
                    <h4 className="font-medium text-gray-800">{challenge.title}</h4>
                    <p className="text-sm text-gray-600">{challenge.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(challenge.difficulty)}`}>
                    {challenge.difficulty}
                  </span>
                  {challenge.completed && (
                    <span className="text-green-600 text-xl">✓</span>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-gray-200 rounded-full h-2 relative">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      challenge.completed ? 'bg-green-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${(challenge.progress / challenge.maxProgress) * 100}%` }}
                  />
                </div>
                <span className="text-sm text-gray-600">
                  {challenge.progress}/{challenge.maxProgress}
                </span>
                <button
                  onClick={() => shareChallenge(challenge)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  Share
                </button>
              </div>
              
              {challenge.completed && (
                <p className="text-sm text-green-600 mt-2">
                  🎉 Reward: {challenge.reward}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Simulate progress buttons (for demo) */}
        <div className="mt-3 flex gap-2">
          <button
            onClick={() => updateChallengeProgress('colorful-plate')}
            className="text-xs bg-gray-200 px-3 py-1 rounded hover:bg-gray-300"
          >
            Add Color
          </button>
          <button
            onClick={() => updateChallengeProgress('zero-waste-hero')}
            className="text-xs bg-gray-200 px-3 py-1 rounded hover:bg-gray-300"
          >
            Use Expiring Item
          </button>
        </div>
      </div>

      {/* Badges */}
      <div>
        <h3 className="font-medium text-gray-700 mb-3">Badge Collection</h3>
        <div className="grid grid-cols-3 gap-3">
          {badges.map((badge) => {
            const isEarned = achievements.some(a => a.id === badge.id);
            return (
              <div
                key={badge.id}
                className={`text-center p-3 rounded-lg ${
                  isEarned ? 'bg-gradient-to-br from-yellow-50 to-orange-50' : 'bg-gray-100'
                }`}
              >
                <div className={`text-3xl mb-1 ${!isEarned && 'grayscale opacity-50'}`}>
                  {badge.icon}
                </div>
                <p className="text-xs font-medium text-gray-700">{badge.name}</p>
                <p className="text-xs text-gray-500 mt-1">{badge.requirement}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Reward Animation */}
      {showReward && (
        <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
          <div className="bg-white rounded-xl shadow-2xl p-8 animate-bounce">
            <div className="text-6xl mb-4 text-center">🎉</div>
            <p className="text-xl font-bold text-gray-800">Achievement Unlocked!</p>
            <p className="text-lg text-gray-600 mt-2">{showReward}</p>
          </div>
        </div>
      )}
    </div>
  );
}