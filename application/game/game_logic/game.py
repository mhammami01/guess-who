from typing import List, Dict

from application.game.game_logic.hint_manager import HintManager
from application.game.game_logic.round import Round
from application.game.game_logic.team import Team
from application.game.observer_logic.observer import Observable



class Game:
    def __init__(self, rounds: List[Round], teams: List[Team], max_rounds: int, max_exchange_length:int,  is_running: bool, hint_data_source=None):
        """
        Represents the overall game, including managing teams, rounds, and game flow.
        """
        self.rounds = rounds
        if len(teams) != 2:
            raise ValueError("Number of teams must be exactly two.")
        self.teams = teams
        self.max_exchange_length = max_exchange_length
        self.max_rounds = max_rounds
        self.current_round_index = 0
        self.hint_manager = HintManager()
        self.is_running = is_running

    def start_round(self) -> Round:
        """
        Start a new round with two teams.
        """

        round_id = f"round_{len(self.rounds) + 1}"
        # game_round = Round(round_id, person, team1, team2, self.hint_manager)
        game_round = Round(
            round_id=round_id,
            person=None,
            llm_team=self.teams[1],
            guess_team=self.teams[0],
            hint_manager=self.hint_manager
        )
        self.rounds.append(game_round)
        return game_round

    def add_person_to_current_round(self, person):
        """
        Add a person to the current round.
        :param person: an LLM Person who needs to be guessed.
        """
        current_round = self.get_current_round()
        if current_round.person is not None:
            raise RuntimeError("The current round already has a person assigned.")
        current_round.person = person

    def end_round(self):
        current_round = self.get_current_round()

        # Ensure the round meets the criteria to be finished
        if not current_round.is_round_finished():
            raise RuntimeError("Cannot end a round that is still running.")

        # Mark the round as finished explicitly
        current_round.mark_finished()

        # Collect round summary and update scores
        round_summary = current_round.get_round_summary()
        current_round.update_total_scores_and_reset_round()

        # Switch teams and increment the round index
        self.switch_teams()
        self.increment_round_index()

        # Check if the game is over
        if self.is_game_over():
            self.is_running = False  # Mark the game as no longer running

        return round_summary

    def get_current_round(self):
        if len(self.rounds) == 0:
            raise RuntimeError("The game does not have any rounds, yet.")
        else:
            return self.rounds[-1]

    def get_game_score(self):
        """
        Get the total score for all teams in the game.
        :return: Dictionary with team names as keys and their scores as values.
        """
        return {team.get_name(): team.get_total_score() for team in self.teams}

    # def conduct_bonus_quiz(self):
    #     """
    #     Conducts a bonus quiz for both teams, where teams take turns answering questions.
    #     Correct answers earn 1 point each.
    #     """
    #     quiz_questions = [
    #         {"question": "What is the capital of France?", "answer": "Paris"},
    #         {"question": "What is 5 + 7?", "answer": "12"},
    #         {"question": "What is the color of the sky on a clear day?", "answer": "blue"},
    #         {"question": "Who wrote '1984'?", "answer": "George Orwell"},
    #         {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"}
    #     ]
    #
    #     # Shuffle questions to ensure randomness
    #     import random
    #     random.shuffle(quiz_questions)
    #
    #     total_questions = len(quiz_questions)
    #     question_index = 0
    #     while question_index < total_questions and quiz_questions:
    #         for team in self.teams:
    #             if not quiz_questions:
    #                 break
    #
    #             question = quiz_questions.pop(0)
    #             print(f"\nTeam {team.get_name()}, it's your turn!")
    #             print(f"Question: {question['question']}")
    #             answer = input("Your answer: ").strip().lower()
    #
    #             if answer == question["answer"].lower():
    #                 print("Correct!")
    #                 self.notify_observers("bonus_point_scored", **{"team_name": team.get_name(), "points": 1})
    #             else:
    #                 print(f"Wrong. The correct answer was {question['answer']}.")
    #
    #             question_index += 1
    #
    #             if question_index >= total_questions:
    #                 break

    def is_game_over(self) -> bool:
        """
        Check if the game is over.
        The game ends if:
        - The maximum number of rounds is reached, AND
        - All rounds are marked as finished.
        :return: True if the game is over, otherwise False.
        """
        return len(self.rounds) == self.max_rounds and all(round.finished for round in self.rounds)

    def declare_winner(self):
        """
        Determine the winner based on total scores.
        :return: Name of the winning team or None in case of a tie.
        """
        team1_score = self.teams[0].get_total_score()
        team2_score = self.teams[1].get_total_score()

        if team1_score > team2_score:
            return self.teams[0].get_name()
        elif team2_score > team1_score:
            return self.teams[1].get_name()
        else:
            return None

    def get_llm_team(self):
        return self.teams[0]

    def get_guess_team(self):
        return self.teams[1]

    def switch_teams(self):
        self.teams.reverse()

    def increment_round_index(self):
        """
        Increment the round index to track the current round.
        """
        self.current_round_index += 1
