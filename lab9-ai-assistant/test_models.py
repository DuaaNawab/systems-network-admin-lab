from google import genai

client = genai.Client()
for name in ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-2.5-flash"]:
    try:
        r = client.models.generate_content(model=name, contents="Say hello in five words.")
        print("OK  ", name, "->", r.text.strip()[:60])
    except Exception as e:
        print("FAIL", name, type(e).__name__, str(e)[:150])
