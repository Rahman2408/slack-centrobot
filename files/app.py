import os
from dotenv import load_dotenv
load_dotenv()
import requests
import anthropic
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# --- Clients ---
slack_app = App(token=os.environ["SLACK_BOT_TOKEN"])
anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

OUTLINE_API_URL = os.environ["OUTLINE_API_URL"]   # e.g. https://yourteam.getoutline.com
OUTLINE_API_TOKEN = os.environ["OUTLINE_API_TOKEN"]


# --- Outline search ---
def search_outline(query: str, max_results: int = 5) -> list[dict]:
    """Search Outline and return a list of {title, text, url} dicts."""
    response = requests.post(
        f"{OUTLINE_API_URL}/api/documents.search",
        headers={
            "Authorization": f"Bearer {OUTLINE_API_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"query": query, "limit": max_results},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("data", []):
        doc = item.get("document", {})
        results.append({
            "title": doc.get("title", "Untitled"),
            "text": doc.get("text", ""),
            "url": f"{OUTLINE_API_URL}/doc/{doc.get('id', '')}",
        })
    return results


# --- Claude answer ---
def ask_claude(question: str, docs: list[dict]) -> str:
    """Ask Claude to answer the question using only the provided docs."""
    if not docs:
        return "I couldn't find any relevant documents in the knowledge base to answer your question. Try rephrasing or check if the topic is covered in Outline."

    # Build context block from docs
    context_parts = []
    for doc in docs:
        context_parts.append(f"### {doc['title']}\nSource: {doc['url']}\n\n{doc['text'][:3000]}")
    context = "\n\n---\n\n".join(context_parts)

    system_prompt = (
        "You are a helpful assistant for this team. "
        "Answer the user's question using ONLY the documentation provided below. "
        "Do not use any outside knowledge. "
        "If the answer is not covered in the docs, say clearly: "
        "'I couldn't find an answer to that in our knowledge base.' "
        "Always cite which document(s) you used by mentioning the title and linking to the source URL.\n\n"
        f"## Knowledge Base Documents\n\n{context}"
    )

    message = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )
    return message.content[0].text


# --- Slack event: app_mention ---
@slack_app.event("app_mention")
def handle_mention(event, say, client):
    channel = event["channel"]
    thread_ts = event.get("thread_ts", event["ts"])  # reply in thread
    user = event["user"]

    # Strip the bot mention from the message text
    bot_user_id = client.auth_test()["user_id"]
    question = event["text"].replace(f"<@{bot_user_id}>", "").strip()

    if not question:
        say(
            text="Hey! Ask me anything and I'll search our knowledge base for you.",
            channel=channel,
            thread_ts=thread_ts,
        )
        return

    # Post a "thinking" message immediately so the user knows we're on it
    say(
        text=f"<@{user}> Searching the knowledge base... 🔍",
        channel=channel,
        thread_ts=thread_ts,
    )

    try:
        docs = search_outline(question)
        answer = ask_claude(question, docs)
    except Exception as e:
        answer = f"Something went wrong while searching: `{e}`"

    say(
        text=answer,
        channel=channel,
        thread_ts=thread_ts,
    )


# --- Run ---
if __name__ == "__main__":
    handler = SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"])
    print("⚡ Bot is running!")
    handler.start()
