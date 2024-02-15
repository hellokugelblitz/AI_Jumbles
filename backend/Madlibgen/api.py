import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from main import API_CREATE_VIDEO, API_RETURN_SCRIPT, API_CLEAN_USERCODE

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Allows for DELETE method.
CORS(app, resources={r"/cleanup-usercode": {"origins": "*", "methods": ["DELETE"]}})

# Global constant -> points to dir of project files.
CURRENT_PROJECT_DIR = os.getcwd()

@app.route("/generate-video", methods=["POST"])
@cross_origin()
def generate_video():
    """
    Generate a video from backend based on the provided user ID and list of words.

    Request Body (JSON):
        - user_id (str): The ID of the user.
        - strings (list): List of strings used to generate the video.

    Returns:
        - If successful, returns the generated video file as an attachment with a status code of 200.
        - If video generation fails, returns an error message with a status code of 404.
    """

    # Get user_id
    user_id = request.json.get('user_id')
    
    # Get the list of strings from the JSON request body
    list_of_strings = request.json.get('strings', [])

    print("\n\nGenerating video from request under ID: ", user_id)

    # Call the function with the user_id and list_of_strings
    if API_CREATE_VIDEO(user_id, list_of_strings):
        # Return the generated video as a response!
        return send_file(CURRENT_PROJECT_DIR + "/user_output/" + user_id + "/" + user_id + ".mp4", as_attachment=True, download_name='generated_video.mp4'), 200
    else:
        return jsonify({"error": "Video Generation failed"}), 404


@app.route("/cleanup-usercode", methods=["DELETE"])
@cross_origin()
def cleanup_usercode():
    """
    Delete the user code directory associated with the provided user ID. (Done automatically after video generation to save space)

    Request Body (JSON):
        - user_id (str): The ID of the user.

    Returns:
        - If the user code directory is successfully cleaned up, returns a success message with a status code of 200.
        - If the user code directory is not found, returns an error message with a status code of 404.
    """
    
    # Grabs user ID from request
    user_id = request.json.get('user_id')

    print("\n\nRemoving files from: ", user_id)

    if API_CLEAN_USERCODE(user_id):
        return  jsonify({"message": "User code cleaned up successfully"}), 200
    else:
        return jsonify({"error": "User code directory not found"}), 404


@app.route("/generate-script", methods=["GET"])
@cross_origin()
def generate_script():
    """
    Retreives script object from backend, based on the provided input string.

    Query Parameters:
        - input_string (str): The input string used to generate the array.

    Returns:
        - If successful, returns the generated array as a JSON response with a status code of 200.
        - If the input string parameter is missing, returns an error message with a status code of 400.
    """

    # Get the string parameter from the query parameters
    input_string = request.args.get('input_string')

    # Check if the input string is provided
    if not input_string:
        return jsonify({'error': 'Input string parameter is required'}), 400

    print(API_RETURN_SCRIPT(input_string))

    # Parse the string into an array (assuming the string is comma-separated)
    array = API_RETURN_SCRIPT(input_string)

    # Return the array as a JSON response
    return jsonify({'script': array}), 200

# Run the server...
if __name__ == "__main__":
    app.run(debug=True)