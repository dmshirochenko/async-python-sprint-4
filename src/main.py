from fastapi import FastAPI
from src.api.v1 import url_routes, users_routes


app = FastAPI()

app.include_router(url_routes.router)
app.include_router(users_routes.router)
