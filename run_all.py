# to Start the API (port 8000) and the web app (port 5000) together. Ctrl+C stops both.
# python run_all.py

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"


def main() -> None:
    subprocess.run([sys.executable, "-m", "scripts.populate_db", "--if-empty"], cwd=ROOT, check=True)
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"], cwd=ROOT)
    web = subprocess.Popen([sys.executable, "app.py"], cwd=FRONTEND,
                           env={**os.environ, "API_URL": "http://localhost:8000"})
    print("\nAPI docs : http://localhost:8000/docs\nWeb app  : http://localhost:5000\n")
    time.sleep(2)
    webbrowser.open("http://localhost:5000")
    webbrowser.open("http://localhost:8000/docs")
    try:
        api.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for p in (api, web):
            p.terminate()


if __name__ == "__main__":
    main()
