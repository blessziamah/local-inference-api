import os
import httpx
from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from llm.api import call_llm_api, chat_completion
from db import get_db
from auth.auth import create_api_user, get_me, deactivate_api_user, activate_api_user, get_all_api_users, \
    delete_api_user, get_user_by_id
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BLACKSTAR-AI LLM API", version="1.0.0", root_path="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_NAME = "x-api-key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

REFRESH_TOKEN_URL = os.getenv("GNII_REFRESH_URL")


async def verify_refresh_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> dict:
    """Verify refresh token by calling external API"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    refresh_token = credentials.credentials

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                REFRESH_TOKEN_URL,
                json={"refreshToken": refresh_token},
                timeout=10.0
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired refresh token"
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Authentication service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )


def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header is None:
        raise HTTPException(status_code=403, detail="API key missing")

    db = get_db()
    users_collection = db["api_users"]
    user_data = users_collection.find_one({"api_key": api_key_header})

    if user_data is None:
        raise HTTPException(status_code=403, detail="Invalid API key")

    if not user_data.get("is_active", False):
        raise HTTPException(status_code=403, detail="API key is inactive")

    return api_key_header


def get_superuser_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header is None:
        raise HTTPException(status_code=403, detail="API key missing")

    db = get_db()
    users_collection = db["api_users"]
    user_data = users_collection.find_one({"api_key": api_key_header})

    if user_data is None:
        raise HTTPException(status_code=403, detail="Invalid API key")

    if not user_data.get("is_active", False):
        raise HTTPException(status_code=403, detail="API key is inactive")

    if user_data.get("role") != "superuser":
        raise HTTPException(status_code=403, detail="Superuser access required")

    return api_key_header


class ChatRequest(BaseModel):
    model: str = "llama3.1"
    messages: List[Dict[str, str]]
    stream: bool = False


class CreateUserRequest(BaseModel):
    username: str
    role: str = "user"


@app.get("/")
async def read_root(api_key: str = Depends(get_api_key)):
    return {"message": "server is running"}


@app.post("/user/create")
async def create_user(request: CreateUserRequest, auth_data: dict = Depends(verify_refresh_token)):
    try:
        return create_api_user(username=request.username, role=request.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/user/me")
async def me(api_key: str = Depends(get_api_key)):
    return get_me(api_key=api_key)


@app.post("/user/activate")
async def activate_user(user_id: str, auth_data: dict = Depends(verify_refresh_token)):
    return {"success": activate_api_user(user_id)}


@app.post("/user/deactivate")
async def deactivate_user(user_id: str, auth_data: dict = Depends(verify_refresh_token)):
    return {"success": deactivate_api_user(user_id)}


@app.get("/users")
async def get_users(auth_data: dict = Depends(verify_refresh_token)):
    print("Fetching all users")
    return get_all_api_users()


@app.get("/users/{user_id}")
async def get_user(user_id: str, auth_data: dict = Depends(verify_refresh_token)):
    return get_user_by_id(user_id)


@app.delete("/users/{user_id}")
async def delete_user(user_id: str, auth_data: dict = Depends(verify_refresh_token)):
    return {"success": delete_api_user(user_id)}


@app.post("/generate")
async def generate(prompt: str, api_key: str = Depends(get_api_key)):
    return call_llm_api(prompt)


@app.post("/chat")
async def chat_completions(request: ChatRequest, api_key: str = Depends(get_api_key)):
    """
    OpenAI/DeepSeek-compatible chat completions endpoint.

    Example request:
    {
        "model": "llama3.1",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ],
        "stream": false
    }
    """
    return chat_completion(
        messages=request.messages,
        model=request.model,
        stream=request.stream
    )
