# Outline Knowledge Base Slack Bot

A Slack bot that answers questions using your GetOutline knowledge base and Claude AI.

## How it works

1. A user @mentions the bot in any Slack channel
2. The bot searches your Outline knowledge base for relevant docs
3. Claude answers the question using **only** the found documents
4. The answer is posted in a thread, with source links

---

## Setup

### 1. Create a Slack App

1. Go to https://api.slack.com/apps → **Create New App** → **From scratch**
2. Under **OAuth & Permissions**, add these **Bot Token Scopes**:
   - `app_mentions:read`
   - `chat:write`
   - `channels:history`
   - `groups:history`
3. Under **Event Subscriptions** → Enable Events → **Subscribe to Bot Events**:
   - `app_mention`
4. Under **Socket Mode** → Enable Socket Mode (this avoids needing a public URL)
5. Generate an **App-Level Token** with `connections:write` scope → this is your `SLACK_APP_TOKEN`
6. Install the app to your workspace → copy the **Bot User OAuth Token** → this is your `SLACK_BOT_TOKEN`

### 2. Get your Outline API token

1. In Outline, go to **Settings → API Tokens** → Create a token
2. Copy your Outline workspace URL (e.g. `https://yourteam.getoutline.com`)

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in all values:

```bash
cp .env.example .env
```

### 4. Run locally

```bash
pip install -r requirements.txt
python app.py
```

---

## Deploy to Railway

1. Push this repo to GitHub
2. Go to https://railway.app → **New Project** → **Deploy from GitHub**
3. Add all environment variables from `.env` in the Railway dashboard
4. Railway auto-detects the `Procfile` and runs `python app.py`

That's it — no need to configure a public URL since the bot uses Socket Mode.

---

## Usage

In any Slack channel where the bot is invited:

```
@YourBot How do I reset my password?
@YourBot What is our onboarding process?
@YourBot Where can I find the engineering runbooks?
```

The bot will reply in a thread with an answer sourced from your Outline docs.
