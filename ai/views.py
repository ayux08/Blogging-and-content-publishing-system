import json
import os
import time
import requests
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).resolve().parent.parent / '.env')


def get_session_context(request):
    return {
        'user_id': request.session.get('user_id'),
        'user_name': request.session.get('user_name', 'Guest'),
        'user_role': request.session.get('user_role', 'reader'),
    }


# AI Dashboard
def index(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "ai", "page": "index"})
    return render(request, "ai/index.html", ctx)


# AI Summarize page
def summarize(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "ai", "page": "summarize"})
    return render(request, "ai/summarize.html", ctx)


# AI Translate page
def translate(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "ai", "page": "translate"})
    return render(request, "ai/translate.html", ctx)


# ═══════════════════════════════════════════════════════════════
#  Helper: call Groq API (free, fast LLM inference)
#  Docs: https://console.groq.com/docs/api-reference
# ═══════════════════════════════════════════════════════════════

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

MAX_RETRIES = 3
RETRY_BASE_WAIT = 5


def _call_llm(api_key, model, prompt):
    """Send a prompt to the Groq API and return the text response.
       Uses OpenAI-compatible chat completions endpoint.
       Automatically retries on 429 (rate-limit) errors."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.4,
        "max_tokens": 2048,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )

            # Handle rate-limit: wait and retry
            if resp.status_code == 429:
                wait = RETRY_BASE_WAIT * attempt
                print(f"[AI] Rate limited (429). Retry {attempt}/{MAX_RETRIES} in {wait}s...")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()

            # Extract text from OpenAI-style response
            choices = data.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                text = message.get("content", "").strip()
                if text:
                    return text

            print(f"[AI] Groq returned no choices: {data}")
            return None

        except requests.exceptions.Timeout:
            print("[AI] Groq API timed out")
            return None
        except requests.exceptions.RequestException as e:
            error_body = ""
            if hasattr(e, 'response') and e.response is not None:
                error_body = e.response.text
            print(f"[AI] Groq API error: {e}\n[AI] Response body: {error_body}")
            return None

    # All retries exhausted
    print("[AI] All retries exhausted due to rate-limiting.")
    return None


# ═══════════════════════════════════════════════════════════════
#  AJAX API: Summarize  (uses SUMMARIZER_API_KEY from .env)
# ═══════════════════════════════════════════════════════════════

@csrf_exempt
def api_summarize(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = {}

    content = data.get("content", "").strip()
    length = data.get("length", "short")
    lang = data.get("lang", "English")

    if not content:
        return JsonResponse({"error": "No content provided"}, status=400)

    # Read API key from .env
    api_key = os.getenv("SUMMARIZER_API_KEY", "")
    model = os.getenv("SUMMARIZER_MODEL", "llama-3.1-8b-instant")

    if not api_key or api_key == "your-groq-api-key-here":
        return JsonResponse(
            {"error": "Summarizer API key is not configured. Please add your Groq API key in the .env file."},
            status=503,
        )

    # Build the prompt based on requested length
    if length == "short":
        length_instruction = "Provide a short summary in 2-3 sentences."
    elif length == "medium":
        length_instruction = "Provide a medium-length summary in 4-6 sentences."
    else:
        length_instruction = "Provide a detailed summary using bullet points covering all key ideas."

    lang_instruction = ""
    if lang and lang != "English":
        lang_instruction = f" Write the summary in {lang} language."

    prompt = (
        f"Summarize the following blog post content. {length_instruction}{lang_instruction}\n\n"
        f"--- BLOG CONTENT ---\n{content}\n--- END ---"
    )

    result = _call_llm(api_key, model, prompt)

    if result is None:
        return JsonResponse(
            {"error": "Failed to generate summary. Please check your API key and try again."},
            status=502,
        )

    return JsonResponse({"summary": result, "lang": lang})


# ═══════════════════════════════════════════════════════════════
#  AJAX API: Translate  (uses TRANSLATOR_API_KEY from .env)
# ═══════════════════════════════════════════════════════════════

LANG_LABELS = {
    'Hindi': 'हिंदी अनुवाद',
    'Tamil': 'தமிழ் மொழிபெயர்ப்பு',
    'Telugu': 'తెలుగు అనువాదం',
    'Marathi': 'मराठी अनुवाद',
    'English': 'English Translation',
    'Japanese': '日本語翻訳',
    'Spanish': 'Traducción al Español',
    'French': 'Traduction Française',
    'Korean': '한국어 번역',
}


@csrf_exempt
def api_translate(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = {}

    content = data.get("content", "").strip()
    target_lang = data.get("lang", "Hindi")

    if not content:
        return JsonResponse({"error": "No content provided"}, status=400)

    # Read API key from .env
    api_key = os.getenv("TRANSLATOR_API_KEY", "")
    model = os.getenv("TRANSLATOR_MODEL", "llama-3.1-8b-instant")

    if not api_key or api_key == "your-groq-api-key-here":
        return JsonResponse(
            {"error": "Translator API key is not configured. Please add your Groq API key in the .env file."},
            status=503,
        )

    label = LANG_LABELS.get(target_lang, "Translation")

    prompt = (
        f"Translate the following text to {target_lang}. "
        f"Return ONLY the translated text, no explanations or notes.\n\n"
        f"--- TEXT ---\n{content}\n--- END ---"
    )

    result = _call_llm(api_key, model, prompt)

    if result is None:
        return JsonResponse(
            {"error": "Failed to translate. Please check your API key and try again."},
            status=502,
        )

    return JsonResponse({
        "translation": result,
        "label": label,
        "lang": target_lang,
    })
