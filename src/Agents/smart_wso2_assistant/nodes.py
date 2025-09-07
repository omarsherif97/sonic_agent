#############################################
#  IMPORTS                                  #
#############################################
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import END
from typing import Literal
import os
import sys
import json

#############################################
#  LOCAL IMPORTS                            #
#############################################
try:
    from .models import wso2_SharedState
    from .prompts import smart_wso2_agent_prompt, history_recorder_prompt
    from src.Agents.LLM import get_llm
    from .tools import tools as tools_list
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    # Set fallback values
    smart_wso2_agent_prompt = "You are a helpful AI assistant."
    history_recorder_prompt = "Record conversation history."
    tools_list = []

#############################################
#  CONFIGURATION                            #
#############################################


#############################################
#  AGENT FUNCTIONS                          #
#############################################
async def smart_wso2_agent(state: wso2_SharedState) -> wso2_SharedState:
    # Setup environment
    #setup_environment()
    
    #user message
    user_message = HumanMessage(content=state["messages"][-1].content)
    #get conversation history
    conversation_history = state.get("conversation_history", "EMPTY")
    
    #build system message
    system_message = SystemMessage(content=smart_wso2_agent_prompt.replace(
        '{conversation_history}', conversation_history
    ))
    #prepare messages
    messages = [system_message, user_message] + state["messages"]
    
    try:
        #get llm
        llm = get_llm()
        #add tools to llm
        if tools_list:
            llm = llm.bind_tools(tools_list)
        #call llm
        response = await llm.ainvoke(messages)
    except Exception as e:
        # Fallback response if LLM fails
        response = AIMessage(content=f"I'm having trouble processing your request right now. Error: {str(e)}")
    
    #always add the AIMessage response to the conversation first
    state["messages"].append(response)
    
    #check if response has tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        # Create a tools dictionary for easy lookup
        tools_dict = {tool.name: tool for tool in tools_list}
        
        # Process each tool call (there might be multiple)
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["args"]
            tool_call_id = tool_call["id"]
            
            # Call the actual tool function
            if tool_name in tools_dict:
                try:
                    tool_result = await tools_dict[tool_name].ainvoke(tool_input)
                    # Create proper ToolMessage
                    tool_message = ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call_id
                    )
                    state["messages"].append(tool_message)
                except Exception as e:
                    # Handle tool execution errors
                    error_message = ToolMessage(
                        content=f"Error executing tool {tool_name}: {str(e)}",
                        tool_call_id=tool_call_id
                    )
                    state["messages"].append(error_message)
            else:
                # Handle unknown tool
                error_message = ToolMessage(
                    content=f"Unknown tool: {tool_name}",
                    tool_call_id=tool_call_id
                )
                state["messages"].append(error_message)
        
        # Final answer that uses the tool outputs
        final_system_hint = SystemMessage(content=(
            "You just received tool result(s). Now craft a concise answer for the user. "
            "If helpful, append the 'Tool result'."
        ))
        follow_up_messages = [final_system_hint] + state["messages"]
        follow_up_response = await llm.ainvoke(follow_up_messages)
        state["messages"].append(follow_up_response)
    
    return state

async def history_recorder(state: wso2_SharedState) -> wso2_SharedState:
    """Record conversation history for memory management"""
    try:
        # Simple history recording
        conversation_text = "\n".join([msg.content for msg in state["messages"] if hasattr(msg, 'content')])
        state["conversation_history"] = conversation_text[:1000]  # Limit to 1000 chars
        
        # Clear old messages to prevent memory issues
        if len(state["messages"]) > 20:
            state["messages"] = state["messages"][-10:]  # Keep last 10 messages
    except Exception as e:
        print(f"Warning: Error in history recorder: {e}")
    
    return state
