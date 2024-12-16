class Score:
    def __init__(self, initial_points: float):
        """
        Represents the score for a round or a team.
        :param initial_points: Starting points for the score (default is 10).
        """
        self.round_score = initial_points
        self.total_score = 0

    def deduct(self, points: float):
        """
        Deduct points from the score.
        :param points: Number of points to deduct.
        """
        self.round_score = max(0.0, self.round_score - points)

    def add(self, points: float):
        """
        Add points to the score.
        :param points: Number of points to add.
        """
        self.round_score += points

    def reset(self, new_points=10):
        """
        Reset the score to a specified value.
        :param new_points: Value to reset the score to.
        """
        self.round_score = new_points

    def get_total_score(self) -> int:
        return self.total_score

    def get_round_score(self) -> int:
        return self.round_score

    def update_total_score(self):
        self.total_score += self.round_score

    def reset_round_score(self):
        self.round_score = 0

    def __str__(self):
        return f"""
        Current total Score: {self.total_score}
        Round Score: {self.round_score}
        """
