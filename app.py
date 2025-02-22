from flask import Flask, request, jsonify, send_file, render_template
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simulated database storing file info
files_db = []  # List of { "filename": ..., "sender": ..., "recipient": ... }

@app.route('/upload', methods=['POST'])
def upload_file():
    """ Handles file uploads and associates them with a specific recipient. """
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    recipient = request.form.get("recipient")  # Get recipient from form
    sender = request.remote_addr  # Sender's IP

    if not recipient:
        return jsonify({"error": "Recipient not specified"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Store file metadata
    files_db.append({
        "filename": file.filename,
        "sender": sender,
        "recipient": recipient
    })

    return jsonify({"message": "File uploaded successfully!"}), 200

@app.route('/get_files', methods=['GET'])
def get_files():
    """ Returns a list of files accessible to the requesting user. """
    user_ip = request.remote_addr
    user_files = [f for f in files_db if f["recipient"] == user_ip]

    return jsonify(user_files)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """ Allows only the recipient to download the file. """
    user_ip = request.remote_addr
    file_info = next((f for f in files_db if f["filename"] == filename), None)

    if not file_info:
        return jsonify({"error": "File not found"}), 404

    if file_info["recipient"] != user_ip:
        return jsonify({"error": "Access denied"}), 403

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
