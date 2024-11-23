from application.game.game_logic.score import Score


class Team:
    def __init__(self, name: str, score: Score):
        self.name = name
        self.score = score

    def get_total_score(self):
        """
        Return the current total score of the team.
        :return: Current total score of the team.
        """
        return self.score.get_total_score()

    def get_round_score(self):
        """
        Return the current score of the team for the round.
        :return: Current round score of the team.
        """
        return self.score.get_round_score()

    def get_name(self):
        """
        Return the team's name.
        :return: Team name.
        """
        return self.name
