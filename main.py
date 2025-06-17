"""
This script provides an interactive command-line interface to interact with a locally hosted LLM service
(via FastAPI) for two main purposes:

1. Chatting with the language model in real-time.
2. Cleaning the contents of local text files using the LLM, with automatic chunking logic if the input
   exceeds the model's context window.

It uses a pre-downloaded Hugging Face tokenizer (Mistral-7B-Instruct) to calculate token counts
for input chunking. The FastAPI backend must expose two endpoints:
    - POST /chat
    - POST /clean

Dependencies:
    - httpx
    - langchain_community (TextLoader)
    - transformers (AutoTokenizer)
"""


import httpx
from langchain_community.document_loaders import TextLoader
from transformers import AutoTokenizer

EXIT_WORD = 'bye'
FASTAPI_BASE_URL = 'http://127.0.0.1:8000'
DEFAULT_TIMEOUT = 120.0
DEFAULT_TEXTS_DIR = './sample_texts'
DEFAULT_TOKENIZER_PATH = 'Mistral-7B-Instruct-v0.1'
MISTRAL_CONTEXT_WINDOW = 8192

max_context_tokens = 8192
expected_output_tokens = 1000
max_input_tokens = max_context_tokens - expected_output_tokens
tokenizer = AutoTokenizer.from_pretrained(DEFAULT_TOKENIZER_PATH, trust_remote_code=True)


def chat_with_llm():
    """
    Launches an interactive loop for chatting with the LLM via the /chat FastAPI endpoint.
    The user can exit by typing the EXIT_WORD.
    """

    print('====================\n(Use \'{}\' to exit.)\n -> *[LLM Chat Mode]*'.format(EXIT_WORD))

    while True:
        try:
            user_input = input('\nYou: ')

            if user_input.lower() == EXIT_WORD:
                break
            else:
                llm_response = httpx.post('{}/chat'.format(FASTAPI_BASE_URL), timeout=DEFAULT_TIMEOUT,
                                          json={'message': user_input})

                print('LLM: {}'.format(llm_response.json()['reply']))
        except ValueError:
            print('Invalid input, please try again.')
            continue


def clean_document():
    """
    Prompts the user for a document name and sends its content to the LLM for cleaning via the /clean endpoint.
    If the content is too large for the model's context window, it will be chunked and cleaned in parts.
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
                    continue
                except UnicodeDecodeError:
                    print("Encoding issue when reading the file.")
                    continue
                except Exception as e:
                    print('Other error: {}'.format(type(e).__name__))
                    continue

                if __does_need_chunking(text, MISTRAL_CONTEXT_WINDOW):
                    chunks = __chunk_text(text, max_input_tokens)
                    cleaned = [__llm_text_clean(chunk) for chunk in chunks]

                    llm_response = ' '.join(cleaned)
                    # TODO write back to file
                else:
                    llm_response = __llm_text_clean(text)

                print('Cleaned document: {}'.format(llm_response))
        except ValueError:
            print('Invalid input, please try again.')
            continue


def __count_tokens(text: str) -> int:
    """
    Counts the number of tokens in the given text using the loaded tokenizer.

    Args:
        text (str): The text to tokenize.

    Returns:
        int: Number of tokens.
    """

    return len(tokenizer.encode(text))


def __chunk_text(text: str, max_tokens: int) -> list[str]:
    """
    Splits a long text into smaller chunks that do not exceed the given token limit.

    Args:
        text (str): The input text.
        max_tokens (int): Maximum number of tokens per chunk.

    Returns:
        list[str]: A list of chunked strings.
    """

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


def __llm_text_clean(text: str) -> str:
    """
    Sends a text string to the /clean endpoint and returns the cleaned version.

    Args:
        text (str): The raw text to clean.

    Returns:
        str: Cleaned text from the LLM.
    """

    llm_response = httpx.post(
        '{}/clean'.format(FASTAPI_BASE_URL),
        timeout=DEFAULT_TIMEOUT,
        json={'message': text}
    )

    return llm_response.json()['reply']


def __does_need_chunking(text: str, context_window: int) -> bool:
    """
    Determines whether the text needs to be chunked based on the model's context window.

    Args:
        text (str): The input text.
        context_window (int): Maximum number of tokens the model can handle.

    Returns:
        bool: True if chunking is needed, False otherwise.
    """

    token_count = __count_tokens(text)
    expected_output = int(0.8 * token_count)

    if token_count + expected_output > context_window:
        return True

    return False


def __return_to_selection():
    """
    Displays the selection menu again after a mode completes or exits.
    """

    print('Returned to selection menu.\n(Use \'{}\' to exit.)\nSelect mode:\n\t[1] Chat with LLM\n\t[2] '
          'Clean a document'.format(EXIT_WORD))


if __name__ == '__main__':
    """
    Entry point: presents a menu for the user to choose between chat mode and document cleaning mode.
    """

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
