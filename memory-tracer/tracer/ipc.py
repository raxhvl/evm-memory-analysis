from web3 import IPCProvider, Web3
from web3.method import Method

from tracer.config import IPC_PATH


def get_block(block_number: str, session: Web3) -> dict:
    """
    Retrieve a block by its number.

    Args:
        block_number (str): The block number to retrieve (hexadecimal format).
        session (Web3): The IPC session to use for the request.

    Returns:
        dict: The block data.
    """
    try:
        return session.eth.getBlockByNumber(block_number, True)
    except Exception as e:
        raise RuntimeError(f"IPC error (eth_getBlockByNumber): {e}") from e


def get_transaction_trace(tx_hash: str, session: Web3) -> dict:
    """
    Trace a transaction by its hash.

    Args:
        tx_hash (str): The transaction hash to trace.
        session (Web3): The IPC session to use for the request.

    Returns:
        dict: The trace result of the transaction.
    """

    try:
        return session.eth.traceTransaction(tx_hash, {"enableMemory": True})
    except Exception as e:
        raise RuntimeError(f"IPC error (debug_traceTransaction): {e}") from e


def create_session() -> Web3:
    """
    Create and return an asynchronous Web3 session using IPC provider.

    This function initializes an instance of `AsyncWeb3` with an `AsyncIPCProvider` configured
    to the path specified by `IPC_PATH`. This allows asynchronous interactions with an Ethereum
    node over IPC.

    Returns:
        AsyncWeb3: An instance of `AsyncWeb3` connected to the Ethereum node via IPC.

    Raises:
        ValueError: If `IPC_PATH` is not defined in the environment configuration.
    """

    # Check if the IPC_PATH configuration is present
    if not IPC_PATH:
        raise ValueError("IPC_PATH not found in environment file")

    session = Web3(IPCProvider(IPC_PATH))
    session.eth.attach_methods(
        {
            "getBlockByNumber": Method("eth_getBlockByNumber", is_property=False),
            "traceTransaction": Method("debug_traceTransaction", is_property=False),
        },
    )

    # Create an instance of `AsyncWeb3` using the IPC provider
    return session
