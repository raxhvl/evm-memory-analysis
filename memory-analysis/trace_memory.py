import os
import csv
import requests
import argparse
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

EVM_WORD_SIZE = 32

# Retrieve the RPC endpoint from environment variables
RPC_ENDPOINT = os.getenv("RPC_ENDPOINT")
API_KEY = os.getenv("RPC_API_KEY")
if not RPC_ENDPOINT:
    raise ValueError("RPC_ENDPOINT not found in environment file")

# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data")


# Function to call Ethereum JSON-RPC API
def call_rpc(method, params):
    response = requests.post(
        RPC_ENDPOINT,
        headers={"x-api-key": API_KEY},
        json={
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        },
    )
    response.raise_for_status()
    result = response.json()
    if "error" in result:
        raise Exception(f"RPC Error: {result['error']}")
    return result["result"]


# Function to get transactions from a block
def get_transactions_from_block(block_number):
    return call_rpc("eth_getBlockByNumber", [block_number, True])[
        "transactions"
    ]


# Function to trace a transaction
def trace_transaction(tx_hash):
    return call_rpc("debug_traceTransaction", [tx_hash, {"enableMemory": True}])


def is_memory_instruction(trace):
    return trace["op"] in ["MSTORE8", "MSTORE", "MLOAD"]


# Function to process the transactions and write to CSV
def process_transactions(start_block, end_block):
    file_name = f"data/memory_trace_{start_block}_to_{end_block}.csv"
    with open(file_name, "w", newline="") as csv_file:
        fieldnames = [
            "block",
            "tx_hash",
            "tx_gas",
            "to",
            "call_depth",
            "memory_instruction",
            "memory_access_offset",
            "memory_gas_cost",
            "pre_active_memory_size",
            "post_active_memory_size",
            "memory_expansion",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        total_blocks = end_block - start_block + 1

        for block_number in range(start_block, end_block + 1):

            progress_percentage = (
                (block_number - start_block + 1) / total_blocks
            ) * 100

            print(f"Processing {block_number} [{progress_percentage:.2f}%]...")

            start_time = time.time()
            block_hex = hex(block_number)
            transactions = get_transactions_from_block(block_hex)
            transactions_count = len(transactions)
            for tx in transactions:
                tx_hash = tx["hash"]
                tx_gas = int(tx["gas"], 0)
                tx_index = int(tx["transactionIndex"], 0) + 1
                tx_to = tx["to"]

                print(
                    f"Tracing tx {tx_hash}[{tx_index}/{transactions_count}]..."
                )

                trace_data = trace_transaction(tx_hash)

                for index, trace in enumerate(trace_data["structLogs"]):
                    if is_memory_instruction(trace):
                        next_trace = trace_data["structLogs"][index + 1]
                        pre_memory = len(trace["memory"]) * EVM_WORD_SIZE
                        post_memory = len(next_trace["memory"]) * EVM_WORD_SIZE
                        expansion = post_memory - pre_memory
                        memory_offset = int(trace["stack"][-1], 0)
                        row = {
                            "block": block_number,
                            "tx_hash": tx_hash,
                            "tx_gas": tx_gas,
                            "to": tx_to,
                            "call_depth": trace["depth"],
                            "memory_instruction": trace["op"],
                            "memory_access_offset": memory_offset,
                            "memory_gas_cost": trace["gasCost"],
                            "pre_active_memory_size": pre_memory,
                            "post_active_memory_size": post_memory,
                            "memory_expansion": expansion,
                        }
                        writer.writerow(row)

            elapsed_time = time.time() - start_time
            print(
                f"Processed block {block_number} in {elapsed_time:.2f} seconds"
                "\n"
                "****"
                "\n"
            )


# Command-line arguments parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace EVM memory usage.")
    parser.add_argument("start_block", type=int, help="Start block number")
    parser.add_argument("end_block", type=int, help="End block number")

    args = parser.parse_args()
    start_block = args.start_block
    end_block = args.end_block

    if start_block > end_block:
        raise ValueError(
            "Start block should be less than or equal to end block number"
        )

    process_transactions(start_block, end_block)
