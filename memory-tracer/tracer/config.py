import os

from dotenv import load_dotenv

load_dotenv(override=True)

EVM_WORD_SIZE = 32
DATA_DIR = "data"
ASYNC_WORKERS_LIMIT = 1000


# Retrieve the RPC endpoint from environment variables
RPC_ENDPOINT = os.getenv("RPC_ENDPOINT")
API_KEY = os.getenv("RPC_API_KEY")
