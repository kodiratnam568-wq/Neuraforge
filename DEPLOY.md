# NeuraForge — Deploy to Cloud in 5 Minutes

## STEP 1 — Push to GitHub (your PC terminal)

Open a terminal (Command Prompt or PowerShell) and run:

```bash
cd "C:\Users\K RUSHITHA\.bob\playground\NeuraForge"
git init
git add .
git commit -m "NeuraForge initial commit"
```

Then go to https://github.com/new
- Create a repo named: `neuraforge`
- Copy the remote URL (e.g. https://github.com/YOURUSERNAME/neuraforge.git)

```bash
git remote add origin https://github.com/YOURUSERNAME/neuraforge.git
git branch -M main
git push -u origin main
```

---

## STEP 2 — Deploy Backend to Render (FREE)

1. Go to https://render.com → Sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your `neuraforge` GitHub repo
4. Settings:
   - **Name:** `neuraforge-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `GROQ_API_KEY` = your groq key
6. Click **"Create Web Service"**
7. Wait ~2 minutes → You get a URL like:
   `https://neuraforge-backend.onrender.com`

---

## STEP 3 — Deploy Frontend to Vercel (FREE)

1. Go to https://vercel.com → Sign up with GitHub
2. Click **"New Project"** → Import your `neuraforge` repo
3. Settings:
   - **Root Directory:** `frontend`
   - **Framework Preset:** `Vite`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Under **Environment Variables**, add:
   - `VITE_API_URL` = `https://neuraforge-backend.onrender.com`
5. Click **"Deploy"**
6. Wait ~1 minute → You get a URL like:
   `https://neuraforge.vercel.app`

---

## DONE ✅

Your live app: `https://neuraforge.vercel.app`

Anyone in the world can open it, paste a GitHub URL, and get an AI onboarding report.
