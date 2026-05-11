from langchain.chat_models import init_chat_model
from typing import TypedDict, Annotated
from langchain.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages
from app.core.config import settings
from langgraph.types import Send
from pydantic import BaseModel, Field
from app.agent.workers.inventory_worker.inventory_graph import inventory_workflow
from app.agent.workers.logistic_worker.logistic_graph import logistic_workflow

# LLM initialization
llm = init_chat_model(
    model="openai/gpt-oss-120b", model_provider="groq", api_key=settings.GROQ_API_KEY
)


# structured output
class NextWorkerOutputStructure(BaseModel):
    next_workers: list[str] = Field(
        description="List of workers to assign tasks to. Options: 'inventory_worker', 'logistics_worker', or 'FINISH'."
    )


# structured llm
supervisor_llm = llm.with_structured_output(schema=NextWorkerOutputStructure)


# State
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    next_workers: list[str]


# Nodes
async def supervisor_node(state: AgentState) -> AgentState:
    messages = state["messages"]

    system_msg = SystemMessage(
        content="""You are an E-Commerce Support Supervisor.
Your workers are:
- 'inventory_worker': Checks stock availability for products.
- 'logistics_worker': Tracks order delivery status.

RULES FOR ROUTING:
1. INDEPENDENT TASKS: If tasks don't depend on each other (e.g., checking stock AND tracking an order), output ALL required workers to run parallelly.
2. DEPENDENT TASKS: If task B needs the result of task A, ONLY output the worker for task A first. Wait for its result in the history before calling task B.
3. EXIT STRATEGY (CRITICAL): If the user's request is fully resolved, OR if the workers cannot solve the issue because they lack the tools, you must add "FINISH" to your next_workers list. 

IMPORTANT: NEVER output raw text. Always return your response using the provided structured output schema!"""
    )

    response: NextWorkerOutputStructure = await supervisor_llm.ainvoke(
        [system_msg] + messages
    )

    return {"next_workers": response.next_workers}


async def parallel_router(state: AgentState):
    workers = state.get("next_workers", [])

    if "FINISH" in workers:
        return END

    elif len(workers) == 0:
        return END

    else:
        tasks = []
        for worker in workers:
            tasks.append(Send(node=worker, arg={"messages": state["messages"]}))

        return tasks


# Graph
graph = StateGraph(state_schema=AgentState)
graph.add_node("supervisor_node", supervisor_node)
graph.add_node("inventory_worker", inventory_workflow)
graph.add_node("logistics_worker", logistic_workflow)


graph.add_edge(START, "supervisor_node")
graph.add_conditional_edges(
    "supervisor_node",
    parallel_router,
    [
        "inventory_worker",
        "logistics_worker",
        END,
    ],
)
graph.add_edge("inventory_worker", "supervisor_node")
graph.add_edge("logistics_worker", "supervisor_node")


agent_workflow = graph.compile()
