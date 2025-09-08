# nodes.py
import asyncio
import logging
from typing import List
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, ToolMessage

from .tools import available_tools_decorated, load_file
from src.Agents.LLM import get_llm


# ================================================================================
# LOGGING CONFIGURATION
# ================================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Get a logger instance for this module


# ================================================================================
# LLM CONFIGURATION
# ================================================================================
# LLM that may CALL tools (first turn)
LLM_WITH_TOOLS = get_llm().bind_tools(available_tools_decorated)
# LLM that will NOT call tools (final humanization turn)
LLM_FINAL = get_llm()

# ================================================================================
# PROMPT CONFIGURATION
# ================================================================================

GENAI_PROMPT = load_file("", "GENAI.txt") 


# ================================================================================
# STATE DEFINITION
# ================================================================================
class SharedState(MessagesState):
    """State shared between all nodes. Inherits 'messages' from MessagesState."""
    pass


# ================================================================================
# HELPER FUNCTIONS
# ================================================================================
def _collect_tool_results_since_last_call(messages: List[BaseMessage], max_chars: int = 4000) -> str:
    """
    Gather ToolMessage contents emitted after the most recent AI tool call.
    """
    buf: List[str] = []
    saw_tool_request = False
    for m in reversed(messages):
        if isinstance(m, ToolMessage):
            buf.append(m.content if isinstance(m.content, str) else str(m.content))
        elif isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            saw_tool_request = True
            break
    if not saw_tool_request:
        return ""
    text = "\n\n".join(reversed(buf)).strip()
    return text


# ================================================================================
# GRAPH NODES
# ================================================================================
async def main_agent_node(state: MessagesState) -> MessagesState:
    """First turn: let model either answer or request tools."""

    messages = [SystemMessage(content=GENAI_PROMPT)] + state["messages"]
    try:
        ai_response = await LLM_WITH_TOOLS.ainvoke(messages)
    except asyncio.CancelledError:
        logger.info("main_agent_node: cancelled")
        return state
    state["messages"] = messages + [ai_response]
    return state

def route_after_main(state: MessagesState) -> str:
    """IF LAST AI ASKED FOR TOOLS -> 'tools', ELSE -> 'end'."""
    last = state["messages"][-1] if state["messages"] else None
    return "tools" if isinstance(last, AIMessage) and getattr(last, "tool_calls", None) else "end"

async def humanize_from_tools_node(state: MessagesState) -> MessagesState:
    """
    Final turn after tools: inject a short system hint with the tool outputs,
    then ask a tool-less LLM to write the human-facing answer.
    """
    tool_txt = _collect_tool_results_since_last_call(state["messages"])
    hint = "You just received tool result(s). Now craft a concise answer for the user. Append the 'Tool result'. with Reasoning about the tool results."
    if tool_txt:
        hint += "\n\nTool result:\n" + tool_txt

    messages = [SystemMessage(content=hint)] + state["messages"] 
    try:
        final_ai = await LLM_FINAL.ainvoke(messages)
    except asyncio.CancelledError:
        logger.info("humanize_from_tools_node: cancelled")
        return state

    state["messages"] = messages + [final_ai]
    return state
