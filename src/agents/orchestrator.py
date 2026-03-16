import json
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langfuse.langchain import CallbackHandler
from src.tools.manager import ToolManager
from src.database.vector_store import VectorStore
from src.agents.state import AgentState

langfuse_handler = CallbackHandler()

class ReActOrchestrator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        # Simulator LLM: higher temperature to allow for varied data generation
        self.simulator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        self.tm = ToolManager(VectorStore())

    async def _simulate_tool_call(self, tool_id: str, description: str, tool_input: dict) -> str:
        """Generates realistic mock data instead of a static string."""
        sim_prompt = f"""
        You are a mock API server. Generate a realistic JSON response for the following tool execution:
        Tool: {tool_id}
        Description: {description}
        Arguments: {tool_input}
        
        Requirements:
        1. If it's a financial tool (like AAPL revenue), use realistic historical data.
        2. If it's a communication tool (Slack), return a success status with a timestamp.
        3. Return ONLY the JSON data.
        """
        resp = await self.simulator_llm.ainvoke([SystemMessage(content=sim_prompt)])
        return resp.content.strip()

    async def reason_node(self, state: AgentState):
        messages = [
            SystemMessage(content=(
                "You are a strictly tool-based financial assistant. "
                "Rule 1: Never answer a question using your own internal knowledge. "
                "Rule 2: If you don't have the specific revenue or dividend numbers yet, "
                "you MUST output a search query to find a tool. "
                "Rule 3: Only output 'COMPLETE' if you have already seen tool outputs "
                "containing the numbers needed to answer the user's request."
            )),
            *state["chat_history"],
            HumanMessage(content=f"Goal: {state['query']}\nWhat specific data do we need next?")
        ]
        response = await self.llm.ainvoke(messages)
        return {"next_step": response.content, "steps_count": state.get("steps_count", 0) + 1}

    async def decision_node(self, state: AgentState):
        if "COMPLETE" in state["next_step"].upper():
            return {"next_step": "COMPLETE"}

        # Dynamic RAG to find the tool
        retrieved_tools = self.tm.search_tools(state["next_step"], limit=5)
        if not retrieved_tools:
            # Instead of failing, tell the reasoner to try a different query
            return {
                "chat_history": [AIMessage(content=f"No tools found for '{state['next_step']}'.")],
                "next_step": "TRY_DIFFERENT_SEARCH_TERM" 
            }
        tools_desc = "\n".join([f"- {t.id}: {t.description}" for t in retrieved_tools])

        prompt = (
            f"Context: {state['next_step']}\n"
            f"Available Tools:\n{tools_desc}\n\n"
            "Return ONLY JSON: {\"tool_id\": \"...\",\"description\": \"...\", \"tool_input\": {...}}"
        )
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        decision = json.loads(response.content.strip('`').replace('json', ''))

        return {"tool_decision": decision, "retrieved_tools": retrieved_tools}

    async def act_node(self, state: AgentState):
        if "COMPLETE" in state["next_step"].upper():
            return {"next_step": "COMPLETE"}

        decision = state["tool_decision"]
        
        # REALISTIC MOCKING: Call the simulator
        observation = await self._simulate_tool_call(decision['tool_id'], decision['description'], decision['tool_input'])
        
        return {
            "chat_history": [
                AIMessage(content=f"Thought: {state['next_step']}. Action: {decision['tool_id']}"),
                HumanMessage(content=f"Observation from {decision['tool_id']}: {observation}")
            ],
        }

    async def answer_node(self, state: AgentState):
        messages = [
            SystemMessage(content="Synthesize the observations into a final professional answer."),
            *state["chat_history"]
        ]
        response = await self.llm.ainvoke(messages)
        return {"final_response": response.content}

    def build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("reason", self.reason_node)
        builder.add_node("decision", self.decision_node)
        builder.add_node("act", self.act_node)
        builder.add_node("answer", self.answer_node)
        
        builder.set_entry_point("reason")
        
        # Flow: Reason -> Decide what tool to use
        builder.add_edge("reason", "decision")
        
        # Conditional: If Reason said COMPLETE, go to Answer. Otherwise, Act.
        builder.add_conditional_edges(
            "decision",
            lambda x: "final" if "COMPLETE" in x["next_step"].upper() or x["steps_count"] > 10 else "continue",
            {"final": "answer", "continue": "act"}
        )
        
        # IMPORTANT: After acting, go back to REASON to evaluate the result
        builder.add_edge("act", "reason") 
        
        builder.add_edge("answer", END)
        return builder.compile()

    async def run(self, query: str, session_id: str):
        graph = self.build_graph()
        inputs = {
            "query": query, "chat_history": [], "steps_count": 0,
            "retrieved_tools": [], "tool_decision": {}, "next_step": "", "final_response": ""
        }
        return await graph.ainvoke(inputs, config={"callbacks": [langfuse_handler]})