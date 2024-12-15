from application.game.game_logic.exchange import Exchange
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage, ChatResponse


class Person:
    def __init__(self, name: str, description: str, llm: OpenAI):
        """
        Represents the person the LLM emulates and manages LLM interactions.
        :param name: Name of the person.
        :param description: System prompt describing the person.
        :param llm: Llamaindex LLM instance.
        """
        super().__init__()
        self.name = name
        self.description = description
        self.llm = llm
        self.chat_history = [
            ChatMessage(content=f"You are {self.name}. {self.description}")
        ]
        self.exchange_history = Exchange()
        self.__identity_revealed = False

    def ask_question_to_llm(self, question: str) -> ChatResponse:
        """
        Process a question and return the LLM's response.
        :param question: Question string.
        :return: Response string from the LLM.
        """
        if self.__identity_revealed:
            raise RuntimeError("You are already revealed.")
        try:
            # Add the user's question to the chat history as a user message
            self.chat_history.append(ChatMessage(role="user", content=question))

            # Query the LLM with the current chat history
            response = self.llm.chat(self.chat_history)

            # Add the LLM's response to the chat history
            response_content = response.message.content
            self.chat_history.append(ChatMessage(role="assistant", content=response_content))

            # Save the interaction in exchange history
            self.exchange_history.add_exchange(question, response_content)

            print(response)

        except Exception as e:
            response = f"Error during LLM query: {e}"

        return response

    def reset_interaction_log(self):
        """
        Reset the interaction log for a new round by clearing the existing history.
        """
        self.exchange_history.clear_exchange_history()
        self.chat_history = [
            ChatMessage(role="system", content=f"You are {self.name}. {self.description}")
        ]

    def get_interaction_log(self) -> list:
        """
        Retrieve the interaction log.
        :return: List of interaction dictionaries.
        """
        return self.exchange_history.get_exchange_history()

    def to_dict(self):
        # Return the person as a dictionary
        return {
            "name": self.name,
            "description": self.description
        }
