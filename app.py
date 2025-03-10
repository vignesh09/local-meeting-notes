import os
import sys
import whisper
import requests
import json
import time
import subprocess
from flask import Flask, request, render_template, jsonify, redirect, url_for
from docx import Document
import logging
import datetime
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account


# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "uploads")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logging.basicConfig(level=logging.DEBUG)
logging.debug("Logger enabled")

# Global variables for transcript and meeting notes
transcript = None
meeting_notes = None
start_time = None

# Global settings dictionary for user-configurable settings
app_settings = {
    "timezone": "UTC",
    "sender_email": "vignez.sr@gmail.com",
    "model": "gemma:7b"
}

########################################### Calendar Functions ###############################################
# Scopes required for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar.events'
]

def get_google_services():
    """
    Runs the OAuth flow and returns authorized Gmail and Calendar service objects.
    The token will be stored in token.json.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials are available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    gmail_service = build('gmail', 'v1', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)
    return gmail_service, calendar_service

def send_email_with_transcript(gmail_service, sender_email, recipient_email):
    """
    Sends an email using Gmail API with the transcript attached.
    """
    global transcript
    global meeting_notes
    message = MIMEMultipart("mixed")
    message["to"] = recipient_email
    message["from"] = sender_email
    message["subject"] = "Meeting Transcript and Invitation"

    body_text = f"""Hello,

Please find attached the transcript of our meeting.

Meeting Notes:
{meeting_notes}

Best regards,
Team Local Notes.
"""
    message.attach(MIMEText(body_text, "plain"))

    transcript_attachment = MIMEText(transcript, "plain")
    transcript_attachment.add_header("Content-Disposition", "attachment", filename="transcript.txt")
    message.attach(transcript_attachment)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {"raw": raw_message}
    sent_message = gmail_service.users().messages().send(userId="me", body=message_body).execute()
    logging.debug("Email sent! Message ID:")
    logging.debug(sent_message.get("id"))

def create_calendar_invite(calendar_service, recipient_email, sender_email):
    """
    Creates a calendar event (invite) using the Calendar API.
    The event will be sent as an invitation to the recipient.
    """
    global meeting_notes
    global start_time
    # Use the configured timezone from settings if needed. Here, we assume UTC.
    event_end = start_time
    event_start = event_end - datetime.timedelta(minutes=10)
    
    event = {
        "summary": "Meeting Invitation: Generated Meeting Notes",
        "description": meeting_notes,
        "start": {
            "dateTime": event_start.isoformat() + "Z",
            "timeZone": app_settings["timezone"],
        },
        "end": {
            "dateTime": event_end.isoformat() + "Z",
            "timeZone": app_settings["timezone"],
        },
        "attendees": [
            {"email": recipient_email},
        ],
        "reminders": {
            "useDefault": True,
        },
    }
    created_event = calendar_service.events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all"
    ).execute()
    logging.debug("Calendar event created:")
    logging.debug(created_event.get("htmlLink"))

########################################### Flask Routes ###############################################

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    global app_settings
    if request.method == "POST":
        tz = request.form.get("timezone")
        sender = request.form.get("sender_email")
        model = request.form.get("model")
        if tz:
            app_settings["timezone"] = tz
        if sender:
            app_settings["sender_email"] = sender
        if model:
            app_settings["model"] = model
        return redirect(url_for("settings"))
    return render_template("settings.html", settings=app_settings)

@app.route("/summarize", methods=["POST"])
def summarize_route():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    file = request.files["file"]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return summarize(file_path)

def summarize(file_path):
    global start_time, transcript, meeting_notes
    start_time = datetime.datetime.now()
    logging.debug("Processing the file in this path:")
    logging.debug(file_path)

    if file_path.lower().endswith(".txt"):
        try:
            with open(file_path, "r") as f:
                transcript = f.read()
        except Exception as e:
            return jsonify({"error": "Error reading transcript file: " + str(e)}), 500
    elif file_path.lower().endswith(".docx"):
        try:
            doc = Document(file_path)
            transcript = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return jsonify({"error": "Error reading DOCX file: " + str(e)}), 500
    else:
        try:
            logging.debug("Using Whisper for transcription")
            # Use the model from settings
            model_name = app_settings["model"]
            whisper_model = whisper.load_model("base")  # Change if you support other models dynamically
            result = whisper_model.transcribe(file_path)
            transcript = result.get("text", "")
            logging.debug("Transcript:")
            logging.debug(transcript)
        except Exception as e:
            return jsonify({"error": "Transcription failed: " + str(e)}), 500

    prompt = (
        """You are an assistant that summarizes meeting transcripts. Your primary goal is to produce a concise, clear, and professional summary of the meeting while extracting key action items. Use the following guidelines to craft your output:

1. **Meeting Summary:**
   - Provide a comprehensive overview of the meeting.
   - Identify and describe the main objectives and discussion points.
   - Highlight decisions made, conclusions reached, and any critical context.
   - Ensure the summary is well-organized.

2. **Action Items:**
   - Extract all actionable tasks mentioned.
   - List each action item using bullet points.
   - For each action item, include:
     - A clear description of the task.
     - The person(s) responsible (if mentioned).
     - Any deadlines or timeframes specified.
   - If details are missing, note placeholders as needed.

Be as detailed as possible.

**Transcript:**""" + transcript
    )
    payload = {
        "model": app_settings["model"],
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "max_tokens": 8000
        }
    }
    try:
        url = "http://localhost:11434/api/generate"
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            meeting_notes = response_data.get("response", "No summary generated.")
            send_calendar_invite()  # This sends both email and calendar invite
            return jsonify({"summary": meeting_notes}), 200
        else:
            return jsonify({"error": f"Failed to generate meeting notes. Status code: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": "Summarization failed: " + str(e)}), 500

@app.route("/send-calendar-invite", methods=["GET"])
def send_calendar_invite():
    try:
        gmail_service, calendar_service = get_google_services()
        global meeting_notes, transcript
        sender = app_settings["sender_email"]
        recipient = sender  # For testing, using the sender email as recipient; change as needed.
        
        send_email_with_transcript(gmail_service, sender, recipient)
        create_calendar_invite(calendar_service, recipient, sender)
        return jsonify({"result": "successful"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send calendar invite: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
