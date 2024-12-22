from llama_index.llms.ollama import Ollama
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
        self.__identity_revealed = False

    def ask_question_to_llm(self, question: str) -> ChatResponse:
        """
        Process a question and return the LLM's response.
        :param question: Question string.
        :return: ChatResponse object from the LLM.
        """
        if self.__identity_revealed:
            raise RuntimeError("You are already revealed.")

        try:
            # Add the user's question to the chat history as a user message
            self.chat_history.append(ChatMessage(role="user", content=question))

            # Query the LLM with the current chat history
            if isinstance(self.llm, Ollama):
                conversation = "\n".join(
                    f"{msg.role.capitalize()}: {msg.content}"
                    for msg in self.chat_history
                )
                response_content = self.llm.complete(conversation)
            else:
                response = self.llm.chat(self.chat_history)
                response_content = response.message.content

            # Add the LLM's response to the chat history
            self.chat_history.append(ChatMessage(role="assistant", content=response_content))

            # Print the response content for debugging
            print(response_content)

            # Create and return a ChatResponse object
            return ChatResponse(message=ChatMessage(role="assistant", content=response_content))

        except Exception as e:
            # Handle errors and return a fallback response
            error_message = f"Error during LLM query: {e}"

            # Log the error in the chat history
            self.chat_history.append(ChatMessage(role="assistant", content=error_message))

            # Return a fallback error response as a ChatResponse object
            return ChatResponse(message=ChatMessage(role="assistant", content=error_message))

    def reset_interaction_log(self):
        """
        Reset the interaction log for a new round by clearing the existing history.
        """
        self.chat_history = [
            ChatMessage(role="system", content=f"You are {self.name}. {self.description}")
        ]

    def to_dict(self):
        # Return the person as a dictionary
        return {
            "name": self.name,
            "description": self.description
        }
