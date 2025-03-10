Below is a sample `README.md` that you can include in your GitHub repository. It explains the project’s purpose, lists its dependencies, and provides step-by-step instructions to set up and run the application on Windows.

---

# Local Meeting Notes

Local Meeting Notes is a Flask-based application that uses OpenAI's Whisper for audio transcription, generates meeting summaries, sends emails with the transcript attached, and creates Google Calendar invites. The project also utilizes a file-watching mechanism (using `watchdog`) to automatically trigger the summarization process when a new file is detected in a specified folder.

## Features

- **Audio Transcription**: Transcribes audio files using OpenAI's Whisper.
- **Document Processing**: Supports `.txt` and `.docx` file formats.
- **Meeting Summary Generation**: Generates meeting summaries and extracts key action items by calling an external API.
- **Email Notifications**: Sends the transcript as an attachment via Gmail API.
- **Calendar Invites**: Creates and sends a Google Calendar event invite using the Calendar API.
- **File Watcher**: Monitors a specific folder for new files and triggers processing automatically.
- **Configurable Settings**: Provides a UI to update settings like timezone, sender email, and the model used for summarization.

## Prerequisites

This setup is designed for Windows and uses the following tools and dependencies:

- **Python 3.13**: Installed via Winget.
- **Git**: Installed via Winget.
- **FFmpeg**: Installed via Winget (Essentials Build).
- **Ollama**: Installed via Winget (for running models locally).
- **Virtual Environment**: For isolating Python dependencies.

## Installation and Setup

Follow these steps to set up your environment from scratch:

1. **Create and Activate a Virtual Environment**

   Open a Command Prompt and run:

   ```batch
   python -m venv local-notes
   local-notes\Scripts\activate
   ```

2. **Install System Dependencies with Winget**

   Install Git and FFmpeg if they are not already installed:

   ```batch
   winget install --id Git.Git
   winget install "FFmpeg (Essentials Build)"
   ```

3. **Clone the Repository**

   Within your activated virtual environment, clone this repository:

   ```batch
   git clone https://github.com/vignesh09/local-meeting-notes.git
   cd local-meeting-notes
   ```

4. **Upgrade pip and Install Python Dependencies**

   Upgrade pip and install required packages:

   ```batch
   python -m pip install --upgrade pip
   pip install git+https://github.com/openai/whisper.git
   pip install python-docx
   pip install Flask
   pip install watchdog
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

   > **Note:** There is no need to install `urlopen` separately; it’s part of Python's standard library.

5. **Set Up Ollama**

   Install Ollama via Winget if not already installed:

   ```batch
   winget install Ollama.Ollama
   ```

   Start Ollama Serve in a new command prompt (if needed):

   ```batch
   start "Ollama Serve" cmd /k "ollama serve"
   ```

   Then, set the environment variable for Ollama host:

   ```batch
   set OLLAMA_HOST=127.0.0.1:11434
   ```

   Pull the desired model (e.g., `llama3` or `gemma:7b`), and set its parameters as needed:
   
   ```bash
   # Example commands in the Ollama console:
   /set parameter num_ctx 32768
   /save qwen2.5max
   /bye
   ```

6. **Get Credentials.json**
   For using the Google authentication user your Google console to create a project and enable authentication API & Services and get oAuth client id and secret.

## Running the Application

1. **Start the Flask App**

   In your virtual environment, run:

   ```batch
   python app.py
   ```

   The Flask app will start (by default on [http://127.0.0.1:5000](http://127.0.0.1:5000)).

2. **Access the Application**

   - **Home Page:**  
     Open a browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) to see the home page.

   - **Settings Page:**  
     Visit [http://127.0.0.1:5000/settings](http://127.0.0.1:5000/settings) to update configuration options (timezone, sender email, and model).

   - **Summarization:**  
     Use the provided UI or send a POST request with a file to [http://127.0.0.1:5000/summarize](http://127.0.0.1:5000/summarize) to trigger the summarization process. The file can be a `.txt`, `.docx`, or audio file.

3. **File Watcher**

   The application includes a file watcher (using `watchdog`) that monitors a specified folder (by default, `C:\Users\<USERNAME>\Videos\Captures`) for new files created within the last 5 minutes. When a new file is detected, it automatically makes a POST request to the `/summarize` endpoint to process the file.

## Testing in an Isolated Environment

If you want to test this setup without affecting your main system:

- **Create a Virtual Environment**:  
  As described above, use `python -m venv local-notes` to create an isolated Python environment.

- **Windows Sandbox**:  
  You can also use Windows Sandbox to test system-level changes (such as running the BAT file for Git installation) without affecting your host system. Create a `.wsb` file to enable networking and launch the sandbox.

## BAT File for Dependency Checks

An example BAT file to check for Git and Python installation and proceed with setup:

```batch
@echo off
REM Check if Git is installed
git --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Git not found. Installing Git...
    winget install --id Git.Git
    echo Git installation completed. Please restart your command prompt to use Git.
) ELSE (
    echo Git is already installed.
    git --version
)

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found. Installing Python 3.13...
    winget install --id Python.Python.3.13
    echo Python 3.13 installation completed. Please restart your command prompt.
) ELSE (
    echo Python is already installed.
    python --version
)

REM (Optional) Start Ollama Serve if needed
start "Ollama Serve" cmd /k "ollama serve"
set OLLAMA_HOST=127.0.0.1:11434

REM Run the Flask app
python app.py
```

## Conclusion

This repository provides a complete setup for local meeting note processing using Flask, OpenAI's Whisper, Google APIs (Gmail and Calendar), and a file watcher. Follow the installation instructions carefully, and adjust settings via the provided UI to customize the experience.

Feel free to raise issues or contribute improvements via pull requests.

Happy coding!

---

You can adjust this README file as needed to fit your project specifics or additional instructions. Upload it to your GitHub repository, and others will have a clear guide to setting up and running your project.
