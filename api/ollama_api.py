from flask import Flask, jsonify, request
import ollama

app = Flask(__name__)


@app.route('/query', methods=['POST'])
def query_llama():
    try:
        # Get the user input (message) from the request body
        user_message = request.json.get('message', '')

        # Make sure there is a message provided
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Query the Ollama model (llama3.2)
        response = ollama.chat(model='llama3', messages=[
            {'role': 'user', 'content': user_message}
        ])

        # Return the response from Llama model
        return jsonify({"response": response.message.content})

    except ollama.ResponseError as e:
        return jsonify({"error": f"Error with the model: {e.error}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
