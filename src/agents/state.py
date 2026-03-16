from typing import TypedDict, Annotated, List, Optional
from src.models.tool import ToolDefinition

from typing import TypedDict, List, Annotated, Union
from operator import add

class AgentState(TypedDict):
    query: str
    chat_history: Annotated[List[dict], add] # Keeps track of thoughts and tool results
    retrieved_tools: List[ToolDefinition]
    tool_decision: dict
    next_step: str # The specific sub-task the agent is currently solving
    final_response: str
    steps_count: int