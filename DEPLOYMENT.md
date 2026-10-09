# Deploying MyGenie

MyGenie uses a React/Vite frontend and a FastAPI backend. Deploy the frontend to
Vercel and the API to a Python host such as Render. The database must be a
persistent PostgreSQL service; do not use SQLite on an ephemeral web-service
filesystem for a hosted application.

## 1. Keep credentials private

- Do not commit `.env` files, API keys, database URLs, or real user data.
- `backend/.env.example` and `frontend/.env.example` are templates only.
- Keep the GitHub repository private unless you intentionally want the source
  code to be public.

## 2. Deploy the API

1. Create a persistent PostgreSQL database with your chosen database provider.
2. Create a Render Web Service from the GitHub repository, using
   `render.yaml` as the blueprint, or enter its settings manually:
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command:
     `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/health`
3. Set these service environment variables:
   - `DATABASE_URL`: the PostgreSQL connection URL from your database provider
   - `SECRET_KEY`: a randomly generated secret of at least 32 characters
   - `ENVIRONMENT`: `production`
   - `FRONTEND_ORIGINS`: the exact Vercel origin, e.g.
     `https://your-project.vercel.app` (no trailing slash)
   - `AI_PROVIDER`: `mock` until a valid Gemini/OpenAI credential is configured.
     For live AI, set the provider and its API key in the host's secret settings.
4. Deploy and check `https://<your-api-host>/health`.

The Render web service blueprint deliberately does not create a database. Attach
a persistent PostgreSQL provider and set `DATABASE_URL`; this avoids silently
deploying with temporary SQLite storage or unexpectedly provisioning a paid
database. Free hosting tiers may sleep, have resource limits, or change their
retention terms; confirm the provider's current terms before using one for real
customer data.

## 3. Deploy the frontend

1. Import the repository into Vercel.
2. Set the project Root Directory to `frontend`.
3. Use `npm run build` as the build command and `dist` as the output directory.
   `frontend/vercel.json` enables client-side route fallback for React Router.
4. Set the Vercel environment variable `VITE_API_URL` to the deployed API origin,
   e.g. `https://your-api.onrender.com` (no trailing slash), then redeploy.
5. Add the final Vercel origin to the API's `FRONTEND_ORIGINS` and redeploy the
   API if needed.

## 4. Local verification

From `frontend`, run `npm run lint` and `npm run build`. From `backend`, run
`alembic upgrade head` against a development database and start the API with
`uvicorn main:app --reload`.
