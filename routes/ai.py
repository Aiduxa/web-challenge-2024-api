from fastapi import APIRouter
from .ResponseModels import Session

AI: APIRouter = APIRouter()

@AI.get("/chats")
async def get_chats(session: Session):
    ...

@AI.post("/new")
async def new_chat(session: Session):
    ...

@AI.put("/chat/{chat_id}/reply")
async def chat_reply(chat_id: int, session: Session):
    ...

@AI.get("/chat/{chat_id}")
async def get_chat(chat_id: int, session: Session):
    ...

@AI.delete("/chat/{chat_id}/delete")
async def chat_delete(chat_id: int):
    ...