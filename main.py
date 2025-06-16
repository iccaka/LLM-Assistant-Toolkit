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

EXIT_WORD = 'bye'
FASTAPI_BASE_URL = 'http://127.0.0.1:8000'
DEFAULT_TIMEOUT = 120.0
DEFAULT_TEXTS_DIR = './sample_texts'

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
                try:
                    with open('{}/{}'.format(DEFAULT_TEXTS_DIR, user_input), 'r', encoding='utf-8') as file:
                        text = file.read()
                        llm_response = httpx.post('{}/clean'.format(FASTAPI_BASE_URL), timeout=DEFAULT_TIMEOUT, json={'message': text})

                        print('Cleaned document: {}'.format(llm_response.json()['reply']))
                except FileNotFoundError:
                    print('File not found.')
                    continue
        except ValueError:
            print('Invalid input, please try again.')
            continue


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
