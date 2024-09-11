from typing import Dict, List

from aiohttp import ClientSession

from tracer.config import EVM_WORD_SIZE
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


def is_memory_instruction(trace: Dict[str, str]) -> bool:
    """
    Check if the trace operation is a memory instruction.

    Args:
        trace (Dict[str, str]): The trace dictionary containing operation details.

    Returns:
        bool: True if the operation is a memory instruction, False otherwise.
    """
    return trace["op"] in ["MSTORE8", "MSTORE", "MLOAD"]


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

    struct_logs = trace_data["structLogs"]
    for index, trace in enumerate(struct_logs):
        if is_memory_instruction(trace):
            next_trace = struct_logs[index + 1]
            pre_memory = len(trace["memory"]) * EVM_WORD_SIZE
            post_memory = len(next_trace["memory"]) * EVM_WORD_SIZE
            expansion = post_memory - pre_memory
            memory_offset = int(trace["stack"][-1], 0) if trace["stack"] else 0

            # Map the instruction or use the original op if not in the mapping
            memory_instruction = {"MSTORE8": "B", "MSTORE": "W", "MLOAD": "R"}.get(
                trace["op"], trace["op"]
            )

            row = {
                "transaction_id": transaction["id"],
                "call_depth": trace["depth"],
                "memory_instruction": memory_instruction,
                "memory_access_offset": memory_offset,
                "memory_gas_cost": trace["gasCost"],
                "pre_active_memory_size": pre_memory,
                "post_active_memory_size": post_memory,
                "memory_expansion": expansion,
            }
            call_frames.append(row)

    return call_frames
