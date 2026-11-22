import os, time
from google import genai
from google.genai import types

print("key present:", bool(os.getenv("GEMINI_API_KEY")), "| model:", os.getenv("GEMINI_MODEL"), flush=True)
c = genai.Client(http_options=types.HttpOptions(timeout=20000))
for m in ["gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.8-flash"]:
    t = time.time()
    try:
        r = c.models.generate_content(model=m, contents="Say hello in five words.")
        print("OK  ", m, round(time.time() - t, 1), "s", r.text.strip()[:40], flush=True)
    except Exception as e:
        print("FAIL", m, type(e).__name__, getattr(e, "code", None), str(e)[:160].replace("\n", " "), flush=True)
