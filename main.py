import os

from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict

from llm.api import call_llm_api, chat_completion

app = FastAPI()

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "x-api-key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=401, detail="Unauthorized")

class ChatRequest(BaseModel):
    model: str = "llama3.1"
    messages: List[Dict[str, str]]
    stream: bool = False


@app.get("/")
async def read_root(api_key: str = Depends(get_api_key)):
    return {"message": "server is running"}


@app.post("/generate")
async def generate(prompt: str):
    return call_llm_api(prompt)


@app.post("/chat")
async def chat_completions(request: ChatRequest):
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
