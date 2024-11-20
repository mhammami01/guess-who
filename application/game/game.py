from typing import List

from application.game.round import Round
from application.game.team import Team


class Game:
    def __init__(self, rounds: List[Round], teams: List[Team]):
        """
        Represents the overall game, including managing teams, rounds, and game flow.
        """
        self.rounds = rounds
        if len(teams) != 2:
            raise ValueError("Number of teams must be exactly two.")
        self.teams = teams

    def start_round(self, person):
        """
        Start a new round with two teams.
        :param person: an LLM Person who needs to be guessed.
        """

        team1, team2 = self.teams[0], self.teams[1]
        game_round = Round(person, team1, team2)
        self.rounds.append(game_round)
        return round

    def get_game_score(self):
        """
        Get the total score for all teams in the game.
        :return: Dictionary with team names as keys and their scores as values.
        """
        return {team.get_name(): team.get_score() for team in self.teams}

    def switch_teams(self):
        self.teams.reverse()

