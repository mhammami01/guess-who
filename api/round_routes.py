# Define API Blueprint for round routes
import uuid

from flasgger import swag_from
from flask import Blueprint, request, jsonify

from api.person_routes import persons
from api.team_routes import teams
from application.game.game_logic.round import Round

round_routes = Blueprint('round_routes', __name__)

# In-memory storage for rounds
rounds = {}


#
# @round_routes.post('/round/start')
# @swag_from({
#     'summary': 'Start a new Round',
#     'description': 'Start a new round by setting up a person and assigning teams for the round.',
#     'parameters': [
#         {
#             'name': 'body',
#             'in': 'body',
#             'required': True,
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'person_id': {'type': 'string', 'example': 'person_1'},
#                     'team_a_id': {'type': 'string', 'example': 'team_1'},
#                     'team_b_id': {'type': 'string', 'example': 'team_2'}
#                 },
#                 'required': ['person_id', 'team_a_id', 'team_b_id']
#             }
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'Round started successfully.',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'round_id': {'type': 'string', 'example': 'round_1'},
#                     'person_id': {'type': 'string'},
#                     'team_a_id': {'type': 'string'},
#                     'team_b_id': {'type': 'string'}
#                 }
#             }
#         },
#         404: {
#             'description': 'Person or Team not found.'
#         }
#     }
# })
# def start_round():
#     data = request.json
#     person_id = data.get("person_id")
#     team_a_id = data.get("team_a_id")
#     team_b_id = data.get("team_b_id")
#
#     # Get person and teams from storage
#     person = persons.get(person_id)
#     team_a = teams.get(team_a_id)
#     team_b = teams.get(team_b_id)
#
#     if not person or not team_a or not team_b:
#         return jsonify({"error": "Person or Team not found."}), 404
#
#     # Start a new round
#     round_id = f"round_{uuid.uuid4()}"
#     current_round = Round(
#         person=person,
#         question_team=team_a,
#         answer_team=team_b,
#         hint_manager=None  # Placeholder for hint manager
#     )
#
#     rounds[round_id] = current_round
#
#     return jsonify({
#         "round_id": round_id,
#         "person_id": person_id,
#         "team_a_id": team_a_id,
#         "team_b_id": team_b_id
#     }), 200


# @round_routes.get('/round/<string:round_id>')
# @swag_from({
#     'summary': 'Get Round Information',
#     'description': 'Retrieve details of a specific round, including participating teams and scores.',
#     'parameters': [
#         {
#             'name': 'round_id',
#             'in': 'path',
#             'required': True,
#             'schema': {'type': 'string'}
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'Round information retrieved successfully.',
#             'content': {
#                 'application/json': {
#                     'schema': {
#                         'type': 'object',
#                         'properties': {
#                             'round_id': {'type': 'string'},
#                             'person_id': {'type': 'string'},
#                             'team_a_id': {'type': 'string'},
#                             'team_b_id': {'type': 'string'},
#                         }
#                     }
#                 }
#             }
#         },
#         404: {
#             'description': 'Round not found.'
#         }
#     }
# })
# def get_round(round_id):
#     round_instance = rounds.get(round_id)
#     if not round_instance:
#         return jsonify({"error": "Round not found"}), 404
#
#     return jsonify({
#         "round_id": round_id,
#         "person": round_instance.person.to_dict(),
#         "team_a": round_instance.question_team.to_dict(),  # Accessing the team id
#         "team_b": round_instance.answer_team.to_dict(),  # Accessing the team id
#     }), 200
#
