from application.game.game_logic.score import Score


class Team:
    def __init__(self, name: str, score: Score):
        self.name = name
        self.score = score

    def update(self, event, **kwargs):
        """
        React to events from the Round, updating scores as needed.
        """
        points = float(kwargs.get("points", 0))
        if event == "hint_used":
            if kwargs.get("deduct_team") == self:
                self.score.deduct(points)
            elif kwargs.get("add_team") == self:
                self.score.add(points)

        elif event == "guess_incorrect":
            if kwargs.get("deduct_team") == self:
                self.score.deduct(points)
            elif kwargs.get("add_team") == self:
                self.score.add(points)

        elif event == "question_asked":
            if kwargs.get("deduct_team") == self:
                self.score.deduct(points)
            elif kwargs.get("add_team") == self:
                self.score.add(points)

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

    def to_dict(self):
        return {
            "name": self.get_name(),
            "total_score": self.get_total_score(),
            "round_score": self.get_round_score(),
        }
