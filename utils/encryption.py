import os
import shutil
import base64
from cryptography.fernet import Fernet
from pathlib import Path

KEY_FILE = "utils/.secretkey"
ENCRYPTED_DIR = ".encrypted_backups"


def generate_key():
    key = Fernet.generate_key()
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_file(filepath, key):
    fernet = Fernet(key)
    with open(filepath, "rb") as f:
        data = f.read()
    encrypted = fernet.encrypt(data)

    filename = os.path.basename(filepath)
    rel_dir = os.path.relpath(os.path.dirname(filepath), start="secure_files")
    target_dir = os.path.join(ENCRYPTED_DIR, rel_dir)
    os.makedirs(target_dir, exist_ok=True)

    encrypted_path = os.path.join(target_dir, filename + ".enc")
    with open(encrypted_path, "wb") as f:
        f.write(encrypted)
    return encrypted_path

def secure_delete(filepath):
    if os.path.exists(filepath):
        length = os.path.getsize(filepath)
        try:
            with open(filepath, "wb") as f:
                f.write(os.urandom(length))
        except:
            pass
        os.remove(filepath)

def secure_delete_folder(folder_path, silent=False):
    if not silent:
        print(f"\n⚠️ Securing contents of: {folder_path}")
    if not os.path.exists(folder_path):
        if not silent:
            print("⚠️ Folder doesn't exist.")
        return

    key = load_key()

    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            if file.endswith(".enc"):  # Skip already encrypted files
                continue
            try:
                enc_path = encrypt_file(full_path, key)
                secure_delete(full_path)
                if not silent:
                    print(f"🔐 Encrypted and deleted: {full_path} → {enc_path}")
            except Exception as e:
                if not silent:
                    print(f"❌ Error with {file}: {e}")

    if not silent:
        print("✅ All files encrypted and securely deleted.\n")
        import sys
        sys.exit(0)


