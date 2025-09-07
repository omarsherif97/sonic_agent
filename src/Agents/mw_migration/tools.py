# tools.py
import os
import logging # Import the logging library
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.tools import tool
import asyncio

# ================================================================================
# LOGGING CONFIGURATION
# ================================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Get a logger instance for this module

# ================================================================================
# CONFIGURATION & SETUP
# ================================================================================

import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure API key is loaded
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables.")

MODEL_NAME = "gpt-4.1" # Or your preferred model

# Use centralized LLM configuration instead of creating separate instances
def get_mw_llm():
    """Get LLM instance for MW Migration tools"""
    return ChatOpenAI(model_name=MODEL_NAME, temperature=0, api_key=OPENAI_API_KEY)

def get_thinking_llm():
    """Get thinking LLM instance for MW Migration tools"""
    return ChatOpenAI(model_name="o3-mini", api_key=OPENAI_API_KEY)

# Create instances dynamically when needed (not at import time)
LLM = None  # Will be set dynamically
thinking_LLM = None  # Will be set dynamically

# ================================================================================
# DIRECTORY CONSTANTS
# ================================================================================

API_ENDPOINT_DIR = "api_endpoint"
EDITING_DIR = "editing"
CUSTOM_FAULT_DIR = "custom_fault"
GENERIC_WSO2_DIR = "generic_wso2_prompt"
REQUEST_DIR = "request_prompts"
RESPONSE_DIR = "response_prompts"
EXAMPLE_DIR = "example"

# ================================================================================
# UTILITY FUNCTIONS
# ================================================================================

async def load_file(folder_name: str, file_name: str) -> str:
    """Load file content from a specified folder"""
    logger.debug(f"Attempting to load file '{file_name}' from folder '{folder_name}'")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_base_dir = os.path.join(base_dir, 'prompt')
    folder_path = os.path.join(prompt_base_dir, folder_name)
    full_path = os.path.join(folder_path, file_name)
    if not os.path.isfile(full_path):
        logger.error(f"File '{file_name}' not found at path '{full_path}'.")
        raise FileNotFoundError(f"File '{file_name}' not found in '{folder_path}'. Searched path: {full_path}")
    try:
        with asyncio.open(full_path, 'r', encoding='utf-8') as file:
            content = await file.read()
            logger.debug(f"Successfully loaded file '{file_name}'. Content length: {len(content)}")
            return content
    except Exception as e:
        logger.error(f"Error reading file '{full_path}': {e}", exc_info=True)
        raise # Re-raise the exception after logging


def load_file_sync(folder_name: str, file_name: str) -> str:
    """Load file content from a specified folder (synchronous version)"""
    logger.debug(f"Attempting to load file '{file_name}' from folder '{folder_name}'")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_base_dir = os.path.join(base_dir, 'prompt')
    folder_path = os.path.join(prompt_base_dir, folder_name)
    full_path = os.path.join(folder_path, file_name)
    if not os.path.isfile(full_path):
        logger.error(f"File '{file_name}' not found at path '{full_path}'.")
        raise FileNotFoundError(f"File '{file_name}' not found in '{folder_path}'. Searched path: {full_path}")
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.debug(f"Successfully loaded file '{file_name}'. Content length: {len(content)}")
            return content
    except Exception as e:
        logger.error(f"Error reading file '{full_path}': {e}", exc_info=True)
        raise # Re-raise the exception after logging

# ================================================================================
# TEMPLATE/EXAMPLE FILE LOADING
# ================================================================================

try:
    logger.info("Loading example/template files...")
    
    # Request-related examples
    request_mw_example = load_file_sync(EXAMPLE_DIR, "request_mw_example.txt")
    request_wso2_example = load_file_sync(EXAMPLE_DIR, "request_wso2_example.txt")
    incoming_request = load_file_sync(EXAMPLE_DIR, "incoming_request.txt")
    sample_request = load_file_sync(EXAMPLE_DIR, "sample_request.txt")

    # Response-related examples
    response_wso2_example = load_file_sync(EXAMPLE_DIR, "response_wso2_example.txt")
    xparam = load_file_sync(EXAMPLE_DIR, "xparam.txt")
    MultiOptions = load_file_sync(EXAMPLE_DIR, "MultiOptions.txt")

    # Dataservice-related examples
    dataservice_example = load_file_sync(EXAMPLE_DIR, "dataservice_connection.txt")
    dataservice_varHandler = load_file_sync(EXAMPLE_DIR, "dataservice_varHandler.txt")

    # General mapping and handling examples
    general_mapper = load_file_sync(EXAMPLE_DIR, "general_mapper.txt")
    variable_handling = load_file_sync(EXAMPLE_DIR, "variable_handling.txt")

    # Failure handling examples
    dafault_failure_handling = load_file_sync(EXAMPLE_DIR, "dafault_failure_handling.txt")
    special_failure_handling = load_file_sync(EXAMPLE_DIR, "special_failure_handling.txt")


    wso2_fault_exception = load_file_sync(EXAMPLE_DIR, "wso2-fault.txt")
    # Additional mediator examples
    extra_data_mediator = load_file_sync(EXAMPLE_DIR, "extra_data_mediator.txt")
    multioption_tag_mediator = load_file_sync(EXAMPLE_DIR, "multioption_tag_mediator.txt")
    
    logger.info("Example/template files loaded successfully.")

