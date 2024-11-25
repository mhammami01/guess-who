from flask_openapi3 import APIBlueprint
from flask import request, jsonify
from application.game.game_logic.game import Game
from application.game.game_logic.team import Team
from application.game.game_logic.score import Score
from flask_openapi3 import Tag

# Define the API Blueprint
game_routes = APIBlueprint('game', __name__)

# OpenAPI tag definition
tag_games = Tag(name="Games", description="Operations related to game management.")

# In-memory storage for game state
games = {}


# @game_routes.post('/game', tags=[tag_games])
# def create_game():
#     """
#     Create Game
#     ---
#     description: Create a new game with teams and parameters.
#     requestBody:
#       required: true
#       content:
#         application/json:
#           schema:
#             type: object
#             properties:
#               teams:
#                 type: array
#                 items:
#                   type: object
#                   properties:
#                     name:
#                       type: string
#                       example: "Team A"
#                     initial_score:
#                       type: integer
#                       example: 0
#               max_rounds:
#                 type: integer
#                 example: 5
#     responses:
#       201:
#         description: Game created successfully
#         content:
#           application/json:
#             schema:
#               type: object
#               properties:
#                 game_id:
#                   type: string
#                   example: "game_123"
#     """
#     data = request.json
#     teams_data = data.get('teams', [])
#     max_rounds = data.get('max_rounds', 5)
#
#     # Validate input
#     if len(teams_data) < 2:
#         return jsonify({"error": "At least two teams are required"}), 400
#
#     # Create teams and scores
#     teams = []
#     for team_data in teams_data:
#         team_name = team_data['name']
#         initial_score = team_data.get('initial_score', 0)
#         teams.append(Team(name=team_name, score=Score(initial_score)))
#
#     # Create the game
#     game_id = f"game_{len(games) + 1}"
#     games[game_id] = Game(teams=teams, max_rounds=max_rounds, rounds=[], hint_data_source=None)
#
#     return jsonify({"game_id": game_id}), 201
#
#
# @game_routes.get('/game/<game_id>', tags=[tag_games])
# def get_game(game_id):
#     """
#     Get Game
#     ---
#     description: Retrieve details of an existing game.
#     parameters:
#       - name: game_id
#         in: path
#         required: true
#         schema:
#           type: string
#     responses:
#       200:
#         description: Returns the game details
#         content:
#           application/json:
#             schema:
#               type: object
#               properties:
#                 game_id:
#                   type: string
#                   example: "game_123"
#                 max_rounds:
#                   type: integer
#                   example: 5
#                 teams:
#                   type: array
#                   items:
#                     type: object
#                     properties:
#                       name:
#                         type: string
#                         example: "Team A"
#                       score:
#                         type: integer
#                         example: 0
#       404:
#         description: Game not found
#     """
#     game = games.get(game_id)
#     if not game:
#         return jsonify({"error": "Game not found"}), 404
#
#     teams_info = [{"name": team.get_name(), "score": team.get_total_score()} for team in game.teams]
#     return jsonify({
#         "game_id": game_id,
#         "max_rounds": game.max_rounds,
#         "teams": teams_info
#     })
#
#
# @game_routes.delete('/game/<game_id>', tags=[tag_games])
# def delete_game(game_id):
#     """
#     Delete Game
#     ---
#     description: Delete a game by its ID.
#     parameters:
#       - name: game_id
#         in: path
#         required: true
#         schema:
#           type: string
#     responses:
#       200:
#         description: Game deleted successfully
#         content:
#           application/json:
#             schema:
#               type: object
#               properties:
#                 message:
#                   type: string
#                   example: "Game deleted successfully"
#       404:
#         description: Game not found
#     """
#     if game_id in games:
#         del games[game_id]
#         return jsonify({"message": "Game deleted successfully"}), 200
#     else:
#         return jsonify({"error": "Game not found"}), 404
