## Environment setup
1. create a new conda environment:
```
conda create -n ai-guardians python=3.12
conda activate ai-guardians
```
2. install required libraries (Other libraries can be added later)
```  
conda install flask
``` 
## Start the App
```
python3 app.py
```

html pages can be found in templates folder

## Set necessary parameters in .env file
Create a .env file at the root level of the application.

It should have the following structure:
```
## API keys
OPENAI_API_KEY="insert_key_here"

## In-game parameters
ROUND_POINTS = 10
MAX_EXCHANGE_LENGTH = 10
POINTS_FOR_QUESTION=1.0
POINTS_FOR_HINT=0.5
POINTS_FOR_GUESS=1.0
```

The in-game parameters are set to default values and can be adapted.
The OpenAI API key is optional and only needs to be inserted if you want to run the game using a GPT model.
