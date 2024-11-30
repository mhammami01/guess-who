import os
import uuid

from dotenv import load_dotenv
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from llama_index.llms.openai import OpenAI

from api.team_routes import teams
from application.game.game_logic.game import Game
from application.game.game_logic.person import Person
from application.game.game_logic.round import Round
from application.game.game_logic.score import Score
from application.game.game_logic.team import Team

game_routes = Blueprint('game_routes', __name__)

# In-memory storage for active games
games = {}


# Initialize LLM instance
def initialise_llm_for_api():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment.")
    return OpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key)


@game_routes.route('/game', methods=['POST'])
@swag_from({
    'summary': 'Create a New Game',
    'description': 'Creates a new game with a unique ID and two teams with custom names.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'max_rounds': {
                        'type': 'integer',
                        'description': 'Optional maximum number of rounds for the game.',
                        'example': 5,
                        'default': 5
                    },
                    'team_a_name': {
                        'type': 'string',
                        'description': 'Name for Team A.',
                        'example': 'Team Alpha'
                    },
                    'team_b_name': {
                        'type': 'string',
                        'description': 'Name for Team B.',
                        'example': 'Team Beta'
                    }
                },
                'required': ['team_a_name', 'team_b_name']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Game successfully created.',
            'schema': {
                'type': 'object',
                'properties': {
                    'game_id': {
                        'type': 'string',
                        'description': 'The unique identifier for the newly created game.',
                        'example': 'game_1'
                    },
                    'max_rounds': {
                        'type': 'integer',
                        'description': 'The maximum number of rounds for the game.',
                        'example': 5
                    },
                    'teams': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string'},
                                'name': {'type': 'string'},
                                'total_score': {'type': 'integer'},
                                'round_score': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        }
    }
})
def create_game():
    # Check if the incoming request is JSON
    if not request.is_json:
        return jsonify({"error": "Invalid JSON. Please ensure your request has 'Content-Type: application/json'."}), 415

    # Parse the JSON data
    data = request.get_json()

    # Check if JSON parsing failed (silent=True just returns None, no error is raised)
    if data is None:
        return jsonify({"error": "Invalid JSON. Please ensure your request has 'Content-Type: application/json'."}), 415

    # Retrieve max_rounds from the JSON, default to 5 if not provided
    max_rounds = data.get('max_rounds', 5)
    team_a_name = data.get('team_a_name')
    team_b_name = data.get('team_b_name')

    # Validate team names
    if not team_a_name or not team_b_name:
        return jsonify({"error": "Both team names are required."}), 400

    # Retrieve team IDs from the JSON
    team_a_id = f"team_{uuid.uuid4()}"
    team_b_id = f"team_{uuid.uuid4()}"

    # Assign unique ID for the game
    game_id = f"game_{len(games) + 1}"

    # Create team objects with initial scores
    team_a = Team(team_id=team_a_id, name=team_a_name, score=Score(initial_points=10))
    team_b = Team(team_id=team_b_id, name=team_b_name, score=Score(initial_points=0))

    # Initialize the Game object and add teams
    new_game = Game(
        rounds=[],  # Initialize with an empty list of rounds
        teams=[team_a, team_b],
        max_rounds=max_rounds,
        hint_data_source=None  # Placeholder if needed
    )

    # Store the game in memory
    games[game_id] = new_game

    # Return the created game details along with team details
    return jsonify({
        "game_id": game_id,
        "max_rounds": max_rounds,
        "teams": [
            {
                "id": team_a.id,
                "name": team_a.name,
                "total_score": team_a.score.total_score,
                "round_score": team_a.score.round_score
            },
            {
                "id": team_b.id,
                "name": team_b.name,
                "total_score": team_b.score.total_score,
                "round_score": team_b.score.round_score
            }
        ]
    }), 201


@game_routes.route('/game/<string:game_id>/status', methods=['GET'])
@swag_from({
    'summary': 'Get the Status of a Game with Round Details',
    'description': 'Fetches the current status of the game, including team scores and round details.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'example': 'game_1'
        }
    ],
    'responses': {
        200: {
            'description': 'Game status retrieved successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'game_id': {'type': 'string'},
                    'teams': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string'},
                                'name': {'type': 'string'},
                                'total_score': {'type': 'integer'},
                                'round_score': {'type': 'integer'}
                            }
                        }
                    },
                    'rounds': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'round_id': {'type': 'string'},
                                'person': {
                                    'type': 'object',
                                    'properties': {
                                        'person_id': {'type': 'string'},
                                        'name': {'type': 'string'},
                                        'description': {'type': 'string'}
                                    }
                                },
                                'status': {'type': 'string', 'enum': ['in_progress', 'finished']},
                                'question_team': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'string'},
                                        'name': {'type': 'string'}
                                    }
                                },
                                'answer_team': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'string'},
                                        'name': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Game not found.'
        }
    }
})
def get_game_status(game_id):
    # Fetch the game by ID
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    # Prepare the game status response
    game_status = {
        "game_id": game_id,
        "teams": [
            {
                "id": team.id,
                "name": team.name,
                "total_score": team.score.total_score,
                "round_score": team.score.round_score
            }
            for team in game.teams
        ],
        "rounds": [
            {
                "round_id": game_round.round_id,
                "person": {
                    "person_id": game_round.person.person_id,
                    "name": game_round.person.name,
                    "description": game_round.person.description
                },
                "status": 'finished' if game_round.is_round_finished() else 'in_progress',
                "question_team": {
                    "id": game_round.question_team.id,
                    "name": game_round.question_team.name
                },
                "answer_team": {
                    "id": game_round.answer_team.id,
                    "name": game_round.answer_team.name
                }
            }
            for game_round in game.rounds
        ]
    }

    return jsonify(game_status), 200


