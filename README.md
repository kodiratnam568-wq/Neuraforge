# NeuraForge — AI-Powered Developer Onboarding Assistant

> Understand any codebase faster.

NeuraForge takes a public GitHub repository URL and generates a complete, beginner-friendly onboarding guide using AI — covering project overview, tech stack, important files, architecture, setup steps, and starter tasks.

---

## Quick Start

### 1. Backend

```bash
cd backend
cp .env.example .env
# Edit .env — add your GROQ_API_KEY (free at https://console.groq.com)
pip install -r requirements.txt
python main.py
```

Backend runs at `http://localhost:8000`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### 3. Use it

Open `http://localhost:5173`, paste any public GitHub URL, click **Analyze**.

---

## Tech Stack

| Layer     | Technology                |
|-----------|---------------------------|
| Frontend  | React + Vite              |
| Backend   | Python + FastAPI          |
| AI        | Groq (Llama 3 70B)        |
| Source    | GitHub REST API           |
| Dev IDE   | IBM Bob                   |

---

## Project Structure

```
NeuraForge/
├── frontend/          React + Vite UI
│   └── src/
│       ├── App.jsx    Main component + report renderer
│       └── index.css  Dark-theme styles
├── backend/
│   ├── main.py        FastAPI app + /analyze endpoint
│   ├── github_service.py  Repo scanning & file extraction
│   ├── ai_service.py  Groq LLM integration
│   └── requirements.txt
├── bob_sessions/      IBM Bob session screenshots (hackathon evidence)
└── README.md
```

---

## Environment Variables

| Variable       | Required | Description                                  |
|----------------|----------|----------------------------------------------|
| `GROQ_API_KEY` | Yes      | Groq API key (free tier available)            |
| `GITHUB_TOKEN` | No       | Increases GitHub rate limit to 5000 req/hour |

---

## Deployment

- **Frontend** → Vercel (`npm run build`, set `VITE_API_URL` env var to your backend URL)
- **Backend** → Render (free tier, set `GROQ_API_KEY` + `GITHUB_TOKEN` env vars)

---

## Built With IBM Bob

This project was developed using IBM Bob IDE as the primary development agent.

