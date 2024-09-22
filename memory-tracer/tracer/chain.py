from typing import Dict, List

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

    for instruction in trace_data["data"]:

        # Some instructions access multiple memory regions
        # because they both read and then back write to memory
        # such as `MCOPY`, `CALL` etc. The regions gets flattened
        # for each instruction in the output.
        for memory_access in instruction["access_regions"]:

            row = {
                "transaction_id": transaction["id"],
                "call_depth": instruction["depth"],
                "opcode": instruction["op"],
                "memory_access_offset": memory_access["offset"],
                "memory_access_size": memory_access["size"],
                "opcode_gas_cost": instruction["gas_cost"],
                "pre_active_memory_size": instruction["pre_memory_size"],
                "post_active_memory_size": instruction["post_memory_size"],
                "memory_expansion": instruction["memory_expansion"],
            }
            call_frames.append(row)

    return call_frames
