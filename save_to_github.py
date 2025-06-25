import os
import subprocess

def save_to_github():
    try:
        subprocess.run(["git", "add", "coins.json", "items.json"], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-save: coins & items updated"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ GitHub に coins.json と items.json を保存しました")
    except subprocess.CalledProcessError as e:
        print("⚠️ GitHub への保存でエラー:", e)
