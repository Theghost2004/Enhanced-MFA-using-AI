import os
import time
import importlib
import tkinter as tk
from tkinter import messagebox
from utils.tts import speak

# === Dependency Check ===
required_modules = ["cv2", "librosa", "numpy", "pyttsx3", "sounddevice", "scipy", "sklearn"]
for module in required_modules:
    try:
        importlib.import_module(module)
    except ImportError:
        messagebox.showerror("Missing Dependency", f"❌ Missing required package: {module}\nInstall it and rerun.")
        exit(1)

# === Auth Modules ===
import face_auth.register_face as face_register
import face_auth.recognize_face as face_verify
import voice_auth.voice_register as voice_register
import voice_auth.voice_verify as voice_verify
from utils.encryption import secure_delete_folder

# === File Paths ===
FACE_DATA_FILE = "face_encodings.pkl"
VOICE_MODEL_FILE = "voiceprint.gmm"
SECRET_PHRASE_FILE = "voice_auth/secret_phrase.txt"

# === Check if Setup is Complete ===
def is_first_time():
    checks = [
        os.path.exists(FACE_DATA_FILE),
        os.path.exists(VOICE_MODEL_FILE),
        os.path.exists(SECRET_PHRASE_FILE)
    ]
    return not all(checks)

# === First-Time Setup ===
def first_time_setup():
    speak("Welcome. Let's start your biometric setup.")
    messagebox.showinfo("Setup", "Starting first-time biometric registration...")

    speak("Registering your face.")
    face_register.capture_and_save_face()

    speak("Now registering your voice.")
    voice_register.record_and_save_voice()

    messagebox.showinfo("Setup Complete", "✅ All biometric data registered.")
    speak("Setup complete. You're ready to proceed.")

# === Verification Mode ===
def begin_verification():
    speak("Starting authentication.")
    messagebox.showinfo("Authentication", "🔐 Starting Authentication...")

    if not all([os.path.exists(FACE_DATA_FILE), os.path.exists(VOICE_MODEL_FILE), os.path.exists(SECRET_PHRASE_FILE)]):
        messagebox.showerror("Error", "❌ Biometric model missing. Please run setup first.")
        speak("Biometric model missing. Please run setup.")
        return

    speak("Please show your face to the camera.")
    if not face_verify.verify_face():
        speak("Face authentication failed.")
        messagebox.showerror("Auth Failed", "❌ Face authentication failed.")
        return

    speak("Face verified. Now verifying your voice and secret phrase.")
    for attempt in range(3):
        time.sleep(3 + attempt)
        result = voice_verify.verify_speaker_and_phrase()
        if result:
            speak("Access granted.")
            messagebox.showinfo("Success", "✅ Access Granted!")
            return

    speak("Authentication failed. Access denied.")
    messagebox.showerror("Denied", "❌ Authentication failed. Files will be deleted.")
    secure_delete_folder("secure_files")

# === UI ===
def launch_app():
    root = tk.Tk()
    root.title("SecureAuthOS")
    root.geometry("400x250")

    tk.Label(root, text="🔐 SecureAuthOS", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(root, text="Biometric Security System").pack()

    if is_first_time():
        tk.Button(root, text="Run First-Time Setup", width=20, command=first_time_setup).pack(pady=15)
    else:
        tk.Button(root, text="Authenticate", width=20, command=begin_verification).pack(pady=15)

    tk.Button(root, text="Exit", width=20, command=root.quit).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    launch_app()