except FileNotFoundError as e:
    logger.warning(f"Could not load example/template file: {e}. Tool prompts might be incomplete.")
    # Assign empty strings or default values for missing files
    request_mw_example = ""
    request_wso2_example = ""
    dataservice_example = ""
    general_mapper = ""
    response_wso2_example = ""
    wso2_fault_exception = ""
    incoming_request = ""
    sample_request = ""
    xparam = ""
    MultiOptions = ""
    dataservice_varHandler = ""
    variable_handling = ""
    dafault_failure_handling = ""
    special_failure_handling = ""
    extra_data_mediator = ""
    multioption_tag_mediator = ""
except Exception as e:
    logger.error(f"Unexpected error loading example/template files: {e}", exc_info=True)

# ================================================================================
# PYDANTIC INPUT SCHEMAS
# ================================================================================

class GenerateWso2RequestInput(BaseModel):
    source_code: str = Field(..., description="source code of the java code")
    service_name: str = Field(..., description="Logical name of the integration service")
    request_parameters: str = Field(..., description="body parameters for the JSON request to the endpoint, ONLY FROM DTO FILE")
    request_type: str = Field(..., description="HTTP method used when calling the external service (GET or POST)")
    hard_coded_parameters: str = Field(..., description="parameters that have hard-coded values in the java code")
    configuration_parameters: str = Field(..., description="parameters that are defined in the configuration file")
    HTTP_HEADERS: str = Field(..., description="Headers to be attached to the outbound request")
    
class GenerateDataserviceInput(BaseModel):
    db_logging_logic: str = Field(description="Description or Camel snippet related ONLY to the database logging/interaction logic (e.g., from a transactionLogProcessor).")
    user_requirements_db: Optional[str] = Field(None, description="Optional specific user requirements ONLY for the Dataservice configuration itself.")

class GenerateWso2ResponseInput(BaseModel):
    succ_DTO_xparam_parameters: str = Field(description="list of parameters which are extracted from the java logic ONLY SPECIFICALLY FROM DTO FILE, NOT FROM INCOMING RESPONSE BODY")
    fail_DTO_xparam_parameters: str = Field(description="list of parameters which are extracted from the java logic ONLY SPECIFICALLY FROM ERROR DTO FILE, NOT FROM INCOMING RESPONSE BODY")
    required_mapping: str = Field(description="Are there any parameters that has a new name in the response?")
    variables_error_handling: str = Field(description="variables that requires validating as per the java logic provided")
    fault_special_handling: str = Field(description="Analyze the java logic and determine what should be done if the response is not successful")
    isMultiOption: bool = Field(description="IF BillDTO is present then it is true else false")
    input_response_structure:str = Field(description="What is the structure of the input response to the sequence?")
    service_name: str = Field(description="What is the name of the service?")
    dataservice_code: Optional[str] = Field(None, description="Optional WSO2 Dataservice (.dbs) XML configuration generated previously, to be potentially referenced by the sequence.")
    


# ================================================================================
# CORE BUSINESS LOGIC FUNCTIONS
# ================================================================================

