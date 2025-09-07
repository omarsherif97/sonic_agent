#############################################
#  IMPORTS                                  #
#############################################
from pydantic import BaseModel, Field
from typing import List
from langchain_core.tools import tool
from .prompts import review_code_tool_prompt, code_editor_prompt, java_analyzer_prompt, sequence_analyzer_prompt, code_comparator_prompt, result_comparison_analyzer_prompt
from src.Agents.LLM import get_llm
from langchain_core.messages import HumanMessage, SystemMessage



#############################################
#  PYDANTIC INPUT SCHEMAS                   #
#############################################
class editing_tool(BaseModel):
    instruction: List[str]
    code: str = Field(description="The code to edit")

class review_code_tool(BaseModel):
    wso2_code: str = Field(description="The WSO2 code to make sure that code is compatible with WSO2 6.0.0")


class java_analyzer_tool(BaseModel):
    java_code: str = Field(description="The Java code to analyze")

class sequence_analyzer_tool(BaseModel):
    wso2_code: str = Field(description="The WSO2 code to analyze")

class code_comparator_tool(BaseModel):
    java_analysis: str = Field(description="The Java analysis")
    sequence_analysis: str = Field(description="The sequence analysis")
    
class result_comparator_analyzer_tool(BaseModel):
    comparison_results: str = Field(description="The comparison result JSON to analyze")
    optional_context: str = Field(description="The optional context for the analysis")
    
#############################################
#  CORE BUSINESS LOGIC FUNCTIONS            #
#############################################
async def edit_code(instruction: List[str], code: str) -> str:
    """
    Edits code based on provided instructions.
    
    Args:
        instruction (List[str]): List of editing instructions to apply
        code (str): Original code to be edited
        
    Returns:
        str: Modified code after applying the instructions
    """
    # Initialize LLM
    llm = get_llm()
    # Create prompt
    # Use safe replacements to avoid accidental format placeholders in the prompt templates
    prompt = code_editor_prompt.replace('{original_code}', str(code)).replace('{editing_instructions}', str(instruction))
    # Invoke LLM
    response = await llm.ainvoke(prompt)
    return response

async def review_code(wso2_code: str) -> str:
    """
    Reviews WSO2 code for compatibility with version 6.0.0.
    
    Args:
        wso2_code (str): WSO2 code to be reviewed
        
    Returns:
        str: Review findings and compatibility assessment
    """
    # Initialize LLM
    llm = get_llm()
    # Create prompt
    prompt = review_code_tool_prompt.replace('{wso2_code}', str(wso2_code))
    response = await llm.ainvoke(prompt)
    return response

async def java_analyzer(java_code: str) -> str:
    """
    Analyzes Java code to extract its logical structure and behavior.
    
    Args:
        java_code (str): Java code to analyze
        
    Returns:
        str: Analysis of the code's logic
    """
    # Create user message with code
    user_message = HumanMessage(content=java_code)
    # Create system message with prompt
    system_message = SystemMessage(content=java_analyzer_prompt.replace('{apache_camel_code}', str(java_code)))
    # Combine messages
    messages = [system_message, user_message]
    # Get LLM instance
    llm = get_llm()
    # Get analysis response
    response = await llm.ainvoke(messages)
    #return the response
    return response.content

async def sequence_analyzer(wso2_code: str) -> str:
    """
    Analyzes WSO2 sequence code to extract its logical structure and behavior.
    
    Args:
        wso2_code (str): WSO2 sequence code to analyze
        
    Returns:
        str: Analysis of the sequence's logic
    """
    # Create user message with code
    user_message = HumanMessage(content=wso2_code)
    # Create system message with prompt
    system_message = SystemMessage(content=sequence_analyzer_prompt.replace('{wso2_code}', str(wso2_code)))
    # Combine messages
    messages = [system_message, user_message]
    # Get LLM instance
    llm = get_llm()
    # Get analysis response
    response = await llm.ainvoke(messages)
    #return the response
    return response.content

