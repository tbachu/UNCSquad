# Pantry Play Deployment Guide

## Running Locally

### Option 1: Next.js Only (Simplified)
If you want to run just the Next.js app without the Python server:

1. Install dependencies:
```bash
npm install
```

2. Set up environment:
```bash
cp .env.example .env
# Add your Gemini API key to .env
```

3. Run development server:
```bash
npm run dev
```

4. Open http://localhost:3000

### Option 2: Full Stack (Next.js + Python API)

1. Install Node.js dependencies:
```bash
npm install
```

2. Install Python dependencies:
```bash
cd src
pip install -r requirements.txt
cd ..
```

3. Set up environment:
```bash
cp .env.example .env
# Add your Gemini API key to .env
```

4. Run both servers:

Terminal 1 - Python API:
```bash
cd src
python api_server.py
```

Terminal 2 - Next.js:
```bash
npm run dev
```

5. Open http://localhost:3000

## Production Deployment

### Vercel (Recommended for Next.js)

1. Push to GitHub
2. Connect repository to Vercel
3. Add environment variables in Vercel dashboard:
   - `GEMINI_API_KEY`
4. Deploy

### Google Cloud Run (Full Stack)

1. Create Dockerfile:
```dockerfile
FROM node:18-alpine AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY src/requirements.txt ./
RUN pip install -r requirements.txt
COPY src/ ./src/
COPY --from=frontend /app/.next ./.next
COPY --from=frontend /app/public ./public
COPY --from=frontend /app/package*.json ./

RUN npm ci --production

EXPOSE 3000 5000
CMD ["sh", "-c", "python src/api_server.py & npm start"]
```

2. Build and deploy:
```bash
gcloud run deploy pantry-play \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables

Required:
- `GEMINI_API_KEY` - Your Google AI Studio API key

Optional:
- `WEATHER_API_KEY` - For weather-based recommendations
- `NEXT_PUBLIC_APP_URL` - Your deployment URL
- `AGENT_PORT` - Python API port (default: 5000)

## Testing

Run tests:
```bash
npm test
```

## Monitoring

- Check Next.js logs: `npm run dev`
- Check Python logs: Terminal running `api_server.py`
- Production: Use platform-specific logging (Vercel, GCP, etc.)