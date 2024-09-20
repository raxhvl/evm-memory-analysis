from typing import Any, Dict, List

from aiohttp import ClientSession

from tracer.rpc import get_block, get_transaction_trace


class TransactionState:
    def __init__(self):
        self.transaction_id = 1

    def get_next_id(self) -> int:
        tx_id = self.transaction_id
        self.transaction_id += 1
        return tx_id


transaction_state = TransactionState()


async def get_transactions_from_block(
    block_number: int, session: ClientSession
) -> List[Dict[str, str]]:

    transactions: List[Dict[str, str]] = []

    block = await get_block(hex(block_number), session)
    for tx in block.get("transactions", []):
        tx_id = transaction_state.get_next_id()
        transactions.append(
            {
                "id": str(tx_id),
                "block": str(block_number),
                "tx_hash": tx.get("hash", ""),
                "to": tx.get("to", ""),
                "tx_gas": str(int(tx.get("gas", "0x0"), 0)),
            }
        )

    return transactions


def process_trace(instructions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process instructions to calculate memory expansion based on the next instruction
    in the call frame, handling inert instructions and return operations.

    Args:
        instructions (List[Dict[str, Any]]): The list of instruction data.

    Returns:
        List[Dict[str, Any]]: The processed instructions with
        'post_memory_size' and 'memory_expansion'.
    """

    # Get the next instruction in the call frame
    maxIndex = len(instructions) - 1
    for index, instruction in enumerate(instructions):
        next_index = min(index + 1, maxIndex)
        next_instruction = instructions[next_index]

        # Instructions are within the call boundary
        if next_instruction["depth"] == instruction["depth"]:
            instructions[index]["post_memory_size"] = next_instruction["memory_size"]
            instructions[index]["memory_expansion"] = (
                next_instruction["memory_size"] - instruction["memory_size"]
            )

        # These instructions change the call depth because they are at the
        # boundary of the call frame. Memory expansion behavior for each
        # instruction MUST be handled explicitly.
        else:
            match instruction["op"]:
                # RETURN
                case "U":
                    # Usually RETURN would not expand memory since the point is to
                    # return data from memory. But it CAN return memory, which
                    # is an edge case probably to be explored later.
                    if instruction["gas_cost"] > 0:
                        raise ValueError("RETURN has expanded memory. TODO: Handle this!")
                    else:
                        instructions[index]["post_memory_size"] = instruction["memory_size"]
                        instructions[index]["memory_expansion"] = 0

                # An inert instruction does not expand memory but is required to ensure the
                # call frame has a boundary.
                case "I":
                    instructions[index]["post_memory_size"] = instruction["memory_size"]
                    instructions[index]["memory_expansion"] = 0
                case _:
                    raise RuntimeError(f"Call boundary not handled for {instruction['op']}")
    return instructions


async def get_call_frames_from_transaction(
    transaction: Dict[str, str], session: ClientSession
) -> List[Dict[str, str]]:
    """
    Get call frames from a transaction by fetching the trace data.

    Args:
        transaction (Dict[str, str]): The transaction details including 'id' and 'tx_hash'.
        session (ClientSession): The aiohttp client session for making API requests.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing call frame information.

    Raises:
        ValueError: If 'tx_hash' or 'id' is missing from the transaction.
    """
    if not transaction.get("tx_hash") or not transaction.get("id"):
        raise ValueError("Transaction must contain 'tx_hash' and 'id'.")

    call_frames: List[Dict[str, str]] = []
    trace_data = await get_transaction_trace(transaction["tx_hash"], session)

    # Ignore failed transactions
    if trace_data["error"]:
        return call_frames

    instructions = process_trace(trace_data["data"])

    for instruction in instructions:

        # Inert instructions can be excluded from output
        # since they don't expand the memory.
        if instruction["op"] == "I":
            continue

        row = {
            "transaction_id": transaction["id"],
            "call_depth": instruction["depth"],
            "memory_instruction": instruction["op"],
            "memory_access_offset": instruction["offset"],
            "memory_gas_cost": instruction["gas_cost"],
            "pre_active_memory_size": instruction["memory_size"],
            "post_active_memory_size": instruction["post_memory_size"],
            "memory_expansion": instruction["memory_expansion"],
        }
        call_frames.append(row)

    return call_frames
