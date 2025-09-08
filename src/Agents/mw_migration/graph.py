# graph.py
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode

from .tools import available_tools_decorated
from .nodes import main_agent_node, route_after_main, humanize_from_tools_node

graph = StateGraph(MessagesState)

graph.add_node("main_agent", main_agent_node)
graph.add_node("tool_executor", ToolNode(available_tools_decorated))
graph.add_node("humanize_from_tools", humanize_from_tools_node)

graph.add_edge(START, "main_agent")

# 2 scenarios: end directly OR run tools
graph.add_conditional_edges(
    "main_agent",
    route_after_main,
    {"end": END, "tools": "tool_executor"},
)

# After tools, do one humanizing LLM turn, then end
graph.add_edge("tool_executor", "humanize_from_tools")
graph.add_edge("humanize_from_tools", END)


# Expose the StateGraph as `builder` so the runtime can call
# `builder.compile(checkpointer=...)` to enable DB-backed memory.
builder = graph

# Compile graph (fallback if runtime does not provide a checkpointer)
compiled_graph = graph.compile()

