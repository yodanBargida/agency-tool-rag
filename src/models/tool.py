from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ToolDefinition(BaseModel):
    id: str = Field(..., description="Unique identifier for the tool")
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Clear description of what the tool does")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for the tool's parameters")
    output_schema: Dict[str, Any] = Field(..., description="JSON schema for the tool's response")

class RetrievalResult(BaseModel):
    tool: ToolDefinition
    score: float = Field(..., description="Similarity score (lower is better for pgvector distance)")

class AgentRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
