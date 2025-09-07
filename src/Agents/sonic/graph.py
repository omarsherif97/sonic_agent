from langgraph.graph import StateGraph, START, END
from .nodes import *
from langchain_core.messages import HumanMessage

graph = StateGraph(sonic_SharedState)

graph.add_node("sonic", main_node)

    

graph.add_edge(START, "sonic")
graph.add_edge("sonic", END)

# Expose the StateGraph as `builder` so the runtime can call
# `builder.compile(checkpointer=...)` to enable DB-backed memory.
builder = graph

# Compile graph (fallback if runtime does not provide a checkpointer)
compiled_graph = graph.compile()



