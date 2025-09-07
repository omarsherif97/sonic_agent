# Imports
from langgraph.graph import START, END, StateGraph
from .nodes import *
from langchain_core.messages import HumanMessage, AIMessage
from typing import Literal

# Initialize state graph and add nodes
graph = StateGraph(wso2_SharedState)
graph.add_node("smart_wso2_agent", smart_wso2_agent)
graph.add_node("history_recorder", history_recorder)

# Router function for smart_wso2_agent node
def smart_wso2_agent_router(state: wso2_SharedState) -> Literal["history_recorder", END]:
    """Route from smart_wso2_agent based on conversation length and completion"""
    
    # Check if we need to record history (memory management)
    if len(state["messages"]) > 30:
        return "history_recorder"
    
    # Otherwise, end the conversation
    return END

# Graph edges and routing configuration
graph.add_edge(START, "smart_wso2_agent")
graph.add_conditional_edges(
    "smart_wso2_agent",
    smart_wso2_agent_router,
    {
        "history_recorder": "history_recorder",
        END: END,
    },
)
graph.add_edge("history_recorder", END)

# Expose the StateGraph as `builder` so the runtime can call
# `builder.compile(checkpointer=...)` to enable DB-backed memory.
builder = graph

# Compile graph (fallback if runtime does not provide a checkpointer)
compiled_graph = graph.compile()
