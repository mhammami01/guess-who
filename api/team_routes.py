from flask import jsonify, request
from application.game.game_logic.team import Team
from application.game.game_logic.score import Score
from flasgger import swag_from
from flask import Blueprint

# Define API Blueprint for team routes
team_routes = Blueprint('team_routes', __name__)

# In-memory storage for teams
teams = {}


# @team_routes.get('/team/<string:team_id>')
# @swag_from({
#     'summary': 'Get Team Information',
#     'description': 'Retrieve team information by ID.',
#     'parameters': [
#         {
#             'name': 'team_id',
#             'in': 'path',
#             'required': True,
#             'schema': {'type': 'string', 'example': 'team_1'}
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'Team information.',
#             'content': {
#                 'application/json': {
#                     'schema': {
#                         'type': 'object',
#                         'properties': {
#                             'id': {'type': 'string'},
#                             'name': {'type': 'string'},
#                             'total_score': {'type': 'integer'},
#                             'round_score': {'type': 'integer'}
#                         }
#                     }
#                 }
#             }
#         },
#         404: {
#             'description': 'Team not found.'
#         }
#     }
# })
# def get_team(team_id):
#     team = teams.get(team_id)
#     if not team:
#         return jsonify({"error": "Team not found"}), 404
#
#     return jsonify({"id": team_id, **team.to_dict()}), 200
