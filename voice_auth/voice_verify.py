import os
import wave
import pickle
import time
import numpy as np
import speech_recognition as sr
from sklearn.mixture import GaussianMixture
import pyaudio
import difflib
from utils import encryption
from utils import tts
from pathlib import Path

VOICE_MODEL_FILE = "voiceprint.gmm"
PHRASE_FILE = "voice_auth/secret_phrase.txt"
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5
TEMP_FILE = "voice_auth/temp_verify.wav"

MAX_ATTEMPTS = 3
SIMILARITY_THRESHOLD = 0.8
LIKELIHOOD_THRESHOLD = -100  # Set a more realistic threshold based on training

def record_for_verification(filename):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("\n🎙 Please speak your secret phrase when prompted...")
    tts.speak("Please speak your secret phrase when prompted")
    time.sleep(1)
    print("🔴 Recording... Speak NOW!")
    tts.speak("Recording started. Speak now.")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("🔵 Done recording.\n")
    tts.speak("Recording done")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def extract_features(filename):
    import librosa
    y, sr = librosa.load(filename, sr=RATE)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)

def recognize_phrase_from_audio(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language='en-IN').lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        print("⚠️ Speech recognition failed. Check internet.")
        return None

def verify_speaker_and_phrase():
    if not os.path.exists(VOICE_MODEL_FILE) or not os.path.exists(PHRASE_FILE):
        print("❌ Voice model or passphrase file not found. Please run initial setup first.")
        tts.speak("Setup incomplete. Please run registration.")
        return False

    with open(VOICE_MODEL_FILE, "rb") as f:
        gmm_model = pickle.load(f)

    with open(PHRASE_FILE, "r") as f:
        saved_phrase = f.read().strip().lower()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n🔁 Attempt {attempt} of {MAX_ATTEMPTS}")
        tts.speak(f"Attempt {attempt} of {MAX_ATTEMPTS}")
        record_for_verification(TEMP_FILE)

        print("🧠 Analyzing voice...")
        tts.speak("Analyzing voice")
        features = extract_features(TEMP_FILE).reshape(1, -1)
        log_likelihood = gmm_model.score(features)

        recognized_phrase = recognize_phrase_from_audio(TEMP_FILE)
        if not recognized_phrase:
            print("❌ Could not understand your voice. Try again.")
            tts.speak("Could not understand your voice. Please try again.")
            time.sleep(5)
            continue

        phrase_similarity = difflib.SequenceMatcher(None, recognized_phrase, saved_phrase).ratio()

        print(f"🗣 You said:            '{recognized_phrase}'")
        print(f"🔍 Phrase similarity:   {phrase_similarity:.2f}")
        print(f"🎯 Voice likelihood:    {log_likelihood:.2f}")

        if phrase_similarity >= SIMILARITY_THRESHOLD and log_likelihood >= LIKELIHOOD_THRESHOLD:
            print("✅ Voice and phrase match! Access granted.")
            tts.speak("Access granted.")
            return True
        else:
            print("❌ Verification failed.")
            tts.speak("Verification failed.")
            time.sleep(5)

    # After 3 failed attempts, encrypt and delete
    print("\n⛔ Maximum attempts reached.")
    print("🔐 Initiating secure file destruction process...")
    tts.speak("Maximum attempts reached. Initiating secure destruction.")
    PROTECTED_FOLDER = Path("secure_files")  
    encryption.secure_delete_folder(PROTECTED_FOLDER)
    return False
