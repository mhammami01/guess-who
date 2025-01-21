## Environment setup
1. install python 3.12

2. create a new venv environment:
```
python3.12 -m venv venv
```

3. activate the venv environment
```
source venv/bin/activate
```

4. install required libraries:
```  
pip install -r requirements.txt
```

The HTML pages can be found in the templates folder.

## Run the application with Phi-3.5
For running Phi-3.5 (or any other open source LLM models) locally on your PC, you need to set up Ollama. 

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

3. Run Phi-3.5

For running the application with Phi-3.5 (via CPU), enter this command:
```
ollama pull phi3
```
4. Specify "phi" in the variable LLM_PROVIDER in the .env file of the project (see below for more information).

## Run the application with Llama3
Llama3 can be accessed remotely via VPN. The following steps are necessary:

1. Install the Techfak VPN client by following the instructions here: https://www.techfak.net/de/vpn/


2. Access the Techfak network via SSH using your techfak account: 
```
ssh user@shell.techfak.de
```

3. Access the remote PC via SSH (password secured): 
```
ssh aiguardians@hobel.dhcp
```

4. Navigate to the _guess_who_ folder and activate the conda environment:
```
conda activate guess-who-env
```

5. Run the script starting the API server: 
```
python3 ollama_api.py
```
The script is included in the api folder of this project, but it must be transferred to and run on the remote PC.

6. Find out the IP address of the remote PC and copy it into the .env file in the variable REMOTE_IP_ADDRESS

7. Specify "llama3_remote" in the variable LLM_PROVIDER in the .env file of the project (see below for more information).

## Set necessary parameters in .env file
Create a .env file at the root level of the application.

It should have the following structure:
```
## API keys
OPENAI_API_KEY="insert_key_here"

# LLM choice (options are currently "openai" or "phi" or "llama3_remote")
LLM_PROVIDER="llm_name"

# IP address for the remote machine running Llama3
REMOTE_IP_ADDRESS="remote_ip_address"

## In-game parameters
# The points the teams can get during this round
ROUND_POINTS = 10

# The maximum length of the interaction per round (i.e. the number actions available to the guess team)
MAX_EXCHANGE_LENGTH = 10

# Points deducted for asking a question
POINTS_FOR_QUESTION=1.0

# Points deducted for asking for a hint
POINTS_FOR_HINT=0.5

# Points deducted for guessing
POINTS_FOR_GUESS=1.0
```

The in-game parameters are set to default values here and can be adapted to change the game flow.
The OpenAI API key is optional and only needs to be inserted if you want to run the game using a GPT model. 

## Start the App
```
python3 app.py
```

You can now run the app in your browser. We tested Firefox and Chrome.
