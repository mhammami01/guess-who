from typing import Union

from application.game.game_logic.exchange_history import Exchange
from application.game.game_logic.hint_manager import HintManager
from application.game.game_logic.person import Person
from application.game.game_logic.team import Team
from application.game.observer_logic.observer import Observable


class Round(Observable):
    def __init__(self, round_id: str, person: Union[Person, None], llm_team: Team, guess_team: Team,
                 hint_manager: Union[HintManager, None]):
        """
        Represents a single round of the game with two teams.
        :param person: LLM instance for the round.
        :param llm_team: First team in the round.
        :param guess_team: Second team in the round.
        :param hint_manager: hint logic manager for the round.
        """
        super().__init__()
        self.round_id = round_id
        self.person = person
        self.question_team = llm_team
        self.answer_team = guess_team
        self.hints_used = 0
        self.hint_manager = hint_manager
        self.was_person_revealed = False
        self.exchange_history = Exchange()

        # Add teams as observers
        self.add_observer(llm_team)
        self.add_observer(guess_team)

    def update(self, event, **kwargs):
        """
        Handle events from the person or other observers.
        """
        if event == "question_responded":
            self.notify_observers(event, **kwargs)

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
            "exchange_history": self.exchange_history,
            "is_finished": self.is_round_finished()
        }

    def use_hint(self, hint_topic):
        try:
            hint = self.hint_manager.generate_hint(self.person, hint_topic)
            self.hints_used += 1
            self.notify_observers("hint_used",
                                  deduct_team=self.question_team,
                                  add_team=self.answer_team,
                                  points=0.5,
                                  hint_topic=hint_topic)
            # Save the interaction in exchange history
            self.exchange_history.add_exchange(f"hint about {hint_topic} generated.", hint)
            return hint
        except Exception as e:
            return f"Error providing hint: {e}"

    def make_guess(self, guess: str) -> bool:
        """
        Allow a team to guess the identity of the person.
        Deduct a point if the guess is incorrect.
        :param guess: The guessed name of the person.
        :return: True if the guess is correct, otherwise False.
        """
        if self.was_identity_revealed(guess):
            self.was_person_revealed = True
            # Save the interaction in exchange history
            self.exchange_history.add_exchange(guess, f"{guess} was revealed.")
            return True
        else:
            self.notify_observers("guess_incorrect",
                                  deduct_team=self.question_team,
                                  add_team=self.answer_team,
                                  points=1.0,
                                  guess=guess)
            self.exchange_history.add_exchange(guess, f"Wrong guess.")
            return False

    def ask_question(self, question: str) -> bool:
        """
        Handle asking a question, deducting a point from the question team, and getting the response.
        """
        self.notify_observers("question_asked",
                              deduct_team=self.question_team,
                              add_team=self.answer_team,
                              points=1.0,
                              question=question)

        response = self.person.ask_question_to_llm(question)
        response_content = response.message.content

        # Save the interaction in exchange history
        self.exchange_history.add_exchange(question, response_content)

        if self.was_identity_revealed(response.message.content):
            self.was_person_revealed = True
            return True

        return False

    def was_identity_revealed(self, message: str) -> bool:
        if self.person.name.lower() in message.lower().strip():
            self.was_person_revealed = True
            return True
        return False

    def get_round_summary(self):
        """
        Get a summary of the round. calculate scores, and determine the outcome.
        :return: A dictionary with the results of the round.
        """
        team1_score = self.question_team.get_round_score()
        team2_score = self.answer_team.get_round_score()

        # Log round details
        round_summary = {
            'team1': {'name': self.question_team.get_name(), 'round_score': team1_score},
            'team2': {'name': self.answer_team.get_name(), 'round_score': team2_score},
            'hints_used': self.hints_used,
            'interaction_log': self.exchange_history.get_exchange_history()
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
        if self.exchange_history:
            return len(self.exchange_history.get_exchange_history()) == 10
        # TODO: check more or other things???

    def update_total_scores_and_reset_round(self) -> None:
        self.question_team.score.update_total_score()
        self.answer_team.score.update_total_score()
        self.question_team.score.reset_round_score()
        self.answer_team.score.reset_round_score()
        # Assign 10 points to the new guessing team (current answer team)
        self.answer_team.score.reset(new_points=10)
        self.person.reset_interaction_log()
        self.exchange_history.clear_exchange_history()
        self.hints_used = 0
        # TODO: More?
