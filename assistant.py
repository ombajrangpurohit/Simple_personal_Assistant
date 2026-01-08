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

# --- CONFIGURATION ---
MIC_INDEX = 2  # Your Laptop Mic

# Initialize Recognizer Globally
recognizer = sr.Recognizer()

# NOTE: We removed the global 'engine = ...' here. 
# We will initialize it inside speak() instead.

contacts = {
    # Add your contacts here
    # "fafnir": "+918529637410" 
}

def speak(text):
    print(f"Fafnir: {text}")
    
    # 1. Wait a split second for the Mic to fully release the driver
    t.sleep(0.5)
    
    try:
        # 2. Re-initialize the engine FRESH every time.
        # This prevents the "Loop Already Running" or "Silent" bugs.
        local_engine = pyttsx3.init('sapi5')
        
        voices = local_engine.getProperty('voices')
        try:
            local_engine.setProperty('voice', voices[1].id) # Female
        except:
            local_engine.setProperty('voice', voices[0].id) # Male fallback

        local_engine.say(text)
        local_engine.runAndWait()
        
        # 3. Clean up
        del local_engine
        
    except Exception as e:
        print(f"TTS Error: {e}")

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

def command_mode():
    query = listen()
    if not query:
        return

    if "send message to" in query:
        name = query.replace("send message to", "").strip()
        send_whatsapp_message(name)

    elif "send message" in query:
        send_whatsapp_message()

    elif "open vs code" in query:
        open_vs_code()

    elif "open youtube" in query:
        open_youtube()

    elif "open google" in query:
        open_google()
        
    elif "play" in query:
        song = query.replace("play", "").strip()
        speak(f"Playing {song}")
        kit.playonyt(song)
        
    elif "open github" in query:
        speak("Opening Github")
        s.press("win")
        t.sleep(1)
        s.write("msedge", interval=0.1)
        t.sleep(1)
        s.press("enter")
        t.sleep(2)
        s.hotkey("ctrl", "l")
        s.write("www.github.com", interval=0.1)
        s.press("enter")
    elif "play" in query:
        play_on_youtube(query)

    elif "stop" in query or "exit" in query:
        speak("Goodbye")
        sys.exit()

def run_fafnir():
    wish()
    while True:
        command_mode()

if __name__ == "__main__":
    run_fafnir()