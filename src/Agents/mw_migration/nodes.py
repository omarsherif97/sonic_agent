import os
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, ToolMessage
from .tools import available_tools_decorated, load_file_sync # Import both the tools and load_file_sync function


# --- Configuration & Setup ---





# Use centralized LLM configuration
from src.Agents.LLM import get_llm
LLM = get_llm()
# Bind tools to the LLM
LLM_with_tools = LLM.bind_tools(available_tools_decorated)

# Load the main conversational prompt using the load_file_sync function from tools.py
GENAI_PROMPT = load_file_sync("", "GENAI.txt") # GENAI.txt is in the root of the prompt directory

# --- State Definition ---
class SharedState(MessagesState):
    """State shared between all nodes. Inherits 'messages' from MessagesState."""
    pass


# --- Node Functions ---
async def main_agent_node(state: SharedState) -> SharedState:
    """
    Main conversational agent node. Invokes the LLM with tools bound.
    The LLM will decide whether to respond directly or request a tool call.
    """
    print("--- Calling Main Agent Node ---")
    # Construct messages for the LLM
    # Include the system prompt and the current message history
    
    system_message = SystemMessage(content=GENAI_PROMPT)
    messages = [system_message] + state["messages"]

    # Invoke the LLM bound with tools
    response = await LLM_with_tools.ainvoke(messages)

    # Append the response (which might contain tool calls) to the state
    # LangGraph's ToolNode will handle executing the calls later
    state["messages"].append(response)

    print(f"--- Agent Response: {response.content}")
    # 2) If tool calls exist, run them, add ToolMessage(s)
    if getattr(response, "tool_calls", None):
        tools_dict = {t.name: t for t in available_tools_decorated}
        for tool_call in response.tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]
            call_id = tool_call["id"]

            try:
                if name not in tools_dict:
                    result = f"Unknown tool: {name}"
                else:
                    result = await tools_dict[name].ainvoke(args)
                state["messages"].append(
                    ToolMessage(content=str(result), tool_call_id=call_id)
                )
            except Exception as e:
                state["messages"].append(
                    ToolMessage(content=f"Error executing tool {name}: {e}", tool_call_id=call_id)
                )

        # 3) Final answer that uses the tool outputs
        final_system_hint = SystemMessage(content=(
            "You just received tool result(s). Now craft a concise answer for the user. "
            "Append the 'Tool result'."
        ))
        follow_up_messages = [final_system_hint] + state["messages"]
        follow_up_response = await LLM.ainvoke(follow_up_messages)
        state["messages"].append(follow_up_response)


    return state