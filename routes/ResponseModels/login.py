__all__ = ["AuthInfo", "Session"]

from pydantic import BaseModel

class AuthInfo(BaseModel):

    name: str
    password: str

class Session(BaseModel):

    token: str