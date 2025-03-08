import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import requests

# Configure logging (optional)
# logging.basicConfig(level=print)

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            current_time = time.time()
            print("AAAAB")
            print("File created: %s", event.src_path)
            file_creation_time = os.path.getctime(event.src_path)
            print(current_time - file_creation_time)
            if (current_time - file_creation_time) <= 300:  # within last 5 minutes
                print("New file detected within the last 5 minutes.")
                print("Processing file: %s", event.src_path)
                
                # Wait a few seconds to allow the file to be fully written and released
                time.sleep(5)  # adjust delay as needed
                print("Trying!!!")
                # Retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        with open(event.src_path, 'rb') as f:
                            files = {'file': (os.path.basename(event.src_path), f)}
                            url = "http://127.0.0.1:5000/summarize"
                            response = requests.post(url, files=files)
                            print("Response from /summarize: %s", response.text)
                        break  # exit the loop if successful
                    except Exception as e:
                        print("Attempt %d: Failed to make POST request: %s", attempt+1, str(e))
                        time.sleep(5)  # wait before retrying

def start_file_monitoring(path_to_watch):
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    observer.start()
    print("Started monitoring new files in:", path_to_watch)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitoring.")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Use a raw string to avoid unicode escape issues in Windows paths
    username = os.getenv("USERNAME")
    path_to_watch = rf"C:\Users\{username}\Videos\Captures"
    start_file_monitoring(path_to_watch)
