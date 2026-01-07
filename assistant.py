import pyttsx3
import speech_recognition as sr
import webbrowser
import pywhatkit as kit
import time as t
import sys
import datetime
import pygetwindow as gw
import pyautogui as s
from googletrans import Translator

# --- CONFIGURATION ---
# Based on your image, Index 2 is likely your main Laptop Mic.
# If you use a headset, change this to 1.
MIC_INDEX = 1

# Initialize Recognizer
recognizer = sr.Recognizer()

# Initialize Engine globally (Fixes crash/loop issues)
try:
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    # Try index 1 for female voice, 0 for male.
    # If 1 gives an error, change to 0.
    engine.setProperty('voice', voices[1].id)
except Exception as e:
    print(f"TTS Engine Error: {e}")

contacts = {
    "owner": "+919938864548",
    "gorilla" : "+919438287938"
}


def speak(text):
    print(f"Fafnir: {text}")  # Print so you can see it trying to speak
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS Error:", e)


def listen(phrase_time_limit=5):
    global recognizer

    # Energy threshold settings
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.0

    with sr.Microphone(device_index=MIC_INDEX) as source:
        print(f"\nListening via Mic Index {MIC_INDEX}...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("... Time out (Silence)")
            return ""

    try:
        print("Recognizing...")
        # We use 'hi-IN' because it captures both Hindi and English words well
        raw_query = recognizer.recognize_google(audio, language="hi-IN")
        print(f"User (Raw): {raw_query}")

        # --- TRANSLATION LAYER ---
        translator = Translator()
        # Translate whatever was said into English
        translated = translator.translate(raw_query, dest='en')
        english_query = translated.text.lower()

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
    # 1. Get the Contact Name
    if not name:
        speak("Who do you want to message?")
        name = listen()

    # Check if contact exists in your dictionary
    if name not in contacts:
        speak(f"I couldn't find {name} in your contact list.")
        return

    # 2. Get the Message
    speak(f"What should I say to {name}?")
    message = listen()

    if not message:
        speak("I didn't hear a message. Cancelling.")
        return

    speak(f"Sending message to {name}")

    # 3. Open WhatsApp Desktop App
    # This uses the Windows Run protocol to open the app quickly
    s.press("win")
    t.sleep(1)
    s.write("whatsapp", interval = 0.1)
    t.sleep(1)
    s.press("enter")

    # Wait for the app to open (Increase this if your PC is slow)
    t.sleep(3)

    # 4. Search for the Contact
    # CTRL+F focuses the search bar in WhatsApp Desktop
    s.hotkey('ctrl', 'f')
    t.sleep(1)

    # Type the name exactly as it appears in your contacts dictionary
    # (Ensure the key in your dictionary matches the saved name in WhatsApp)
    # Using the name variable here (e.g., "fafnir")
    s.write(name)
    t.sleep(2)  # Wait for search results

    # Select the contact (Press Down Arrow then Enter)
    s.press('down')
    t.sleep(0.5)
    s.press('enter')
    t.sleep(1)

    # 5. Type and Send the Message
    s.write(message, interval = 0.2)
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
    s.write("vs code", interval = 0.1)
    t.sleep(1)
    s.press("enter")



def command_mode():
    query = listen()
    if not query:
        return

    if "play" in query:
        song = query.replace("play", "").strip()
        speak(f"Playing {song}")
        kit.playonyt(song)

    elif "send message to" in query:
        # Extracts "fafnir" from "send message to fafnir"
        name = query.replace("send message to", "").strip()
        send_whatsapp_message(name)

    elif "send message" in query:
        # If you didn't say the name, it will ask you inside the function
        send_whatsapp_message()

    elif "open vs code" in query:
        open_vs_code()

    elif "open whatsapp" in query:
        speak("Opening WhatsApp")
        s.press("win")
        t.sleep(1)
        s.write("whatsapp", interval = 0.1)
        t.sleep(1)
        s.press("enter")

    elif "open youtube" in query:
        speak("Opening YouTube")
        s.press("win")
        t.sleep(1)
        s.write("edge", interval = 0.1)
        t.sleep(1)
        s.press("enter")
        t.sleep(1)
        s.press("search bar")
        s.write("youtube", interval = 0.1)
        s.press("enter")
    elif "open google" in query:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "open github" in query:
        s.press("win")
        t.sleep(1)
        s.write("edge", interval = 0.1)
        t.sleep(1)
        s.press("enter")
        t.sleep(1)
        s.press("search bar")
        s.write("github", interval = 0.1)
        s.press("enter")

    elif "stop" in query or "exit" in query:
        speak("Goodbye")
        sys.exit()


def run_fafnir():
    wish()
    while True:
        command_mode()


if __name__ == "__main__":
    run_fafnir()