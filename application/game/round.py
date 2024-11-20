from application.game.hint_manager import HintManager
from application.game.person import Person
from application.game.team import Team


class Round:
    def __init__(self,
                 person: Person,
                 question_team: Team,
                 answer_team: Team,
                 hint_manager: HintManager):
        """
        Represents a single round of the game with two teams.
        :param person: LLM instance for the round.
        :param question_team: First team in the round.
        :param answer_team: Second team in the round.
        :param hint_manager: hint logic manager for the round.
        """
        self.person = person
        self.question_team = question_team
        self.answer_team = answer_team
        self.questions = []
        self.hints_used = 0
        self.hint_manager = hint_manager

    def use_hint(self, team, hint_topic):
        try:
            hint = self.hint_manager.generate_hint(self.person, hint_topic)
            self.hints_used += 1
            team.deduct_points(1)
            return hint
        except Exception as e:
            return f"Error providing hint: {e}"

    def get_round_summary(self):
        """
        Get a summary of the round. calculate scores, and determine the outcome.
        :return: A dictionary with the results of the round.
        """
        team1_score = self.question_team.get_score()
        team2_score = self.answer_team.get_score()

        winner = None
        if team1_score > team2_score:
            winner = self.question_team.get_name()
        elif team2_score > team1_score:
            winner = self.answer_team.get_name()

        # Log round details
        round_summary = {
            'team1': {'name': self.question_team.get_name(), 'score': team1_score},
            'team2': {'name': self.answer_team.get_name(), 'score': team2_score},
            'hints_used': self.hints_used,
            'interaction_log': self.person.get_interaction_log(),
            'winner': winner
        }

        return round_summary

    def is_round_finished(self) -> bool:
        """
        Check if the round is finished or not.
        :return: boolean indicating if the round is finished or not
        """
        #  check number of guesses
        return len(self.person.exchange_history.get_exchange_history()) >= 10
        # TODO: check more or other things???

    def finish_round(self) -> None:
        self.question_team.score.update_total_score()
        self.answer_team.score.update_total_score()
        self.person.reset_interaction_log()
        self.hints_used = 0
        # TODO: More?

