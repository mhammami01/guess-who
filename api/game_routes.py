from flask_openapi3 import Tag, APIBlueprint

game_routes = APIBlueprint('game_routes', __name__, url_prefix='/api')

tag = Tag(name='Game', description='Game related operations')


@game_routes.get('/game', tags=[tag])
def game():
    """
    Get Game
    ---
    description: Get the game information
    responses:
      200:
        description: Returns the game information
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Game route"
    """
    return {"message": "Game route"}
