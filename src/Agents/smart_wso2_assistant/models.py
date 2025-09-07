from typing import List, Optional, Literal, Dict, Any, Union, Deque
from collections import deque
from pydantic import BaseModel, Field, ConfigDict
from langgraph.graph import MessagesState






# --- Base Item Schemas (some are from before) ---

class PropertyItem(BaseModel):
    name: str
    scope: Literal["default", "axis2", "transport", "synapse", "operation"]
    type: Optional[str] = Field(None, description="STRING, INTEGER, BOOLEAN, OM, etc.")
    valueExpression: Optional[str] = Field(None, description="Value expression or literal")
    action: Optional[Literal["set", "remove"]] = Field(None, description="Action performed on the property")
    defaultValue: Optional[str] = Field(None, description="Fallback value if any")
    execution_order: Optional[int] = Field(None, description="Order of execution")

class HeaderItem(BaseModel):
    name: str
    scope: Literal["transport", "axis2", "default"]
    action: Literal["set", "remove", "modify"]
    valueExpression: Optional[str] = Field(None, description="Value expression or literal")
    execution_order: Optional[int] = Field(None, description="Order of execution")


class UnclassifiedItem(BaseModel):
    type: str
    details: str
    location: Optional[str] = Field(None, description="Method or line reference")
    xml_location: Optional[str] = Field(None, description="XPath or line reference in sequence")
    execution_order: Optional[int] = Field(None, description="Order of execution")


class RequestItem(BaseModel):
    method: Literal["GET", "POST", "PUT", "DELETE"]
    url: str
    headers: List[HeaderItem] = Field(default_factory=list)
    body: Optional[str] = Field(None, description="Body of the request")
    execution_order: Optional[int] = Field(None, description="Order of execution")


class ResponseItem(BaseModel):
    status_code: int
    headers: List[HeaderItem] = Field(default_factory=list)
    body: Optional[str] = Field(None, description="Body of the response")
    execution_order: Optional[int] = Field(None, description="Order of execution")
    # Fixed the type annotation - this should probably be a more specific type
    # For now, making it a list of strings to represent response cases/conditions
    cases: List[str] = Field(default_factory=list, description="Response conditions or cases")


# --- NEW Schemas Based on Analysis ---

class ComplianceFinding(BaseModel):
    """Represents a single compliance finding from code comparison."""
    classification: Literal["MISSING", "MISMATCHED", "REDUNDANT"]
    category: Literal["properties", "headers", "transformations", "invocations", "database_interactions", "flow_control", "terminations", "security_operations", "requests", "responses", "unclassified_items"]
    details: str = Field(..., description="A clear description of the deviation. For mismatches, state what was found vs. what was required.")

class CodeComparisonResult(BaseModel):
    """The result of comparing Java analysis against Synapse sequence analysis."""
    findings: List[ComplianceFinding] = Field(default_factory=list, description="List of all compliance findings")

class TransformationItem(BaseModel):
    """Represents a significant change to the message body."""
    type: Literal["PayloadFactory", "DataMapping", "Enrich", "Clone", "Iterate", "ObjectConstruction", "PayloadBuilder", "Script"]
    media_type: Optional[str] = Field(None, description="e.g., 'application/json', 'application/xml'")
    template: str = Field(..., description="The format string or template used.")
    arguments: List[str] = Field(default_factory=list, description="List of variables or expressions used as arguments.")
    source_config: Optional[str] = Field(None, description="Enrich source configuration")
    target_config: Optional[str] = Field(None, description="Enrich target configuration")
    execution_order: Optional[int] = Field(None, description="Order of execution")

class InvocationItem(BaseModel):
    """Represents a call to an external system or endpoint."""
    target: str = Field(..., description="The name of the endpoint, service, or class being called.")
    is_asynchronous: bool = Field(default=False, description="True if the call is non-blocking.")
    method: Optional[Literal["GET", "POST", "PUT", "DELETE"]] = Field(None, description="HTTP method if applicable")
    endpoint_type: Optional[Literal["http", "address", "wsdl", "loadbalance", "failover"]] = Field(None, description="Type of endpoint")
    addressing_config: Optional[str] = Field(None, description="Endpoint addressing details")
    preparation_steps: List[str] = Field(default_factory=list, description="Steps to prepare the call")
    execution_order: Optional[int] = Field(None, description="Order of execution")

class DatabaseInteractionItem(BaseModel):
    """Represents an interaction with a database."""
    operation: Literal["update", "query", "insert", "delete", "select"]
    target_entity: str = Field(..., description="The name of the database table or entity being modified.")
    source_variable: Optional[str] = Field(None, description="The variable holding the data for the operation.")
    conditions: Optional[str] = Field(None, description="Where clause or conditions")
    configuration: Optional[str] = Field(None, description="Database connector configuration")
    entity_fields: List[str] = Field(default_factory=list, description="List of all entity fields for WSO2 mapping")
    property_mappings: Optional[Dict[str, str]] = Field(default=None, description="Java property to WSO2 property equivalent mappings")
    execution_order: Optional[int] = Field(None, description="Order of execution")

