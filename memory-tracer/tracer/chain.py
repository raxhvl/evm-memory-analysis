from typing import Dict, List

from aiohttp import ClientSession

from tracer.rpc import get_block


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
