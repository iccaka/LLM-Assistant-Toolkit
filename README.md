# Metasim-task

*A task written for the company Metasim.*

## Getting started

### Running locally

1. Clone the **Metasim-task** repository in your desired directory:
    ```bash
   $> git clone https://github.com/iccaka/Metasim-task.git
   ```
2. Run these commands in order:
    ```bash
   # create a new virtual environment
   $> python3 -m venv venv

   # start the virtual environment
   $> source /venv/bin/activate
   
   # install project dependencies
   $> pip3 install -r requirements.txt
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
   
#### LLMs used

1. qwen:1.8b

In order to pull the models, run:

```bash
   $> ollama pull <model_name>
```

## Dependencies

Please refer to [requirements.txt](requirements.txt) for a list of the python module dependencies.

## Authors

* **Hristo Mitsev** - *Initial work* - [iccaka](https://github.com/iccaka)

See also the list of [contributors]() who participated 
in this project.

## Built With

* [PyCharm](https://www.jetbrains.com/pycharm/) - *The IDE used*

## License

This project is licensed under the MIT License - *see the* 
[LICENSE](https://github.com/iccaka/Metasim-task/blob/master/LICENSE.md) *file for details.*
