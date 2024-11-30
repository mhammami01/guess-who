import os

from dotenv import load_dotenv
from flasgger import swag_from
from flask import request, jsonify, Blueprint
from llama_index.llms.openai import OpenAI

from application.game.game_logic.person import Person

person_routes = Blueprint('person', __name__)

# In-memory storage for people
persons = {}

# @person_routes.route('/person/<person_id>/log', methods=['GET'])
# @swag_from({
#     'summary': 'Get Interaction Log',
#     'description': 'Retrieve the interaction log of a specific person.',
#     'parameters': [
#         {
#             'name': 'person_id',
#             'in': 'path',
#             'required': True,
#             'type': 'string',
#             'example': 'person_1'
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'Interaction log retrieved successfully.',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'interaction_log': {
#                         'type': 'array',
#                         'items': {
#                             'type': 'object',
#                             'properties': {
#                                 'question': {'type': 'string'},
#                                 'response': {'type': 'string'}
#                             }
#                         }
#                     }
#                 }
#             }
#         },
#         404: {
#             'description': 'Person not found.'
#         }
#     }
# })
# def get_interaction_log(person_id):
#     person = persons.get(person_id)
#     if not person:
#         return jsonify({"error": "Person not found."}), 404
#
#     interaction_log = person.get_interaction_log()
#     return jsonify({"interaction_log": interaction_log})
