import os
from typing import Dict

from dotenv import load_dotenv
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from llama_index.llms.openai import OpenAI
from application.game.game_logic.game import Game
from application.game.game_logic.llm import LLMInitializer
from application.game.game_logic.person import Person
from application.game.game_logic.quiz_manager import QuizManager
from application.game.game_logic.score import Score
from application.game.game_logic.team import Team

game_routes = Blueprint('game_routes', __name__)

# In-memory storage for active games
games: Dict[str, Game] = {}

# in-memory storage for LLM persons
persons: Dict[str, Person] = {}

# In-memory storage for active quizzes
quizzes: Dict[str, QuizManager] = {}


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
                        'example': 'Team Beta',
                    },
                    'is_running': {
                        'type': 'boolean',
                        'description': 'game status',
                        'example': True
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
                                'name': {'type': 'string'},
                                'total_score': {'type': 'integer'},
                                'round_score': {'type': 'integer'}
                            }
                        }
                    },
                    'is_running': {
                        'type': 'boolean',
                        'description': 'game status',
                        'example': True
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

    # Check if JSON parsing failed
    if data is None:
        return jsonify({"error": "Invalid JSON. Please ensure your request has 'Content-Type: application/json'."}), 415

    # Retrieve max_rounds from the JSON, default to 5 if not provided
    max_rounds = data.get('max_rounds', 5)
    team_a_name = data.get('team_a_name')
    team_b_name = data.get('team_b_name')

    # Validate team names
    if not team_a_name or not team_b_name:
        return jsonify({"error": "Both team names are required."}), 400

    # Assign unique ID for the game
    game_id = f"game_{len(games) + 1}"

    # Create team objects with initial scores
    team_a = Team(name=team_a_name, score=Score(initial_points=float(os.getenv("ROUND_POINTS"))))
    team_b = Team(name=team_b_name, score=Score(initial_points=0))

    # Retrieve is_running from the JSON, default to False if not provided
    is_running = data.get('is_running', True)

    # Initialize the Game object and add teams
    new_game = Game(
        rounds=[],
        teams=[team_a, team_b],
        max_rounds=max_rounds,
        is_running=is_running,
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
                "name": team_a.name,
                "total_score": team_a.score.total_score,
                "round_score": team_a.score.round_score
            },
            {
                "name": team_b.name,
                "total_score": team_b.score.total_score,
                "round_score": team_b.score.round_score
            }
        ],
        "is_running": is_running
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
                    'game_status': {'type': 'string'},
                    'quiz_status': {'type': 'string'},
                    'teams': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
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
                                        'name': {'type': 'string'},
                                        'description': {'type': 'string'}
                                    }
                                },
                                'status': {'type': 'string', 'enum': ['in_progress', 'finished']},
                                'llm_team': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string'}
                                    }
                                },
                                'guess_team': {
                                    'type': 'object',
                                    'properties': {
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

    quiz_manager = quizzes.get(game_id)

    # Prepare the game status response
    game_status = {
        "game_id": game_id,
        "game_status": 'finished' if game.is_game_over() else 'in_progress',
        "quiz_status": 'active' if quiz_manager and quiz_manager.is_running else 'not_active',
        "teams": [
            {
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
                    "name": game_round.person.name if game_round.person else "Not yet assigned",
                    "description": game_round.person.description if game_round.person else "Not yet assigned"
                },
                "round_status": "finished" if game_round.finished else "in_progress",
                "llm_team": {
                    "name": game_round.question_team.name
                },
                "guess_team": {
                    "name": game_round.answer_team.name
                }
            }
            for game_round in game.rounds
        ]
    }

    return jsonify(game_status), 200


@game_routes.route('/game/<string:game_id>/round/start', methods=['POST'])
@swag_from({
    'summary': 'Start a new Round',
    'description': 'Starts a new round by assigning a person and two teams within a game.',
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
            'description': 'Round started successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'round_id': {'type': 'string', 'example': 'round_1'},
                    'game_id': {'type': 'string'},
                    'teams': {
                        'type': 'object',
                        'properties': {
                            'llm_team': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'}
                                }
                            },
                            'guess_team': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Game or Team or Person not found.'
        }
    }
})
def start_round(game_id):
    # Fetch the game by its ID
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    # Create a new round
    current_round = game.start_round()

    # Return response
    return jsonify({
        "round_id": current_round.round_id,
        "is_finished": current_round.is_round_finished(),
        "game_id": game_id,
        "teams": {
            "llm_team": {
                "name": game.get_llm_team().get_name()
            },
            "guess_team": {
                "name": game.get_guess_team().get_name()
            }
        }
    }), 200


