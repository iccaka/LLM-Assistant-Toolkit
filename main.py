"""
Command-line client for interacting with a FastAPI server hosting an Ollama-based language model.

Provides two modes:
1. Chat Mode: Chat with the LLM in real-time through the `/chat` endpoint.
2. Document Clean Mode: Reads a local text file and sends it to the `/clean` endpoint to get a cleaned version.

Constants:
- EXIT_WORD: Keyword to exit any mode or return to the main menu.
- FASTAPI_BASE_URL: Base URL of the FastAPI server.
- DEFAULT_TIMEOUT: Timeout in seconds for HTTP requests.
- DEFAULT_TEXTS_DIR: Directory containing local text documents for cleaning.

Requires:
- The FastAPI app to be running locally and accessible at the configured URL.
"""

import logging
import httpx
from langchain_community.document_loaders import TextLoader
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer


EXIT_WORD = 'bye'
FASTAPI_BASE_URL = 'http://127.0.0.1:8000'
DEFAULT_TIMEOUT = 120.0
DEFAULT_TEXTS_DIR = './sample_texts'
DEFAULT_TOKENIZER = 'mistralai/Mistral-7B-Instruct-v0.1'
DEFAULT_MISTRAL_CONTEXT_WINDOW = 8192

max_context_tokens = 8192
expected_output_tokens = 1000
max_input_tokens = max_context_tokens - expected_output_tokens
tokenizer = MistralTokenizer.v1()

def chat_with_llm():
    """
    Interactive chat loop with the LLM via the FastAPI `/chat` endpoint.

    - Prompts the user for input.
    - Sends each message to the server and prints the model's reply.
    - Maintains no session state on the client side.
    - Typing the EXIT_WORD ends the loop.
    """

    print('====================\n(Use \'{}\' to exit.)\n -> *[LLM Chat Mode]*'.format(EXIT_WORD))

    while True:
        try:
            user_input = input('\nYou: ')

            if user_input.lower() == EXIT_WORD:
                break
            else:
                llm_response = httpx.post('{}/chat'.format(FASTAPI_BASE_URL), timeout=DEFAULT_TIMEOUT, json={'message': user_input})

                print('LLM: {}'.format(llm_response.json()['reply']))
        except ValueError:
            print('Invalid input, please try again.')
            continue


def clean_document():
    """
    Document cleaning loop using the FastAPI `/clean` endpoint.

    - Prompts the user for the filename of a text document in DEFAULT_TEXTS_DIR.
    - Reads the file and sends its content to the server for cleaning.
    - Prints the cleaned output from the model.
    - Typing the EXIT_WORD ends the loop.
    - Handles file not found and invalid input errors gracefully.
    """

    print('====================\n(Use \'{}\' to exit.)\n -> *[Document Clean Mode]*'.format(EXIT_WORD))

    while True:
        try:
            user_input = input('\nDocument\'s name: ')

            if user_input.lower() == EXIT_WORD:
                break
            else:
                text = ''
                try:
                    loader = TextLoader('{}/{}'.format(DEFAULT_TEXTS_DIR, user_input))
                    docs = loader.load()
                    text = docs[0].page_content
                except FileNotFoundError:
                    print("File not found.")
                except UnicodeDecodeError:
                    print("Encoding issue when reading the file.")
                except Exception as e:
                    print('Other error: {}'.format(type(e).__name__))

                if __does_need_chunking(text, DEFAULT_MISTRAL_CONTEXT_WINDOW):
                    chunks = __chunk_text(text, max_input_tokens)
                    cleaned = [__llm_text_clean(chunk) for chunk in chunks]

                    llm_response = ' '.join(cleaned)
                else:
                    llm_response = __llm_text_clean(text)

                print('Cleaned document: {}'.format(llm_response))
        except ValueError:
            print('Invalid input, please try again.')
            continue


def __count_tokens(text):
    return len(tokenizer.encode(text))


def __chunk_text(text, max_tokens):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        token_len = __count_tokens(' '.join(current_chunk))

        if token_len > max_tokens:
            current_chunk.pop()
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def __llm_text_clean(text):
    llm_response =  httpx.post(
        '{}/clean'.format(FASTAPI_BASE_URL),
        timeout=DEFAULT_TIMEOUT,
        json={'message': text}
    )

    return llm_response.json()['reply']


def __does_need_chunking(text, context_window):
    token_count = len(tokenizer.encode_chat_completion(text))
    expected_output = int(0.8 * token_count)

    if token_count + expected_output > context_window:
        return True

    return False


def __return_to_selection():
    """
    Prints the main menu after completing a task, reminding the user of available options.
    """

    print('Returned to selection menu.\n(Use \'{}\' to exit.)\nSelect mode:\n\t[1] Chat with LLM\n\t[2] '
          'Clean a document'.format(EXIT_WORD))


if __name__ == '__main__':
    logging.getLogger('httpx').disabled = True

    print('(Use \'{}\' to exit.)\nSelect mode:\n\t[1] Chat with LLM\n\t[2] Clean a document'.format(EXIT_WORD))

    while True:
        try:
            user_input = input('\nYou: '.format(EXIT_WORD))

            if user_input == '1':
                chat_with_llm()
                __return_to_selection()
            elif user_input == '2':
                clean_document()
                __return_to_selection()
            elif user_input.lower() == EXIT_WORD:
                break
            else:
                print('Invalid input. Try again.')
        except ValueError:
            print('Invalid input, please try again.')
            continue
