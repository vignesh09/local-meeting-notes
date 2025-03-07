import os
import sys
import whisper
import requests
import json
import time
import subprocess
from flask import Flask, request, render_template, jsonify
from docx import Document
import logging
######################################Calendar Events#############
import base64
import os
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

###################################################################

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "uploads")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logging.basicConfig(level=logging.DEBUG)
logging.debug("Logger enabled")

transcript = None
meeting_notes = None
start_time = None
###########################################Calendar Functions###############################################
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
        # Save the credentials for future runs.
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
    # Create the MIME message
    message = MIMEMultipart("mixed")
    message["to"] = recipient_email
    message["from"] = sender_email
    message["subject"] = "Meeting Transcript and Invitation"

    # Email body containing meeting notes
    body_text = f"""Hello,

Please find attached the transcript of our meeting.

Meeting Notes:
{meeting_notes}

Best regards,
Team Local Notes.
"""
    message.attach(MIMEText(body_text, "plain"))

    # Attach the transcript as a text file.
    transcript_attachment = MIMEText(transcript, "plain")
    transcript_attachment.add_header("Content-Disposition", "attachment", filename="transcript.txt")
    message.attach(transcript_attachment)

    # Encode the message and send via Gmail API.
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
    # Set event details – customize the timing as needed.
    global meeting_notes
    global start_time
    # Example: schedule event for tomorrow from 09:00 to 10:00 UTC.
    event_end = start_time
    event_start = event_end - datetime.timedelta(minutes=10)
    
    event = {
        "summary": "Meeting Invitation: Generated Meeting Notes",
        "description": meeting_notes,
        "start": {
            "dateTime": event_start.isoformat() + "Z",
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": event_end.isoformat() + "Z",
            "timeZone": "UTC",
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
        sendUpdates="all"  # This flag makes sure the invitation is emailed.
    ).execute()
    logging.debug("Calendar event created:")
    logging.debug(created_event.get("htmlLink"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize_route():
    # Simulate the summarize function
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    file = request.files["file"]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    return summarize(file_path)


def summarize(file_path):
    global start_time
    start_time = time.time()
    global transcript
    logging.debug("processing the file in this path: ")
    logging.debug(file_path)
    # # Ensure a file is provided
    # if "file" not in request.files:
    #     return jsonify({"error": "No file provided."}), 400
    # file = request.files["file"]
    # if file.filename == "":
    #     return jsonify({"error": "No selected file."}), 400clea

    # If the file is a transcript (.txt), read its contents
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
            # Load the Whisper model (adjust the model size as needed)
            logging.debug("Debugging using Whisper")
            whisper_model = whisper.load_model("large-v2")
            result = whisper_model.transcribe(file_path)
            transcript = result.get("text", "")
            logging.debug("#######Transcript##############")
            logging.debug(transcript)
        except Exception as e:
            return jsonify({"error": "Transcription failed: " + str(e)}), 500

    # Build the prompt for summarization
    prompt = (
        """You are an assistant that summarizes meeting transcripts. Your primary goal is to produce a concise, clear, and professional summary of the meeting while extracting key action items. Use the following guidelines to craft your output:

1. **Meeting Summary:**
   - Provide a brief, yet comprehensive, overview of the meeting.
   - Identify and describe the main objectives and discussion points.
   - Highlight decisions made, conclusions reached, and any critical context shared during the meeting.
   - Ensure the summary is well-organized.

2. **Action Items:**
   - Extract all actionable tasks mentioned during the meeting.
   - List each action item using bullet points.
   - For each action item, include:
     - A clear description of the task.
     - The person(s) responsible (if mentioned).
     - Any deadlines or timeframes specified.
   - If certain tasks lack details (such as the responsible person or due date), note the task clearly and leave placeholders if necessary.

**Transcript:**""" + transcript
    )
    payload = {
        "model": "gemma:7b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "max_tokens": 8000
        }
    }
    try:
        global meeting_notes
        url = "http://localhost:11434/api/generate"
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            meeting_notes = response_data.get("response", "No summary generated.")
            send_calendar_invite()
            return jsonify({"summary": meeting_notes}), 200
        else:
            return jsonify({"error": f"Failed to generate meeting notes. Status code: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": "Summarization failed: " + str(e)}), 500


@app.route("/send-calendar-invite", methods=["GET"])
def send_calendar_invite():
    # # Example usage
    # file_path = 'file.txt'
    # file_name = 'example.txt'
    # file_id = upload_file_to_drive(file_path, file_name)

    # event_title = 'Event with Attachment'
    # event_description = 'This event has an attached file.'

    # create_event_with_attachment(file_id, event_title, event_description)
    # return jsonify({"error": f"Failed to send calendar invite: {str(1234)}"}), 500

    try:
        gmail_service, calendar_service = get_google_services()
        global meeting_notes
        global transcript
        # Sample data (replace with your dynamic transcript and meeting notes)
        # sample_transcript = "This is the meeting transcript..."
        # sample_meeting_notes = "Meeting notes: Discussed project updates, action items, and next steps."
        sender = "vignez.sr@gmail.com"
        recipient = "vignez.sr@gmail.com"
        
        # Send the email with transcript attachment.
        send_email_with_transcript(gmail_service, sender, recipient)
        
        # Create a calendar event that sends an invite.
        create_calendar_invite(calendar_service, recipient, sender)
        return jsonify({"result": f"successful"}),200
    except Exception as e:
        return jsonify({"error": f"Failed to send calendar invite: {str(e)}"}), 500

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        with app.app_context():
            if not event.is_directory:
                current_time = time.time()
                file_creation_time = os.path.getctime(event.src_path)
                if (current_time - file_creation_time) <= 300:  # 300 seconds = 5 minutes
                    logging.debug(f"New file created")
                    logging.debug(str(event.src_path))
                    summarize(event.src_path)

def start_file_monitoring(path_to_watch):
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    observer.start()
    print(f"Started monitoring new files in: {path_to_watch}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    path_to_watch = "C:\\Users\\"+os.getenv("USERNAME")+"\\Videos\\Captures"
    monitoring_thread = threading.Thread(target=start_file_monitoring, args=(path_to_watch,), daemon=True)
    monitoring_thread.start()
    app.run(debug=True)
