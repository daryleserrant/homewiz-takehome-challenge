from fastapi import FastAPI
from pydantic import BaseModel
from agent import get_or_create_agent_executor
from contextlib import asynccontextmanager
from db import setup_db
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event to setup the database when the app starts.
    """
    setup_db()
    yield
    # Cleanup can be added here if needed in the future

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    agent_executor = get_or_create_agent_executor(req.session_id)
    result = await agent_executor.ainvoke({"input": req.message})
    return ChatResponse(reply=result["output"])
