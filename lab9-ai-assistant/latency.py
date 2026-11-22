import time
from google import genai
from google.genai import types

client = genai.Client(http_options=types.HttpOptions(timeout=30000))
for name in ["gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.8-flash"]:
    t = time.time()
    try:
        r = client.models.generate_content(model=name, contents="Say hello in five words.")
        print("OK  ", name, round(time.time() - t, 1), "s")
    except Exception as e:
        print("FAIL", name, type(e).__name__, round(time.time() - t, 1), "s")
