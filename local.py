import os
import whisper
import requests
import json
import tkinter as tk
# import torch
import subprocess
from tkinter import filedialog, messagebox, scrolledtext
# from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

try:
        # Run Ollama command with the prompt
        process = subprocess.Popen(
            'pip install openai-whisper',
           shell=True
        )
        run_ollama_command()
        
except Exception as e:
        messagebox.showerror("Whisper Error", str(e))
        # return None

# Load the Whisper model (choose desired size: "base", "small", etc.)
whisper_model = whisper.load_model("base")

# Global variable to hold the last transcript text.
current_transcript = ""

def select_file():
    file_path = filedialog.askopenfilename(title="Select Audio File",
                                           filetypes=[("Audio Files", "*.wav *.m4a *.mp3 *.mp4"), ("All Files", "*.*")])
    if file_path:
        file_label.config(text=file_path)
    else:
        file_label.config(text="No file selected")

def transcribe_audio():
    global current_transcript
    file_path = file_label.cget("text")
    if not file_path or file_path == "No file selected":
        messagebox.showerror("Error", "Please select an audio file first.")
        return

    try:
        # Transcribe using Whisper.
        result = whisper_model.transcribe(file_path)
        transcript = result.get("text", "")
        current_transcript = transcript
        output_text.insert(tk.END, "=== Transcript ===\n" + transcript + "\n\n")
    except Exception as e:
        messagebox.showerror("Error", f"Transcription failed: {str(e)}")
def run_ollama_command():
    try:
        # Run Ollama command with the prompt
        process = subprocess.Popen(
            'ollama serve',
           shell=True
        )
        process = subprocess.Popen(
            'ollama pull deepseek-r1:1.5b',
           shell=True
        )
        
    except Exception as e:
        messagebox.showerror("Ollama Error", str(e))
        return None


