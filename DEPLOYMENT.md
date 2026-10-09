# Deploying MyGenie on Vercel

MyGenie uses a React/Vite frontend, a FastAPI backend, and PostgreSQL. Deploy the
backend and frontend as two Vercel projects connected to the same GitHub
repository. Use a persistent PostgreSQL provider such as the Neon project
created for MyGenie; do not use SQLite on a serverless filesystem.

## Backend project

Create a Vercel project from `iftiurhossenriyad/MyGenie` with:

- Root Directory: `backend`
- Framework: FastAPI (or the detected Python framework)
- Build Command: leave the default; `backend/pyproject.toml` runs database
  migrations after Python dependencies are installed.

Add these environment variables in Vercel Project Settings (Production and any
other environments you intend to use):

- `DATABASE_URL`: copy the PostgreSQL connection string directly from Neon into
  this secret field. Do not commit it or send it in chat.
- `SECRET_KEY`: generate a random value of at least 32 characters and save it as
  a Vercel secret.
- `ENVIRONMENT`: `production`
- `FRONTEND_ORIGINS`: the exact frontend origin after the frontend is deployed,
  e.g. `https://mygenie-frontend.vercel.app` (no trailing slash).
- `AI_PROVIDER`: `mock` until a valid Gemini/OpenAI API key is configured.

Deploy the backend, then test `https://<backend-project>.vercel.app/health`.
The build runs Alembic migrations against `DATABASE_URL`; it will fail rather
than silently switching to temporary SQLite if the database is unavailable.

## Frontend project

Create another Vercel project from the same GitHub repository with:

- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment variable `VITE_API_URL`: `https://<backend-project>.vercel.app`
  (no trailing slash).

Deploy the frontend, then set `FRONTEND_ORIGINS` on the backend to the exact
frontend origin and redeploy the backend. `frontend/vercel.json` handles
React Router page refreshes.

## Notes

- The Neon PostgreSQL project is in Singapore to reduce latency for Bangladesh.
- Vercel and Neon free tiers have usage, resource, and service limits that can
  change. Review current terms and monitor usage before using this for real
  customers.
- The public GitHub repository excludes `.env` files, database files, and
  virtual environments. Never add credentials or private customer data to it.
- For local development, use `frontend/.env.example` and `backend/.env.example`
  as templates; keep the actual `.env` files untracked.
