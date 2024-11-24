from flask import jsonify, request
from flask_openapi3 import APIBlueprint

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
    'description': 'Create two teams with initial scores.',
    'responses': {
        201: {
            'description': 'Successfully created teams.',
            'content': {
                'application/json': {
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
        }
    }
})
def create_teams():
    """
    Create Teams
    ---
    description: Create two teams with initial scores.
    responses:
      201:
        description: Successfully created teams.
        content:
          application/json:
            schema:
              type: object
              properties:
                teams:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      name:
                        type: string
                      total_score:
                        type: integer
                      round_score:
                        type: integer
    """
    # Create two teams with predefined scores
    team_a = Team(name="Team A", score=Score(initial_points=10))
    team_b = Team(name="Team B", score=Score(initial_points=0))

    # Assign unique IDs for teams
    team_a_id = f"team_{len(teams) + 1}"
    team_b_id = f"team_{len(teams) + 2}"

    teams[team_a_id] = team_a
    teams[team_b_id] = team_b

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
            'schema': {'type': 'string'}
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
    """
    Get Team
    ---
    description: Retrieve team information by ID.
    parameters:
      - name: team_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Team information.
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: string
                name:
                  type: string
                total_score:
                  type: integer
                round_score:
                  type: integer
      404:
        description: Team not found.
    """
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
                            'points': {'type': 'integer'}
                        },
                        'example': {
                            'points': 10
                        }
                    },
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
            'schema': {'type': 'string'}
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
