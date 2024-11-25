from flask import Flask, render_template
from flasgger import Swagger
from flask_openapi3 import Info, OpenAPI

from api.game_routes import game_routes
from api.round_routes import round_routes
from api.team_routes import team_routes
from api.person_routes import person_routes

# Initialize Flask app
app = Flask(__name__)

# Initialize Flasgger (Swagger UI)
swagger = Swagger(app)

# Register the API Blueprints (ensure these are registered properly)
app.register_blueprint(game_routes)
app.register_blueprint(round_routes)
app.register_blueprint(team_routes)
app.register_blueprint(person_routes)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/game')
def game():
    return render_template('game.html')


if __name__ == '__main__':
    app.run(debug=True)
