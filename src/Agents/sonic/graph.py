from langgraph.graph import StateGraph, START, END
from .nodes import *
from langchain_core.messages import HumanMessage

graph = StateGraph(sonic_SharedState)

graph.add_node("sonic", main_node)

    

graph.add_edge(START, "sonic")
graph.add_edge("sonic", END)

compiled_graph = graph.compile()



