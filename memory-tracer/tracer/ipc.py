from web3 import AsyncIPCProvider, AsyncWeb3

from tracer.config import IPC_PATH


async def get_block(block_number: str, session: AsyncWeb3):
    """
    Retrieve a block by its number.

    Args:
        block_number (str): The block number to retrieve (hexadecimal format).
        session (AsyncWeb3): The IPC session to use for the request.

    Returns:
        dict: The block data.
    """
    result = await session.provider.make_request("eth_getBlockByNumber", [block_number, True])
    if "error" in result:
        raise Exception(f"IPC error (eth_getBlockByNumber[{block_number}]): {result['error']}")
    return result.get("result")


async def get_transaction_trace(tx_hash: str, session: AsyncWeb3):
    """
    Trace a transaction by its hash.

    Args:
        tx_hash (str): The transaction hash to trace.
        session (AsyncWeb3): The IPC session to use for the request.

    Returns:
        dict: The trace result of the transaction.
    """
    # Custom tracer
    # Learn more: https://geth.ethereum.org/docs/developers/evm-tracing/custom-tracer
    # Memory instruction is mapped to single characters to reduce response size.
    # `MSTORE`  =  "W" (for "write [w]ord")
    # `MSTORE8` =  "B" (for "write [b]yte")
    # `MLOAD`   =  "R" (for "[r]ead")

    tracer = """
    {
        data: [],
        memoryInstructions: {"MSTORE":"W", "MSTORE8":"B", "MLOAD":"R"},
        fault: function (log) {},
        step: function (log) {
            let op = log.op.toString();
            let instructions = this.memoryInstructions
            if (Object.keys(instructions).includes(op)) {
            this.data.push({
                op: instructions[op],
                depth: log.getDepth(),
                offset: log.stack.peek(0),
                gasCost: log.getCost(),
                memorySize: log.memory.length()
            });
            }
        },
        result: function (ctx, _) {
            let error = !!ctx.error
            return {
                error,
                data: error ? [] : this.data
            };
        }
    }
    """
    result = await session.provider.make_request(
        "debug_traceTransaction", [tx_hash, {"tracer": tracer}]
    )
    if "error" in result:
        raise Exception(f"IPC error (debug_traceTransaction[{tx_hash}]): {result['error']}")
    return result.get("result")


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
