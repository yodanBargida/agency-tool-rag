from fastapi import FastAPI, HTTPException
from src.models.tool import ToolDefinition, AgentRequest
from src.agents.orchestrator import Orchestrator
from src.database.vector_store import VectorStore
from src.tools.manager import ToolManager
import uuid
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Tools RAG Orchestration Agent")
orchestrator = Orchestrator()
tool_manager = ToolManager(VectorStore())

@app.post("/agent/query")
async def query_agent(request: AgentRequest):
    session_id = request.session_id or str(uuid.uuid4())
    result = await orchestrator.run(request.query, session_id)
    return result

@app.post("/tools/")
async def create_tool(tool: ToolDefinition):
    tool_manager.create_tool(tool)
    return {"message": f"Tool {tool.name} registered successfully"}

@app.delete("/tools/{tool_id}")
async def delete_tool(tool_id: str):
    tool_manager.remove_tool(tool_id)
    return {"message": f"Tool {tool_id} removed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
