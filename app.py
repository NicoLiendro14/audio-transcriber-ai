import random

from flask import Flask, request, jsonify
from flask_cors import CORS

from app.transcriber import transcribe_video_mp4
from app.utils import get_files_with_metadata

app = Flask(__name__)
CORS(app)


@app.route('/list_files', methods=['POST'])
def list_files():
    folder_path = request.json.get('folder_path')

    files_with_metadata = get_files_with_metadata(folder_path)

    return jsonify(files_with_metadata)


@app.route('/transcribe', methods=['POST'])
def execute_function():
    path = request.json.get('path')
    text_transcribed = transcribe_video_mp4(path)
    return {"text": text_transcribed}


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
