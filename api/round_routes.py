from flask_openapi3 import APIBlueprint
from flask import jsonify, request
from application.game.game_logic.round import Round
from application.game.game_logic.person import Person
from application.game.game_logic.team import Team

round_routes = APIBlueprint('round', __name__)

# # OpenAPI tag definition
# tag = {"name": "Round", "description": "Round-related operations"}
#
# # In-memory storage for rounds
# rounds = {}
#
#
# @round_routes.post('/round', tags=[tag])
# def create_round():
#     """
#     Create Round
#     ---
#     description: Create a new round for a game.
#     requestBody:
#       required: true
#       content:
#         application/json:
#           schema:
#             type: object
#             properties:
#               game_id:
#                 type: string
#                 example: "game_123"
#               person_id:
#                 type: string
#                 example: "person_1"
#               question_team_id:
#                 type: string
#                 example: "team_1"
#               answer_team_id:
#                 type: string
#                 example: "team_2"
#     responses:
#       201:
#         description: Round created successfully
#         content:
#           application/json:
#             schema:
#               type: object
#               properties:
#                 round_id:
#                   type: string
#                   example: "round_1"
#       404:
#         description: Game, Person, or Team not found
#     """
#     data = request.json
#     game_id = data.get('game_id')
#     person_id = data.get('person_id')
#     question_team_id = data.get('question_team_id')
#     answer_team_id = data.get('answer_team_id')
#
#     # Validate existence
#     game = games.get(game_id)
#     person = people.get(person_id)
#     question_team = teams.get(question_team_id)
#     answer_team = teams.get(answer_team_id)
#
#     if not game or not person or not question_team or not answer_team:
#         return jsonify({"error": "Invalid game, person, or team"}), 404
#
#     # Create round
#     round_id = f"round_{len(rounds) + 1}"
#     rounds[round_id] = Round(
#         person=person,
#         question_team=question_team,
#         answer_team=answer_team,
#         hint_manager=None
#     )
#
#     return jsonify({"round_id": round_id}), 201
