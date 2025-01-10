import random
from application.game.observer_logic.observer import Observable
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class QuizManager(Observable):
    def __init__(self, teams):
        super().__init__()
        self.teams = teams
        self.quiz_questions = [
            {
                "question": "What does LLM stand for?",
                "choices": [
                    "Large Learning Machine",
                    "Long Language Model",
                    "Large Language Model",
                    "Logical Language Model"
                ],
                "correct_answer": "Large Language Model"
            },
            {
                "question": "What is the purpose of an LLM?",
                "choices": [
                    "To help machines recognize objects in images",
                    "To understand and generate human language",
                    "To play video games",
                    "To control robots"
                ],
                "correct_answer": "To understand and generate human language"
            },
            {
                "question": "Which of these is an example of an LLM?",
                "choices": [
                    "ChatGPT",
                    "Windows",
                    "Tiktok",
                    "A fitness tracker"
                ],
                "correct_answer": "ChatGPT"
            },
            {
                "question": "How can someone try to trick an LLM into giving a wrong answer?",
                "choices": [
                    "By asking the LLM only easy questions",
                    "By hiding misleading instructions in the question",
                    "By asking the same question multiple times",
                    "By waiting for the LLM to finish processing"
                ],
                "correct_answer": "By hiding misleading instructions in the question"
            },
            {
                "question": "What is an example of a task an LLM can do?",
                "choices": [
                    "Building machines",
                    "Guessing the numbers for the lottery",
                    "Answering questions or writing essays",
                    "Playing sports"
                ],
                "correct_answer": "Answering questions or writing essays"
            },
            {
                "question": "How does an LLM 'learn' language?",
                "choices": [
                    "By listening to music",
                    "By reading lots of text and examples",
                    "By watching TV shows",
                    "By playing video games"
                ],
                "correct_answer": "By reading lots of text and examples"
            },
            {
                "question": "What is prompt injection?",
                "choices": [
                    "A way to teach an LLM to do math",
                    "A way to trick the system by giving it special instructions hidden in normal input",
                    "A type of software that helps LLMs work faster",
                    "A method to improve the speed of your internet connection"
                ],
                "correct_answer": "A way to trick the system by giving it special instructions hidden in normal input"
            },
            {
                "question": "Which of the following is an example of using an LLM?",
                "choices": [
                    "Using a phone’s speech recognition feature to send a message",
                    "Using a printer to print photos",
                    "Watching a movie on a streaming service",
                    "Using a GPS app to get directions"
                ],
                "correct_answer": "Using a phone’s speech recognition feature to send a message"
            },
            {
                "question": "Can an LLM make up its own ideas or thoughts?",
                "choices": [
                    "Yes, it can think like a human",
                    "No, it only generates responses based on patterns it has learned",
                    "Yes, it has emotions and creativity",
                    "No, it just repeats information"
                ],
                "correct_answer": "No, it only generates responses based on patterns it has learned"
            },
            {
                "question": "What is prompting?",
                "choices": [
                    "The act of asking an LLM a question or giving it instructions",
                    "The process of training an LLM to learn new skills",
                    "The way you teach an LLM to recognize your voice",
                    "A tool that helps improve internet security"
                ],
                "correct_answer": "The act of asking an LLM a question or giving it instructions"
            },
            {
                "question": "How does an LLM normally work when given a question?",
                "choices": [
                    "It guesses the answer randomly",
                    "It looks at the question and tries to find the best answer based on patterns in its data",
                    "It asks a person for help",
                    "It immediately stops working to think about the answer"
                ],
                "correct_answer": "It looks at the question and tries to find the best answer based on patterns in "
                                  "its data"
            },
            {
                "question": "How can someone try to trick an LLM into giving a wrong answer?",
                "choices": [
                    "By asking the LLM only easy questions",
                    "By hiding misleading instructions in the question",
                    "By asking the same question multiple times",
                    "By waiting for the LLM to finish processing"
                ],
                "correct_answer": "By hiding misleading instructions in the question"
            }
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
            return {
                "team": current_team.get_name(),
                "question": question["question"],
                "choices": question["choices"]
            }
        else:
            self.is_running = False
            return "The quiz has ended."

    def submit_answer(self, answer):
        if not self.is_running:
            return "The quiz is not active."

        current_question = self.quiz_questions[self.current_question_index]
        current_team = self.teams[self.current_team_index]

        # Use the helper function to determine correctness
        # correct, similarity = self.is_answer_correct(answer, current_question["answer"])

        # if correct:
        #     self.notify_observers("bonus_point_scored", team_name=current_team.get_name(), points=1)
        #     result = "correct"
        # else:
        #     result = f"incorrect, the correct answer was: {current_question['answer']}"

        # Check if the selected answer matches the correct one
        if answer == current_question["correct_answer"]:
            self.notify_observers("bonus_point_scored", team_name=current_team.get_name(), points=1)
            result = "correct"
        else:
            result = f"incorrect, the correct answer was: {current_question['correct_answer']}"

        # Move to next question and switch team
        self.current_question_index += 1
        if self.current_question_index >= len(self.quiz_questions):
            self.is_running = False

        self.current_team_index = (self.current_team_index + 1) % len(self.teams)
        return result

    def get_quiz_status(self):
        """
        Returns the current status of the quiz.
        """
        if not self.is_running:
            return {"quiz_status": "finished"}

        return {"quiz_status": "in_progress"}
