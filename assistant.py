import pyttsx3
import speech_recognition as sr
import webbrowser
import pywhatkit as kit
import time as t
import sys
import datetime
import pygetwindow as gw
import pyautogui as s
from deep_translator import GoogleTranslator
import wikipedia
import google.generativeai as genai
import os
import pygame
import asyncio
import edge_tts
from textblob import TextBlob

# --- CONFIGURATION ---
MIC_INDEX = 1  # Your Laptop Mic

# Initialize Recognizer Globally
recognizer = sr.Recognizer()

# NOTE: We removed the global 'engine = ...' here. 
# We will initialize it inside speak() instead.

contacts = {
    # Add your contacts here
    # "fafnir": "+918529637410" 
}


# Initialize Pygame Mixer for playing audio
pygame.mixer.init()

async def generate_voice(text):
    # Voices: "en-US-AriaNeural" (Female) or "en-US-GuyNeural" (Male)
    voice = "en-US-AriaNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("temp_voice.mp3")

async def generate_emotional_voice(text, emotion):
    voice = "en-IN-NeerjaNeural"  # Use "en-US-GuyNeural" for male
    
    # DEFAULT SETTINGS (Neutral)
    rate = "+0%"
    pitch = "+0Hz"
    
    # ADJUST VOICE BASED ON EMOTION
    if emotion == "happy":
        rate = "+15%"    # Speak faster
        pitch = "+5Hz"   # Higher pitch (sound excited)
    elif emotion == "sad":
        rate = "-15%"    # Speak slower
        pitch = "-5Hz"   # Lower pitch (sound down)
    elif emotion == "angry":
        rate = "+10%"    # Fast
        pitch = "-2Hz"   # Slightly deeper/serious
    
    # Generate the audio with these settings
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save("temp_voice.mp3")

def speak(text, emotion="neutral"):
    print(f"Fafnir ({emotion}): {text}")
    
    try:
        # Generate audio
        asyncio.run(generate_emotional_voice(text, emotion))
        
        # Play audio
        pygame.mixer.music.load("temp_voice.mp3")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Audio Error: {e}")

def listen(phrase_time_limit=5):
    global recognizer

    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.0

    # FIX: Removed 'device_index=MIC_INDEX'
    # using 'source=None' forces it to use the System Default Mic
    try:
        with sr.Microphone() as source:
            print("\nListening via Default Microphone...")
            
            # This line caused your crash before; now it's wrapped in safety
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                print("... Time out (Silence)")
                return ""
    except OSError:
        print("ERROR: No microphone found! Check your Windows Sound Settings.")
        return ""

    try:
        print("Recognizing...")
        raw_query = recognizer.recognize_google(audio, language="hi-IN")
        print(f"User (Raw): {raw_query}")

        english_query = GoogleTranslator(source='auto', target='en').translate(raw_query)
        english_query = english_query.lower()
        
        print(f"Translated to: {english_query}")
        return english_query

    except sr.UnknownValueError:
        print("... Unclear audio")
        return ""
    except sr.RequestError:
        print("... Internet connection error")
        return ""
    except Exception as e:
        print(f"... Translation/Error: {e}")
        return ""

def wish():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        greet = "Good Morning Sir"
    elif hour >= 12 and hour < 18:
        greet = "Good Afternoon Sir"
    else:
        greet = "Good Evening Sir"
    speak(f"{greet}")

def get_emotion(query):
    # 1. Check for specific keywords first (Manual Override)
    query = query.lower()
    if any(word in query for word in ["sad", "cry", "depressed", "heartbroken"]):
        return "sad"
    elif any(word in query for word in ["happy", "great", "joy", "excited", "wow"]):
        return "happy"
    elif any(word in query for word in ["angry", "mad", "hate", "stupid"]):
        return "angry"
    
    # 2. Use TextBlob for automatic detection
    analysis = TextBlob(query)
    polarity = analysis.sentiment.polarity # Score from -1 to +1
    
    if polarity > 0.3:
        return "happy"
    elif polarity < -0.3:
        return "sad"
    else:
        return "neutral"

def search_wikipedia(query):
    speak("Searching Wikipedia...")
    # Remove command words to get the actual topic
    query = query.replace("wikipedia", "").replace("search", "").replace("who is", "").replace("what is", "").strip()
    
    try:
        # Get a short summary (2 sentences)
        results = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia")
        print(results)
        speak(results)
    except Exception:
        speak("I couldn't find any information on that topic.")

def send_whatsapp_message(name=None):
    if not name:
        speak("Who do you want to message?")
        name = listen()

    if name not in contacts:
        speak(f"I couldn't find {name} in your contact list.")
        return

    speak(f"What should I say to {name}?")
    message = listen()

    if not message:
        speak("I didn't hear a message. Cancelling.")
        return

    speak(f"Sending message to {name}")

    s.press("win")
    t.sleep(1)
    s.write("whatsapp", interval=0.1)
    t.sleep(1)
    s.press("enter")

    t.sleep(3) # Wait for App to open

    s.hotkey('ctrl', 'f')
    t.sleep(1)

    s.write(name)
    t.sleep(2)

    s.press('down')
    t.sleep(0.5)
    s.press('enter')
    t.sleep(1)

    s.write(message, interval=0.1)
    t.sleep(0.5)
    s.press('enter')

    speak("Message sent")

