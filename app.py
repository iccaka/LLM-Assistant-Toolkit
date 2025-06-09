import uuid
import logging
import httpx
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

app = FastAPI()
# OLLAMA_MODEL_NAME = 'qwen3:4b'
OLLAMA_MODEL_NAME = 'qwen:1.8b'
OLLAMA_BASE_URL = 'http://localhost:11434/api/chat'
chat_sessions = {}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post('/clean')
async def clean(request: Request):
    pass

@app.post('/chat')
async def chat(request: Request):
    client_payload = await request.json()
    session_id = client_payload.get('session_id')
    user_message = client_payload.get('message', '')

    logger.info('Session ID: {}'.format(session_id))
    logger.info('User message: {}'.format(user_message))

    if not session_id or session_id not in chat_sessions:
        session_id = str(uuid.uuid4())
        chat_sessions[session_id] = []

    chat_sessions[session_id].append({'role': 'user', 'content': user_message})
    ollama_config = {
        'model': OLLAMA_MODEL_NAME,
        'messages': chat_sessions[session_id],
        'stream': False
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OLLAMA_BASE_URL, json=ollama_config)
        response.raise_for_status()
        llm_response = response.json()

    assistant_message = llm_response['message']['content']
    chat_sessions[session_id].append({'role': 'assistant', 'content': assistant_message})

    return JSONResponse(content={'reply': assistant_message, 'session_id': session_id})