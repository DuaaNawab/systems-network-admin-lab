import os
import re
from pathlib import Path

import psycopg

KB_DIR = Path(__file__).parent / "kb"

CATEGORY_KEYWORDS = {
    "password_reset": ["password", "reset", "forgot", "forgotten", "change password"],
    "wifi": ["wifi", "wi-fi", "internet", "network", "connect", "wireless"],
    "software_install": ["install", "software", "download", "licence", "license", "application"],
    "account_access": ["account", "locked", "login", "log in", "sign in", "access", "lms", "portal"],
}
ALLOWED_STATUS = {"open", "escalated"}


def guess_category(question: str) -> str:
    """Simple rule-based classifier, used as a fallback when the model is not available."""
    q = question.lower()
    scores = {c: sum(k in q for k in kws) for c, kws in CATEGORY_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"


def search_kb(question: str, category: str | None = None):
    """Tool 1: read-only search over the approved support documents."""
    if category not in CATEGORY_KEYWORDS:
        category = guess_category(question)
    if category == "unknown":
        return None
    path = KB_DIR / f"{category}.md"
    if not path.is_file():
        return None
    return {"source": path.name, "category": category, "text": path.read_text()}


def _dsn() -> str:
    return (
        f"host={os.getenv('DB_HOST', 'db')} dbname={os.environ['POSTGRES_DB']} "
        f"user={os.getenv('APP_DB_USER', 'helpdesk_app')} "
        f"password={os.environ['APP_DB_PASSWORD']} connect_timeout=5"
    )


def create_ticket(student_id: str, question: str, ai_response: str, status: str):
    """Tool 2: validated insert into PostgreSQL (the only write the agent can do)."""
    if not re.fullmatch(r"[A-Za-z0-9/_-]{3,20}", student_id or ""):
        raise ValueError("invalid student_id")
    if not 5 <= len(question or "") <= 1000:
        raise ValueError("invalid question length")
    if status not in ALLOWED_STATUS:
        raise ValueError("invalid status")
    with psycopg.connect(_dsn()) as conn:
        row = conn.execute(
            "INSERT INTO support_requests (student_id, question, ai_response, status) "
            "VALUES (%s, %s, %s, %s) RETURNING request_id",
            (student_id, question, ai_response[:4000], status),
        ).fetchone()
    return row[0]


def db_ok() -> bool:
    try:
        with psycopg.connect(_dsn()) as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False
