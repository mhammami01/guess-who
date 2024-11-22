from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
import os

from application.game.game_logic.game import Game
from application.game.game_logic.person import Person
from application.game.game_logic.score import Score
from application.game.game_logic.team import Team


def initialise_llm_for_testing():
    # Load environment variables
    load_dotenv()

    # Ensure the API key is set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment.")

    # Initialize the OpenAI model
    model = OpenAI(
        model_name="gpt-4o-mini",  # Specify the OpenAI model
        openai_api_key=openai_api_key  # Pass the API key
    )
    return model


# Step 1a: Setup Person
def setup_person():
    print("Setting up the person for the game...")
    person_name = input("Enter the name of the person to be guessed: ")
    person_description = input("Enter a system message for the person to be guessed: ")
    llm = initialise_llm_for_testing()
    person_llm = Person(name=person_name, description=person_description, llm=llm)
    print(f"Person set up: {person_llm.name}")
    return person_llm


# Step 1b: Setup Teams
def setup_teams():
    print("Setting up the teams...")
    team_count = 2  # Enforce two teams as per your design
    teams = []
    # First team is always "guessers"
    guesser_name = input("Enter the name for the Guessers team: ")
    guesser_score = Score(10)
    teams.append(Team(name=guesser_name, score=guesser_score))

    # Second team is always "agents"
    agent_name = input("Enter the name for the Agents team: ")
    agent_score = Score(0)
    teams.append(Team(name=agent_name, score=agent_score))

    print(f"Teams set up: {[team.name for team in teams]}")
    return teams


# Step 1c: Setup Game Parameters
def setup_game_parameters(teams):
    print("Configuring game parameters...")
    max_rounds = int(input("Enter the maximum number of rounds: "))
    hint_data_source = None  # Adjust with real hint source
    game_setup = Game(rounds=[], teams=teams, max_rounds=max_rounds, hint_data_source=hint_data_source)
    print(f"Game set up with max rounds: {max_rounds}")
    return game_setup


# Step 1: Main Setup Game Method
def setup_game():
    print("Welcome to the game Guess Who!\n")
    person_setup = setup_person()
    teams = setup_teams()
    game_setup = setup_game_parameters(teams)
    print("\n--- Game Setup Complete ---")
    return game_setup, person_setup


if __name__ == "__main__":
    game, person = setup_game()
