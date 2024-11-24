from flask import Flask, render_template
from flask_openapi3 import Info, OpenAPI

from api.game_routes import game_routes
from api.round_routes import round_routes
from api.team_routes import team_routes
from api.person_routes import person_routes

info = Info(title='Guess Who API', version='1.0.0')
app = OpenAPI(__name__, info=info)

# Register API routes
app.register_api(game_routes)
app.register_api(round_routes)
app.register_api(team_routes)
app.register_api(person_routes)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/game')
def game():
    return render_template('game.html')


if __name__ == '__main__':
    app.run(debug=True)
