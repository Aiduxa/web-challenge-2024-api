__all__ = ["AIRoutes"]

from fastapi import APIRouter, Response, status
from .ResponseModels import Session, Chat
from utils import ChatsDB, SessionDB, UsersDB
from json import loads, dumps
from requests import request
from requests import Response as WEBResponse
from asyncio import sleep

AIRoutes: APIRouter = APIRouter()
_AIAPIROUTE: str = "http://172.16.50.58:5000/api"

async def validate_session(token):
    sessiondb: SessionDB = SessionDB()
    usersdb: UsersDB = UsersDB()

    session_data = await sessiondb.get(token)

    if not session_data: 
        return Response(
            content={"error":"Session not found"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    _user_id = session_data[1]
    
    user = await usersdb.get(_user_id)

    if not user:
        return Response(
            content={"error":"User not found"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return user

async def getAnswer(prompt: str):

    resp: WEBResponse = request(
        method="POST",
        headers = {"Authorization": "Bearer 39d615008caf42f5a157151e6ab132eb"},
        url=f"{_AIAPIROUTE}/text/generate",
        json={"prompt": prompt}
    )
    job_data = resp.json()

    job: WEBResponse = request(
        method="GET",
        headers = {"Authorization": "Bearer 39d615008caf42f5a157151e6ab132eb"},
        url=f"{_AIAPIROUTE}/text/status/{job_data["job_id"]}"
    )
    while job.json()["job_running"]:
        job = request(
        method="GET",
        headers = {"Authorization": "Bearer 39d615008caf42f5a157151e6ab132eb"},
        url=f"{_AIAPIROUTE}/text/status/{job_data["job_id"]}",
    )
        await sleep(1)
    
    return job.json(), job_data

@AIRoutes.get("/chats")
async def get_chats(session: Session):
    response = await validate_session(session.token)

    if isinstance(response, Response):
        return response
    
    chatsdb: ChatsDB = ChatsDB()
    
    chats: list = await chatsdb.get_user_chats(response[0])

    return chats if len(chats) > 0 else []



@AIRoutes.post("/new")
async def new_chat(session: Session):
    response = await validate_session(session.token)

    if isinstance(response, Response):
        return response
    
    chatsdb: ChatsDB = ChatsDB()

    chat_id = await chatsdb.new_chat(response[0])

    answer, job_data = await getAnswer("Who are you? Greet me.")

    messages = {
        job_data["job_id"]: {
            "prompt": "",
            "answer": answer["job_result"]
        }
    }

    await chatsdb.update(chat_id, "messages", dumps(messages))

    return {
        "chat_id": chat_id
    }



@AIRoutes.put("/chat/{chat_id}/reply")
async def chat_reply(chat_id: int, chat_data: Chat):
    response = await validate_session(chat_data.token)

    if isinstance(response, Response):
        return response
    
    chatsdb: ChatsDB = ChatsDB()

    chat = await chatsdb.get_chat(chat_id)

    if not chat:
        return Response(
            content='{"error": "No chat found"}',
            status_code = status.HTTP_404_NOT_FOUND
        )
    
    if str(chat[3]) == "":
        answer, job_data = await getAnswer(f"Summarize this prompt in a few words: \"{chat_data.prompt}\"")
        await chatsdb.update(chat[0], "name", answer["job_result"])
    
    answer, job_data = await getAnswer(chat_data.prompt)

    messages = loads(chat[1]) if chat[1] else {}

    messages.update({
        job_data["job_id"]: {
            "prompt": chat_data.prompt,
            "answer": answer["job_result"]
        }
    })

    await chatsdb.update(chat[0], "messages", dumps(messages))

    return {job_data["job_id"]: {
            "prompt": chat_data.prompt,
            "answer": answer["job_result"]
        }}


@AIRoutes.get("/chat/{chat_id}")
async def get_chat(chat_id: int, session: Session):
    response = await validate_session(session.token)

    if isinstance(response, Response):
        return response
    
    chatsdb: ChatsDB = ChatsDB()

    chat = await chatsdb.get_chat(chat_id)

    if not chat:
        return Response(
            {"error": "No chat found"},
            status_code=404
        )
    
    return chat

@AIRoutes.delete("/chat/{chat_id}/delete")
async def chat_delete(chat_id: int, session: Session):
    print(chat_id)

    response = await validate_session(session.token)

    if isinstance(response, Response):
        return response
    
    chatsdb: ChatsDB = ChatsDB()

    await chatsdb.chat_delete(chat_id)
    
    return {"status": "success"}
