import hmac
import logging
import os
import time
from collections import defaultdict, deque

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from agent import run_agent
from tools import db_ok

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("api")

app = FastAPI(title="University IT Helpdesk Agent")
API_KEY = os.getenv("HELPDESK_API_KEY", "")
RATE_LIMIT, RATE_WINDOW = 10, 60  # 10 requests per 60 seconds per client
_hits = defaultdict(deque)


class HelpRequest(BaseModel):
    student_id: str = Field(min_length=3, max_length=20, pattern=r"^[A-Za-z0-9/_-]+$")
    question: str = Field(min_length=5, max_length=1000)


def check_rate(client_id: str):
    now = time.time()
    q = _hits[client_id]
    while q and now - q[0] > RATE_WINDOW:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests, try again later")
    q.append(now)


@app.get("/health")
def health():
    return {"status": "ok", "database": "ok" if db_ok() else "unreachable"}


@app.post("/ask")
def ask(body: HelpRequest, request: Request, x_api_key: str = Header(default="")):
    if not API_KEY or not hmac.compare_digest(x_api_key.encode(), API_KEY.encode()):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    client_id = request.headers.get("x-real-ip") or (request.client.host if request.client else "?")
    check_rate(client_id)
    try:
        result = run_agent(body.student_id, body.question)
    except Exception as e:
        log.error("request failed: %s", type(e).__name__)
        raise HTTPException(status_code=502, detail=f"Agent error: {type(e).__name__}")
    log.info("ticket=%s category=%s status=%s", result["ticket_id"], result["category"], result["status"])
    return result
