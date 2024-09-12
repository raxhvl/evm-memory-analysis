from web3 import AsyncIPCProvider, AsyncWeb3

from tracer.config import IPC_PATH


async def call_ipc(method: str, params: list, session: AsyncWeb3) -> dict:
    """
    Call the Ethereum JSON-RPC via IPC.

    Args:
        method (str): The JSON-RPC method to call.
        params (list): Parameters for the JSON-RPC method.
        session (AsyncWeb3): The IPC session to use for the request.

    Returns:
        dict: The result of the IPC call.

    Raises:
        Exception: If there is an error in the response.
    """

    result = await session.provider.make_request(method, params)

    if "error" in result:
        raise Exception(f"IPC Error: {result['error']}")
    return result.get("result")


async def get_block(block_number: str, session: AsyncWeb3) -> dict:
    """
    Retrieve a block by its number.

    Args:
        block_number (str): The block number to retrieve (hexadecimal format).
        session (AsyncWeb3): The IPC session to use for the request.

    Returns:
        dict: The block data.
    """
    return await call_ipc("eth_getBlockByNumber", [block_number, True], session)


async def get_transaction_trace(tx_hash: str, session: AsyncWeb3) -> dict:
    """
    Trace a transaction by its hash.

    Args:
        tx_hash (str): The transaction hash to trace.
        session (AsyncWeb3): The IPC session to use for the request.

    Returns:
        dict: The trace result of the transaction.
    """
    return await call_ipc("debug_traceTransaction", [tx_hash, {"enableMemory": True}], session)


def create_session() -> AsyncWeb3:
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

    # Create an instance of `AsyncWeb3` using the IPC provider
    return AsyncWeb3(AsyncIPCProvider(IPC_PATH))