# --- WSO2 Request Sequence Generation ---
async def generate_wso2_request_sequence(source_code: str, service_name: str, request_parameters: str, request_type: str,
    hard_coded_parameters: str, configuration_parameters: str, HTTP_HEADERS: str) -> str:
    """
    Business‑logic wrapper: calls prompt templates, LLMs, etc.
    Keep this function unaware of the LangChain tool layer.
    """
    try:
        logger.info("Generating WSO2 request sequence for %s", service_name)

        # LAYER 1: JAVA SOURCE CODE ANALYSIS
        source_code_analysis = await load_file(REQUEST_DIR, "java_source_code_analysis.txt").format(
            java_source_code=source_code
        )
        
        # Get thinking LLM instance dynamically
        thinking_llm_instance = get_thinking_llm()
        java_analysis = thinking_llm_instance.invoke([SystemMessage(content=source_code_analysis)]).content
                      
        # LAYER 2: BASELINE OUTPUT
        generation_prompt_template = await load_file(REQUEST_DIR, "request_WSO2_GENERATION.txt")

        prompt = generation_prompt_template.format(
            java_analysis=java_analysis,
            service_name=service_name,
            incoming_request=incoming_request,
            request_parameters=request_parameters,
            request_type=request_type,
            hard_coded_parameters=hard_coded_parameters,
            variable_handling=variable_handling,
            configuration_parameters=configuration_parameters,
            HTTP_HEADERS=HTTP_HEADERS,
            dataservice_varHandler=dataservice_varHandler,
            dataservice_connection=dataservice_example,
            general_mapper=general_mapper,
            sample_request=sample_request
        )

        # Get LLM instance dynamically
        llm_instance = get_mw_llm()
        BASELINE_WSO2_CODE = await llm_instance.ainvoke([SystemMessage(content=prompt)]).content
        
        # LAYER 3: SELF-REFLECTION
        reflection_prompt = await load_file(REQUEST_DIR, "SELF_REFLECTION_1.txt").format(
            wso2_generated_file=BASELINE_WSO2_CODE,
            configuration_parameters=configuration_parameters,
            general_mapper=general_mapper,
            incoming_request=incoming_request
        )
        # Use same LLM instance for consistency
        wso2_refined = await llm_instance.ainvoke([SystemMessage(content=reflection_prompt)]).content
        
        return wso2_refined

    except FileNotFoundError as e:
        logger.exception("Prompt file not found")
        return f"Tool Error: Missing prompt resource – {e}"

    except Exception as e:
        logger.exception("Unexpected error while building WSO2 sequence")
        return f"Tool Error: {e}"

# --- WSO2 Dataservice Configuration Generation ---
async def generate_wso2_dataservice_config(db_logging_logic: str, user_requirements_db: Optional[str] = None) -> str:
    """Generates WSO2 Dataservice (.dbs) XML config based on DB logging logic."""
    logger.info("--- Entering Tool: generate_wso2_dataservice_config ---")
    try:
        prompt_file = "response_DATASERVICE_GENERATION.txt"
        logger.debug(f"Loading dataservice generation prompt from: {RESPONSE_DIR}/{prompt_file}")
        prompt_template = await load_file(RESPONSE_DIR, prompt_file)

        required_keys_ds = ["dataservice_example"]
        if not all(f"{{{key}}}" in prompt_template for key in required_keys_ds):
             logger.warning(f"Potential missing keys in {prompt_file}. Required: {required_keys_ds}")

        prompt_text = prompt_template.format(
            dataservice_example=dataservice_example
        )

        human_message_content = f"Generate the WSO2 Dataservice connection based on the following database logging requirements:\n```\n{db_logging_logic}\n```"
        if user_requirements_db:
            human_message_content += f"\n\nSpecific requirements for the Dataservice configuration: {user_requirements_db}"
        else:
             human_message_content += "\n\nFocus on creating the necessary queries and operations based on the logic described."

        logger.debug(f"Dataservice Human Message (start): {human_message_content[:100]}...")
        messages = [
            SystemMessage(content=prompt_text),
            HumanMessage(content=human_message_content)
        ]
        logger.info("Invoking LLM for dataservice config generation...")
        # Get LLM instance dynamically
        llm_instance = get_mw_llm()
        response = await llm_instance.ainvoke(messages)
        content = response.content
        logger.info("--- Exiting Tool: generate_wso2_dataservice_config (Success) ---")
        return content

    except FileNotFoundError as e:
        logger.error(f"Tool Error (Dataservice): Prompt file not found. {e}", exc_info=True)
        return f"Tool Error: Failed to generate dataservice config due to missing prompt file: {e}"
    except KeyError as e:
        logger.error(f"Tool Error (Dataservice): Missing key in prompt template formatting. Key: {e}", exc_info=True)
        return f"Tool Error: Failed to generate dataservice config due to a formatting error in the prompts (missing key: {e})."
    except Exception as e:
        logger.error(f"Tool Error (Dataservice): Unexpected error. {e}", exc_info=True)
        return f"Tool Error: An unexpected error occurred while generating the dataservice config: {e}"