async def code_comparator(java_analysis: str, sequence_analysis: str) -> str:
    """
    Compares Java code analysis with WSO2 sequence analysis to identify gaps and differences.
    
    Args:
        java_analysis (str): Analysis of Java code
        sequence_analysis (str): Analysis of WSO2 sequence
        
    Returns:
        str: Contains original comparison results and semantic analysis
    """
    
    # Create a system message with the base comparison prompt
    system_message = SystemMessage(content=code_comparator_prompt.replace('{apache_camel_analysis}', str(java_analysis)).replace('{wso2_analysis}', str(sequence_analysis)))
    # Combine the messages into a list for the LLM
    messages = [system_message]
    
    # Get a new LLM instance for the comparison
    llm = get_llm()
    # Get the initial comparison results from the LLM
    comparison_response = await llm.ainvoke(messages)
    #return the comparison response
    return comparison_response.content


async def result_comparator_analyzer(comparison_results: str, optional_context: str) -> str:
    """
    Analyzes the comparison result and returns the findings.
    
    Args:
        comparison_results (str): The comparison result JSON to analyze
        optional_context (str): The optional context
    Returns:
        str: Analysis of the comparison result
    """
    # Create a message for semantic analysis containing the comparison results
    user_message = HumanMessage(content=f"Analysis of the comparison result against the source of truth (Apache Camel) and the candidate (WSO2)")
    # Create a system message with the semantic analysis prompt
    prompt_content = result_comparison_analyzer_prompt.replace('{comparison_results}', comparison_results)
    prompt_content = prompt_content.replace('{optional_context}', optional_context)
    # Combine messages for semantic analysis
    system_message = SystemMessage(content=prompt_content)
    # Combine messages for semantic analysis
    messages = [system_message, user_message]
    # Get a fresh LLM instance for semantic analysis
    analyzer_llm = get_llm()
    # Get the semantic analysis of the comparison results
    analyzed_response = await analyzer_llm.ainvoke(messages)
    #return the analyzed response
    return analyzed_response.content



#############################################
#  TOOL DECORATORS                          #
#############################################
# Tool for code editing
@tool(args_schema=editing_tool)
async def edit_code_tool(instruction: List[str], code: str) -> str:
    """Edits the code based on the instruction."""
    return await edit_code(instruction, code)

# Tool for code review
@tool(args_schema=review_code_tool)
async def review_code_tool(wso2_code: str) -> str:
    """Reviews the code and returns the findings."""
    return await review_code(wso2_code)

# Tool for Java analysis
@tool(args_schema=java_analyzer_tool)
async def java_analyzer_tool(java_code: str) -> str:
    """Analyzes the Java code and returns the analysis."""
    return await java_analyzer(java_code)

# Tool for sequence analysis
@tool(args_schema=sequence_analyzer_tool)
async def sequence_analyzer_tool(wso2_code: str) -> str:
    """Analyzes the WSO2 code and returns the analysis."""
    return await sequence_analyzer(wso2_code) 

# Tool for code comparison
@tool(args_schema=code_comparator_tool)
async def code_comparator_tool(java_analysis: str, sequence_analysis: str) -> str:
    """Compares the Java and WSO2 code and returns the findings."""
    return await code_comparator(java_analysis, sequence_analysis)

# Tool for result comparator analyzer
@tool(args_schema=result_comparator_analyzer_tool)
async def result_comparator_analyzer_tool(comparison_results: str, optional_context: str) -> str:
    """Analyzes the comparison result and returns the findings."""
    return await result_comparator_analyzer(comparison_results, optional_context)

#############################################
#  TOOL REGISTRY                            #
#############################################
# List of all available tools
tools = [edit_code_tool, review_code_tool, java_analyzer_tool, sequence_analyzer_tool, code_comparator_tool, result_comparator_analyzer_tool]




