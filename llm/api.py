import json
import time
import requests
from typing import List, Dict
import os


def parse_response(response_text: str) -> str:
    """
    Parses the response from the LLM API and returns the relevant content.

    Args:
        response_text (dict): The response dictionary from the LLM API.

    Returns:
        str: The parsed content from the response.
    """
    if isinstance(response_text, bytes):
        response_text = response_text.decode("utf-8")
    response = ""
    for line in response_text.strip().split("\n"):
        if line:
            try:
                data = json.loads(line)
                if "response" in data:
                    response += data["response"]
            except json.JSONDecodeError:
                continue
    return response


def call_llm_api(prompt, model="llama3.1", base_url=None) -> str:
    """
    Calls the LLM API with the given prompt and model, and returns the parsed response.
    """
    if base_url is None:
        base_url = os.getenv("LLM_URL", "http://0.0.0.0:11434")
    url = f"{base_url}/api/generate"

    config = {
        "model": f"{model}",
        "prompt": prompt,
        "stream": True,
    }

    response = requests.post(url, json=config)
    return parse_response(response.content)


def _extract_streaming_content(response) -> str:
    """Extract content from Ollama streaming response."""
    content = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                if "message" in data and "content" in data["message"]:
                    content += data["message"]["content"]
                elif "response" in data:
                    content += data["response"]
            except json.JSONDecodeError:
                continue
    return content


def _extract_non_streaming_content(response) -> str:
    """Extract content from Ollama non-streaming response."""
    data = response.json()
    if "message" in data and "content" in data["message"]:
        return data["message"]["content"]
    elif "response" in data:
        return data["response"]
    return ""


def _build_chat_response(response_text: str, messages: List[Dict[str, str]], model: str) -> Dict:
    """Build OpenAI-compatible chat completion response."""
    prompt_tokens = sum(len(msg.get("content", "").split()) for msg in messages)
    completion_tokens = len(response_text.split())

    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
    }


def chat_completion(
        messages: List[Dict[str, str]],
        model: str = "llama3.1",
        base_url: str = None,
        stream: bool = False
) -> Dict:
    """
    Calls the LLM API with chat completion format.

    """
    if base_url is None:
        base_url = os.getenv("LLM_URL", "http://0.0.0.0:11434")
    url = f"{base_url}/api/chat"

    config = {
        "model": model,
        "messages": messages,
        "stream": stream
    }

    response = requests.post(url, json=config, stream=stream)

    if stream:
        response_text = _extract_streaming_content(response)
    else:
        response_text = _extract_non_streaming_content(response)

    return _build_chat_response(response_text, messages, model)