# --- WSO2 Response Sequence Generation ---
async def generate_wso2_response_sequence(
    succ_DTO_xparam_parameters: str,
    fail_DTO_xparam_parameters: str,
    required_mapping: str,
    variables_error_handling: str,
    fault_special_handling: str,
    isMultiOption: bool,
    input_response_structure:str,
    service_name: str,
    dataservice_code: Optional[str] = None
) -> str:
    """
    Generates WSO2 response sequence XML based on response handling logic.
    Optionally incorporates provided dataservice code.
    Generates a baseline if user_requirements_response is not provided.
    """
    logger.info(f"Dataservice code provided: {bool(dataservice_code)}")

    try:
        
        human_message_content = f"""Generate a WSO2 response sequence based strictly on the following requirements:
            1.  **Service Name:** {service_name}
            2.  **Expected Response Structure:** This is the expected response structure that will be input to the response sequence: ```{input_response_structure}```
                USE IT ONLY AND ONLY IF YOU NEED TO DEFINE THE PATH OF A PROPERTY. AND IF YOU NEED TO DEFINE THE PARAMETER THAT DEFINES THE STATUS OF THE RESPONSE.
            3.  **MultiOption Tag Flag:** {isMultiOption}

            4.  **extracted parameters from java logic for XParam:**
                ```
                {succ_DTO_xparam_parameters}
                ```
                IF THERE IS RESPONSE BUT IT IS A FAILED RESPONSE USE THIS
                ```
                {fail_DTO_xparam_parameters}
                ```
                IF IT IS EMPTY THEN CONSIDER DEFAULT HANDLING

            5.  **Parameter Mapping:** Apply these mappings when defining properties keep the original name as the name for the property and the real name for the extraction path:
                ```
                {required_mapping or 'No specific mappings required.'}
                ```

            6.  **Validation and Error Handling:** Implement the following validation logic using filter mediators, switch mediators, etc..
                ```
                {variables_error_handling or 'No specific validation required'}
                ```
                

            7.  **Special Fault Handling:** If the main success check indicates failure, implement this specific fault handling logic. 
                ```
                {fault_special_handling or 'No specific fault handling required'}
                ```

            8.  **Potentially relevant Dataservice Code (for context if DB calls are mentioned in requirements):**
                ```xml
                {dataservice_code or 'N/A'}
                ```
            """
        prompt_file = "response_WSO2_GENERATION.txt"
        logger.debug(f"Loading response sequence generation prompt from: {RESPONSE_DIR}/{prompt_file}")
        prompt_template = await load_file(RESPONSE_DIR, prompt_file) 


        required_keys_seq = ["wso2_example", "dataservice_code"]
        if not all(f"{{{key}}}" in prompt_template for key in required_keys_seq):
             logger.warning(f"Potential missing keys in {prompt_file}. Required: {required_keys_seq}")

        prompt_text = prompt_template.format(
            wso2_example=response_wso2_example,
            dataservice_code=dataservice_code,
            MultiOptions=MultiOptions,
            xparam=xparam,
            fail_DTO_xparam_parameters=fail_DTO_xparam_parameters,
            special_failure_handling=special_failure_handling,
            dafult_failure_handling=dafault_failure_handling,
            variable_handling=variable_handling,
            multioption_tag_mediator=multioption_tag_mediator,
            extra_data_mediator=extra_data_mediator
        )
        logger.info(f"Response Sequence Prompt Text: {prompt_text}")
        logger.debug(f"Response Sequence Human Message (start): {human_message_content[:100]}...")
        messages = [
            SystemMessage(content=prompt_text),
            HumanMessage(content=human_message_content)
        ]
        logger.info("Invoking LLM for response sequence generation...")
        # Get LLM instance dynamically
        llm_instance = get_mw_llm()
        WSO2_CODE = await llm_instance.ainvoke(messages)
        wso2_generated = WSO2_CODE.content
        self_reflection = await load_file(RESPONSE_DIR,"RS_SLF_REFLECT.txt")
        self_reflection_prompt = self_reflection.format(
            wso2_generated_file=wso2_generated,
            service_name=service_name
        )
        # Use same LLM instance for consistency
        refined_wso2_code = await llm_instance.ainvoke([SystemMessage(content=self_reflection_prompt)]).content
        logger.info(f"Generated response sequence received (start): {refined_wso2_code[:200]}...")
        logger.info("--- Exiting Tool: generate_wso2_response_sequence (Success) ---")
        return refined_wso2_code

    except FileNotFoundError as e:
        logger.error(f"Tool Error (Response Seq): Prompt file not found. {e}", exc_info=True)
        return f"Tool Error: Failed to generate response sequence due to missing prompt file: {e}"
    except KeyError as e:
        logger.error(f"Tool Error (Response Seq): Missing key in prompt template formatting. Key: {e}", exc_info=True)
        return f"Tool Error: Failed to generate response sequence due to a formatting error in the prompts (missing key: {e})."
    except Exception as e:
        logger.error(f"Tool Error (Response Seq): Unexpected error. {e}", exc_info=True)
        return f"Tool Error: An unexpected error occurred while generating the response sequence: {e}"