@game_routes.route('/game/<string:game_id>/round/add_person', methods=['POST'])
@swag_from({
    'summary': 'Create a new Person and add it to the game round',
    'description': 'Creates a new person for assigning to a game round.',
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
                    'person_description': {'type': 'string', 'example': 'Do not reveal your identity.'}
                },
                'required': ['person_name', 'person_description']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Person created and added to round successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'round_id': {'type': 'string'},
                    'person': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'description': {'type': 'string'}
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Game or Round not found.'
        },
        400: {
            'description': 'Person with the same name already exists.'
        }
    }
})
def create_person_and_add_to_round(game_id):
    data = request.json
    person_name = data.get("person_name")
    person_description = data.get("person_description")

    # Fetch the game and round
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    current_round = game.get_current_round()
    if not current_round:
        return jsonify({"error": f"Round with ID '{current_round}' not found."}), 404

    # Check if the person already exists
    if person_name in persons:
        return jsonify({"error": f"Person with name '{person_name}' already exists."}), 400

    # Initialize the Person instance
    llm = LLMInitializer.initialise_llm()
    person = Person(name=person_name, description=person_description, llm=llm)

    # Store the person in the in-memory dictionary
    persons[person_name] = person

    # Add the person to the round
    game.add_person_to_current_round(person)

    # Return response
    return jsonify({
        "round": current_round.to_dict(),
        "person": {
            "name": person.name,
            "description": person.description
        }
    }), 200


@game_routes.route('/game/<string:game_id>/round/ask', methods=['POST'])
@swag_from({
    'summary': 'Ask a Question to a Person in a Specific Round',
    'description': 'Ask a question to a specific person in a given round and get the LLM-generated response. Also '
                   'checks if the identity was revealed.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'example': 'game_1'
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
            'description': 'Game not found.'
        }
    }
})
def ask_question(game_id):
    # Fetch the game by ID
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    # Fetch the round from the game by round_id
    current_round = game.get_current_round()

    # Ensure the person is part of the round (access the person assigned to this round)
    person = current_round.person
    if not person:
        return jsonify({"error": "Person not found in this round."}), 404

    # Retrieve the question from the request body
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Question is required."}), 400

    # Ask the Person instance
    result = current_round.ask_question(question)
    was_identity_revealed = result["identity_revealed"]
    response = result["response"]
    is_round_finished = current_round.is_round_finished()

    return jsonify({
        "question": question,
        "response": response,
        "identity_revealed": was_identity_revealed,
        "is_round_finished": is_round_finished
    })


@game_routes.route('/game/<string:game_id>/round/make_guess', methods=['POST'])
@swag_from({
    'summary': 'Make a Guess',
    'description': 'Make a guess about the person\'s identity.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'example': 'game_1'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'guess': {'type': 'string', 'example': 'Albert Einstein'}
                },
                'required': ['guess']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Guess made successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'identity_revealed': {'type': 'boolean'},
                    'message': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Game not found.'
        }
    }
})
def make_guess_in_round(game_id):
    # Fetch the game by ID
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    # Fetch the round from the game by round_id
    current_round = game.get_current_round()

    data = request.json
    guess = data.get("guess")
    if not guess:
        return jsonify({"error": "Guess is required."}), 400

    # Make the guess
    correct = current_round.make_guess(guess)
    is_round_finished = current_round.is_round_finished()

    return jsonify({
        "identity_revealed": correct,
        "message": "Correct guess!" if correct else "Incorrect guess.",
        "is_round_finished": is_round_finished
    })


@game_routes.route('/game/<string:game_id>/round/use_hint', methods=['POST'])
@swag_from({
    'summary': 'Use a Hint',
    'description': 'Use a hint during the round.',
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
            'description': 'Hint used successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'hint': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Round not found.'
        }
    }
})
def use_hint_in_round(game_id):
    # Fetch the game by ID
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    # Fetch the round from the game by round_id
    current_round = game.get_current_round()

    # Use the hint
    hint = current_round.use_hint()
    is_round_finished = current_round.is_round_finished()

    return jsonify({
        "hint": hint,
        "is_round_finished": is_round_finished
    })


