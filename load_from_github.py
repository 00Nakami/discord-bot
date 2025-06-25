import subprocess
import os

def restore_from_github():
    if os.path.exists("coins.json"):
        os.remove("coins.json")
    subprocess.run(["git", "pull", "origin", "main"])  # or your branch

if __name__ == "__main__":
    restore_from_github()
