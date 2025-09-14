import os
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import pickle
import time
from sklearn.mixture import GaussianMixture as GMM
from utils.tts import speak
import librosa

SAMPLE_RATE = 16000
DURATION = 4  # seconds
TEMP_DIR = "voice_auth/temp"
MODEL_FILE = "voiceprint.gmm"
SECRET_FILE = "voice_auth/secret_phrase.txt"

def record_voice(filename):
    try:
        speak(f"Recording started. Please speak now.")
        print(f"🎤 Recording: {filename}")
        audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
        sd.wait()

        if np.max(audio) - np.min(audio) < 500:
            print("❌ Audio too quiet. Please speak louder.")
            return False

        wav.write(filename, SAMPLE_RATE, audio)
        return True
    except Exception as e:
        print(f"❌ Error recording voice: {e}")
        return False

def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=SAMPLE_RATE)
        if np.abs(y).mean() < 0.001:
            print("❌ Audio file too silent. Skipping.")
            return None
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        if mfcc.shape[1] < 5:
            print("❌ Not enough MFCC data. Skipping.")
            return None
        return np.mean(mfcc.T, axis=0)
    except Exception as e:
        print(f"❌ Error extracting features: {e}")
        return None

def record_and_save_voice():
    os.makedirs(TEMP_DIR, exist_ok=True)
    features = []

    speak("We will now record your voice three times using different sentences.")
    guided_sentences = [
        "Security is not a product, it's a process.",
        "Voice authentication is active now.",
        "This is a test to train your voice model."
    ]

    for i, sentence in enumerate(guided_sentences, start=1):
        file_path = os.path.join(TEMP_DIR, f"sample_{i}.wav")
        speak(f"Please say the following sentence: {sentence}")
        print(f"🗣️ Speak this: \"{sentence}\"")

        success = record_voice(file_path)
        if success:
            feat = extract_features(file_path)
            if feat is not None:
                features.append(feat)
            else:
                print("❌ Skipped invalid sample.")
        else:
            print("❌ Voice recording failed.")

    if len(features) < 2:
        speak("Not enough valid audio data. Please try again.")
        raise ValueError("Not enough valid samples to train voice model.")

    speak("Training voice model now.")
    gmm = GMM(n_components=3, max_iter=200, covariance_type='diag', n_init=3, reg_covar=1e-2)

    try:
        gmm.fit(np.vstack(features))
        with open(MODEL_FILE, 'wb') as f:
            pickle.dump(gmm, f)
        speak("Voice model saved successfully.")
        print("✅ Voice model trained and saved.")
    except Exception as e:
        print(f"❌ Error training GMM: {e}")
        speak("Voice model training failed due to audio or hardware issue. Please restart the application.")
        exit(1)

    capture_secret_phrase()

def capture_secret_phrase():
    for attempt in range(3):
        speak("Please speak your secret phrase.")
        print(f"🔐 Attempt {attempt + 1}: Speak your secret phrase.")
        success = record_voice("voice_auth/temp/secret.wav")
        if success:
            try:
                y, sr = librosa.load("voice_auth/temp/secret.wav", sr=SAMPLE_RATE)
                text_attempt = input("🗣️ Enter what you just said (as best as you can): ").strip()
                speak(f"You said: {text_attempt}. Is this correct?")
                confirm = input("✅ Is this correct? (y/n): ").strip().lower()
                if confirm == "y":
                    with open(SECRET_FILE, "w") as f:
                        f.write(text_attempt)
                    speak("Secret phrase saved successfully.")
                    print("✅ Secret phrase saved.")
                    return
            except Exception as e:
                print(f"❌ Could not process recording: {e}")

    speak("Voice input failed. Please type your secret phrase.")
    print("❌ Voice recording failed. Please type your secret phrase manually:")
    phrase = input("📝 Secret phrase: ").strip()
    try:
        with open(SECRET_FILE, "w") as f:
            f.write(phrase)
        speak("Secret phrase saved successfully.")
        print("✅ Secret phrase saved.")
    except:
        print("❌ Failed to save secret phrase.")
        print("Please manually create a file at voice_auth/secret_phrase.txt or rerun the app.")