class FlowControlOperation(BaseModel):
    """Represents a single operation within flow control."""
    operation_type: str = Field(..., description="Type of operation (property, transformation, etc.)")
    details: str = Field(..., description="Serialized operation details")

class FlowControlCase(BaseModel):
    """Represents a single case within a switch or a 'then' block in an if."""
    case_condition: str
    operations: List[FlowControlOperation] = Field(default_factory=list, description="A list of nested operation objects (e.g., PropertyItem).")
    target_sequence: Optional[str] = Field(None, description="Sequence name if applicable")

class FlowControlItem(BaseModel):
    """Represents conditional logic like if/else or switch/case."""
    type: Literal["if", "switch", "filter", "iterate", "clone", "try", "try-catch", "loop"]
    condition: str = Field(..., description="The top-level condition to evaluate.")
    cases: List[FlowControlCase] = Field(default_factory=list, description="List of cases for a switch, or the 'then' block for an if.")
    default_or_else_operations: List[FlowControlOperation] = Field(default_factory=list, description="Operations for the default or else block.")
    error_handling: List[str] = Field(default_factory=list, description="Exception handling operations")
    onError_sequence: Optional[str] = Field(None, description="Fault sequence name")
    onComplete_sequence: Optional[str] = Field(None, description="Completion sequence name")
    execution_order: Optional[int] = Field(None, description="Order of execution")

class TerminationItem(BaseModel):
    """Represents an action that stops the current flow."""
    type: Literal["ThrowException", "Respond", "Drop", "Send", "Fault", "Return", "Break", "Continue", "Sequence"]
    details: str = Field(..., description="The type of exception (e.g., 'CustomException') or a description of the response action.")
    condition: Optional[str] = Field(None, description="When this termination occurs")
    target_sequence: Optional[str] = Field(None, description="Fault or response sequence name")
    execution_order: Optional[int] = Field(None, description="Order of execution")

class SecurityOperationItem(BaseModel):
    """Represents security-related operations like masking, validation, sanitization."""
    type: Literal["masking", "validation", "sanitization", "authentication", "encrypt", "decrypt", "signature", "usernametoken"]
    target: str = Field(..., description="Field or data being secured")
    method: str = Field(..., description="Exact security method applied")
    configuration: Optional[str] = Field(None, description="Security configuration details")
    execution_order: Optional[int] = Field(None, description="Order of execution")


# --- The MAIN Class for the LLM Output ---

class CodeLogicAnalysisV2(BaseModel):
    """A structured representation of the runtime logic from a source code file (Version 2)."""
    properties: List[PropertyItem] = Field(default_factory=list)
    headers: List[HeaderItem] = Field(default_factory=list)
#    logs: List[LogItem] = Field(default_factory=list)
    transformations: List[TransformationItem] = Field(default_factory=list)
    invocations: List[InvocationItem] = Field(default_factory=list)
    database_interactions: List[DatabaseInteractionItem] = Field(default_factory=list)
    flow_control: List[FlowControlItem] = Field(default_factory=list)
    terminations: List[TerminationItem] = Field(default_factory=list)
    security_operations: List[SecurityOperationItem] = Field(default_factory=list)
    requests: List[RequestItem] = Field(default_factory=list, description="HTTP requests being formatted or prepared")
    responses: List[ResponseItem] = Field(default_factory=list, description="HTTP responses being processed or expected")
    unclassified_items: List[UnclassifiedItem] = Field(default_factory=list)



class StrictBase(BaseModel):
    model_config = ConfigDict(extra='forbid')  # -> additionalProperties: false

# Result analyzer output
class ResultAnalyzerFinding(StrictBase):
    classification: Literal["MISSING", "MISMATCHED", "REDUNDANT"]
    category: Literal[
        "properties", "headers", "transformations", "invocations",
        "database_interactions", "flow_control", "terminations",
        "security_operations", "requests", "responses", "unclassified_items"
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    details: str
    suggested_fix: Optional[str] = None
    apache_camel_context: str
    wso2_context: str

class ResultAnalyzerOutput(StrictBase):
    findings: List[ResultAnalyzerFinding] = Field(default_factory=list)
    summary: Optional[str] = None


# --- The Shared State ---
class wso2_SharedState(MessagesState):
    next_step: str = "END"
    java_analysis_json: Optional[CodeLogicAnalysisV2] = None
    is_java_analysis_complete: bool = False
    sequence_analysis_json: Optional[CodeLogicAnalysisV2] = None
    is_sequence_analysis_complete: bool = False
    result_of_code_review_json: Optional[CodeComparisonResult] = None
    report: str = ""
    conversation_history: str = ""
    is_wso2_refined_code: bool = False
    history_processed: bool = False
    
