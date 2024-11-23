from typing import List

from application.game.game_logic.hint_manager import HintManager
from application.game.game_logic.round import Round
from application.game.game_logic.team import Team


class Game:
    def __init__(self, rounds: List[Round], teams: List[Team], max_rounds: int, hint_data_source=None):
        """
        Represents the overall game, including managing teams, rounds, and game flow.
        """
        self.rounds = rounds
        if len(teams) != 2:
            raise ValueError("Number of teams must be exactly two.")
        self.teams = teams
        self.max_rounds = max_rounds
        self.current_round_index = 0
        self.hint_manager = HintManager(hint_data_source)

    def start_round(self, person):
        """
        Start a new round with two teams.
        :param person: an LLM Person who needs to be guessed.
        """

        team1, team2 = self.teams[0], self.teams[1]
        game_round = Round(person, team1, team2, self.hint_manager)
        self.rounds.append(game_round)
        return round

    def get_game_score(self):
        """
        Get the total score for all teams in the game.
        :return: Dictionary with team names as keys and their scores as values.
        """
        return {team.get_name(): team.get_total_score() for team in self.teams}

    def check_game_over(self) -> bool:
        """
        Check if the game is over.
        :return: True if the game is over, otherwise False.
        """
        return self.current_round_index >= self.max_rounds

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

    def switch_teams(self):
        self.teams.reverse()

    def increment_round_index(self):
        """
        Increment the round index to track the current round.
        """
        self.current_round_index += 1
