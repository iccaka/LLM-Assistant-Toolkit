# LLM-Assistant-Toolkit

A versatile toolkit for interacting with a locally hosted Large Language Model (LLM) service using FastAPI. This repository provides two primary functionalities:

- Real-time Chat Interface: Engage in dynamic conversations with the LLM, simulating a sales scenario where the user acts as a salesperson and the model plays a skeptical buyer. The session-based memory ensures context is preserved across interactions.

- Document Cleaning Utility: Clean and reformat local text files using the LLM. The toolkit automatically handles large inputs by chunking them to fit within the model's context window, ensuring efficient processing.

This toolkit leverages the Mistral-7B-Instruct model and includes essential components for seamless integration with FastAPI, making it ideal for developers and researchers looking to harness the power of LLMs for interactive applications and text processing tasks.

## Getting started

### Running locally

1. Clone the **LLM-Assistant-Toolkit** repository in your desired directory:
    ```bash
   $> git clone https://github.com/iccaka/LLM-Assistant-Toolkit.git
   ```
2. Run these commands in order:
    ```bash
   # create a new virtual environment
   $> python3 -m venv venv

   # start the virtual environment
   $> source /venv/bin/activate
   
   # install project dependencies
   $> pip3 install -r requirements.txt
    ```
3. Before starting the project, both ollama and fastapi need to be running:
   ```bash
   # start ollama (models should be pulled beforehand; explanation provided below)
   $> ollama serve
   # (optional, if you get this error message -> 'Error: listen tcp 127.0.0.1:XXXXX: bind: address already in use')
   $> systemctl stop ollama.service
   # start the fastapi entrypoint
   $> fastapi dev app.py
   # finally run main.py
   $> python3 main.py
    ```
   
Tested on python version **3.10.12**

#### LLMs used

1. mistral:7b

In order to pull the models, run:

```bash
   $> ollama pull <model_name>
```

## Dependencies

Please refer to [requirements.txt](requirements.txt) for a list of the python module dependencies.

## Authors

* **Hristo Mitsev** - *Initial work* - [iccaka](https://github.com/iccaka)

See also the list of [contributors](https://github.com/iccaka/LLM-Assistant-Toolkit/graphs/contributors) who participated 
in this project.

## Built With

* [PyCharm](https://www.jetbrains.com/pycharm/) - *The IDE used*

## License

This project is licensed under the MIT License - *see the* 
[LICENSE](https://github.com/iccaka/Metasim-task/blob/master/LICENSE.md) *file for details.*
