from flask import Flask, render_template
from flasgger import Swagger
from api.game_routes import game_routes

# Initialize Flask app
app = Flask(__name__)

# Initialize Flasgger (Swagger UI)
swagger = Swagger(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/game')
def game():
    return render_template('game.html')


@app.route('/game/<string:game_id>/bonus-quiz', methods=['GET'])
def bonus_quiz(game_id):
    return render_template('bonus_quiz.html', game_id=game_id)


# Register the API Blueprints (ensure these are registered properly)
app.register_blueprint(game_routes)

if __name__ == '__main__':
    app.run(debug=True)
