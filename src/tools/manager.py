from typing import List, Dict, Any
from src.database.vector_store import VectorStore
from src.models.tool import ToolDefinition

class ToolManager:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def create_tool(self, tool_def: ToolDefinition):
        self.vector_store.upsert_tool(
            tool_id=tool_def.id,
            tool_name=tool_def.name,
            description=tool_def.description,
            input_schema=tool_def.input_schema,
            output_schema=tool_def.output_schema
        )

    def remove_tool(self, tool_id: str):
        self.vector_store.delete_tool(tool_id)

    def search_tools(self, query: str, limit: int = 5) -> List[ToolDefinition]:
        results = self.vector_store.search_tools(query, limit)
        return [
            ToolDefinition(
                id=res["id"],
                name=res["tool_name"],
                description=res["description"],
                input_schema=res["input_schema"] if isinstance(res["input_schema"], dict) else eval(res["input_schema"] or "{}"),
                output_schema=res["output_schema"] if isinstance(res["output_schema"], dict) else eval(res["output_schema"] or "{}")
            ) for res in results
        ]
