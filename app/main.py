from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.routers.v1 import users as v1_users_routes
from app.routers import token as token_routes


# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Application Initialization
app = FastAPI()

version = "v1.0"

@app.get("/")
async def main():
    return RedirectResponse(url="/docs")

# CORS Configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "POST", "PUT"],
    allow_headers=["*"],
)

app.include_router(
    token_routes.router,
    prefix="/token",
    tags=["Auth"]
)

app.include_router(
    v1_users_routes.router,
    prefix="/api/v1/users",
    tags=[version, "users"]
)
