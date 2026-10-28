"""ChakshuRakshak AI eye-health chatbot.

A small FastAPI service in front of Google Gemini (google-genai SDK). It serves the
chat page at "/" and answers POST /api/chat. Deployed on Google Cloud Run; see
README.md for the commands.

Configuration (environment variables):
  GEMINI_API_KEY      Gemini API key (Google AI Studio). Alternatively run on Vertex AI
                      with GOOGLE_GENAI_USE_VERTEXAI=true, GOOGLE_CLOUD_PROJECT and
                      GOOGLE_CLOUD_LOCATION; the SDK reads these itself.
  GEMINI_MODEL        Model id. Default "gemini-3.6-flash" (older models are closed to
                      new API keys; the newest flash models are often overloaded).
  GEMINI_FALLBACK_MODEL  Second model, tried when the first stays busy.
                      Default "gemini-3.5-flash"; set to "" to turn off.
  ALLOWED_ORIGINS     Comma-separated CORS origins. Default "*" (any origin).
  RATE_LIMIT_PER_MIN  Requests per minute per client IP. Default 20.
"""

import asyncio
import base64
import binascii
import logging
import os
import re
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("eye-chatbot")

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash").strip()
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "20"))

MAX_MESSAGE_CHARS = 4000
MAX_IMAGE_BYTES = 8 * 1024 * 1024          # decoded size
MAX_HISTORY_TURNS = 12                     # earlier messages sent back for context
RETRY_DELAYS = (1.5, 4.0)                  # waits before retrying a busy model
TRANSIENT_CODES = {429, 500, 503, 504}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}

SYSTEM_INSTRUCTION = (
    "You are an expert ophthalmology AI assistant. Analyze patient symptoms and retinal "
    "images (Fundus/OCT/FFA). You specialize in identifying retinal diseases, diabetic "
    "retinopathy grading, and retinal vessel abnormalities. Provide preliminary advice in "
    "simple language (Hindi or English, matching the user). Always conclude with a strong "
    "disclaimer to consult a certified ophthalmologist."
)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="ChakshuRakshak AI eye-health chatbot", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# One client per process. genai.Client() picks up GEMINI_API_KEY / GOOGLE_API_KEY, or the
# Vertex AI variables, from the environment. Created lazily so the app still starts (and
# /healthz answers) when the key is missing, and the error is reported per request.
_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(http_options=types.HttpOptions(timeout=60_000))
    return _client


# ── Request / response models ─────────────────────────────────────────────────

class Turn(BaseModel):
    role: Literal["user", "model"]
    text: str = Field(max_length=MAX_MESSAGE_CHARS)


class ChatRequest(BaseModel):
    message: str = Field(default="", max_length=MAX_MESSAGE_CHARS)
    # Optional image as a data URL ("data:image/png;base64,...") or bare base64.
    image: Optional[str] = None
    # Optional earlier turns, so follow-up questions keep their context.
    history: List[Turn] = Field(default_factory=list)


async def generate(contents: List[types.Content]):
    """Call Gemini, retrying briefly when the model is busy (429/5xx), then the fallback model."""
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.4,
        max_output_tokens=2048,
    )
    models = [MODEL] + ([FALLBACK_MODEL] if FALLBACK_MODEL and FALLBACK_MODEL != MODEL else [])
    last_error: Exception = RuntimeError("no model tried")
    for model in models:
        for attempt in range(len(RETRY_DELAYS) + 1):
            try:
                resp = await get_client().aio.models.generate_content(model=model, contents=contents, config=config)
                return resp, model
            except errors.APIError as e:
                last_error = e
                if getattr(e, "code", None) not in TRANSIENT_CODES:
                    raise
                if attempt < len(RETRY_DELAYS):
                    log.warning("Gemini %s busy (%s), retrying", model, e.code)
                    await asyncio.sleep(RETRY_DELAYS[attempt])
    raise last_error


class ChatResponse(BaseModel):
    reply: str
    model: str


# ── Simple per-IP rate limit (per instance; enough to stop casual abuse) ─────

_hits: dict = defaultdict(deque)


def check_rate_limit(ip: str) -> None:
    now = time.monotonic()
    q = _hits[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= RATE_LIMIT_PER_MIN:
        raise HTTPException(status_code=429, detail="Too many messages. Please wait a minute and try again.")
    q.append(now)


def client_ip(request: Request) -> str:
    # Cloud Run sets X-Forwarded-For; the first entry is the caller.
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown")


# ── Image handling ────────────────────────────────────────────────────────────

_DATA_URL = re.compile(r"^data:(?P<mime>[\w/+.-]+);base64,(?P<data>.+)$", re.S)


def decode_image(value: str) -> types.Part:
    """Turn a data URL (or bare base64) into a Gemini image part, with checks."""
    mime = "image/jpeg"
    m = _DATA_URL.match(value.strip())
    data = value
    if m:
        mime, data = m.group("mime").lower(), m.group("data")
    if mime not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Please attach a JPG, PNG or WebP image.")
    try:
        raw = base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="The image could not be read.")
    if not raw:
        raise HTTPException(status_code=400, detail="The image is empty.")
    if len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="The image is too large (max 8 MB).")
    return types.Part.from_bytes(data=raw, mime_type=mime)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def chat_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "model": MODEL}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    check_rate_limit(client_ip(request))

    text = req.message.strip()
    if not text and not req.image:
        raise HTTPException(status_code=400, detail="Type a message or attach an image.")

    parts: List[types.Part] = []
    if req.image:
        parts.append(decode_image(req.image))
    parts.append(types.Part.from_text(text=text or "Please look at this eye image and explain what you see."))

    contents: List[types.Content] = [
        types.Content(role=t.role, parts=[types.Part.from_text(text=t.text)])
        for t in req.history[-MAX_HISTORY_TURNS:]
        if t.text.strip()
    ]
    contents.append(types.Content(role="user", parts=parts))

    try:
        resp, used_model = await generate(contents)
    except Exception:  # SDK / network / quota errors: log details, return a plain message
        log.exception("Gemini request failed")
        raise HTTPException(status_code=502, detail="The assistant is unavailable right now. Please try again shortly.")

    reply = (resp.text or "").strip()
    if not reply:
        # Empty text usually means the response was blocked by a safety filter.
        reply = ("I could not answer that. Please rephrase your question, or consult a certified "
                 "ophthalmologist for advice about your eyes.")
    return ChatResponse(reply=reply, model=used_model)
