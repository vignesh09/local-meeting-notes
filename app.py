import os
import sys
import whisper
import requests
import json
import subprocess
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "uploads")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load the Whisper model (adjust the model size as needed)
whisper_model = whisper.load_model("base")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    # Ensure a file is provided
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file."}), 400

    # If the file is a transcript (.txt), read its contents
    if file.filename.lower().endswith(".txt"):
        try:
            transcript = file.read().decode("utf-8")
        except Exception as e:
            return jsonify({"error": "Error reading transcript file: " + str(e)}), 500
    else:
        # Otherwise assume it is an audio file and save it
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        if not os.path.exists(file_path):
            return jsonify({"error": "Uploaded file not found."}), 400
        try:
            result = whisper_model.transcribe(file_path)
            transcript = result.get("text", "")
        except Exception as e:
            return jsonify({"error": "Transcription failed: " + str(e)}), 500

    # Build the prompt for summarization
    prompt = (
        "You are an assistant that summarizes meeting transcripts. "
        "Provide a concise summary of the meeting and list the key action items.\n\n"
        "Transcript:\n" + transcript
    )
    payload = {
        "model": "deepseek-r1:1.5b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "max_tokens": 4096
        }
    }
    try:
        url = "http://localhost:1143/api/generate"
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            summary = response_data.get("response", "No summary generated.")
            return jsonify({"summary": summary}), 200
        else:
            return jsonify({"error": f"Failed to generate meeting notes. Status code: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": "Summarization failed: " + str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
