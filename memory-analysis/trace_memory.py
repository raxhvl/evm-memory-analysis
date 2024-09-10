import asyncio
from aiohttp import ClientSession, TCPConnector
from dotenv import load_dotenv
import os
import csv
import argparse
import sys
import pypeln as pl

# Load environment variables from .env file
load_dotenv(override=True)

EVM_WORD_SIZE = 32
DATA_DIR = "data"
WORKERS = 1000

# Retrieve the RPC endpoint from environment variables
RPC_ENDPOINT = os.getenv("RPC_ENDPOINT")
API_KEY = os.getenv("RPC_API_KEY")
if not RPC_ENDPOINT:
    raise ValueError("RPC_ENDPOINT not found in environment file")


# Function to call Ethereum JSON-RPC API
async def call_rpc(method: str, params: list, session: ClientSession) -> dict:
    """
    Call the Ethereum JSON-RPC API.

    Args:
        method (str): The JSON-RPC method to call.
        params (list): Parameters for the JSON-RPC method.
        session (aiohttp.ClientSession): The aiohttp session to use for the request.

    Returns:
        dict: The result of the RPC call.

    Raises:
        Exception: If there is an error in the RPC response.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }

    async with session.post(
        RPC_ENDPOINT,
        headers={"x-api-key": API_KEY},
        json=payload,
    ) as response:
        result = await response.json()
        if "error" in result:
            raise Exception(f"RPC Error: {result['error']}")
        return result.get("result")


# Function to get transactions from a block
async def get_blocks(block_number, session):
    return (await call_rpc("eth_getBlockByNumber", [block_number, True], session))[
        "transactions"
    ]


# Function to trace a transaction
async def trace_transaction(tx_hash, session):
    return await call_rpc(
        "debug_traceTransaction", [tx_hash, {"enableMemory": True}], session
    )


def is_memory_instruction(trace):
    return trace["op"] in ["MSTORE8", "MSTORE", "MLOAD"]


async def get_blocks(start_block, end_block):
    block_numbers = list(range(start_block, end_block + 1))

    async with ClientSession(connector=TCPConnector(limit=0)) as session:
        blocks = []

        async def fetch(block_number):
            result = await get_blocks(block_number, session)
            transactions = [
                {"hash": tx.get("hash"), "to": tx.get("to"), "gas": tx.get("gas")}
                for tx in result
            ]
            blocks.append({"block_number": block_number, "transactions": transactions})

        await pl.task.each(
            fetch,
            block_numbers,
            workers=WORKERS,
        )

        return blocks


async def trace_transaction(block_number, tx, writer):
    try:
        tx_hash = tx["hash"]
        tx_gas = int(tx["gas"], 0)
        tx_to = tx["to"]

        trace_data = await trace_transaction(tx_hash)

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
        print(f"Failed to trace tx:  {tx['hash']}: {e}")


def write_blocks_to_disk(blocks):

    with open(f"data/fragment_tx.csv", "w", newline="") as csv_file:
        fieldnames = ["id", "block", "tx_hash", "tx_gas", "to"]
        writer = csv.DictWriter(
            csv_file, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        tx_id = 1
        for block in blocks:
            for tx in block["transactions"]:
                tx["id"] = tx_id
                writer.writerow(tx)


# Trace memory trends for given range of blocks
async def trace_memory(start_block, end_block):
    total_blocks = end_block - start_block + 1

    # Get transactions
    blocks = await get_blocks(start_block, end_block)

    write_blocks_to_disk(blocks)

    trace_transaction(blocks)


# Command-line arguments parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace EVM memory usage.")
    parser.add_argument("start_block", type=int, help="Start block number")
    parser.add_argument("end_block", type=int, help="End block number")

    args = parser.parse_args()
    start_block = args.start_block
    end_block = args.end_block

    if start_block > end_block:
        raise ValueError("Start block should be less than or equal to end block number")

    asyncio.run(trace_memory(start_block, end_block))
