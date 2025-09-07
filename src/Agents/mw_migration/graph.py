# graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode # Import ToolNode
from langchain_core.messages import AIMessage

# Import nodes and state with relative imports
from .nodes import SharedState, main_agent_node
# Import tools (needed for ToolNode) with relative imports
from .tools import available_tools_decorated # Use the decorated tools list

# --- Graph Definition ---
graph_builder = StateGraph(SharedState)

# Add the main agent node
graph_builder.add_node("main_agent", main_agent_node)

# Add the ToolNode: This node executes tools when called
# It needs the list of tool functions/objects that the LLM is aware of
tool_executor_node = ToolNode(available_tools_decorated)
graph_builder.add_node("tool_executor", tool_executor_node)

# --- Edge Logic ---

# Start node goes to the main agent
graph_builder.add_edge(START, "main_agent")

# Conditional edge after the main agent
def should_continue(state: SharedState) -> str:
    """Determines whether to continue invoking tools or end the conversation."""
    last_message = state["messages"][-1]
    # If the LLM made tool calls, route to the tool executor
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        print("--- Decision: Route to Tool Executor ---")
        return "tool_executor"
    # Otherwise, the LLM provided a final answer, so end
    else:
        print("--- Decision: End ---")
        return END

graph_builder.add_conditional_edges(
    "main_agent", # Source node
    should_continue, # Function to decide the next node
    {
        "tool_executor": "tool_executor", # If 'should_continue' returns "tool_executor"
        END: END                      # If 'should_continue' returns END
    }
)

# Edge from the tool executor back to the main agent
# After tools are executed, the results (as ToolMessages) are added to the state,
# and we loop back to the main agent to let the LLM process the tool results.
graph_builder.add_edge("tool_executor", "main_agent")


# Expose the StateGraph as `builder` so the runtime can call
# `builder.compile(checkpointer=...)` to enable DB-backed memory.
builder = graph_builder

# Compile graph (fallback if runtime does not provide a checkpointer)
compiled_graph = graph_builder.compile()

