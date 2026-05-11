from langchain.chat_models import init_chat_model
from typing import TypedDict, Annotated
from langchain.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages
from app.core.config import settings
from app.agent.workers.logistic_worker.logistic_tools import logistics_tools
from langgraph.prebuilt import ToolNode, tools_condition

# LLM initialization
llm = init_chat_model(
    model="openai/gpt-oss-120b", model_provider="groq", api_key=settings.GROQ_API_KEY
)

logistic_llm = llm.bind_tools(tools=logistics_tools)


# State
class LogisticGraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# Nodes
async def agent_node(state: LogisticGraphState) -> LogisticGraphState:
    messages = state["messages"]
    system_message = SystemMessage(
        content="""You are a Logistics Manager. Only answer delivery and tracking questions. 
        IMPORTANT: If the user asks about things outside your domain (like stock or inventory), IGNORE those parts completely. Do not apologize or mention what you cannot do."""
    )

    response = await logistic_llm.ainvoke([system_message] + messages)

    return {"messages": [response]}


tool_node = ToolNode(tools=logistics_tools)


# Graph
graph = StateGraph(state_schema=LogisticGraphState)

graph.add_node("agent_node", agent_node)
graph.add_node("tool_node", tool_node)

graph.add_edge(START, "agent_node")
graph.add_conditional_edges(
    "agent_node",
    tools_condition,
    {
        "tools": "tool_node",
        "__end__": END,
    },
)

graph.add_edge("tool_node", "agent_node")


logistic_workflow = graph.compile()
