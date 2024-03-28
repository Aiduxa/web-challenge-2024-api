from fastapi import FastAPI
from routes import AuthentificationRoute

app: FastAPI = FastAPI()

app.include_router(AuthentificationRoute)