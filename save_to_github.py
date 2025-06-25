import subprocess
import datetime

def backup_to_github():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # git add / commit / push
    subprocess.run(["git", "add", "coins.json"])
    subprocess.run(["git", "commit", "-m", f"Backup coins.json at {timestamp}"])
    subprocess.run(["git", "push", "origin", "main"])  # or your branch name

if __name__ == "__main__":
    backup_to_github()
