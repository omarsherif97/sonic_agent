from pydantic import BaseModel
from typing import List, Dict, Any
from pydantic import Field

class InputSchema(BaseModel):
    agent_input: Dict[str, Any] = Field(default_factory=dict)
    thread_id: str
    agent_name: str

class OutputSchema(BaseModel):
    AI_Response: str