@game_routes.post('/game/<string:game_id>/round/end')
@swag_from({
    'summary': 'End the Round',
    'description': 'Finalize the round and reset scores.',
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
            'description': 'Round ended successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'round_summary': {'type': 'string'},
                    'is_game_over': {'type': 'boolean'}
                }
            }
        },
        404: {
            'description': 'Round not found.'
        }
    }
})
def end_round(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    round_summary = game.end_round()
    # is_game_over = game.is_game_over()

    return jsonify({"round_summary": round_summary})


@game_routes.route('/game/<string:game_id>/winner', methods=['POST'])
@swag_from({
    'summary': 'Declare Winner',
    'description': 'Determines and signals the winner of the game without ending the game.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'The ID of the game to declare a winner.',
            'example': 'game_1'
        }
    ],
    'responses': {
        200: {
            'description': 'Winner successfully declared.',
            'schema': {
                'type': 'object',
                'properties': {
                    'game_id': {'type': 'string'},
                    'is_running': {'type': 'boolean'},
                    'current_scores': {
                        'type': 'object',
                        'additionalProperties': {'type': 'integer'}
                    },
                    'winner': {'type': 'string', 'nullable': True},
                    'message': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Game not found.'
        }
    }
})
def declare_winner(game_id):
    # Fetch the game by ID
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    current_scores = game.get_game_score()
    winner = game.declare_winner()

    # If there's a tie, set winner to a message indicating a tie
    if winner is None:
        winner_message = "It's a tie!"
    else:
        winner_message = winner

    # Return the winner
    return jsonify({
        "game_id": game_id,
        "current_scores": current_scores,
        "winner": winner_message,
        "message": "Winner declared successfully."
    }), 200


@game_routes.route('/game/<string:game_id>/quiz/start', methods=['POST'])
@swag_from({
    'summary': 'Start a Bonus Quiz',
    'description': 'Starts a bonus quiz for the specified game, initializing the state and shuffling questions.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'Unique identifier for the game.',
            'example': 'game_1'
        }
    ],
    'responses': {
        200: {
            'description': 'Quiz started successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Game not found.'
        }
    }
})
def start_quiz(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": f"Game with ID '{game_id}' not found."}), 404

    # Initialize a QuizManager for the game if not already present
    if game_id not in quizzes:
        quizzes[game_id] = QuizManager(game.teams)

    quiz_manager = quizzes[game_id]
    quiz_manager.start_quiz()

    return jsonify({"message": "Quiz started successfully."}), 200


@game_routes.route('/game/<string:game_id>/quiz/next', methods=['GET'])
@swag_from({
    'summary': 'Get Next Quiz Question',
    'description': 'Fetches the next question for the current team in the bonus quiz.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'Unique identifier for the game.',
            'example': 'game_1'
        }
    ],
    'responses': {
        200: {
            'description': 'Next question retrieved successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'team': {'type': 'string'},
                    'question': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Quiz not found.'
        },
        400: {
            'description': 'Quiz is not active.'
        }
    }
})
def get_next_question(game_id):
    quiz_manager = quizzes.get(game_id)
    if not quiz_manager:
        return jsonify({"error": f"Quiz for game ID '{game_id}' not found."}), 404

    next_question = quiz_manager.get_next_question()
    if isinstance(next_question, str):
        return jsonify({"error": next_question}), 400

    return jsonify(next_question), 200


@game_routes.route('/game/<string:game_id>/quiz/answer', methods=['POST'])
@swag_from({
    'summary': 'Submit Quiz Answer',
    'description': 'Submits an answer for the current question in the bonus quiz.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'Unique identifier for the game.',
            'example': 'game_1'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'answer': {'type': 'string', 'example': 'Paris'}
                },
                'required': ['answer']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Answer submitted and processed.',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Quiz not found.'
        },
        400: {
            'description': 'Quiz is not active.'
        }
    }
})
def submit_answer(game_id):
    quiz_manager = quizzes.get(game_id)
    if not quiz_manager:
        return jsonify({"error": f"Quiz for game ID '{game_id}' not found."}), 404

    data = request.json
    answer = data.get("answer")
    if not answer:
        return jsonify({"error": "Answer is required."}), 400

    result = quiz_manager.submit_answer(answer)
    return jsonify({"result": result}), 200


@game_routes.route('/game/<string:game_id>/quiz/status', methods=['GET'])
@swag_from({
    'summary': 'Get Quiz Status',
    'description': 'Retrieves the current status of the quiz for a given game.',
    'parameters': [
        {
            'name': 'game_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'Unique identifier for the game.',
            'example': 'game_1'
        }
    ],
    'responses': {
        200: {
            'description': 'Quiz status retrieved successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'quiz_status': {'type': 'string', 'enum': ['in_progress', 'finished']}
                }
            }
        },
        404: {
            'description': 'Quiz not found.'
        }
    }
})
def get_quiz_status(game_id):
    # Retrieve the quiz manager for the given game_id
    quiz_manager = quizzes.get(game_id)
    if not quiz_manager:
        return jsonify({"error": f"Quiz for game ID '{game_id}' not found."}), 404

    # Get the status of the quiz
    status = quiz_manager.get_quiz_status()

    # Return the quiz status in the response
    return jsonify(status), 200
