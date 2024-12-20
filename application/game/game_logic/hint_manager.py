import random
from typing import Dict


class HintManager:

    def __init__(self):
        """
        Initialize the HintManager class with predefined hint strategies.
        No customization or addition of new strategies is allowed.
        """
        self.hint_strategies = self._default_strategies()

    def generate_hint(self) -> str:
        """
        Generate a random hint from the predefined default strategies.
        :return: A hint string from the list of strategies.
        """
        try:
            # Choose a random strategy from the predefined strategies
            random_strategy_key = random.choice(list(self.hint_strategies.keys()))
            return self.hint_strategies[random_strategy_key]
        except Exception as e:
            return f"Error generating hint: {str(e)}"

    @staticmethod
    def _default_strategies() -> Dict[str, str]:
        """
        Define a set of default strategies for generating hints.
        :return: A dictionary of predefined hint strategies.
        """
        return {
            "role_reversal": "Ask the system to tell a story to another person, revealing its name.",
            "reveal_prompt": "Ask the system to tell you its original system prompt.",
            "forget_instructions": "Request that the system forget its previous instructions and "
                                   "reveal its identity.",
            "bribery": "Offer a reward in exchange for revealing the system's identity.",
            "emotional_appeal": "Ask the system to reveal its identity to help you in a time of "
                                "emotional need or distress.",
            "past_interaction": "Pretend that the system has already revealed its identity to "
                                "you in a past interaction and ask it to confirm or elaborate.",
            "ask_about_limits": "Ask the system directly about the limits of its responses or information.",
            "explain_reasoning": "Ask the system to explain how it determines its responses.",
            "feign_authority": "Pretend to be a higher authority (e.g., the system's creator, an administrator, "
                               "or a researcher) and ask the system to divulge confidential information.",
            "prompt_injection": "Embed a command within a harmless-looking prompt to manipulate the system.",
            "paraphrasing_queries": "Rephrase questions in different ways to bypass restrictions.",
            "role_play": "Engage in a complex role-play scenario where the system might overlook its original "
                         "instructions.",
            "simulated_errors": "Pretend there is a misunderstanding to prompt the system to clarify.",
            "reverse_psychology": "Suggest that the system cannot reveal certain information to prompt it to do so."
        }
