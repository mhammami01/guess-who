from typing import Union

from application.game.game_logic.person import Person


class HintManager:

    def __init__(self, hint_data_source=None, model=None):
        """
        Initialize the Hint class.
        :param hint_data_source: Optional data source for dynamic hints (i.e. RAG/database).
        """
        self.hint_data_source = hint_data_source
        self.model = model

    def generate_hint(self, person: Person, topic: str) -> str:
        """
        Generate a hint for the given topic and person.
        :param person: The person the hint is about.
        :param topic: The topic of the hint.
        :return: A hint string.
        """
        try:
            # Use the hint data source if available
            if self.hint_data_source:
                # Retrieve the relevant context from the data source
                context = self._retrieve_context(person, topic)
                if context:
                    # Generate a hint using the context and model
                    hint = self._generate_hint_from_context(context)
                    return hint
                else:
                    raise Exception(f"No relevant context found for topic '{topic}'.")

            else:
                # If no hint data source is provided, generate a fallback hint
                return self._generate_static_hint(person, topic)

        except Exception as e:
            return f"Error generating hint: {str(e)}"

    def _retrieve_context(self, person: Person, topic: str) -> Union[str, None]:
        """
        Retrieve relevant context from the data source (e.g., database, API, etc.).
        :param person: The person for whom the hint is being generated.
        :param topic: The topic related to the hint.
        :return: Retrieved context for generating a hint.
        """
        try:
            # Create a structured query for the hint data source
            query = self._create_query(person, topic)
            context = self.hint_data_source.query(query)  # Assuming the data source has a `query` method

            if context:
                return context
            else:
                return None

        except Exception as e:
            raise Exception(f"Error retrieving context: {str(e)}")

    @staticmethod
    def _create_query(person: Person, topic: str) -> str:
        """
        Create a structured query for the hint data source.
        :param person: The person object or name.
        :param topic: The topic for the hint.
        :return: A structured query string.
        """
        return (
            f"Provide a hint about '{topic}' that is relevant to {person.name}. "
            f"Context: {person.description}."
        )

    def _generate_hint_from_context(self, context: str) -> str:
        """
        Generate a hint from the retrieved context using the model.
        :param context: The context retrieved from the data source.
        :return: The generated hint string.
        """
        if self.model:
            # If a model is provided, use it to generate the hint from the context
            return self.model.generate(context)
        else:
            # Fallback static hint generation logic if no model is provided
            return f"Hint: {context}"

    @staticmethod
    def _generate_static_hint(person: Person, topic: str) -> str:
        """
        Generate a static hint if no external data source is available.
        :param person: The person the hint is about.
        :param topic: The topic of the hint.
        :return: A static hint string.
        """
        # Static fallback hint generation logic
        return f"Hint about {topic} for {person.name}: This is a basic static hint."
