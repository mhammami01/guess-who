import json

import requests
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage, ChatResponse


class Person:
    def __init__(self, name: str, description: str, llm):
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
                response = self.llm.complete(conversation)
                response_content = response.text

            # Check for "llama3" model type and make the API request if matched
            elif self.llm == "llama3_remote":
                # response_content = self.call_llama3_api(question)
                conversation = "\n".join(
                    f"{msg.role.capitalize()}: {msg.content}"
                    for msg in self.chat_history
                )
                response_content = self.call_llama3_api(conversation)
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

    @staticmethod
    def call_llama3_api(question: str):
        """
        Calls the Flask API endpoint for llama3 and retrieves the response.
        :param question: The user's question.
        :return: The response from the Flask server.
        """
        api_url = "http://129.70.134.199:8080/query"  # Replace with your actual Flask API endpoint URL
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({"message": question})

        response = requests.post(api_url, headers=headers, data=payload)

        if response.status_code == 200:
            # Only return the 'response' field, not the entire JSON
            return response.json().get("response", "No response received.")
        else:
            return "Error: Failed to get response from API."
