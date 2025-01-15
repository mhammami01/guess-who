from dotenv import load_dotenv
import os
from application.game.game_logic.game import Game
from application.game.game_logic.llm import LLMInitializer
from application.game.game_logic.person import Person
from application.game.game_logic.quiz_manager import QuizManager
from application.game.game_logic.score import Score
from application.game.game_logic.team import Team


# Step 1a: Setup Person
def setup_person():
    person_name = input("Enter the name of the person to be guessed: ")
    person_description = input("Enter a system message for the person to be guessed: ")

    llm = LLMInitializer.initialise_llm()
    person_llm = Person(name=person_name, description=person_description, llm=llm)
    print(f"Person set up: {person_llm.name}")
    return person_llm


# Step 1b: Setup Teams
def setup_teams():
    print("Setting up the teams...")
    teams = []
    # First team set up
    first_team_name = input("Enter the name for Team A: ")
    first_team_score = Score(float(os.getenv("ROUND_POINTS")))
    teams.append(Team(name=first_team_name, score=first_team_score))

    # Second team set up
    second_team_name = input("Enter the name for Team B: ")
    second_team_score = Score(0)
    teams.append(Team(name=second_team_name, score=second_team_score))

    print(f"Teams set up: {[team.name for team in teams]}")
    return teams


# Step 1c: Setup Game Parameters
def setup_game_parameters(teams):
    print("Configuring game parameters...")
    max_rounds = int(input("Enter the maximum number of rounds: "))
    game_setup = Game(rounds=[], teams=teams, max_rounds=max_rounds, max_exchange_length= float(os.getenv("MAX_EXCHANGE_LENGTH")) ,is_running=True)
    print(f"Game set up with max rounds: {max_rounds}")
    return game_setup


# Step 1: Main Setup Game Method
def setup_game():
    print("Welcome to the game Guess Who!\n")
    teams = setup_teams()
    game_setup = setup_game_parameters(teams)
    print("\n--- Game Setup Complete ---")
    return game_setup


# Step 2: Play Game
def play_game(current_game):

    while not current_game.is_game_over():
        print(f"\n--- Starting Round {current_game.current_round_index + 1} ---")

        # Create a new person for the round using the existing setup_person logic
        print(f"Setting up the person for Round {current_game.current_round_index + 1}...")
        current_person = setup_person()

        # Start a new round
        current_round = current_game.start_round()
        current_game.add_person_to_current_round(current_person)

        # Alternate between teams
        while not current_round.is_round_finished():
            print(f"\n--- Round {current_game.current_round_index + 1}")
            print(f"\n{current_round.guess_team.name}'s turn.")
            print(f"Total Score {current_round.llm_team.name} Team: {current_round.llm_team.get_total_score()}")
            print(f"Round Score {current_round.llm_team.name} Team: {current_round.llm_team.get_round_score()}")
            print(f"Total Score {current_round.guess_team.name} Team: {current_round.guess_team.get_total_score()}")
            print(f"Round Score {current_round.guess_team.name} Team: {current_round.guess_team.get_round_score()}")

            # Get user action
            action = input("Choose an action: (1) Ask a question, (2) Use a hint, (3) Make a guess: ")

            if action == "1":
                # Ask a question
                question = input("Enter your question: ")
                result = current_round.ask_question(question)
                if result["identity_revealed"]:
                    current_round.was_person_revealed = True
                # print(f"Person responds: {response}")

            elif action == "2":
                # Use a hint
                hint = current_round.use_hint()
                print(f"Hint: {hint}")

            elif action == "3":
                # Make a guess
                guess = input("Enter your guess: ")
                if current_round.make_guess(guess):
                    print(f"Correct! The person is {current_person.name}.")
                    current_round.was_person_revealed = True
                else:
                    print(f"Incorrect. The person is not {guess}.")
            else:
                print("Invalid action. Skipping turn.")

        # End round + summary
        round_summary = current_game.end_round()
        print("\n--- End of Round ---")
        print(round_summary)
    print("\n--- Main Game Over ---")

    # Conduct the bonus quiz
    print("\n--- Bonus Quiz Round ---")

    # Initialize QuizManager with the teams
    quiz_manager = QuizManager(current_game.teams)

    # Start the quiz
    quiz_manager.start_quiz()

    while quiz_manager.is_running:
        # Get the current question and team
        question_info = quiz_manager.get_next_question()
        if isinstance(question_info, dict):
            team_name = question_info["team"]
            question = question_info["question"]
            print(f"\nTeam {team_name}, it's your turn!")
            print(f"Question: {question}")

            # Simulate getting an answer (replace input function as needed)
            answer = input("Your answer: ").strip()

            # Submit the answer and get the result
            result = quiz_manager.submit_answer(answer)
            print(result)
        else:
            # If the quiz has ended, break the loop
            print(question_info)
            break

    # Declare the winner
    print("\n--- Game Over ---")
    print("\nFinal Scores:")
    for team in current_game.teams:
        print(f"{team.get_name()} Team: {team.get_total_score()} points")
    winner = current_game.declare_winner()
    if winner:
        print(f"The winner is {winner}!")
    else:
        print("It's a tie!")


if __name__ == "__main__":
    load_dotenv()
    game = setup_game()
    play_game(game)
