import os

MEMORY_DIR = os.getenv("MEMORY_DIR", os.path.expanduser("~/.personal-buddy/memory"))
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", os.path.expanduser("~/.personal-buddy/credentials.json"))
