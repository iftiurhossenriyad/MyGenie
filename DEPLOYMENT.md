# Deploying MyGenie on Vercel

MyGenie uses a React/Vite frontend, a FastAPI backend, and PostgreSQL. The
repository is configured as one Vercel project with two services sharing one
domain. A persistent Neon PostgreSQL project has been created in Singapore; do
not use SQLite on a serverless filesystem.

## Create the Vercel project

Import `iftiurhossenriyad/MyGenie` into Vercel and keep the project Root
Directory at the repository root. The root `vercel.json` routes `/api/*` and
`/health` to FastAPI and all other paths to the Vite frontend. Its services
configuration supports direct frontend and backend deployments from this
monorepo.

Before the first deployment, add these environment variables to the Vercel
project's Production environment:

- `DATABASE_URL`: copy the PostgreSQL connection string directly from Neon into
  this secret field. Do not commit it or send it in chat.
- `SECRET_KEY`: generate a random value of at least 32 characters and save it
  as a Vercel secret.
- `ENVIRONMENT`: `production`
- `FRONTEND_ORIGINS`: the Vercel project origin, e.g.
  `https://mygenie.vercel.app` (no trailing slash; adjust if Vercel assigns a
  different domain).
- `AI_PROVIDER`: set to `gemini` after adding `GEMINI_API_KEY`; use `mock` if
  you intentionally want deterministic development responses.
- `GEMINI_API_KEY`: create a key in [Google AI Studio](https://aistudio.google.com/app/apikey)
  and save it as a Vercel secret. Never commit it or send it in chat.
- `GEMINI_MODEL`: optional; defaults to `gemini-3.8-flash`.

The official asynchronous Google Gen AI SDK is included in the backend
dependencies. Gemini requests use the Interactions API with stateless
conversation history (`store=false`), so chat content is not retained by
Google for server-side conversation state. After setting `GEMINI_API_KEY` and
`AI_PROVIDER=gemini` in Vercel, redeploy the backend and verify a real chat
response. OpenAI remains optional and requires its separate SDK and API key. A
missing key or SDK never silently returns mock answers; the chat will report
that it cannot respond and the backend will log the provider configuration
error.

The backend's `pyproject.toml` runs Alembic migrations during the build. If the
database URL is missing or unavailable, the build should fail rather than
silently switching to temporary SQLite. After deployment, verify `/health`,
register a test account, and try the core screens.

The frontend and API use the same Vercel origin, so `VITE_API_URL` does not need
to be set. React Router deep links are handled by the frontend service rewrite.

## Notes

- Vercel Services are currently in beta. Vercel and Neon free tiers have
  usage/resource limits that can change; review the current terms and monitor
  usage before using the app with real customers.
- The public GitHub repository excludes `.env` files, database files, and
  virtual environments. Never add credentials or private customer data to it.
- For local development, use `frontend/.env.example` and `backend/.env.example`
  as templates; keep the actual `.env` files untracked.