@game_routes.route('/game/<string:game_id>/round/start', methods=['POST'])
@swag_from({
    'summary': 'Start a new Round and Create Person',
    'description': 'Starts a new round by creating a person and assigning them, along with teams, '
                   'to the round within the specified game.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string', 'example': 'game_1'}
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'person_name': {'type': 'string', 'example': 'Albert Einstein'},
                    'person_description': {'type': 'string', 'example': 'Do not reveal your identity.'},
                    'team_a_id': {'type': 'string', 'example': 'team_1'},
                    'team_b_id': {'type': 'string', 'example': 'team_2'}
                },
                'required': ['person_name', 'person_description', 'team_a_id', 'team_b_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Round started successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'round_id': {'type': 'string', 'example': 'round_1'},
                    'game_id': {'type': 'string'},
                    'person': {
                        'type': 'object',
                        'properties': {
                            'person_id': {'type': 'string'},
                            'name': {'type': 'string'},
                            'description': {'type': 'string'}
                        }
                    },
                    'teams': {
                        'type': 'object',
                        'properties': {
                            'team_a': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'string'},
                                    'name': {'type': 'string'}
                                }
                            },
                            'team_b': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'string'},
                                    'name': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Game or Team not found.'
        }
    }
})
def start_round(game_id):  # game_id is now part of the route
    # Get data from request body
    data = request.json
    person_name = data.get("person_name")
    person_description = data.get("person_description")
    team_a_id = data.get("team_a_id")
    team_b_id = data.get("team_b_id")

    # Fetch the game by ID from the route parameter
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    # Fetch teams from the game object
    team_a = next((team for team in game.teams if team.id == team_a_id), None)
    team_b = next((team for team in game.teams if team.id == team_b_id), None)

    if not team_a or not team_b:
        return jsonify({"error": "One or both teams not found in the specified game."}), 404

    # Create a new Person if it doesn't exist
    person_id = f"person_{uuid.uuid4()}"
    # Initialize the Person instance
    llm = initialise_llm_for_api()  # Assuming you have this function defined elsewhere
    person = Person(person_id=person_id, name=person_name, description=person_description, llm=llm)

    # Generate a unique round ID
    round_id = f"round_{len(game.rounds) + 1}"

    # Create and assign the new round
    current_round = Round(
        round_id=round_id,
        person=person,
        question_team=team_a,
        answer_team=team_b,
        hint_manager=None  # Assuming you handle hints here, if needed
    )

    # Add the round to the game's rounds list
    game.rounds.append(current_round)

    # Return nested JSON response
    return jsonify({
        "round_id": round_id,
        "game_id": game_id,
        "person": {
            "person_id": person_id,
            "name": person.name,
            "description": person.description
        },
        "teams": {
            "team_a": {
                "id": team_a.id,
                "name": team_a.name
            },
            "team_b": {
                "id": team_b.id,
                "name": team_b.name
            }
        }
    }), 200


@game_routes.put('/game/<string:game_id>/switch_teams')
@swag_from({
    'summary': 'Switch Teams',
    'description': 'Switch the roles of the teams (question team and answer team) for the next round.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string', 'example': 'game_1'}
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully switched teams.',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'game_id': {'type': 'string'},
                            'teams': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'string'},
                                        'name': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Game not found.'
        }
    }
})
def switch_teams(game_id):
    # Retrieve the game by ID
    game = games.get(game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Switch the teams using the method from the Game class
    game.switch_teams()

    # Return the updated team order
    return jsonify({
        "game_id": game_id,
        "teams": [{"id": team.id, "name": team.get_name()} for team in game.teams]
    }), 200


@game_routes.route('/game/<string:game_id>/round/<string:round_id>/ask', methods=['POST'])
@swag_from({
    'summary': 'Ask a Question to a Person in a Specific Round',
    'description': 'Ask a question to a specific person in a given round and get the LLM-generated response. Also checks if the identity was revealed.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'example': 'game_1'
        },
        {
            'name': 'round_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'example': 'round_1'
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
            'description': 'Game, Round, or Person not found.'
        }
    }
})
def ask_question(game_id, round_id):
    # Fetch the game by ID
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    # Fetch the round from the game by round_id
    round = next((round for round in game.rounds if round.round_id == round_id), None)
    if not round:
        return jsonify({"error": f"Round with ID '{round_id}' not found."}), 404

    # Ensure the person is part of the round (access the person assigned to this round)
    person = round.person
    if not person:
        return jsonify({"error": "Person not found in this round."}), 404

    # Retrieve the question from the request body
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
