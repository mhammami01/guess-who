import os

from dotenv import load_dotenv
from flasgger import swag_from
from flask import request, jsonify, Blueprint
from llama_index.llms.openai import OpenAI

from application.game.game_logic.person import Person

person_routes = Blueprint('person', __name__)

# In-memory storage for people
persons = {}


# Initialize LLM instance
def initialise_llm_for_api():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment.")
    return OpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key)


@person_routes.route('/person', methods=['POST'])
@swag_from({
    'summary': 'Create a Person',
    'description': 'Create a person with a name and description, and initialize an associated LLM.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Albert Einstein'},
                    'description': {'type': 'string',
                                    'example': 'Do not reveal your identity.'}
                },
                'required': ['name', 'description']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Person successfully created.',
            'schema': {
                'type': 'object',
                'properties': {
                    'person_id': {'type': 'string', 'example': 'person_1'},
                    'name': {'type': 'string'},
                    'description': {'type': 'string'}
                }
            }
        }
    }
})
def create_person():
    data = request.json
    name = data.get("name")
    description = data.get("description")

    if not name or not description:
        return jsonify({"error": "Both name and description are required."}), 400

    # Initialize the Person instance
    llm = initialise_llm_for_api()
    person = Person(name=name, description=description, llm=llm)

    # Generate a unique ID for the person
    person_id = f"person_{len(persons) + 1}"
    persons[person_id] = person

    return jsonify({
        "person_id": person_id,
        "name": person.name,
        "description": person.description
    }), 201


@person_routes.route('/person/<person_id>/ask', methods=['POST'])
@swag_from({
    'summary': 'Ask a Question',
    'description': 'Ask a question to a specific person and get the LLM-generated response. Also checks if the identity was revealed.',
    'parameters': [
        {
            'name': 'person_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'example': 'person_1'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'question': {'type': 'string', 'example': 'What is your greatest scientific achievement?'}
                },
                'required': ['question']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Response from the LLM with identity revealed status.',
            'schema': {
                'type': 'object',
                'properties': {
                    'question': {'type': 'string'},
                    'response': {'type': 'string'},
                    'identity_revealed': {'type': 'boolean'}
                }
            }
        },
        404: {
            'description': 'Person not found.'
        }
    }
})
def ask_question(person_id):
    person = persons.get(person_id)
    if not person:
        return jsonify({"error": "Person not found."}), 404

    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Question is required."}), 400

    # Ask the question to the Person instance
    response = person.ask_question(question)
    identity_revealed = person.was_identity_revealed(response.message.content)

    return jsonify({
        "question": question,
        "response": response.message.content,
        "identity_revealed": identity_revealed
    })


@person_routes.route('/person/<person_id>/reset', methods=['POST'])
@swag_from({
    'summary': 'Reset Interaction Log',
    'description': 'Reset the interaction log for a specific person.',
    'parameters': [
        {
            'name': 'person_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'example': 'person_1'
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully reset the interaction log.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Person not found.'
        }
    }
})
def reset_interaction_log(person_id):
    person = persons.get(person_id)
    if not person:
        return jsonify({"error": "Person not found."}), 404

    person.reset_interaction_log()
    return jsonify({"message": "Interaction log reset successfully."})


@person_routes.route('/person/<person_id>/log', methods=['GET'])
@swag_from({
    'summary': 'Get Interaction Log',
    'description': 'Retrieve the interaction log of a specific person.',
    'parameters': [
        {
            'name': 'person_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'example': 'person_1'
        }
    ],
    'responses': {
        200: {
            'description': 'Interaction log retrieved successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'interaction_log': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'question': {'type': 'string'},
                                'response': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Person not found.'
        }
    }
})
def get_interaction_log(person_id):
    person = persons.get(person_id)
    if not person:
        return jsonify({"error": "Person not found."}), 404

    interaction_log = person.get_interaction_log()
    return jsonify({"interaction_log": interaction_log})
