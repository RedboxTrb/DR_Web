# Eye-health chatbot (ChakshuRakshakAI)

A FastAPI service in front of Google Gemini (`google-genai` SDK). It serves the chat page
at `/` and answers `POST /api/chat`. The website opens it in a floating panel (see
`CHATBOT_URL` in the site's `index.html`).

```
chatbot/
  main.py            FastAPI app: /, /healthz, POST /api/chat
  static/index.html  chat page: text, voice (hi-IN / en-US), image upload
  requirements.txt
  Dockerfile         for Google Cloud Run
```

This folder is listed in the site's `.vercelignore`, so Vercel does not publish it.

## API

`POST /api/chat`

```json
{ "message": "मेरी आँखें धुंधली हैं",
  "image": "data:image/jpeg;base64,...",          // optional, JPG/PNG/WebP, max 8 MB
  "history": [{"role": "user", "text": "..."},     // optional, earlier turns
              {"role": "model", "text": "..."}] }
```

Response: `{ "reply": "...", "model": "gemini-3.6-flash" }`. Errors return
`{ "detail": "..." }` with 400 / 413 / 415 / 422 / 429 (rate limit) / 502 (Gemini failed).

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `GEMINI_API_KEY` | — | Gemini API key from Google AI Studio |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Any current Gemini model id. Older models (1.5, 2.5) are closed to new API keys; the newest flash models (3.7, 3.8) are often overloaded (503). |
| `GEMINI_FALLBACK_MODEL` | `gemini-3.5-flash` | Second model, tried when the first stays busy; set empty to turn off |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS origins for direct API calls |
| `RATE_LIMIT_PER_MIN` | `20` | Messages per minute per client IP (per instance) |

Instead of an API key you can use Vertex AI with the service account: set
`GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`.

## Run locally

```bash
cd chatbot
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=your-key
uvicorn main:app --reload --port 8080
```

Open http://localhost:8080.

## Deploy to Cloud Run

From the `chatbot/` folder, with `gcloud` logged in and a project selected:

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
```

Store the key in Secret Manager (not in the image or the command line history of others):

```bash
printf '%s' "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
```

```bash
PROJECT_NUMBER=$(gcloud projects describe "$(gcloud config get-value project)" --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor
```

Build from the Dockerfile and deploy:

```bash
gcloud run deploy eye-chatbot --source . --region asia-south1 \
  --allow-unauthenticated \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --set-env-vars ALLOWED_ORIGINS=https://www.chakshurakshakai.com,https://chakshurakshakai.com \
  --memory 512Mi --max-instances 3
```

The command prints the service URL (`https://eye-chatbot-....run.app`). Check it:

```bash
curl https://YOUR-SERVICE-URL/healthz
```

## Show it on the website

In the site's `index.html`, set

```js
const CHATBOT_URL = 'https://YOUR-SERVICE-URL/';
```

and push. A "Ask Eye AI" button appears at the bottom right of every page; it opens the
chat in a panel (full screen on phones). The iframe is allowed to use the microphone, so
voice input works inside it.

## Notes

- Voice input uses the browser's Web Speech API (Chrome, Edge, Safari). Firefox does not
  support it; the mic button is disabled there.
- The rate limit is kept in memory per instance. For stronger protection put Cloud Armor
  or an API gateway in front, or lower `--max-instances`.
- Replies come from a general-purpose model. They are preliminary information, not a
  diagnosis, and the system instruction makes every answer end with advice to consult a
  certified ophthalmologist.
