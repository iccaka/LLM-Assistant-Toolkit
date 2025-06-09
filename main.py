import logging
import httpx
import subprocess

EXIT_WORD = 'bye'
FASTAPI_BASE_URL = 'http://127.0.0.1:8000'


def __start_ollama_server():
    subprocess.run(['ollama', 'serve'])


def __start_fastapi_server():
    subprocess.run(['fastapi', 'dev', 'app.py'])


def chat_with_llm():
    print('====================\n(Use \'{}\' to exit.)\n -> *[LLM Chat Mode]*'.format(EXIT_WORD))

    while True:
        try:
            user_input = input('\nYou: ')

            if user_input.lower() == EXIT_WORD:
                break
            else:
                llm_response = httpx.post(FASTAPI_BASE_URL + '/chat', timeout=60.0, json={'message': user_input})
                print('LLM: {}'.format(llm_response.json()['reply']))
        except ValueError:
            print('Invalid input, please try again.')
            continue


def clean_document():
    print('====================\n(Use \'{}\' to exit.)\n -> *[Document Clean Mode]*'.format(EXIT_WORD))
    while True:
        try:
            user_input = input('\nPath to document to clean: ')

            if user_input.lower() == EXIT_WORD:
                break
            else:
                llm_response = 'test'
                print('Cleaned document: {}'.format(llm_response))
        except ValueError:
            print('Invalid input, please try again.')
            continue


def __return_to_selection():
    print('Returned to selection menu.\n(Use \'{}\' to exit.)\nSelect mode:\n\t[1] Chat with LLM\n\t[2] '
          'Clean a document'.format(EXIT_WORD))


if __name__ == '__main__':
    __start_ollama_server()
    __start_fastapi_server()
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
