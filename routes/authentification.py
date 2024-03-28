__all__ = ["AuthentificationRoute"]

from fastapi import APIRouter
from utils import UsersDB, SessionDB
from .ResponseModels import AuthInfo
from hashlib import sha256
from jwt import encode as jwtencode

AuthentificationRoute: APIRouter = APIRouter()

@AuthentificationRoute.post("/login")
async def login_route(authInfo: AuthInfo) -> None:

    database: UsersDB = UsersDB()
    session: SessionDB = SessionDB()

    data = await database.get_by_name(authInfo.name)

    hash = sha256()
    hash.update(authInfo.password.encode())

    hashed_password = hash.hexdigest()

    if data[2] == hashed_password:

        session = await session.get_by_userid(data[0])
        
        if not session:

            token = jwtencode({"data": data}, "thisisasecretkey")
            
            try:
                await session.create(token, data[0])
            except:
                return { "error": "something went wrong "}
            
            session = [token]
        
        return {
            "status": "success",
            "token": session[0]
            }
    else:
        return { "status" : "wrong_pass" }


