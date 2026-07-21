# Syllabot Deployment Guide: Supabase, Render & Vercel

This guide explains how to deploy the Syllabot platform in production using free-tier services:
1. **Supabase** (PostgreSQL Database)
2. **Render** (FastAPI Backend Python Service)
3. **Vercel** (Next.js Frontend React Web App)

---

## 1. Database Setup (Supabase)

1. Go to [supabase.com](https://supabase.com) and sign up for a free account.
2. Click **New Project** and select your organization.
3. Configure your project name, select a database region close to your target audience, and set a **strong Database Password** (save this password somewhere secure).
4. Wait for the project provisioning to complete (usually 1-2 minutes).
5. In your Supabase dashboard:
   - Navigate to **Project Settings** (gear icon) -> **Database**.
   - Scroll down to the **Connection Pooler** section (do NOT use the direct connection string, as it resolves to an IPv6 address which is not supported by Render's build network, causing a `Network is unreachable` error).
   - Ensure the pooler **Mode** is set to **Session** (which uses port `5432`).
   - Copy the **URI connection string** from the Connection Pooler section. It looks like this:
     ```text
     postgresql://postgres.[project-ref]:[password]@[pooler-host]:5432/postgres
     ```
   - Swap the placeholder `[password]` with your real Database Password.

---

## 2. Backend Setup (Render)

1. Go to [render.com](https://render.com) and log in.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository containing the Syllabot code.
4. Configure the Web Service settings:
   - **Name**: `syllabot-backend`
   - **Language**: `Python`
   - **Branch**: `main`
   - **Root Directory**: `backend` (or leave empty and adjust build commands if deploying from the project root)
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head` (if Root Directory is `backend`) or `pip install -r backend/requirements.txt && cd backend && alembic upgrade head` (if Root Directory is empty)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT` (if Root Directory is `backend`) or `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` (if Root Directory is empty)
   - **Instance Type**: Select **Free**
5. Click **Advanced** and add the following **Environment Variables**:
   - `PROJECT_NAME`: `Syllabot`
   - `DATABASE_URL`: Paste the Supabase connection string you copied in Step 1.
   - `JWT_SECRET_KEY`: Generate a random hex string (run `openssl rand -hex 32` in a terminal) and paste it here.
   - `GEMINI_API_KEY`: Your Google AI Studio key.
   - `GROQ_API_KEY`: Your Groq API key.
   - `AI_PROVIDER`: `gemini`
   - `FRONTEND_URL`: Paste the URL of your Vercel deployment (you can update this later once Vercel is set up).
6. Click **Create Web Service**. Render will build and deploy your FastAPI backend. Copy your Render web service URL (e.g. `https://syllabot-backend.onrender.com`).

---

## 3. Frontend Setup (Vercel)

1. Go to [vercel.com](https://vercel.com) and log in.
2. Click **Add New** -> **Project**.
3. Import your GitHub repository containing the Syllabot code.
4. Configure the Vercel project settings:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Select `frontend`
5. Expand the **Environment Variables** section and add:
   - `NEXT_PUBLIC_API_URL`: Paste your Render backend web service URL (e.g. `https://syllabot-backend.onrender.com`).
6. Click **Deploy**. Vercel will automatically build and publish your Next.js application.
7. Copy your Vercel deployment URL (e.g. `https://syllabot-frontend.vercel.app`).
8. Go back to Render -> **syllabot-backend** -> **Environment** and update `FRONTEND_URL` to match this Vercel deployment URL so that CORS is locked securely to your frontend domain in production.
