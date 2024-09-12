import os

from dotenv import load_dotenv

load_dotenv(override=True)

EVM_WORD_SIZE = 32
DATA_DIR = "data"

# The number of concurrent workers for network calls
# Read: https://cgarciae.github.io/pypeln/advanced/#workers
ASYNC_WORKERS_LIMIT = 1000


# Retrieve the IPC_PATH from environment variables
IPC_PATH = os.getenv("IPC_PATH")
