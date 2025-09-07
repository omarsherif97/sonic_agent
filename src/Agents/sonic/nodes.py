from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field

import sys
from pathlib import Path

# Define current directory and parent directories clearly
current_dir = Path(__file__).parent  # This is: src/Agents/sonic/
sonic_dir = current_dir
agents_dir = current_dir.parent      # This is: src/Agents/
src_dir = agents_dir.parent          # This is: src/
project_root = src_dir.parent         # This is: / (project root)

# Add the project root and src directory to path for absolute imports if not already present
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Now, import modules using absolute paths
from src.Agents.sonic.prompts import main_prompt
from src.Agents.LLM import get_llm

class sonic_SharedState(MessagesState):
    pass



async def main_node(state: sonic_SharedState):
    """Main node for the sonic agent"""
    try:
        # Get the last user message
        #user_message = HumanMessage(content=state["messages"][-1].content)
        
        # Create system message with the main prompt
        system_message = SystemMessage(content=main_prompt)
        
        # Prepare messages for LLM
        messages = [system_message] + state["messages"]
        
        # Get LLM instance
        llm = get_llm()
        
        # Generate response
        response = llm.invoke(messages)
        
        # Add AI response to state
        state["messages"].append(response)
        
    except Exception as e:
        # Fallback response if anything fails
        if AIMessage:
            fallback_response = AIMessage(content=f"I'm having trouble processing your request. Error: {str(e)}")
            state["messages"].append(fallback_response)
        print(f"Error in sonic main_node: {e}")
    
    return state



