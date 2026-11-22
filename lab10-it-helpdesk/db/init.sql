CREATE TABLE IF NOT EXISTS support_requests (
    request_id  SERIAL PRIMARY KEY,
    student_id  VARCHAR(20) NOT NULL,
    question    TEXT NOT NULL,
    ai_response TEXT,
    status      VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
