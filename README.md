# AI-Powered Unified Inbox Management Web App

A Final Year Project by Yi Zheng Tang at Atlantic Technological University (ATU).

This web app consolidates Gmail and Outlook into a single unified inbox. AI agents automatically summarize emails, categorize them, extract calendar events, score priority, detect spam, and generate reply drafts. A RAG (Retrieval-Augmented Generation) pipeline embeds your inbox into a local vector database so the AI can retrieve relevant context before responding.

Project Poster: https://github.com/yizhengtang/Intellimail/blob/master/documents/FYP%20Poster.pdf

Project Presentation: https://github.com/yizhengtang/Intellimail/blob/master/documents/Intellimail.pdf

---

## Features

- Unified inbox — view Gmail and Outlook side by side in one interface
- Email operations — read, send, reply, reply-all, draft, search, trash, label/folder management, attachments
- AI summarization — one-paragraph summary of any email using RAG context
- AI categorization — classifies emails (e.g. Work, Finance, Personal)
- AI priority scoring — rates urgency on a 1–10 scale with a reason
- AI event extraction — pulls out dates, times, and locations from emails
- Spam detection — flags likely spam before you open it
- AI reply generation — drafts a context-aware reply based on your inbox history
- Vector search — ChromaDB stores email embeddings locally; no cloud vector DB required

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | React 19 + TypeScript + Vite |
| Gmail | Google Gmail API via OAuth2 |
| Outlook | Microsoft Graph API via MSAL |
| AI agents | OpenAI gpt-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | ChromaDB (local, persisted to disk) |

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd FYP
```

### 2. Create the backend environment file

Copy the example file and fill in your credentials:

```bash
cp backend/.env.example backend/.env
```

Then open `backend/.env` and replace each placeholder with a real value.

### 3. Get your credentials

| Credential | Where to get it |
|---|---|
| Google OAuth2 (Client ID, Secret, Project ID) | https://console.cloud.google.com/apis/credentials |
| Microsoft OAuth2 (Client ID, Secret) | https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps |
| OpenAI API Key | https://platform.openai.com/api-keys |

For Google: create an OAuth 2.0 Client ID of type **Desktop app**, then download the credentials JSON and copy the values into `.env`.

For Microsoft: register a new app in Azure, add a **Mobile and desktop application** redirect URI of `http://localhost:8090/`, and create a client secret under **Certificates & secrets**.

For OpenAI: create a new secret key from the API keys page.

### 4. Install backend dependencies

```bash
cd backend
pip install -r ../requirements.txt
```

### 5. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running the App

Use the `run.sh` script from the project root.

| Command | What it does |
|---|---|
| `bash run.sh run` | Start the backend with hot-reload (development) |
| `bash run.sh start` | Start the backend without hot-reload (production) |
| `bash run.sh frontend` | Start the frontend dev server |

You need two terminals — one for the backend, one for the frontend.

**Terminal 1 — backend:**

```bash
bash run.sh run
```

Backend will be available at [http://localhost:8000](http://localhost:8000).

**Terminal 2 — frontend:**

```bash
bash run.sh frontend
```

Frontend will be available at [http://localhost:5173](http://localhost:5173).

### First-time OAuth login

- Open the app in your browser and click **Connect Gmail**. A browser window will open for Google sign-in. After authorizing, it redirects to `localhost:8080` automatically.
- Click **Connect Outlook**. A browser window will open for Microsoft sign-in. After authorizing, it redirects to `localhost:8090` automatically.

Tokens are saved locally in `backend/Gmail/token_files/` and `backend/Outlook/refresh_token.txt`. You will not need to log in again unless the tokens expire.

---

## Environment Variables Reference

All variables go in `backend/.env`. See `backend/.env.example` for the full template.

| Variable | Description |
|---|---|
| `GOOGLE_CLIENT_ID` | Google OAuth2 client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth2 client secret |
| `GOOGLE_PROJECT_ID` | Google Cloud project ID |
| `GOOGLE_AUTH_URI` | Google authorization endpoint (keep default) |
| `GOOGLE_TOKEN_URI` | Google token endpoint (keep default) |
| `GOOGLE_AUTH_PROVIDER_CERT_URL` | Google cert URL (keep default) |
| `GOOGLE_REDIRECT_URI` | OAuth callback — must be `http://localhost:8080/` |
| `MICROSOFT_CLIENT_ID` | Azure app client ID |
| `MICROSOFT_CLIENT_SECRET` | Azure app client secret |
| `MICROSOFT_REDIRECT_URI` | OAuth callback — must be `http://localhost:8090/` |
| `OPENAI_API_KEY` | OpenAI secret key for embeddings and agents |

---

## Project Structure

```
FYP/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   └── routers/         # gmail.py, outlook.py, ai.py
│   ├── ai/
│   │   ├── agents.py        # All 6 AI agents
│   │   ├── embeddings.py    # OpenAI embedding function
│   │   ├── vector_store.py  # ChromaDB wrapper
│   │   ├── ingestion.py     # Email ingestion pipeline
│   │   └── retrieval.py     # RAG context retrieval
│   ├── Gmail/               # Gmail OAuth + API functions
│   ├── Outlook/             # Outlook OAuth + API functions
│   └── .env.example         # Credential template
├── frontend/
│   └── src/
│       ├── pages/           # InboxPage, EmailPage, ComposePage
│       ├── components/      # EmailList, EmailDetail, ComposeForm
│       ├── services/        # gmailService.ts, outlookService.ts
│       ├── hooks/           # useEmails, useEmailDetail
│       └── context/         # ProviderContext (gmail | outlook | unified)
├── run.sh                   # Start backend or frontend
└── requirements.txt         # Python dependencies
```
