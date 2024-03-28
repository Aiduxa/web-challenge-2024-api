from fastapi import FastAPI
from routes import AuthentificationRoute, AIRoutes

app: FastAPI = FastAPI()

app.include_router(AuthentificationRoute)
app.include_router(AIRoutes)