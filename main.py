import os
import time
import importlib
import subprocess
import sys
from utils.tts import speak
from rich.console import Console
from rich.text import Text

console = Console()

# === Animation Banner ===
def typewriter(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def show_banner():
    lock_art = Text()
    lock_art.append("      .--------.\n", style="bold cyan")
    lock_art.append("     / .------. \\\n", style="bold cyan")
    lock_art.append("    / /        \\ \\\n", style="bold cyan")
    lock_art.append("    | |        | |\n", style="bold cyan")
    lock_art.append("   _| |________| |_\n", style="bold cyan")
    lock_art.append(" .' |_|        |_| '.\n", style="bold cyan")
    lock_art.append(" '._____ ____ _____.'\n", style="bold cyan")
    lock_art.append(" |     .'____'.     |\n", style="bold cyan")
    lock_art.append(" '.__.'.'    '.'.__.'\n", style="bold cyan")
    lock_art.append(" '.__  | LOCK |  __.'\n", style="bold cyan")
    lock_art.append(" |   '.'.____.'.'   |\n", style="bold cyan")
    lock_art.append(" '.____'.____.'____.'\n", style="bold cyan")
    lock_art.append(" '.________________.'\n", style="bold cyan")

    console.print(lock_art)

    typewriter("\n🔐  SecureAuthOS - Biometric Security System")
    # typewriter("🛡️   Developed by Kartik Rawal\n")
    time.sleep(0.5)

show_banner()

# === Dependency Check ===
required_modules = ["cv2", "librosa", "numpy", "pyttsx3", "sounddevice", "scipy", "sklearn"]
for module in required_modules:
    try:
        importlib.import_module(module)
    except ImportError:
        print(f"❌ Missing required package: {module}")
        print("Please install missing packages and rerun the application.")
        exit(1)

# === Auth Modules ===
import face_auth.register_face as face_register
import face_auth.recognize_face as face_verify
import voice_auth.voice_register as voice_register
import voice_auth.voice_verify as voice_verify

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
    print("\n🛠️  Starting first-time biometric registration...\n")

    speak("Registering your face.")
    face_register.capture_and_save_face()

    speak("Now registering your voice.")
    voice_register.record_and_save_voice()

    print("\n✅ All biometric data registered.\n")
    speak("All biometric data registered. You're ready to proceed.")

# === Verification Mode ===
def begin_verification():
    speak("Starting authentication.")
    print("\n🔐 Starting Authentication...\n")

    # Extra check before starting verification
    if not all([os.path.exists(FACE_DATA_FILE), os.path.exists(VOICE_MODEL_FILE), os.path.exists(SECRET_PHRASE_FILE)]):
        print("❌ Voice model or passphrase file not found. Please run initial setup first.")
        speak("Biometric model missing. Please run setup.")
        return

    speak("Please show your face to the camera.")
    print("[Face Auth] Please align your face with the camera...")
    if not face_verify.verify_face():
        speak("Face authentication failed.")
        print("❌ Face authentication failed.")
        return
    print("✅ Face match successful.")

    speak("Face verified. Now verifying your voice and secret phrase.")

    # Retry voice authentication 3 times
    for attempt in range(3):
        time.sleep(5 + attempt * 2)
        result = voice_verify.verify_speaker_and_phrase()
        if result:
            speak("Access granted.")
            print("✅ Access Granted!")
            return

    speak("Authentication failed. Access denied.")
    print("❌ Authentication failed. Please try again later.")

    # Optional: Trigger secure deletion/encryption
    from utils.encryption import secure_delete_folder
    secure_delete_folder("secure_files")
    return


# === Main Execution ===
if __name__ == "__main__":
    if is_first_time():
        speak("Biometric data missing.")
        print("⚠️  Some biometric data is missing.")
        first_time_setup()
    else:
        begin_verification()
        

