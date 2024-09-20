import os

from dotenv import load_dotenv

load_dotenv(override=True)

EVM_WORD_SIZE = 32
DATA_DIR = "data"

# The number of concurrent workers for network calls
# Read: https://cgarciae.github.io/pypeln/advanced/#workers
ASYNC_WORKERS_LIMIT = 1000


# Retrieve the RPC endpoint from environment variables
RPC_ENDPOINT = os.getenv("RPC_ENDPOINT")
API_KEY = os.getenv("RPC_API_KEY")


INSTRUCTIONS = {
    "MLOAD": "R",  # "R" (for "[R]ead")
    "MSTORE": "W",  # "W" (for "write [W]ord")
    "MSTORE8": "B",  # "B" (for "write [B]yte")
    "CALLDATACOPY": "L",  # "L" (for "copy cal[L]data")
    "CODECOPY": "D",  # "D" (for "copy co[D]e")
    "EXTCODECOPY": "X",  # "X" (for "copy e[X]ternal code")
    "RETURNDATACOPY": "N",  # "N" (for "copy retur[N] data")
    "MCOPY": "M",  # "M" (for "copy [M]emory")
    "RETURN": "U",  # "U"  (for "Ret[U]rn")
    # STOP and CALL* instructions are inert. They are required to capture frame
    # boundaries. These are ignored during memory analysis
    "STOP": "I",
    "CALL": "I",
    "CALLCODE": "I",
    "DELEGATECALL": "I",
    "STATICCALL": "I",
}
