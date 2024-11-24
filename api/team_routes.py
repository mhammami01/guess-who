from flask import jsonify, request
from application.game.game_logic.team import Team
from application.game.game_logic.score import Score
from flasgger import swag_from
from flask import Blueprint

# Define API Blueprint for team routes
team_routes = Blueprint('team_routes', __name__)

# In-memory storage for teams
teams = {}


@team_routes.post('/team')
@swag_from({
    'summary': 'Create Teams',
    'description': 'Create two teams with custom names and initial scores.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'team_a_name': {'type': 'string', 'example': 'Team 1'},
                    'team_b_name': {'type': 'string', 'example': 'Team 2'}
                },
                'required': ['team_a_name', 'team_b_name']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Successfully created teams.',
            'schema': {
                'type': 'object',
                'properties': {
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
def create_teams():
    # Parse team names from request body
    data = request.json
    team_a_name = data.get("team_a_name")
    team_b_name = data.get("team_b_name")

    # Validate team names
    if not team_a_name or not team_b_name:
        return jsonify({"error": "Both team names are required."}), 400

    # Create teams with provided names
    team_a = Team(name=team_a_name, score=Score(initial_points=10))
    team_b = Team(name=team_b_name, score=Score(initial_points=0))

    # Assign unique IDs for teams
    team_a_id = f"team_{len(teams) + 1}"
    team_b_id = f"team_{len(teams) + 2}"

    # Save teams to in-memory storage
    teams[team_a_id] = team_a
    teams[team_b_id] = team_b

    # Return created teams
    return jsonify({
        "teams": [
            {"id": team_a_id, **team_a.to_dict()},
            {"id": team_b_id, **team_b.to_dict()}
        ]
    }), 201


@team_routes.get('/team/<string:team_id>')
@swag_from({
    'summary': 'Get Team Information',
    'description': 'Retrieve team information by ID.',
    'parameters': [
        {
            'name': 'team_id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string', 'example': 'team_1'}
        }
    ],
    'responses': {
        200: {
            'description': 'Team information.',
            'content': {
                'application/json': {
                    'schema': {
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
        },
        404: {
            'description': 'Team not found.'
        }
    }
})
def get_team(team_id):
    team = teams.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    return jsonify({"id": team_id, **team.to_dict()}), 200


# Route for updating the round score of a team
@team_routes.put('/team/<team_id>/update_round_score')
@swag_from({
    'summary': 'Update Round Score',
    'description': 'Add points to a team\'s round score.',
    'parameters': [
        {
            'name': 'team_id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string'}
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'points': {'type': 'integer', 'example': 10}
                        },
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully updated round score.',
            'content': {
                'application/json': {
                    'schema': {
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
        },
        404: {
            'description': 'Team not found.'
        }
    }
})
def update_round_score(team_id):
    # Get the points from the request body
    data = request.json
    points = data.get('points', 0)

    # Retrieve the team by ID
    team = teams.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    # Update the team's round score
    team.score.add(points)

    # Return the updated team info
    return jsonify({
        "id": team_id,
        "name": team.get_name(),
        "total_score": team.get_total_score(),
        "round_score": team.get_round_score()
    }), 200


# Route for finalizing the round, adding round score to total score
@team_routes.put('/team/<team_id>/update_total_score')
@swag_from({
    'summary': 'Finalize Round',
    'description': 'Add the round score to the total score and reset the round score.',
    'parameters': [
        {
            'name': 'team_id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string', 'example': 'team_1'}
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully finalized round score.',
            'content': {
                'application/json': {
                    'schema': {
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
        },
        404: {
            'description': 'Team not found.'
        }
    }
})
def finalize_round(team_id):
    # Retrieve the team by ID
    team = teams.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    # Add round score to total score and reset round score
    team.score.update_total_score()
    team.score.reset_round_score()

    # Return the updated team info
    return jsonify({
        "id": team_id,
        "name": team.get_name(),
        "total_score": team.get_total_score(),
        "round_score": team.get_round_score()
    }), 200
