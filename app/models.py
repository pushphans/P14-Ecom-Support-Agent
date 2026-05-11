from pydantic import BaseModel

class AgentQuery(BaseModel):
    user_input: str

class AgentResponse(BaseModel):
    response: str
    error: str | None = None