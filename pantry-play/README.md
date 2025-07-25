# Pantry Play - Your Daily Culinary Adventure

Pantry Play is an AI-powered culinary adventure companion that transforms ordinary ingredients and daily routines into creative, fun, and zero-waste meal experiences. Powered by Google's Gemini AI, it provides a smarter, more delightful way to cook, shop, and share food.

## 🌟 Key Features

### 1. AI-Powered Pantry Inspiration
- Upload photos or manually enter pantry items
- Get instant creative recipe suggestions using only available ingredients
- Smart substitutions with scientific explanations

### 2. Zero-Waste Meal Flow
- Proactive meal planning to use ingredients before expiration
- "Leftover Remix" mode for creative transformations
- Visual timeline of food usage and waste reduction stats

### 3. Mood & Weather-Based Recommendations
- Personalized meal suggestions based on mood and local weather
- Curated playlists and ambiance suggestions

### 4. Culinary Challenges & Gamification
- Daily/weekly meal challenges
- Earn badges and unlock new cuisines
- Challenge friends and family

### 5. Collaborative Cooking
- Share pantries and meal plans
- Vote on meal ideas
- Co-create shopping lists

### 6. Intelligent Shopping Assistant
- Auto-generated grocery lists
- Budget-friendly alternatives
- Seasonal recommendations

### 7. Personalized Nutrition & Insights
- Track nutritional intake
- Adapt recommendations to dietary goals
- Progress tracking

### 8. Story Mode Cooking
- Each meal becomes an adventure
- Fun facts and mini-games
- Make cooking memorable

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- A Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/pantry-play.git
cd pantry-play

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Add your Gemini API key to .env file

# Run the app
npm run dev

# Open http://localhost:3000
```

### First Time Setup
1. When you open the app, you'll be prompted to enter your Gemini API key
2. Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Enter the key and click "Start Your Culinary Adventure"
4. You're ready to go!

## 🏗️ Architecture

The app follows an agentic AI architecture with three core modules:

### Core Agent Workflow
1. **Receive user input** - Natural language processing of user requests
2. **Retrieve relevant memory** - Access user preferences, history, and patterns
3. **Plan sub-tasks** - Break down complex requests using ReAct pattern
4. **Call tools/APIs** - Execute tasks using Gemini API
5. **Generate final response** - Compile results into actionable insights

### Core Modules

#### `src/planner.py` & `lib/agent/planner.ts`
- Breaks down user goals into sub-tasks
- Implements ReAct (Reasoning and Acting) pattern
- Prioritizes tasks based on context

#### `src/executor.py` & `lib/agent/executor.ts`
- Executes tasks using Gemini API
- Handles image analysis, recipe generation, and recommendations
- Manages API calls and response parsing

#### `src/memory.py` & `lib/agent/memory.ts`
- Stores user preferences and interaction history
- Tracks achievements and statistics
- Analyzes patterns for personalization

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **AI**: Google Gemini API
- **State Management**: React hooks
- **Agent Architecture**: Custom TypeScript/Python implementation

## 📱 Usage

1. **Initial Setup**: Enter your Gemini API key when prompted
2. **Add Pantry Items**: 
   - Upload a photo of your pantry/fridge
   - Or manually add items
3. **Get Recommendations**: Ask the AI assistant for:
   - Recipe suggestions
   - Shopping lists
   - Meal planning
   - Leftover transformations
4. **Track Progress**: View your stats and achievements

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for the Google Hackathon
- Powered by Google Gemini AI
- Inspired by the need to reduce food waste and make cooking fun