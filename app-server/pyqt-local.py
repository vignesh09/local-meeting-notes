import sys
import os
import whisper
import requests
import json
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt


print(os.getcwd())
class DropArea(QLabel):
    def __init__(self, parent=None):
        super(DropArea, self).__init__(parent)
        self.setText("Drag and drop an audio file here")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed #aaa; padding: 20px;")
        self.setAcceptDrops(True)
        self.file_path = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            # Use the first dropped file
            self.file_path = urls[0].toLocalFile()
            self.setText(f"File Selected:\n{self.file_path}")
            event.acceptProposedAction()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Transcription and Meeting Notes")
        self.current_transcript = ""
        
        # Load the Whisper model (adjust the model size if needed)
        self.whisper_model = whisper.load_model("base")
        
        # Optionally install openai-whisper and run Ollama commands
        try:
            # subprocess.Popen('pip install openai-whisper', shell=True)
            self.run_ollama_command()
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", str(e))
        
        # Build UI using PyQt
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Drag and drop area for audio file
        self.drop_area = DropArea()
        layout.addWidget(self.drop_area)
        
        # Button to transcribe audio
        self.transcribe_btn = QPushButton("Transcribe Audio")
        self.transcribe_btn.clicked.connect(self.transcribe_audio)
        layout.addWidget(self.transcribe_btn)
        
        # Button to generate meeting notes
        self.summarize_btn = QPushButton("Get Meeting Notes")
        self.summarize_btn.clicked.connect(self.summarize_meeting)
        layout.addWidget(self.summarize_btn)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        central_widget.setLayout(layout)
    
    def run_ollama_command(self):
        try:
            # Start Ollama serve and pull a model
            subprocess.Popen('ollama serve', shell=True)
            subprocess.Popen('ollama pull deepseek-r1:1.5b', shell=True)
        except Exception as e:
            QMessageBox.critical(self, "Ollama Error", str(e))
    
    def transcribe_audio(self):
        file_path = self.drop_area.file_path
        file_path = r"C:\Users\r.vignesh\local-notes\local-meeting-notes\test.mp4"
        if not file_path:
            QMessageBox.critical(self, "Error", "Please drag and drop an audio file first.")
            return
        try:
            self.output_text.append("Transcribing audio...\n")
            # Transcribe the audio file using Whisper
            print(file_path)
            result = self.whisper_model.transcribe(file_path)
            transcript = result.get("text", "")
            self.current_transcript = transcript
            self.output_text.append("=== Transcript ===\n" + transcript + "\n")
        except Exception as e:
            QMessageBox.critical(self, "Transcription Error", f"Transcription failed: {str(e)}")
    
    def summarize_meeting(self):
        # If there is no transcript, try transcribing first
        if not self.current_transcript:
            self.transcribe_audio()
        prompt = (
            "You are an assistant that summarizes meeting transcripts. "
            "Provide a concise summary of the meeting and list the key action items.\n\n"
            "Transcript:\n" + self.current_transcript
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
            url = "http://localhost:11434/api/generate"
            self.output_text.append("Requesting meeting summary...\n")
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                summary = response_data.get('response', 'No summary generated.')
                self.output_text.append("=== Meeting Notes ===\n" + summary + "\n")
            else:
                QMessageBox.critical(self, "Error", f"Failed to generate meeting notes. Status code: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate meeting notes: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
