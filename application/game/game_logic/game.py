from typing import List, Dict

from application.game.game_logic.hint_manager import HintManager
from application.game.game_logic.round import Round
from application.game.game_logic.team import Team


class Game:
    def __init__(self, rounds: List[Round], teams: List[Team], max_rounds: int, is_running: bool, hint_data_source=None):
        """
        Represents the overall game, including managing teams, rounds, and game flow.
        """
        self.rounds = rounds
        if len(teams) != 2:
            raise ValueError("Number of teams must be exactly two.")
        self.teams = teams
        self.max_rounds = max_rounds
        self.current_round_index = 0
        self.hint_manager = HintManager()
        self.is_running = is_running

    def start_round(self) -> Round:
        """
        Start a new round with two teams.
        :param person: an LLM Person who needs to be guessed.
        """

        round_id = f"round_{len(self.rounds) + 1}"
        # game_round = Round(round_id, person, team1, team2, self.hint_manager)
        game_round = Round(
            round_id=round_id,
            person=None,
            llm_team=self.teams[0],
            guess_team=self.teams[1],
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
        round_summary = self.get_current_round().get_round_summary()
        self.get_current_round().update_total_scores_and_reset_round()
        self.switch_teams()
        self.increment_round_index()
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

    def is_game_over(self) -> bool:
        """
        Check if the game is over.
        :return: True if the game is over, otherwise False.
        """
        return len(self.rounds) == self.max_rounds and self.get_current_round().is_round_finished()

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
