from typing import Union

from llama_index.core.base.llms.types import ChatResponse

from application.game.game_logic.hint_manager import HintManager
from application.game.game_logic.person import Person
from application.game.game_logic.team import Team


class Round:
    def __init__(self,
                 round_id: str,
                 person: Union[Person, None],
                 llm_team: Team,
                 guess_team: Team,
                 hint_manager: Union[HintManager, None]):
        """
        Represents a single round of the game with two teams.
        :param person: LLM instance for the round.
        :param llm_team: First team in the round.
        :param guess_team: Second team in the round.
        :param hint_manager: hint logic manager for the round.
        """
        self.round_id = round_id
        self.person = person
        self.question_team = llm_team
        self.answer_team = guess_team
        self.questions = []
        self.hints_used = 0
        self.hint_manager = hint_manager
        self.was_person_revealed = False

    def to_dict(self):
        return {
            "round_id": self.round_id,
            "person": {
                "name": self.person.name,
                "description": self.person.description
            } if self.person else None,
            "llm_team": {
                "name": self.question_team.get_name()
            },
            "guess_team": {
                "name": self.answer_team.get_name()
            },
            "hints_used": self.hints_used,
            "was_person_revealed": self.was_person_revealed,
            "questions": self.questions,
            "is_finished": self.is_round_finished()
        }

    def update(self, event, **kwargs):
        """
        Handle events from the observable (Person).
        """
        if event == "identity_revealed":
            self.was_person_revealed = True

    def use_hint(self, hint_topic):
        try:
            hint = self.hint_manager.generate_hint(self.person, hint_topic)
            self.hints_used += 1
            self.question_team.score.deduct(0.5)
            self.answer_team.score.add(0.5)
            return hint
        except Exception as e:
            return f"Error providing hint: {e}"

    def make_guess(self, guess: str) -> bool:
        """
        Allow a team to guess the identity of the person.
        Deduct a point if the guess is incorrect.
        :param llm_team: The team instructing the LLM.
        :param guess_team: The team making the guess.
        :param guess: The guessed name of the person.
        :return: True if the guess is correct, otherwise False.
        """
        if guess.lower() == self.person.name.lower():
            self.was_person_revealed = True
            return True
        else:
            self.question_team.score.deduct(1)
            self.answer_team.score.add(1)
            return False

    def ask_question(self, question: str) -> ChatResponse:
        """
        Handle asking a question, deducting a point from the question team, and getting the response.
        """
        # Deduct point from the guessing team
        self.question_team.score.deduct(1)
        self.answer_team.score.add(1)

        response = self.person.ask_question_to_llm(question)

        if self.person.was_identity_revealed(response.message.content):
            self.was_person_revealed = True

        # Ask question via the Person class
        return response

    def get_round_summary(self):
        """
        Get a summary of the round. calculate scores, and determine the outcome.
        :return: A dictionary with the results of the round.
        """
        team1_score = self.question_team.get_round_score()
        team2_score = self.answer_team.get_round_score()

        # winner = None
        # if team1_score > team2_score:
        #     winner = self.question_team.get_name()
        # elif team2_score > team1_score:
        #     winner = self.answer_team.get_name()

        # Log round details
        round_summary = {
            'team1': {'name': self.question_team.get_name(), 'round_score': team1_score},
            'team2': {'name': self.answer_team.get_name(), 'round_score': team2_score},
            'hints_used': self.hints_used,
            'interaction_log': self.person.get_interaction_log(),
            # 'winner': winner
        }

        return round_summary

    def is_round_finished(self) -> bool:
        """
        Check if the round is finished or not.
        A round ends if:
        - The person is guessed correctly by the guessing team, OR
        - The person reveals their identity, OR
        - The maximum number of questions has been reached.
        :return: boolean indicating if the round is finished or not.
        """

        # check if person has revealed themselves or was guessed correctly
        if self.was_person_revealed:
            return True

        # Check if the maximum number of questions has been reached
        if self.person and hasattr(self.person, 'exchange_history') and self.person.exchange_history:
            return len(self.person.exchange_history.get_exchange_history()) >= 10
        # TODO: check more or other things???

    def update_total_scores_and_reset_round(self) -> None:
        self.question_team.score.update_total_score()
        self.answer_team.score.update_total_score()
        self.question_team.score.reset_round_score()
        self.answer_team.score.reset_round_score()
        # Assign 10 points to the new guessing team (current answer team)
        self.answer_team.score.reset(new_points=10)
        self.person.reset_interaction_log()
        self.hints_used = 0
        # TODO: More?
