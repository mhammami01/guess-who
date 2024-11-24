from flask_openapi3 import APIBlueprint, Tag
from flask import request, jsonify
from application.game.game_logic.person import Person
from application.game.game_logic.game import Game

person_routes = APIBlueprint('person', __name__)

# # OpenAPI tag definition
# tag_persons = Tag(name="Person", description="Operations related to the person.")
#
# # In-memory storage for people (linked to games)
# people = {}
#
#
# @person_routes.post('/person', tags=[tag_persons])
# def create_person():
#     """
#     Create Person
#     ---
#     description: Create a person to guess.
#     requestBody:
#       required: true
#       content:
#         application/json:
#           schema:
#             type: object
#             properties:
#               name:
#                 type: string
#                 example: "Albert Einstein"
#               description:
#                 type: string
#                 example: "Famous theoretical physicist"
#               game_id:
#                 type: string
#                 example: "game_123"
#     responses:
#       201:
#         description: Person created successfully
#         content:
#           application/json:
#             schema:
#               type: object
#               properties:
#                 person_id:
#                   type: string
#                   example: "person_1"
#       404:
#         description: Game not found
#     """
#     data = request.json
#     name = data.get('name')
#     description = data.get('description')
#     game_id = data.get('game_id')
#
#     # Validate game existence
#     if game_id not in games:
#         return jsonify({"error": "Game not found"}), 404
#
#     # Create person
#     person_id = f"person_{len(people) + 1}"
#     people[person_id] = Person(name=name, description=description, llm=None)
#
#     return jsonify({"person_id": person_id}), 201
#
#
# @person_routes.get('/person/<person_id>', tags=[tag])
# def get_person(person_id):
#     """
#     Get Person
#     ---
#     description: Retrieve details of a person.
#     parameters:
#       - name: person_id
#         in: path
#         required: true
#         schema:
#           type: string
#     responses:
#       200:
#         description: Returns person details
#         content:
#           application/json:
#             schema:
#               type: object
#               properties:
#                 name:
#                   type: string
#                   example: "Albert Einstein"
#                 description:
#                   type: string
#                   example: "Famous theoretical physicist"
#       404:
#         description: Person not found
#     """
#     person = people.get(person_id)
#     if not person:
#         return jsonify({"error": "Person not found"}), 404
#
#     return jsonify({
#         "name": person.name,
#         "description": person.description
#     })
