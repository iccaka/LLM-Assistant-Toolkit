import logging
import httpx
from langchain_community.document_loaders import DirectoryLoader

EXIT_WORD = 'bye'
FASTAPI_BASE_URL = 'http://127.0.0.1:8000'
DEFAULT_TIMEOUT = 120.0

def chat_with_llm():
    print('====================\n(Use \'{}\' to exit.)\n -> *[LLM Chat Mode]*'.format(EXIT_WORD))

    while True:
        try:
            user_input = input('\nYou: ')

            if user_input.lower() == EXIT_WORD:
                break
            else:
                llm_response = httpx.post(FASTAPI_BASE_URL + '/chat', timeout=DEFAULT_TIMEOUT, json={'message': user_input})

                print('LLM: {}'.format(llm_response.json()['reply']))
        except ValueError:
            print('Invalid input, please try again.')
            continue


def clean_document():
    print('====================\n(Use \'{}\' to exit.)\n -> *[Document Clean Mode]*'.format(EXIT_WORD))
    while True:
        try:
            user_input = input('\nDocument\'s name: ')

            if user_input.lower() == EXIT_WORD:
                break
            else:
                loader = DirectoryLoader("./sample_texts/{}".format(user_input), glob="*.txt")
                print(len(loader.load()))
                # TODO request
                llm_response = 'test'
                print('Cleaned document: {}'.format(llm_response))
        except ValueError:
            print('Invalid input, please try again.')
            continue


def __return_to_selection():
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
