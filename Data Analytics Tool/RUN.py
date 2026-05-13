import subprocess
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

MAIN_FILE = os.path.join(BASE_DIR, "app", "main.py")


def run_app():
    try:
        if not os.path.exists(MAIN_FILE):
            print(f"Error: main.py not found at {MAIN_FILE}")
            return

        print("Starting Streamlit app...")
        print(f"Project root: {BASE_DIR}")
        print(f"Main file: {MAIN_FILE}")

        
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            MAIN_FILE
        ]
        
        subprocess.run(cmd, cwd=BASE_DIR, check=True)

    except KeyboardInterrupt:
        print("\nStopping the app...")
    except subprocess.CalledProcessError as e:
        print(f"Streamlit failed to start: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    run_app()
