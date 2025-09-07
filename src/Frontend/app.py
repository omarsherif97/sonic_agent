# src/Frontend/app.py
# Context-ready Chainlit frontend. Keeps thread_id stable per chat and
# sends only the new user turn. SSE client handles 'done' and 'error'.

import os
import json
import uuid
from typing import Any, Dict, List, Tuple

import aiohttp
import chainlit as cl
from chainlit.input_widget import Select

# ---- Environment ------------------------------------------------------------

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

# ---- Agent registry ---------------------------------------------------------
AGENTS = {
    "sonic": {
        "name": "Sonic Agent",
        "description": "A fast and efficient AI assistant powered by advanced language models",
        "icon": "🚀",
        "color": "#FF6B6B",
        "backend_name": "sonic",
    },
    "wso2": {
        "name": "Smart WSO2 Assistant",
        "description": "Specialized assistant for WSO2 platform and enterprise integration",
        "icon": "⚡",
        "color": "#4ECDC4",
        "backend_name": "smart_wso2_assistant",
    },
    "mw_migration": {
        "name": "MW Migration",
        "description": "A tool for migrating WSO2 applications to modern platforms",
        "icon": "🔄",
        "color": "#96CEB4",
        "backend_name": "mw_migration",
    },
}

selected_agent = "mw_migration"

# =============================================================================
# File helpers
# =============================================================================
TEXT_EXTS = {".txt", ".md", ".markdown", ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".sql", ".csv", ".tsv", ".log"}
TEXT_MIME_PREFIXES = ("text/", "application/json", "application/xml", "application/x-yaml", "application/yaml")
MAX_CHARS_PER_FILE = 60_000
MAX_TOTAL_CHARS = 180_000


def _looks_textual(name: str, mime: str | None) -> bool:
    import os as _os
    ext = _os.path.splitext(name or "")[1].lower()
    if ext in TEXT_EXTS:
        return True
    if mime:
        return mime.startswith(TEXT_MIME_PREFIXES)
    return False


async def _read_uploaded_file(uploaded) -> Tuple[str, str | None]:
    name = getattr(uploaded, "name", "uploaded_file")
    mime = getattr(uploaded, "mime", None) or getattr(uploaded, "type", None) or getattr(uploaded, "content_type", None)

    data = None
    try:
        if hasattr(uploaded, "read") and callable(uploaded.read):
            data = await uploaded.read()
        elif hasattr(uploaded, "content") and uploaded.content:
            data = uploaded.content
        elif getattr(uploaded, "path", None):
            with open(uploaded.path, "rb") as f:
                data = f.read()
        elif hasattr(uploaded, "url") and uploaded.url:
            async with aiohttp.ClientSession() as session:
                async with session.get(uploaded.url) as response:
                    data = await response.read()
        else:
            return "", f"- {name}: unable to access content (no read/content/path/url)"
    except Exception as e:  # defensive
        return "", f"- {name}: read error: {e}"

    if not _looks_textual(name, mime):
        return "", f"- {name}: non-text file (skipped)."

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = data.decode("latin-1")
        except Exception:
            return "", f"- {name}: not decodable as text (skipped)."

    if len(text) > MAX_CHARS_PER_FILE:
        text = text[:MAX_CHARS_PER_FILE] + f"\n...[truncated {len(text)-MAX_CHARS_PER_FILE} chars]"

    wrapped = f"\n\n--- file:{name} ---\n{text}"
    return wrapped, None


async def collect_files_text(message: cl.Message) -> Tuple[str, List[str]]:
    notes: List[str] = []
    chunks: List[str] = []

    uploaded_files = []
    if hasattr(message, "elements") and message.elements:
        uploaded_files = [el for el in message.elements if hasattr(el, "type") and el.type in ["file", "image", "audio", "video"]]
    if not uploaded_files and hasattr(message, "attachments") and message.attachments:
        uploaded_files = message.attachments

    current_total = 0
    for f in uploaded_files:
        chunk, note = await _read_uploaded_file(f)
        if note:
            notes.append(note)
        if chunk:
            if current_total + len(chunk) > MAX_TOTAL_CHARS:
                remaining = MAX_TOTAL_CHARS - current_total
                chunks.append(chunk[: max(0, remaining)] + "\n...[additional files truncated]")
                notes.append("- some files were truncated due to size limits.")
                break
            chunks.append(chunk)
            current_total += len(chunk)

    return "".join(chunks), notes