# # --- WSO2 Fault Sequence Generation ---
# async def generate_wso2_fault_sequence(source_code: str, sequence_name: str) -> str:
#     """
#     Generates a WSO2 fault sequence XML based on a description of the error handling requirements.
#     """
#     logger.info("--- Entering Tool: generate_wso2_fault_sequence ---")
#     try:
#         prompt_file = "fault-analyzer.txt"
#         logger.debug(f"Loading prompt: {prompt_file}")
#         prompt_template = await load_file(CUSTOM_FAULT_DIR, prompt_file)
# 
#         prompt_text = prompt_template.format(
#             route_blueprint=source_code,
#             sequence_name=sequence_name
#         )
#         messages = [ SystemMessage(content=prompt_text)]
#         logger.info("Invoking LLM for fault sequence generation...")
#         fault_analysis = await thinking_LLM.ainvoke(messages).content
# 
#         """
#         wso2_fault_example = await load_file(EXAMPLE_DIR, "wso2-fault.txt")
#         sequence_prompt = await load_file(CUSTOM_FAULT_DIR, "fault_sequence_orchestrator.txt")
#         sequence_prompt = sequence_prompt.format(
#             extracted_info=fault_analysis,
#             sequence_name=sequence_name,
#             wso2_fault_example=wso2_fault_example
#         )
#         fault_sequence = await LLM.ainvoke([SystemMessage(content=sequence_prompt)]).content
#         """
#         return fault_analysis
# 
#     except FileNotFoundError as e:
#         logger.error(f"Tool Error: Prompt file not found. {e}", exc_info=True)
#         return f"Tool Error: Failed to generate fault sequence due to missing prompt file: {e}"
#     except KeyError as e:
#         logger.error(f"Tool Error: Missing key in prompt template formatting. Key: {e}", exc_info=True)
#         return f"Tool Error: Failed to generate fault sequence due to a formatting error in the prompts (missing key: {e})."
#     except Exception as e:
#         logger.error(f"Tool Error: Unexpected error in generate_wso2_fault_sequence. {e}", exc_info=True)
#         return f"Tool Error: An unexpected error occurred while generating the fault sequence: {e}"


# ================================================================================
# LANGCHAIN TOOL DECORATORS
# ================================================================================

@tool(args_schema=GenerateWso2RequestInput)
async def generate_wso2_request_sequence_tool(source_code: str, service_name: str, request_parameters: str, request_type: str, hard_coded_parameters: str, configuration_parameters: str, HTTP_HEADERS: str) -> str:
    """Generates WSO2 request sequence XML. Analyzes Camel, uses requirements, produces sequence."""
    return await generate_wso2_request_sequence(source_code, service_name, request_parameters, request_type, hard_coded_parameters, configuration_parameters, HTTP_HEADERS)

@tool(args_schema=GenerateDataserviceInput)
async def generate_wso2_dataservice_config_tool(db_logging_logic: str, user_requirements_db: Optional[str] = None) -> str:
    """Generates WSO2 Dataservice (.dbs) XML config based ONLY on database logging logic/requirements."""
    return await generate_wso2_dataservice_config(db_logging_logic, user_requirements_db)

@tool(args_schema=GenerateWso2ResponseInput)
async def generate_wso2_response_sequence_tool(succ_DTO_xparam_parameters: str,fail_DTO_xparam_parameters: str,
    required_mapping: str,
    variables_error_handling: str,
    fault_special_handling: str,
    isMultiOption: bool,
    input_response_structure:str,
    service_name: str,
    dataservice_code: Optional[str] = None) -> str:
    """Generates WSO2 response sequence XML based ONLY on response handling logic. Optionally uses provided dataservice code. Generates baseline if requirements are missing."""
    return await generate_wso2_response_sequence(succ_DTO_xparam_parameters,fail_DTO_xparam_parameters,
    required_mapping,
    variables_error_handling,
    fault_special_handling,
    isMultiOption,
    input_response_structure,
    service_name,
    dataservice_code)

# ================================================================================
# TOOL REGISTRY
# ================================================================================

available_tools_decorated = [
    generate_wso2_request_sequence_tool,
    generate_wso2_dataservice_config_tool,
    generate_wso2_response_sequence_tool,
]

logger.info("Tools module initialized with decorated tools.")