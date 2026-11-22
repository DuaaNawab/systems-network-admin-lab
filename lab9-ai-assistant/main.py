import logging
import os
import time

from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("assistant")

app = FastAPI()

PRIMARY = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACKS = ["gemini-3.5-flash", "gemini-3.7-flash"]
MODELS = [PRIMARY] + [m for m in FALLBACKS if m != PRIMARY]
BUDGET_SECONDS = 80

# har Gemini call par 30 second ka timeout (milliseconds mein)
client = genai.Client(http_options=types.HttpOptions(timeout=30000))

SYSTEM = (
    "You are a University AI Assistant. Answer student questions about "
    "courses, facilities and academic services briefly and politely. "
    "If you are not sure, say so and advise contacting the university office."
)


class Query(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "University AI Assistant"}


@app.post("/ask")
def ask(query: Query):
    deadline = time.time() + BUDGET_SECONDS
    last_error = None
    for model in MODELS:
        for attempt in (1, 2):
            if time.time() > deadline:
                break
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=query.question,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM),
                )
                return {
                    "question": query.question,
                    "model": model,
                    "answer": response.text or "",
                }
            except Exception as e:
                last_error = e
                log.warning("model=%s attempt=%d failed: %s", model, attempt, type(e).__name__)
                time.sleep(1)
    raise HTTPException(
        status_code=502,
        detail=f"Model error: {type(last_error).__name__ if last_error else 'Timeout'}",
    )
