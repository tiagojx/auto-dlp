import os

VENV_FOLDER = ".venv"
PYTHON_VERSION = 3.11
PYTHON_BIN_NAME = "python" if os.name == "nt" else "python3"
PLATFORM = "win" if os.name == "nt" else "unix"
DW_SCRIPT = "download_packages.py"
YDL_SCRIPT = "ydl.py"
REQUIREMENTS_OK_FILE = "requirements_ok.txt"
