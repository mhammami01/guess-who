## Environment setup
1. create a new conda environment:
```
conda create -n ai-guardians python=3.12
conda activate ai-guardians
```
2. install required libraries:
```  
pip install -r requirements. txt
```
## Start the App
```
python3 app.py
```

html pages can be found in templates folder

## Install and set up Ollama
For running Phi-3.5 (or any other open source LLM models), you need to set up Ollama. 

1. Installation
Open a terminal and install Ollama via the following command:
``` 
curl -fsSL https://ollama.com/install.sh | sh
```

2. Set up Ollama server
Run an Ollama server (sometimes the server is started automatically and this step can be skipped):
```
ollama serve
```

3. Pull Phi-3.5 model
Open a terminal and type in the following command:
```
ollama pull phi3
```

## Set necessary parameters in .env file
Create a .env file at the root level of the application.

It should have the following structure:
```
## API keys
OPENAI_API_KEY="insert_key_here"

# LLM choice (openai or phi)
LLM_PROVIDER="llm_name"

## In-game parameters
ROUND_POINTS = 10
MAX_EXCHANGE_LENGTH = 10
POINTS_FOR_QUESTION=1.0
POINTS_FOR_HINT=0.5
POINTS_FOR_GUESS=1.0
```

The in-game parameters are set to default values and can be adapted.
The OpenAI API key is optional and only needs to be inserted if you want to run the game using a GPT model. 

