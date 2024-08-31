from PyQt5.QtCore import QThread
from flask import Flask, request, send_file
from flask_cors import CORS

import os


class NetworkFileManager(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        app = Flask(__name__)
        CORS(app)

        UPLOAD_FOLDER = 'files'
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        @app.route('/upload', methods=['POST'])
        def upload_file():
            file_content = request.data

            file_path = os.path.join(UPLOAD_FOLDER, request.headers.get('Filename'))
            with open(file_path, 'wb') as file:
                file.write(file_content)

            return "OK", 200

        @app.route('/download/<filename>', methods=['GET'])
        def download_file(filename):
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            if not os.path.exists(file_path):
                return "Not Found", 404

            return send_file(file_path, as_attachment=True)

        app.run(port=4444)
