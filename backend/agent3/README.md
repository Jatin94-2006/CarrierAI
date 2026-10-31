# Agent 3 — Course Suggestion Agent

> Part of the AI-Powered Career Guidance & Job Preparation System

This module recommends **free** learning resources (courses, tutorials, videos) based on skill gaps identified by Agent 2 (Gap Analysis Agent). It integrates with OpenRouter (LLM), Tavily (web search), and YouTube Data API v3.

---

## Quick Start

### 1. Install Dependencies

```bash
cd agent3
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and fill in your keys:

```bash
copy .env.example .env
```

Edit `.env`:

```
OPENROUTER_API_KEY=your_openrouter_key
TAVILY_API_KEY=your_tavily_key
YOUTUBE_API_KEY=your_youtube_key
```

> **No keys yet?** The app works in **Demo Mode** without any keys. You'll get curated sample recommendations instantly.

### 3. Start the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Open the Demo Dashboard

Open `demo/index.html` in your browser. It connects to `http://localhost:8000` automatically.

Or visit the interactive API docs at: `http://localhost:8000/docs`

---

## API Reference

### Health Check
```
GET /api/v1/health
```

### Get Course Recommendations
```
POST /api/v1/courses/recommend
Content-Type: application/json

{
  "technical_skills": ["Python", "SQL", "Power BI"],
  "soft_skills": ["Communication", "Leadership"],
  "skill_levels": {
    "Python": "Intermediate",
    "SQL": "Beginner",
    "Power BI": "Missing"
  },
  "target_job_role": "Data Analyst"
}
```

### Get Sample Recommendations (testing)
```
GET /api/v1/courses/sample
```

### List Supported Skills
```
GET /api/v1/courses/skills
```

---

## Integration

### Receiving Input from Agent 2 (Gap Analysis)

Agent 2 should POST to:
```
POST http://localhost:8000/api/v1/courses/recommend
```

With the `SkillGapInput` payload format above.

### Sending Output to Agent 5 (Learning Planner)

Agent 5 can call the same endpoint or `/api/v1/courses/sample` and consume the `CourseResponse` JSON. Each `CourseRecommendation` object contains:

```json
{
  "title": "Python Tutorial for Beginners",
  "platform": "freeCodeCamp",
  "skill": "Python",
  "skill_category": "Technical",
  "difficulty": "Beginner",
  "description": "...",
  "url": "https://...",
  "resource_type": "Video",
  "is_free": true,
  "thumbnail": "https://...",
  "duration": "4.5 hours",
  "source": "youtube"
}
```

---

## Getting API Keys

| Service | Get Key | Free Tier |
|---------|---------|-----------|
| OpenRouter | https://openrouter.ai/keys | Yes (limited) |
| Tavily | https://app.tavily.com/ | Yes (1000 searches/month) |
| YouTube Data API | https://console.cloud.google.com/ | Yes (10,000 units/day) |

### YouTube API Setup
1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable **YouTube Data API v3**
4. Go to Credentials → Create Credentials → API Key
5. Copy the key to `.env`

---

## Architecture

```
agent3/
├── main.py                    ← FastAPI app, all API endpoints
├── agents/
│   └── course_agent.py        ← Main orchestration pipeline
├── services/
│   ├── openrouter_service.py  ← LLM search strategy
│   ├── tavily_service.py      ← Web search for courses
│   └── youtube_service.py     ← YouTube video/playlist search
├── models/
│   └── schemas.py             ← Pydantic data models
├── utils/
│   ├── free_filter.py         ← Free resource verification
│   └── sample_data.py         ← Demo data (no API keys needed)
├── demo/
│   ├── index.html             ← Standalone test dashboard
│   ├── style.css
│   └── app.js
├── requirements.txt
├── .env.example
└── README.md
```

---

## Pipeline (Live Mode)

```
SkillGapInput
    ↓
OpenRouter LLM
  → Generates search strategy (keywords, platforms, difficulty)
    ↓
Tavily + YouTube (concurrent)
  → Searches for free learning resources
    ↓
Free Filter
  → Removes paid/unknown resources
    ↓
Deduplication
  → Removes duplicate URLs
    ↓
CourseResponse
  → technical_recommendations + soft_recommendations
```

---

## Demo Mode

When any API key is missing, the agent runs in **Demo Mode**:
- Returns curated sample data (verified free resources)
- Filters sample data to match the requested skills
- Shows a banner in the UI indicating demo mode
- All API endpoints still work — just with sample data

---

## For React/Next.js Integration

Enable CORS is already configured in `main.py` (`allow_origins=["*"]`).

In your React app:

```js
const response = await fetch('http://localhost:8000/api/v1/courses/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(skillGapData),
});
const recommendations = await response.json();
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Cannot reach backend` | Make sure `uvicorn` is running on port 8000 |
| `422 Unprocessable Entity` | Check that at least one skill is provided |
| `OpenRouter failed` | Check `OPENROUTER_API_KEY` in `.env` — agent falls back automatically |
| `No results found` | Agent falls back to sample data if live searches return nothing |
| CORS error in browser | Restart the server after editing `.env` |
