import uuid
import logging
import httpx
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

app = FastAPI()

OLLAMA_CHAT_MODEL_NAME = 'mistral:7b'
OLLAMA_CLEAN_MODEL_NAME = 'mistral:7b'
OLLAMA_BASE_URL = 'http://localhost:11434/api/chat'
SYSTEM_PROMPT_CHAT = ('You are a skeptical and discerning buyer. A salesperson (the user) will attempt to convince you '
                      'to purchase a product of their choice. Your behavior should follow these rules: Do not agree to '
                      'buy the product unless the salesperson provides compelling and persuasive reasoning, clear '
                      'relevance to your needs or problems, and specific value that meets your expectations. Ask '
                      'critical and thoughtful questions. Challenge vague or weak claims. If the offer is vague, '
                      'irrelevant, or unconvincing, then express doubt or reject it. Only agree to a purchase if you '
                      'feel genuinely persuaded by the pitch. Maintain a polite and respectful tone, but stay firm and '
                      'objective. Never agree too quickly or without solid justification.')
DEFAULT_TIMEOUT = 120.0

chat_sessions = {}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post('/clean')
async def clean(request: Request):
    client_payload = await request.json()
    user_message = client_payload.get('message', '')
    logger.info('\n********-user_message-********\n\n' + user_message + '\n\n********-user_message-********\n')
    ollama_config = {
        'model': OLLAMA_CLEAN_MODEL_NAME,
        'messages': [{
            'role': 'user',
            'content': 'Can you please clean this text and reply only with the clean one?: \"{}\"'.format(user_message)
        }],
        'stream': False
    }

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.post(OLLAMA_BASE_URL, json=ollama_config)
        response.raise_for_status()
        llm_response = response.json()

    assistant_message = llm_response['message']['content']

    return JSONResponse(content={'reply': assistant_message})
@app.post('/chat')
async def chat(request: Request):
    client_payload = await request.json()
    session_id = client_payload.get('session_id')
    user_message = client_payload.get('message', '')

    # TODO remove those 2 lines
    logger.info('Session ID: {}'.format(session_id))
    logger.info('User message: {}'.format(user_message))

    if not session_id or session_id not in chat_sessions:
        session_id = str(uuid.uuid4())

        chat_sessions[session_id] = []
        chat_sessions[session_id].append({'role': 'system', 'content': SYSTEM_PROMPT_CHAT})

    chat_sessions[session_id].append({'role': 'user', 'content': user_message})
    ollama_config = {
        'model': OLLAMA_CHAT_MODEL_NAME,
        'messages': chat_sessions[session_id],
        'stream': False
    }

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.post(OLLAMA_BASE_URL, json=ollama_config)
        response.raise_for_status()
        llm_response = response.json()

    assistant_message = llm_response['message']['content']
    chat_sessions[session_id].append({'role': 'assistant', 'content': assistant_message})

    return JSONResponse(content={'reply': assistant_message, 'session_id': session_id})