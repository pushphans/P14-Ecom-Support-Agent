from fastapi import FastAPI, APIRouter
from app.agent.supervisor.supervisor import agent_workflow
from langchain.messages import AIMessage, HumanMessage
from app.models import AgentQuery, AgentResponse

router = APIRouter()


@router.post("/agent")
async def query_agent(query: AgentQuery):
    try:
        messages = [HumanMessage(content=query.user_input)]
        result = await agent_workflow.ainvoke({"messages": messages})

        # 🌟 NAYA LOGIC: Sirf AI ke final messages uthane hain
        final_responses = []
        
        for msg in reversed(result["messages"]):
            if isinstance(msg, HumanMessage):
                break
            
            # SIRF AIMessage uthao (ToolMessage ignore karo), aur check karo usme text ho
            if isinstance(msg, AIMessage) and msg.content:
                final_responses.append(msg.content)
                
        final_responses.reverse()
        combined_response = "\n\n".join(final_responses)

        return AgentResponse(response=combined_response)

    except Exception as e:
        return AgentResponse(response="", error=str(e))


@router.get("/health")
async def health_check():
    return {"status": "ok"}
