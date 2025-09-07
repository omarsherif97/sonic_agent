# src/Backend/routes/agent.py
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
import json
import asyncio

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tracers import LangChainTracer

# Import compiled apps that were built with the checkpointer
from src.Agents.runtime import get_sonic_app, get_wso2_app, get_mw_migration_app

# Import your Pydantic schemas (unchanged shapes expected)
from ..schema.input_schema import InputSchema, OutputSchema

agent_router = APIRouter(prefix="/agent")

# -----------------------------------------------------------------------------
# Optional helper: accept uploaded files and return concatenated text (unchanged)
# -----------------------------------------------------------------------------
@agent_router.post("/upload_files")
def file_to_text(files: List[UploadFile] = File(...)):
    # Minimal text concatenation. Extend with MIME checks if needed.
    texts = []
    last_filename = None
    for f in files:
        last_filename = f.filename
        texts.append(f.file.read().decode("utf-8", errors="ignore"))
    return {"filename": last_filename, "content": "\n".join(texts)}

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def _rehydrate_messages(raw: List[Dict[str, Any]]):
    msgs = []
    for m in raw or []:
        role = (m.get("type") or m.get("role") or "").lower()
        content = m.get("content", "")
        if role in {"human", "user"}:
            msgs.append(HumanMessage(content=content))
        elif role in {"assistant", "ai"}:
            msgs.append(AIMessage(content=content))
        elif role == "system":
            msgs.append(SystemMessage(content=content))
        elif role == "tool":
            msgs.append(ToolMessage(content=content, tool_call_id=m.get("tool_call_id")))
        else:
            msgs.append(HumanMessage(content=content))
    return msgs


def _tracer_for(agent_name: str):
    project = {
        "smart_wso2_assistant": "Smart WSO2 Assistant",
        "sonic": "Sonic Agent",
        "mw_migration": "MW Migration",
    }.get(agent_name, "Default Project")
    return LangChainTracer(project_name=project)


async def _select_app(name: str):
    if name == "smart_wso2_assistant":
        return await get_wso2_app()
    if name == "sonic":
        return await get_sonic_app()
    if name == "mw_migration":
        return await get_mw_migration_app()
    raise ValueError(f"Unsupported agent {name}")

@agent_router.post("/stream")
async def stream_agent_response(agent_input: InputSchema):
    app = await _select_app(agent_input.agent_name)
    thread_id = agent_input.thread_id or "default_thread"

    incoming = agent_input.agent_input or {}
    incoming_msgs = _rehydrate_messages(incoming.get("messages", []))

    async def generate_stream():
        try:
            tracer = _tracer_for(agent_input.agent_name)
            config = {
                "callbacks": [tracer],
                "tags": [f"agent:{agent_input.agent_name}"],
                "metadata": {"agent": agent_input.agent_name, "thread_id": thread_id},
                "configurable": {"thread_id": thread_id, "checkpoint_ns": agent_input.agent_name},
            }
            state_in = {"messages": incoming_msgs}

            result = await app.ainvoke(state_in, config)
            output = result["messages"][-1].content if result.get("messages") else ""

            # Stream character by character for smooth typing effect
            for char in output:
                yield f"data: {json.dumps({'content': char, 'done': False})}\n\n"
                await asyncio.sleep(0.01)  # Slightly faster for better UX
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@agent_router.post("/invoke")
async def invoke_agent(agent_input: InputSchema) -> OutputSchema:
    app = await _select_app(agent_input.agent_name)
    thread_id = agent_input.thread_id or "default_thread"
    incoming = agent_input.agent_input or {}
    incoming_msgs = _rehydrate_messages(incoming.get("messages", []))

    tracer = _tracer_for(agent_input.agent_name)
    config = {
        "callbacks": [tracer],
        "tags": [f"agent:{agent_input.agent_name}"],
        "metadata": {"agent": agent_input.agent_name, "thread_id": thread_id},
        "configurable": {"thread_id": thread_id, "checkpoint_ns": agent_input.agent_name},
    }
    state_in = {"messages": incoming_msgs}

    result = await app.ainvoke(state_in, config)
    output = result["messages"][-1].content if result.get("messages") else ""
    return {"AI_Response": output}