from application.game.person import Person


class HintManager:

    def __init__(self, hint_data_source=None):
        """
        Initialize the Hint class.
        :param hint_data_source: Optional data source for dynamic hints (i.e. RAG/database).
        """
        self.hint_data_source = hint_data_source

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
                query = self._create_query(person, topic)
                response = self.hint_data_source.query(query)
                if response:
                    # TODO: Do stuff
                    pass
                else:
                    # TODO: raise exception of some kind
                    pass

        except Exception as e:
            return f"Error generating hint: {str(e)}"

    @staticmethod
    def _create_query(person, topic: str) -> str:
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
