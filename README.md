# AI_assistant_for_farmers
drdo project
prerquisites
1. python
2. langchain
3. ollama - llama3 model
4. chroma db 
5. embedding model: mxbai-embed-large
6. torch



- download ollama then run command  ``ollama pull llama3`` or any model you like to act as the llm model
    also run command ``ollama pull mxbai-embed-large``

- after install ollama
    exit ollama and run command ``ollama serve``\
- create the folder called text_dataset to input all the dataset in pdf format and run the python file by ``python database.py``
- after the textdataset file has all your pdf files run the command ``python app.py`` to use the ui.
username-"farmin2"
password- "123"

