from application.game.score import Score


class Team:
    def __init__(self, name: str, score: Score):
        self.name = name
        self.score = score

    def get_score(self):
        """
        Return the current score of the team.
        :return: Current score of the team.
        """
        return self.score.get_total_score()

    def get_name(self):
        """
        Return the team's name.
        :return: Team name.
        """
        return self.name
