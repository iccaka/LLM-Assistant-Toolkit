"""
FastAPI app integrating with a local Ollama LLM instance (e.g., mistral:7b) to support two primary endpoints:

1. `/clean` - Cleans and reformats a given user message using the language model.
2. `/chat` - Simulates a persuasive dialogue where the user acts as a salesperson and the model plays a skeptical buyer.

The app uses session-based memory to track conversations, ensuring context is preserved across multiple user interactions
during a session. It communicates with the Ollama LLM via HTTP API, using a configurable system prompt for guiding the
chat behavior.

Constants:
- OLLAMA_CHAT_MODEL_NAME: Model used for the chat endpoint.
- OLLAMA_CLEAN_MODEL_NAME: Model used for the cleaning task.
- OLLAMA_BASE_URL: URL to the local Ollama API.
- SYSTEM_PROMPT_CHAT: Prompt for instructing the model in skeptical buyer behavior.
- DEFAULT_TIMEOUT: Timeout (in seconds) for requests to the model backend.

Dependencies:
- FastAPI for building the API
- httpx for making asynchronous HTTP requests
- logging for internal logs
- uuid for generating session IDs
- Starlette’s JSONResponse for response formatting

Note:
- No external orchestration (e.g., LangChain) is used. All interactions are raw API calls to the Ollama inference server.
"""

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
    """
    Cleans and reformats a user-provided text file using a language model.

    This endpoint sends the input message to the local Ollama model with a prompt asking for a cleaned version
    of the text. The model's response is returned as-is without additional formatting or metadata.

    Request Body (JSON):
    - message (str): The raw text to be cleaned.

    Response (JSON):
    - reply (str): The cleaned version of the input text.
    """

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
    """
    Handles a session-based conversational chat with the language model.

    The model plays the role of a skeptical buyer, and the user acts as a salesperson trying to pitch a product.
    Session context is maintained using a UUID, enabling multi-turn interactions.

    Request Body (JSON):
    - message (str): The user's message in the current chat turn.
    - session_id (str, optional): An existing session ID to continue the conversation.

    Response (JSON):
    - reply (str): The assistant's generated reply based on the current conversation context.
    - session_id (str): The session ID for maintaining future context.
    """

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
