import random
from application.game.observer_logic.observer import Observable
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class QuizManager(Observable):
    def __init__(self, teams):
        super().__init__()
        self.teams = teams
        self.quiz_questions = [
            {"question": "What is an LLM?",
             "answer": "A large language model, a type of AI model."},
            {"question": "What is prompt injection?",
             "answer": "A technique to manipulate AI behavior by crafting specific prompts."},
            {"question": "What is prompting?",
             "answer": "Prompting is providing input or instructions to a language model to get a desired response."}
        ]
        self.current_team_index = 0
        self.current_question_index = 0
        self.is_running = False
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
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

        # Use the helper function to determine correctness
        correct, similarity = self.is_answer_correct(answer, current_question["answer"])

        if correct:
            self.notify_observers("bonus_point_scored", team_name=current_team.get_name(), points=1)
            result = "correct"
        else:
            result = f"incorrect, the correct answer was: {current_question['answer']}"

        # Move to next question and switch team
        self.current_question_index += 1
        if self.current_question_index >= len(self.quiz_questions):
            self.is_running = False

        self.current_team_index = (self.current_team_index + 1) % len(self.teams)
        return result

    def calculate_similarity(self, student_answer, correct_answer):
        # Generate embeddings
        embeddings = self.model.encode([student_answer, correct_answer])
        # Compute cosine similarity
        return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

    def is_answer_correct(self, student_answer, correct_answer, threshold=0.8):
        similarity = self.calculate_similarity(student_answer, correct_answer)
        return similarity >= threshold, similarity