def open_vs_code():
    try:
        windows = gw.getWindowsWithTitle("Visual Studio Code")
        if windows:
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            speak("Visual Studio Code is already open")
            return
    except Exception:
        pass
        
    speak("Opening Visual Studio Code")
    s.press("win")
    t.sleep(1)
    s.write("vs code", interval=0.1)
    t.sleep(1)
    s.press("enter")

def open_youtube():
    speak("Opening YouTube")
    s.press("win")
    t.sleep(1)
    s.write("msedge", interval=0.1)
    t.sleep(1)
    s.press("enter")
    
    t.sleep(2) # Wait for Edge to open
    
    s.hotkey("ctrl", "l") # Highlight Address Bar
    t.sleep(0.5)
    s.write("www.youtube.com", interval=0.1)
    s.press("enter")

def open_google():
    speak("Opening Google")
    s.press("win")
    t.sleep(1)
    s.write("msedge", interval=0.1)
    t.sleep(1)
    s.press("enter")
    
    t.sleep(2)
    
    s.hotkey("ctrl", "l")
    t.sleep(0.5)
    s.write("www.google.com", interval=0.1)
    s.press("enter")

genai.configure(api_key="AIzaSyDoCZa9Ws3UNTWnPfgOWvIroyHYsy_HhS4")
# 'gemini-1.5-flash' is the newer, faster model
model = genai.GenerativeModel('gemini-flash-latest')

def ask_ai(query):
    try:
        response = model.generate_content(query)
        # Clean text (remove * or # symbols that AI uses for formatting)
        clean_text = response.text.replace("*", "").replace("#", "")
        speak(clean_text)
    except Exception as e:
        print(f"AI Error: {e}")
        speak("I am having trouble connecting to the AI brain.")


def play_on_youtube(query):
    # Remove the word "play" to get the actual song name
    video = query.replace("play", "").strip()
    
    if not video:
        speak("What should I play?")
        # Optional: Listen again if they didn't say a name
        video = listen()
        if not video:
            return

    speak(f"Playing {video} on YouTube")
    
    try:
        # kit.playonyt automatically searches and plays the first result
        kit.playonyt(video)
    except Exception as e:
        print(f"Error playing video: {e}")
        speak("I couldn't play the video.")

def take_screenshot():
    speak("Taking screenshot")
    # Save with a timestamp so files don't overwrite each other
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Make sure you create a 'screenshots' folder, or just save to C drive
    s.screenshot(f"screenshot_{timestamp}.png")
    speak("Screenshot saved")

def system_control(command):
    if "volume up" in command:
        s.press("volumeup")
        s.press("volumeup") # Press twice for noticeable change
        speak("Volume increased")
    elif "volume down" in command:
        s.press("volumedown")
        s.press("volumedown")
        speak("Volume decreased")
    elif "mute" in command:
        s.press("volumemute")
        speak("System muted")

def command_mode():
    # 1. Listen for the command
    query = listen()
    if not query:
        return

    # 2. Detect Emotion (Happy/Sad/Angry/Neutral)
    # This determines HOW Fafnir speaks back to you
    current_emotion = get_emotion(query)

    # --- SPECIFIC COMMANDS (The Old Stuff) ---
    
    if "send message to" in query:
        name = query.replace("send message to", "").strip()
        # You can even pass the emotion to these functions if you update them
        send_whatsapp_message(name)

    elif "send message" in query:
        send_whatsapp_message()

    elif "open vs code" in query:
        # We pass 'current_emotion' so he sounds happy if you are happy!
        speak("Opening Visual Studio Code", current_emotion)
        open_vs_code()

    elif "open whatsapp" in query:
        speak("Opening WhatsApp", current_emotion)
        s.press("win")
        t.sleep(1)
        s.write("whatsapp", interval=0.1)
        t.sleep(1)
        s.press("enter")

    elif "open youtube" in query:
        # Note: Your open_youtube function handles its own speaking.
        # Ideally, update open_youtube() to accept an 'emotion' argument too.
        open_youtube()

    elif "open google" in query:
        open_google()
        
    elif "play" in query:
        play_on_youtube(query)
        
    elif "open github" in query:
        speak("Opening Github", current_emotion)
        s.press("win")
        t.sleep(1)
        s.write("msedge", interval=0.1)
        t.sleep(1)
        s.press("enter")
        t.sleep(2)
        s.hotkey("ctrl", "l")
        s.write("www.github.com", interval=0.1)
        s.press("enter")

    elif "wikipedia" in query or "who is" in query or "what is" in query:
        search_wikipedia(query)
        
    elif "screenshot" in query:
        take_screenshot()
        
    elif "volume" in query or "mute" in query:
        system_control(query)

    elif "stop" in query or "exit" in query:
        speak("Goodbye, Sir.", current_emotion)
        sys.exit()

    # --- AI FALLBACK (The New Stuff) ---
    # If NONE of the above commands matched, ask the AI
    else:
        # If you are using Gemini
        try:
            # Generate the text answer
            response = model.generate_content(query)
            clean_text = response.text.replace("*", "").replace("#", "")
            
            # Speak it using the emotion detected earlier
            speak(clean_text, current_emotion)
        except Exception as e:
            print(f"AI Error: {e}")
            speak("I am having trouble connecting to the internet brain.", "sad")

def run_fafnir():
    wish()
    while True:
        command_mode()

if __name__ == "__main__":
    run_fafnir()