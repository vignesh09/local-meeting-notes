@echo off
wsl bash -c "cd ~; rm -rf local-meeting-notes; git clone https://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@github.com/vignesh09/local-meeting-notes.git; python3 -m venv local-notes; source local-notes/bin/activate;cd local-meeting-notes; pip install -r requirements.txt; python local.py; exec bash"
