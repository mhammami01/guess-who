from flask_openapi3 import APIBlueprint

person_routes = APIBlueprint('person_routes', __name__, url_prefix='/api')