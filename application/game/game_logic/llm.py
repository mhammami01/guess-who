from dotenv import load_dotenv
import os
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama


class LLMInitializer:
    @staticmethod
    def initialise_llm():
        """
        Initialize the LLM based on the configuration in the .env file.
        :return: Initialized LLM object.
        """
        load_dotenv()
        llm_provider = os.getenv("LLM_PROVIDER").lower()

        if llm_provider == "openai":
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set in the environment.")
            return OpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key)
        elif llm_provider == "phi":
            return Ollama(model="phi3", request_timeout=100.0)
        elif llm_provider == "llama3_local":
            return Ollama(model="llama3.2", request_timeout=100.0)
        elif llm_provider == "llama3_remote":
            return "llama3_remote"
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
