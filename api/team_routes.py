from flask_openapi3 import APIBlueprint

team_routes = APIBlueprint('team_routes', __name__, url_prefix='/api')