'use client';

import { useState, useEffect } from 'react';
import { PantryPlayAgent } from '@/lib/agent';

interface MoodWeatherRecommenderProps {
  agent: PantryPlayAgent | null;
  onRecipeSelect: (recipe: any) => void;
}

const moods = [
  { emoji: '😊', name: 'Happy', color: 'bg-yellow-100 text-yellow-700' },
  { emoji: '😌', name: 'Relaxed', color: 'bg-blue-100 text-blue-700' },
  { emoji: '😴', name: 'Tired', color: 'bg-purple-100 text-purple-700' },
  { emoji: '🤗', name: 'Cozy', color: 'bg-orange-100 text-orange-700' },
  { emoji: '😤', name: 'Stressed', color: 'bg-red-100 text-red-700' },
  { emoji: '🎉', name: 'Celebratory', color: 'bg-pink-100 text-pink-700' },
];

interface WeatherData {
  temp: number;
  condition: string;
  icon: string;
}

export default function MoodWeatherRecommender({ agent, onRecipeSelect }: MoodWeatherRecommenderProps) {
  const [selectedMood, setSelectedMood] = useState<string>('');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [playlist, setPlaylist] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Simulate weather data (in real app, would use weather API)
    setWeather({
      temp: Math.floor(Math.random() * 30) + 10,
      condition: ['Sunny', 'Cloudy', 'Rainy', 'Snowy'][Math.floor(Math.random() * 4)],
      icon: ['☀️', '☁️', '🌧️', '❄️'][Math.floor(Math.random() * 4)],
    });
  }, []);

  const getRecommendations = async () => {
    if (!agent || !selectedMood) return;

    setIsLoading(true);
    try {
      const response = await agent.processUserInput(
        `I'm feeling ${selectedMood} and the weather is ${weather?.condition} (${weather?.temp}°C). What should I cook?`,
        {
          mood: selectedMood,
          weather: weather,
          timeOfDay: new Date().getHours() < 12 ? 'morning' : 
                     new Date().getHours() < 17 ? 'afternoon' : 'evening',
        }
      );

      if (response.results?.mood_weather_recommend) {
        // Parse recommendations
        const text = response.results.mood_weather_recommend;
        
        // Extract meal suggestions (simplified parsing)
        const mealMatches = text.match(/\d\.\s*([^:]+):\s*([^\.]+)/g) || [];
        const meals = mealMatches.slice(0, 3).map((match: string) => {
          const [, name, description] = match.match(/\d\.\s*([^:]+):\s*([^\.]+)/) || [];
          return { name: name?.trim(), description: description?.trim() };
        });
        setRecommendations(meals);

        // Extract playlist suggestions
        const playlistMatch = text.match(/playlist[^:]*:([^\.]+)/i);
        if (playlistMatch) {
          const songs = playlistMatch[1].split(',').map(s => s.trim());
          setPlaylist(songs);
        }
      }
    } catch (error) {
      console.error('Error getting recommendations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getAmbianceColor = () => {
    if (!weather) return 'from-gray-50 to-gray-100';
    
    switch (weather.condition) {
      case 'Sunny': return 'from-yellow-50 to-orange-50';
      case 'Cloudy': return 'from-gray-50 to-blue-50';
      case 'Rainy': return 'from-blue-50 to-indigo-50';
      case 'Snowy': return 'from-blue-50 to-purple-50';
      default: return 'from-gray-50 to-gray-100';
    }
  };

  return (
    <div className={`bg-gradient-to-br ${getAmbianceColor()} rounded-xl shadow-lg p-6`}>
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">🌈</span> Mood & Weather Meals
      </h2>

      {weather && (
        <div className="bg-white/70 backdrop-blur rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Current Weather</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-2xl">{weather.icon}</span>
                <span className="font-medium">{weather.condition}</span>
                <span className="text-gray-600">{weather.temp}°C</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Time</p>
              <p className="font-medium">{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
            </div>
          </div>
        </div>
      )}

      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">How are you feeling?</p>
        <div className="grid grid-cols-3 gap-2">
          {moods.map((mood) => (
            <button
              key={mood.name}
              onClick={() => setSelectedMood(mood.name)}
              className={`p-3 rounded-lg transition ${
                selectedMood === mood.name
                  ? mood.color + ' ring-2 ring-offset-2 ring-gray-400'
                  : 'bg-white hover:bg-gray-50'
              }`}
            >
              <div className="text-2xl mb-1">{mood.emoji}</div>
              <p className="text-sm font-medium">{mood.name}</p>
            </button>
          ))}
        </div>
      </div>

      {selectedMood && (
        <button
          onClick={getRecommendations}
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition disabled:from-gray-400 disabled:to-gray-500"
        >
          {isLoading ? 'Finding Perfect Meals...' : 'Get Mood-Based Recommendations'}
        </button>
      )}

      {recommendations.length > 0 && (
        <div className="mt-6 space-y-4">
          <h3 className="font-medium text-gray-700">Perfect Meals for Your Mood</h3>
          {recommendations.map((rec, index) => (
            <div
              key={index}
              className="bg-white rounded-lg p-4 cursor-pointer hover:shadow-md transition"
              onClick={() => onRecipeSelect(rec)}
            >
              <h4 className="font-medium text-gray-800">{rec.name}</h4>
              <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
            </div>
          ))}
        </div>
      )}

      {playlist.length > 0 && (
        <div className="mt-4 bg-white/70 backdrop-blur rounded-lg p-4">
          <h3 className="font-medium text-gray-700 mb-2 flex items-center">
            <span className="mr-2">🎵</span> Cooking Playlist
          </h3>
          <div className="space-y-1">
            {playlist.map((song, index) => (
              <p key={index} className="text-sm text-gray-600">• {song}</p>
            ))}
          </div>
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="mt-4 p-3 bg-purple-50 rounded-lg">
          <p className="text-sm text-purple-800">
            <span className="font-medium">Ambiance Tip:</span> Set warm lighting and play some relaxing music to enhance your {selectedMood.toLowerCase()} dining experience!
          </p>
        </div>
      )}
    </div>
  );
}