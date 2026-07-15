"""
Service layer for talking to the LLM (Google Gemini).

Why is this in its own file instead of inside the routers?
- Routers (Step 7) should only deal with HTTP: read the request, call a
  service function, return a response. They shouldn't know *how* a summary
  gets produced, only *that* calling summarize_text() gives one back.
- If we ever switch from Gemini to another provider, or add caching/retries,
  we only touch this file. Routers, tests, and even a CLI script could all
  reuse the same functions.
- It's much easier to unit test: you can call summarize_text() directly
  with a fake API key/mocked client, no HTTP server needed.

Every public function here can raise LLMServiceError. Routers are expected
to catch it and turn it into a clean HTTP error (Step 7), so a Gemini outage
never turns into an unhandled 500 crash.
"""

import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)

# a small, fast, cheap model is enough for these 3 features
MODEL_NAME = "gemini-2.0-flash"

# how long we wait for Gemini before giving up (seconds)
REQUEST_TIMEOUT = 30


class LLMServiceError(Exception):
    """Raised whenever the LLM call fails for any reason (timeout, API error, bad response)."""


def _generate(prompt: str) -> str:
    """
    Shared low-level call: sends one prompt to Gemini, returns the plain text
    reply. All 3 features funnel through here so error handling only lives
    in one place.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            prompt,
            request_options={"timeout": REQUEST_TIMEOUT},
        )
    except Exception as exc:
        # covers network errors, timeouts, auth errors, rate limits from
        # Google's side, etc. We don't try to distinguish them here - the
        # router only needs to know "the LLM call failed".
        raise LLMServiceError(f"Gemini request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise LLMServiceError("Gemini returned an empty response")

    return text.strip()


def summarize_text(text: str) -> str:
    prompt = (
        "Summarize the following text in 2-4 concise sentences. "
        "Keep the same language as the original text.\n\n"
        f"Text:\n{text}"
    )
    return _generate(prompt)


def answer_question(context: str, question: str) -> str:
    prompt = (
        "Answer the question using only the information in the given context. "
        "If the context does not contain the answer, say so clearly instead of guessing.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )
    return _generate(prompt)


def analyze_sentiment(text: str) -> str:
    """Returns one of: "positive", "negative", "neutral"."""
    prompt = (
        "Classify the overall sentiment of the following text. "
        "Reply with exactly one word: positive, negative, or neutral.\n\n"
        f"Text:\n{text}"
    )
    raw = _generate(prompt).lower().strip().strip(".")

    for label in ("positive", "negative", "neutral"):
        if label in raw:
            return label

    # the model didn't follow instructions - treat it as a service error
    # rather than silently returning a made-up label
    raise LLMServiceError(f"Could not parse sentiment from LLM response: {raw!r}")
