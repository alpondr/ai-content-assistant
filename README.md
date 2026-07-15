# AI Content Assistant API

A small FastAPI backend I built to learn how to combine JWT auth, PostgreSQL,
and an LLM (Google Gemini) in one project. It exposes 3 AI-powered endpoints
(summarize, question answering, sentiment analysis) behind auth and a daily
per-user rate limit.

## Stack

- FastAPI
- PostgreSQL + SQLAlchemy + Alembic
- JWT auth (python-jose + passlib)
- Google Gemini API (google-generativeai)
- slowapi for rate limiting

## Project structure

```
app/
  core/       settings, JWT/password helpers, rate limiter
  database/   SQLAlchemy engine and session
  models/     SQLAlchemy models (User, RequestLog)
  schemas/    Pydantic request/response models
  routers/    FastAPI endpoints (auth, ai, history)
  services/   LLM service layer (all Gemini calls go through here)
```

The service layer is kept separate from the routers on purpose: routers only
handle HTTP (parse the request, call a service, return a response), while
`services/llm_service.py` is the only place that knows how to talk to
Gemini. Swapping providers or adding retries/caching later only touches
that one file.

## Setup

1. Create a virtualenv and install dependencies:

   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your own values (DB credentials,
   JWT secret, Gemini API key). Never commit the real `.env`.

3. Start Postgres:

   ```
   docker compose up -d
   ```

4. Run the migrations:

   ```
   alembic upgrade head
   ```

5. Start the server:

   ```
   uvicorn app.main:app --reload
   ```

Interactive docs: http://localhost:8000/docs

## Endpoints

**Auth**
- `POST /auth/register` - create a user (email + password)
- `POST /auth/login` - get a JWT (form fields: `username`=email, `password`)

**AI** (need `Authorization: Bearer <token>`)
- `POST /ai/summarize` - summarize a text
- `POST /ai/qa` - answer a question about a given context
- `POST /ai/sentiment` - classify text sentiment (positive/negative/neutral)

**History**
- `GET /history?page=1&page_size=10` - list your own past requests, newest first

## Rate limiting

Each user can make `DAILY_REQUEST_LIMIT` (default 20) AI requests per day,
shared across summarize/qa/sentiment combined. Going over it returns 429
with a clear error message. The counter is per-user (based on the JWT, not
IP) and kept in memory, so it resets if the server restarts.

## Error handling

If the Gemini API call fails or times out, the endpoint returns 503 instead
of crashing, and the failed attempt is still saved to the request history
(with an empty output).
