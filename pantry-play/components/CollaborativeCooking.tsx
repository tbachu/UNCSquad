'use client';

import { useState } from 'react';
import { PantryPlayAgent } from '@/lib/agent';
import { Recipe } from '@/lib/agent/types';

interface CollaborativeCookingProps {
  agent: PantryPlayAgent | null;
  currentRecipe: Recipe | null;
}

interface Friend {
  id: string;
  name: string;
  avatar: string;
  status: 'online' | 'cooking' | 'offline';
}

interface Vote {
  userId: string;
  recipeId: string;
  vote: 'yes' | 'no';
}

interface SharedPantryItem {
  name: string;
  owner: string;
  available: boolean;
}

const mockFriends: Friend[] = [
  { id: '1', name: 'Sarah', avatar: '👩', status: 'online' },
  { id: '2', name: 'Mike', avatar: '👨', status: 'cooking' },
  { id: '3', name: 'Emma', avatar: '👩‍🦰', status: 'online' },
  { id: '4', name: 'James', avatar: '👨‍🦱', status: 'offline' },
];

export default function CollaborativeCooking({ agent, currentRecipe }: CollaborativeCookingProps) {
  const [activeTab, setActiveTab] = useState<'vote' | 'share' | 'cook-together'>('vote');
  const [friends, setFriends] = useState<Friend[]>(mockFriends);
  const [recipeVotes, setRecipeVotes] = useState<Record<string, Vote[]>>({});
  const [sharedPantry, setSharedPantry] = useState<SharedPantryItem[]>([
    { name: 'Olive Oil', owner: 'Sarah', available: true },
    { name: 'Pasta', owner: 'Mike', available: true },
    { name: 'Tomatoes', owner: 'You', available: true },
  ]);
  const [cookingSession, setCookingSession] = useState<{
    active: boolean;
    participants: Friend[];
    recipe: Recipe | null;
  }>({
    active: false,
    participants: [],
    recipe: null,
  });

  const voteForRecipe = (recipeId: string, vote: 'yes' | 'no') => {
    const newVote: Vote = {
      userId: 'current-user',
      recipeId,
      vote,
    };
    
    setRecipeVotes(prev => ({
      ...prev,
      [recipeId]: [...(prev[recipeId] || []), newVote],
    }));
  };

  const inviteFriends = (friendIds: string[]) => {
    const invited = friends.filter(f => friendIds.includes(f.id));
    setCookingSession(prev => ({
      ...prev,
      participants: [...prev.participants, ...invited],
    }));
  };

  const startCookingSession = () => {
    if (!currentRecipe) return;
    
    setCookingSession({
      active: true,
      participants: friends.filter(f => f.status === 'online'),
      recipe: currentRecipe,
    });
  };

  const shareIngredient = (ingredient: string) => {
    setSharedPantry(prev => [...prev, {
      name: ingredient,
      owner: 'You',
      available: true,
    }]);
  };

  const requestIngredient = (item: SharedPantryItem) => {
    alert(`Request sent to ${item.owner} for ${item.name}`);
  };

  const getVotePercentage = (recipeId: string) => {
    const votes = recipeVotes[recipeId] || [];
    const yesVotes = votes.filter(v => v.vote === 'yes').length;
    return votes.length > 0 ? Math.round((yesVotes / votes.length) * 100) : 0;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">👥</span> Cook Together
      </h2>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('vote')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            activeTab === 'vote'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Vote on Meals
        </button>
        <button
          onClick={() => setActiveTab('share')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            activeTab === 'share'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Share Pantry
        </button>
        <button
          onClick={() => setActiveTab('cook-together')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            activeTab === 'cook-together'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          Live Cooking
        </button>
      </div>

      {/* Vote on Meals Tab */}
      {activeTab === 'vote' && (
        <div className="space-y-4">
          <p className="text-sm text-gray-600 mb-4">
            Vote on meal suggestions with friends and family
          </p>
          
          {currentRecipe && (
            <div className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-medium text-gray-800">{currentRecipe.name}</h4>
                  <p className="text-sm text-gray-600">{currentRecipe.description}</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    {getVotePercentage(currentRecipe.id)}%
                  </p>
                  <p className="text-xs text-gray-500">approval</p>
                </div>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={() => voteForRecipe(currentRecipe.id, 'yes')}
                  className="flex-1 bg-green-100 text-green-700 py-2 rounded-lg hover:bg-green-200 transition"
                >
                  👍 Yes
                </button>
                <button
                  onClick={() => voteForRecipe(currentRecipe.id, 'no')}
                  className="flex-1 bg-red-100 text-red-700 py-2 rounded-lg hover:bg-red-200 transition"
                >
                  👎 No
                </button>
                <button className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition">
                  Share
                </button>
              </div>
              
              <div className="mt-3 flex -space-x-2">
                {friends.slice(0, 3).map((friend) => (
                  <div
                    key={friend.id}
                    className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm border-2 border-white"
                  >
                    {friend.avatar}
                  </div>
                ))}
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-xs border-2 border-white">
                  +{friends.length - 3}
                </div>
              </div>
            </div>
          )}
          
          <div className="text-center py-4">
            <button className="text-blue-600 hover:text-blue-700 text-sm">
              Browse More Recipe Suggestions →
            </button>
          </div>
        </div>
      )}

      {/* Share Pantry Tab */}
      {activeTab === 'share' && (
        <div className="space-y-4">
          <p className="text-sm text-gray-600 mb-4">
            Share ingredients with friends and reduce waste together
          </p>
          
          <div className="space-y-2">
            {sharedPantry.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🥗</span>
                  <div>
                    <p className="font-medium text-gray-800">{item.name}</p>
                    <p className="text-sm text-gray-600">Shared by {item.owner}</p>
                  </div>
                </div>
                {item.owner !== 'You' && (
                  <button
                    onClick={() => requestIngredient(item)}
                    className="text-sm bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 transition"
                  >
                    Request
                  </button>
                )}
              </div>
            ))}
          </div>
          
          <button className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 transition">
            + Share an Ingredient
          </button>
          
          <div className="p-3 bg-green-50 rounded-lg">
            <p className="text-sm text-green-800">
              <span className="font-medium">Community Impact:</span> Together we've saved 47 items from waste this month!
            </p>
          </div>
        </div>
      )}

      {/* Cook Together Tab */}
      {activeTab === 'cook-together' && (
        <div className="space-y-4">
          {!cookingSession.active ? (
            <>
              <p className="text-sm text-gray-600 mb-4">
                Cook the same recipe with friends in real-time
              </p>
              
              <div className="space-y-2">
                <h4 className="font-medium text-gray-700">Online Friends</h4>
                {friends.filter(f => f.status !== 'offline').map((friend) => (
                  <div key={friend.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{friend.avatar}</span>
                      <div>
                        <p className="font-medium text-gray-800">{friend.name}</p>
                        <p className="text-sm text-gray-600">
                          {friend.status === 'cooking' ? '👨‍🍳 Currently cooking' : '🟢 Available'}
                        </p>
                      </div>
                    </div>
                    <button className="text-sm text-blue-600 hover:text-blue-700">
                      Invite
                    </button>
                  </div>
                ))}
              </div>
              
              <button
                onClick={startCookingSession}
                disabled={!currentRecipe}
                className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition disabled:bg-gray-300"
              >
                Start Cooking Session
              </button>
            </>
          ) : (
            <div className="space-y-4">
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-medium text-purple-800 mb-2">
                  Live Cooking: {cookingSession.recipe?.name}
                </h4>
                <div className="flex -space-x-2 mb-3">
                  {cookingSession.participants.map((friend) => (
                    <div
                      key={friend.id}
                      className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-lg border-2 border-purple-300"
                    >
                      {friend.avatar}
                    </div>
                  ))}
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-green-600">✓</span>
                    <span className="text-sm">Sarah completed: Prep vegetables</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-yellow-400 animate-pulse"></div>
                    <span className="text-sm">Mike is working on: Boil pasta</span>
                  </div>
                </div>
              </div>
              
              <button className="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition">
                End Session
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}