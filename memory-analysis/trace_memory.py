import os
import csv
import requests
import argparse
from dotenv import load_dotenv
import concurrent.futures

# Load environment variables from .env file
load_dotenv(override=True)

EVM_WORD_SIZE = 32
DATA_DIR = "data"
CACHE_DIR = os.path.join(DATA_DIR, ".cache")
MAX_THREAD_WORKERS = 10

# Retrieve the RPC endpoint from environment variables
RPC_ENDPOINT = os.getenv("RPC_ENDPOINT")
print(RPC_ENDPOINT)
API_KEY = os.getenv("RPC_API_KEY")
if not RPC_ENDPOINT:
    raise ValueError("RPC_ENDPOINT not found in environment file")


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


# Process a single block
def process_block(block_number, start_block, total_blocks):
    try:
        progress_percentage = (
            (block_number - start_block + 1) / total_blocks
        ) * 100

        print(f"Processing {block_number} [{progress_percentage:.2f}%]...")

        block_hex = hex(block_number)
        transactions = get_transactions_from_block(block_hex)
        transactions_count = len(transactions)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_THREAD_WORKERS
        ) as executor:
            futures = []
            for tx in transactions:
                future = executor.submit(
                    process_transaction, block_number, tx, transactions_count
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"[Task] Transaction processing failed: {e}")

    except Exception as e:
        print(f"Failed to fetch txs from block {block_number}: {e}")


def process_transaction(block_number, tx, transactions_count):
    try:
        tx_hash = tx["hash"]
        tx_gas = int(tx["gas"], 0)
        tx_index = int(tx["transactionIndex"], 0) + 1
        tx_to = tx["to"]

        print(f"Tracing tx {tx_hash}[{tx_index}/{transactions_count}]...")

        trace_data = trace_transaction(tx_hash)

        # Write the tx trace to cache file
        cache_path = os.path.join(CACHE_DIR, str(block_number), str(tx_index))
        os.makedirs(
            os.path.dirname(cache_path), exist_ok=True
        )  # Ensure the directory exists

        with open(cache_path, "w", newline="") as cache:
            writer = csv.writer(cache)

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
                    writer.writerow(row.values())
    except Exception as e:
        print(f"Failed to trace tx: {block_number} >> {tx['hash']}: {e}")


# Compile all the result from cache file
def compile_result(start_block, end_block):
    print("Compiling results...")

    file_name = f"{DATA_DIR}/memory_trace_{start_block}_to_{end_block}.csv"

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

        for block_number in range(start_block, end_block + 1):
            block_cache_dir = os.path.join(CACHE_DIR, str(block_number))
            if os.path.exists(block_cache_dir):
                sorted_cache = sorted(map(int, os.listdir(block_cache_dir)))
                sorted_cache = map(str, sorted_cache)
                for file_name in sorted_cache:
                    file_path = os.path.join(block_cache_dir, file_name)
                    with open(file_path, "r") as f:
                        row = f.read()
                        csv_file.write(row)

    # os.rmdir(CACHE_DIR)
    print("Tracing complete 🎉")


# Trace memory trends for given range of blocks
def trace_memory(start_block, end_block):
    total_blocks = end_block - start_block + 1

    # Setup up cache
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Process blocks in parallel
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_THREAD_WORKERS
    ) as executor:
        futures = []
        for block_number in range(start_block, end_block + 1):
            future = executor.submit(
                process_block, block_number, start_block, total_blocks
            )
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"[Task] Block processing failed: {e}")

    # Compile the result once all blocks are processed
    compile_result(start_block, end_block)


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

    trace_memory(start_block, end_block)