async def check_backend_health() -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                return resp.status == 200
    except Exception:
        return False


# =============================================================================
# Agent session helpers
# =============================================================================
async def set_agent(agent_id: str):
    global selected_agent
    selected_agent = agent_id
    agent_info = AGENTS[agent_id]
    cl.user_session.set("agent_id", agent_id)
    cl.user_session.set("agent_info", agent_info)


# =============================================================================
# UI lifecycle
# =============================================================================
@cl.on_chat_start
async def start():
    if not await check_backend_health():
        await cl.Message(
            content=(
                "⚠️ **Warning: Backend Service Unavailable**\n\n"
                "The backend is not responding. Some features may not work."
            ),
            author="System",
        ).send()

    await set_agent(selected_agent)
    cl.user_session.set("thread_id", f"thread_{uuid.uuid4().hex}")

    await cl.Message(
        content=(
            "🎉 **Welcome to SEQ_SONIC Chatbot!**\n\nUse *Chat Settings* to switch between agents."
        ),
        author="System",
    ).send()

    await cl.ChatSettings([
        Select(
            id="agent",
            label="Active Agent",
            values=list(AGENTS.keys()),
            initial_index=list(AGENTS.keys()).index(selected_agent),
            description="Switch between available agents at runtime.",
        ),
    ]).send()


@cl.on_settings_update
async def on_settings_update(settings: Dict[str, Any]):
    agent_id = settings.get("agent") or selected_agent
    if agent_id in AGENTS and agent_id != cl.user_session.get("agent_id"):
        await set_agent(agent_id)
        await cl.Message(content=f"✅ **Agent switched to {AGENTS[agent_id]['name']}**", author="System").send()


# =============================================================================
# Message handler (streams from backend SSE)
# =============================================================================
@cl.on_message
async def main(message: cl.Message):
    agent_id = cl.user_session.get("agent_id", selected_agent)
    agent_info = cl.user_session.get("agent_info", AGENTS[selected_agent])

    thinking_msg = cl.Message(
        content=f"{agent_info['icon']} **{agent_info['name']}** is thinking...",
        author="System",
    )
    await thinking_msg.send()

    try:
        if not await check_backend_health():
            await thinking_msg.remove()
            await cl.Message(
                content=(
                    "❌ **Backend Unavailable**\n\nPlease try again later or contact support."
                ),
                author="System",
            ).send()
            return

        files_text, file_notes = await collect_files_text(message)
        user_text = (message.content or "").strip()
        if files_text:
            user_text = (user_text + "\n\n[Attached files]" + files_text).strip()
        if file_notes:
            await cl.Message(content="ℹ️ File notes:\n" + "\n".join(file_notes), author="System").send()

        # Only the new human turn. Checkpointer restores prior state by thread_id.
        messages = [{"type": "human", "content": user_text}]
        input_data = {"messages": messages}

        response_msg = cl.Message(content="", author=AGENTS[agent_id]["name"])
        await response_msg.send()

        async for chunk in stream_response(agent_id, input_data):
            await response_msg.stream_token(chunk)
        await response_msg.update()
        await thinking_msg.remove()

    except Exception as e:
        await thinking_msg.remove()
        await cl.Message(content=f"❌ **Error**: {str(e)}", author="System").send()


async def stream_response(agent_id: str, input_data: Dict[str, Any]):
    try:
        agent_info = AGENTS[agent_id]
        payload = {
            "agent_name": agent_info["backend_name"],
            "thread_id": cl.user_session.get("thread_id", "default_thread"),
            "agent_input": input_data,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/agent/stream",
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as resp:
                if resp.status != 200:
                    yield f"Error: Backend returned status {resp.status}"
                    return

                async for raw in resp.content:
                    line = raw.decode("utf-8", errors="ignore").strip()
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    if obj.get("error"):
                        yield f"Error: {obj['error']}"
                        break
                    if obj.get("done") is True:
                        break
                    if "content" in obj and obj["content"]:
                        yield obj["content"]
    except aiohttp.ClientError as e:
        yield f"Error: Network error connecting to backend - {str(e)}"
    except Exception as e:
        yield f"Error: {str(e)}"


@cl.on_chat_end
async def end():
    await cl.Message(
        content="👋 **Chat session ended. Thank you for using SEQ_SONIC!**",
        author="System",
    ).send()