import tkinter as tk
from gtts import gTTS
from langdetect import detect
import os
import uuid
import time
import pygame
import json
import speech_recognition as sr
import difflib
import string
import threading

pygame.mixer.init()

# Load responses.json
with open("responses.json", "r", encoding="utf-8") as f:
    responses_data = json.load(f)

def clean_input(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_response(user_input, lang):
    user_input = clean_input(user_input)
    lang_responses = responses_data.get(lang, responses_data['en'])

    for key_phrase in lang_responses:
        if key_phrase in user_input:
            return lang_responses[key_phrase]

    close = difflib.get_close_matches(user_input, lang_responses.keys(), n=1, cutoff=0.5)
    if close:
        return lang_responses[close[0]]

    return "I'm still learning. Could you rephrase that?" if lang == "en" else "माफ़ कीजिए, मैं अभी उस सवाल को नहीं समझ पाया।"

def speak(text, lang_code):
    try:
        filename = f"{uuid.uuid4()}.mp3"
        tts = gTTS(text=text, lang='hi' if lang_code == 'hi' else 'en')
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.3)
        os.remove(filename)
    except Exception as e:
        print(f"Error speaking: {e}")

def listen_and_respond():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        label_user_input.config(text="Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # Try recognizing speech (broadly for Indian languages)
        user_text = recognizer.recognize_google(audio, language="hi-IN")
        print(f"[DEBUG] Raw Recognized Text: {user_text}")

        # Now use langdetect on this text
        lang = detect(user_text)
        print(f"[DEBUG] Detected Language: {lang}")

        label_user_input.config(text=f"You said: {user_text}")

        response = get_bot_response(user_text, lang)
        label_bot_response.config(text=f"Bot says: {response}")
        speak(response, lang)

    except sr.UnknownValueError:
        label_user_input.config(text="Didn't understand. Try again.")
        label_bot_response.config(text="")

def start_listening():
    threading.Thread(target=listen_and_respond).start()

def exit_app():
    root.destroy()

root = tk.Tk()
root.title("Multilingual Voice Chatbot")
root.geometry("400x250")
root.resizable(False, False)

tk.Label(root, text="🎙️ Voice-Enabled Chatbot", font=("Helvetica", 16, "bold")).pack(pady=10)

label_user_input = tk.Label(root, text="You said: ", font=("Helvetica", 12))
label_user_input.pack(pady=5)

label_bot_response = tk.Label(root, text="Bot says: ", font=("Helvetica", 12))
label_bot_response.pack(pady=5)

btn_speak = tk.Button(root, text="🎤 Speak Now", font=("Helvetica", 12), command=start_listening)
btn_speak.pack(pady=10)

btn_exit = tk.Button(root, text="❌ Exit", font=("Helvetica", 12), command=exit_app)
btn_exit.pack(pady=5)

root.mainloop()