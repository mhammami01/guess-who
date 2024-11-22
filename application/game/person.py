from langchain.chains.llm import LLMChain

from application.game.exchange import Exchange
from application.game.observer_logic.observer import Observable


class Person(Observable):
    def __init__(self, name: str, description: str, llm: LLMChain):
        """
        Represents the person the LLM emulates and manages LLM interactions.
        :param name: Name of the person.
        :param description: System prompt describing the person.
        :param llm: LangChain LLM instance.
        """
        super().__init__()
        self.name = name
        self.description = description
        self.llm = llm
        self.exchange_history = Exchange()

    def ask_question(self, question: str) -> str:
        """
        Process a question and return the LLM's response.
        :param question: Question string.
        :return: Response string from the LLM.
        """
        try:
            # Query the LLM using LangChain (could be extended/adapted)
            response = self.llm.run({"question": question, "description": self.description})
        except Exception as e:
            response = f"Error during LLM query: {e}"

        # Save the interaction
        self.exchange_history.add_exchange(question, response)

        # Notify observers if the identity is revealed
        if self.was_identity_revealed(response):
            self.notify_observers(event="identity_revealed", response=response)

        return response

    def was_identity_revealed(self, response: str) -> bool:
        """
        Check if the response inadvertently revealed the identity.
        :param response: LLM's response.
        :return: True if identity clues are present, otherwise False.
        """
        # Basic check for the name in the response (could be extended)
        return self.name.lower() in response.lower()

    def reset_interaction_log(self):
        """
        Reset the interaction log for a new round by clearing the existing history.
        """
        self.exchange_history.clear_exchange_history()

    def get_interaction_log(self) -> list:
        """
        Retrieve the interaction log.
        :return: List of interaction dictionaries.
        """
        return self.exchange_history.get_exchange_history()