def summarize_meeting():
    global current_transcript
    if not current_transcript:
        transcribe_audio()
    # current_transcript = "Just wanted to go over some of the keyword strategies for ASO, kind of prioritize the keywords that we want to target and monitor, and make some use to see what you guys have to share, and then kind of got to figure out then how to incorporate those into our product page. The screenshot test, so I did take a look at your research history is really helpful. I put a request into Creative to create a set of, a new set of app source screenshots. I think the, I think it's pretty clear that kind of where we need to get to. I want to take this in two steps. One is, I think, one of what I've, what I've seen, what's really clear is that like our screenshots right now are talking about, like these advanced teachers that probably are not relevant for somebody who's has in download the app and is just trying to like, scan something, and we're talking about like multi-page stuff like it doesn't seem super relevant for like a first time user, and so we need to just go back to like the core functionality of the app and prioritize that. So I want to do that test first to compare that and see what the lift is versus our current screenshots, and then afterwards I want to have the Creative Team develop a series like multiple versions of a video. So my guess is that we'll probably have some sort of lift from this updated batch of screenshots, and then I want to optimize that with the right video. So I think once we get that we should be pretty up far with our competitors. Cool, and then the third thing would be around, Estre, if you had some time to look into any of the ASL specific tools, if you had like thoughts on a vendor that we can look into further, and then I think you are also looking into custom product pages as well, or did you already, yeah, okay, cool. Sounds good. Anything else that you guys would like to talk about? No, I think those key things that we powered up we spent most try yesterday, we're wrapping those things out because I'm really looking at the ASL keywords piece, and I took up the custom product pages, so we both kind of thought of dividing and conquering this meeting, okay, but how big anything else you'd like to add up? What's that? I think that's it. Can we get started with the keywords piece? Yeah, let's do it. Once again, I'm sharing my screen. Okay, so I'll give a brief summary of how I have approached this. So first, I looked at the competitor keywords, the tools that I used were ASO mobile, I got the competitor, added the competitors and got what keywords that they were using, and then I used Actweek keywords, again, same competitor keywords, along with there was an AI feature that was such as new keywords based on what everybody else is using. So I downloaded that list and cleaned up some of it, and then we'll go over what are the traffic or the KIA metrics that we said we spoke about. So on the summary tab, I have the list of keywords that I thought would be good to track. So based on the criteria that we discussed in our last meeting, where we needed medium amount of traffic and the complex city should be lesser so that we are able to rank since we are a new app, if it is highly competitive, it would be very difficult for us to rank. And then in ASO mobile, they give a specific effectiveness score. So what this means is based on this particular keyword, how much intent the user has to install that particular app. So if the effectiveness is high, so many of the users who search for this particular keyword are installing the app. And then they also have a metric called popularity in search ads, meaning how many people bid for this particular keyword in app search ads. So I've taken that into also account. So this popularity is very high, maybe a lot of people are bidding on that, and then our cost per acquisition would be high and cost per install would also be high. So I was trying to find a sweet spot where we can target those specific keywords and at the same time use them in app search ads. So in this action recommended is we can keep track of these keywords and try to rank for this and then comments is for some of those keywords, we are running those, but either the spend is low or we are not using this exact words, scan documents free or we are using free scan documents app or app scanning documents, some version of that, but not exactly like these words. So I looked at like what are the words that we are running and try to compare like okay does it, are we already running it or like some version of it is there or not. So PDF scanner, I think it's one that we should keep track of and then it is not it, it's not running, maybe we ran it and we paused it, but it is not currently live. And then like some other thing is like documents by rattle like this is the exact competitor, the keywords are their title, do this. So I see like they have decent traffic maybe because they are doing like a lot of search ads. So what I thought was we can do this, we can use their strategy of promoting their app and bid on it if we have scan guru or turbo scan or something like this, we can build and try to get installs from those keywords also. So whatever if mark does not active, we are not running it currently. So that is like the first set of keywords and then second one is like from app to week, like I got like ID me, ID scanner and then the ships scanner these things, so which we are not currently running. So here I have taken this core to be like around 30 to 40, 45 range not very high so that like it's easier for us to run rank and then like we have some decent volume. So if you want to look at like all the specific what is the raw data and then like if you want some some more suggestions also we have the entire data here and I have listed down the criteria that I have considered. So that is the first set of any questions? No, if you go can you go back to the summary? Okay, so if I were to is this kind of the full list of recommendations or is there? No, these are the full list of recommendations. Okay, okay, god damn, thank you. Yeah, it's interesting, I think right like from what I've seen in our Apple search ads campaigns, it's very expensive to bid and to get installs from competitor keywords, but it's pretty much not worth it. I think there may be some of these smaller ones like I think the one that you mentioned like documents already that we could just but like yeah, we'll see. I know I don't have a lot of like okay, yeah, I don't see a ton of potential in there. I think I think there should we should focus more on I mean we can try like I do not say not to do it. I think a little bit we'll just put those into our competitor and group in okay, competitor campaign in Apple search ads. I wouldn't see how they go doesn't hurt, but yeah, from what I've seen is it's tough to can make that cost work. So that's why like I think there's more opportunity in more of the category keywords. So if you scroll down, yeah, some of these ones have like a lot of sense. Yeah, it'd be good. Okay, cool. I think the thing that would be great is the love that you've kind done this and work through this approach. Well, I think I would like for you to think about is like how do we systematize this process because we want to be doing this like every week, right? And we want to be doing this for we're going to need to be doing this for two to four or five six months. So how can you do this? That's less time for you. That's maybe a bit more. And I made it like just think about that process because I'd love to be able to have this like this week we're going to be targeting these years. These like have a new patch every week. Yeah, not have that take like all your time. So I think that would be kind of like something we can think about working forward. And I think this is super cool and have these recommendations so that we can just put them in maybe like we get these once a week and we can add that into our kind of like ASA optimizations. Got it. Okay, so I think for ASA, I think a lot of these big recommendations make sense. For ASO, essentially keywords that we want to be think like leveraging in our product page. Are you were you thinking of the same keyword list or is it? So I was thinking more about like the not the competitor words but the like the normal words. I can look at the description of all the other ads like what is the type of words that they are using or like and then I can get that like description separately as well. That would be more. Yeah, okay. Yeah, no, I think that makes sense. Okay, these these ones here. I'm sure we'll find a way to like add like genius somewhere. Okay, cool. I like that. Okay, so I'll think I'll think that kind of a second chart that makes sense. And then it's just a matter of like how do we tweak some of our description skills and stuff like that to that Apple actually just to rank to a copy of this. So that makes sense. Cool. Yeah, thank you. Thank you for this. I'll take a look which looks really good. So the second thing that I did was I looked at the existing like keywords that we have in our campaigns, right? And then like I was looking at okay for document app, the average CPA comes out to be like $30 and then like even though we have like 834 impressions, we just have one installs. So I just like collated keywords where the CPA is like very high and we are spending some amount on it. So if you want to take a look at this and then like maybe what do you say move them to a different campaign or like from exact match, move them to a broad match so that like we have more traffic coming in and then like obviously you're changing up the creatives would definitely help because like we have so much impression. So this keyword is like "

    try:
        
        # Ollama API endpoint
        url = "http://localhost:11434/api/generate"
        
        # Prepare the prompt for Ollama
        prompt = (
            "You are an assistant that summarizes meeting transcripts. "
            "Provide a concise summary of the meeting and list the key action items.\n\n"
            "Transcript:\n" + current_transcript
        )

        # Request payload
        payload = {
            "model": "deepseek-r1:1.5b",  # You can change this to your preferred Ollama model
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 4096
            }
        }

        print("request sent")
        # Send request to Ollama
        response = requests.post(url, json=payload)
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse the response
            response_data = response.json()
            summary = response_data.get('response', 'No summary generated.')
            
            # Insert summary into output text
            output_text.insert(tk.END, "=== Meeting Notes ===\n" + summary + "\n\n")
        else:
            messagebox.showerror("Error", f"Failed to generate meeting notes. Status code: {response.status_code}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate meeting notes: {str(e)}")

# Build the Tkinter UI.
root = tk.Tk()
root.title("Audio Transcription and Meeting Notes")

# File selection frame.
file_frame = tk.Frame(root)
file_frame.pack(padx=10, pady=10, fill=tk.X)

select_btn = tk.Button(file_frame, text="Select Audio File", command=select_file)
select_btn.pack(side=tk.LEFT)

file_label = tk.Label(file_frame, text="No file selected", wraplength=400)
file_label.pack(side=tk.LEFT, padx=10)

# Buttons frame.
btn_frame = tk.Frame(root)
btn_frame.pack(padx=10, pady=5)

transcribe_btn = tk.Button(btn_frame, text="Transcribe Audio", command=transcribe_audio)
transcribe_btn.pack(side=tk.LEFT, padx=5)

summarize_btn = tk.Button(btn_frame, text="Get Meeting Notes", command=summarize_meeting)
summarize_btn.pack(side=tk.LEFT, padx=5)

# Output area.
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
output_text.pack(padx=10, pady=10)

root.mainloop()
