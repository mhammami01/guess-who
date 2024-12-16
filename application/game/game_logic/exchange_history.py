from llama_index.core.base.llms.types import ChatResponse


class Exchange:
    def __init__(self):
        """
        Initializes an empty exchange history.
        """
        self.exchange_history = []

    def add_exchange(self, question: str, response: str):
        """
        Add a question and response pair to the exchange.
        :param question: The question asked.
        :param response: The response received from the LLM.
        """
        self.exchange_history.append({"question": question, "response": response})

    def get_exchange_history(self) -> list:
        """
        Retrieve the full exchange history.
        :return: List of exchange dictionaries.
        """
        return self.exchange_history

    def clear_exchange_history(self):
        """
        Clears all logged interactions.
        """
        self.exchange_history = []

    def to_dict(self) -> dict:
        """
        Converts the exchange to a dictionary for JSON serialization.
        """
        return {"exchange_history": self.exchange_history}

    def __str__(self):
        """
        String representation for printing exchange.
        """
        return "\n".join([f"Q: {entry['question']} -> A: {entry['response']}" for entry in self.exchange_history])
