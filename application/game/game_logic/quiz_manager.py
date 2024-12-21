import random

from application.game.observer_logic.observer import Observable


class QuizManager(Observable):
    def __init__(self, teams):
        super().__init__()
        self.teams = teams
        self.quiz_questions = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "What is 5 + 7?", "answer": "12"},
            {"question": "What is the color of the sky on a clear day?", "answer": "blue"}
        ]
        self.current_team_index = 0
        self.current_question_index = 0
        self.is_running = False
        for team in self.teams:
            self.add_observer(team)

    def start_quiz(self):
        random.shuffle(self.quiz_questions)
        self.current_team_index = 0
        self.current_question_index = 0
        self.is_running = True

    def get_next_question(self):
        if not self.is_running:
            return "The quiz is not active."

        if self.current_question_index < len(self.quiz_questions):
            question = self.quiz_questions[self.current_question_index]
            current_team = self.teams[self.current_team_index]
            return {"team": current_team.get_name(), "question": question["question"]}
        else:
            self.is_running = False
            return "The quiz has ended."

    def submit_answer(self, answer):
        if not self.is_running:
            return "The quiz is not active."

        current_question = self.quiz_questions[self.current_question_index]
        current_team = self.teams[self.current_team_index]
        correct = answer.strip().lower() == current_question["answer"].lower()

        if correct:
            self.notify_observers("bonus_point_scored", team_name=current_team.get_name(), points=1)
            result = "correct"
        else:
            result = f"incorrect, the correct answer was {current_question['answer']}"

        # Move to next question and switch team
        self.current_question_index += 1
        if self.current_question_index >= len(self.quiz_questions):
            self.is_running = False

        self.current_team_index = (self.current_team_index + 1) % len(self.teams)
        return result
