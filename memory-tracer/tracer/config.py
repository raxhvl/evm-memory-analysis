import os
from enum import Enum

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


class MEMORY_ACCESS_SIZE(Enum):
    VARIABLE = "variable"
    FIXED = "fixed"


# There are two types of instructions:
# 1. Instruction that access a fixed size of memory, in which case the dict below
#    has a `size`.
# 2. Instructions that access a variable size of memory, in which case the size is
#    read from stack using `stack_input_positions`.
INSTRUCTIONS = {
    "KECCAK256": {
        "opcode": "20",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 1}],
    },
    "CALLDATACOPY": {
        "opcode": "37",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 2}],
    },
    "CODECOPY": {
        "opcode": "39",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 2}],
    },
    "MLOAD": {
        "opcode": "51",
        "access_size": MEMORY_ACCESS_SIZE.FIXED.value,
        "stack_input_positions": [{"offset": 0}],
        "size": 32,
    },
    "MSTORE": {
        "opcode": "52",
        "access_size": MEMORY_ACCESS_SIZE.FIXED.value,
        "stack_input_positions": [{"offset": 0}],
        "size": 32,
    },
    "MSTORE8": {
        "opcode": "53",
        "access_size": MEMORY_ACCESS_SIZE.FIXED.value,
        "stack_input_positions": [{"offset": 0}],
        "size": 8,
    },
    "EXTCODECOPY": {
        "opcode": "3c",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 1, "size": 3}],
    },
    "RETURNDATACOPY": {
        "opcode": "3e",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 2}],
    },
    "MCOPY": {
        "opcode": "5e",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 2}, {"offset": 1, "size": 2}],
    },
    "LOG0": {
        "opcode": "a0",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 1}],
    },
    "LOG1": {
        "opcode": "a1",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 1}],
    },
    "LOG2": {
        "opcode": "a2",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 1}],
    },
    "LOG3": {
        "opcode": "a3",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 1}],
    },
    "LOG4": {
        "opcode": "a4",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 1}],
    },
    "CREATE": {
        "opcode": "f0",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 1, "size": 2}],
    },
    "CALL": {
        "opcode": "f1",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 3, "size": 4}, {"offset": 5, "size": 6}],
    },
    "CALLCODE": {
        "opcode": "f2",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 3, "size": 4}, {"offset": 5, "size": 6}],
    },
    "RETURN": {
        "opcode": "f3",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 1}],
    },
    "DELEGATECALL": {
        "opcode": "f4",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 2, "size": 3}, {"offset": 4, "size": 5}],
    },
    "CREATE2": {
        "opcode": "f5",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 1, "size": 2}],
    },
    "STATICCALL": {
        "opcode": "fa",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 2, "size": 3}, {"offset": 4, "size": 5}],
    },
    "REVERT": {
        "opcode": "fd",
        "access_size": MEMORY_ACCESS_SIZE.VARIABLE.value,
        "stack_input_positions": [{"offset": 0, "size": 1}],
    },
}
