from aiohttp import ClientSession

from tracer.config import API_KEY, RPC_ENDPOINT


async def call_rpc(method: str, params: list, session: ClientSession) -> dict:
    """
    Call the Ethereum JSON-RPC API.

    Args:
        method (str): The JSON-RPC method to call.
        params (list): Parameters for the JSON-RPC method.
        session (ClientSession): The aiohttp session to use for the request.

    Returns:
        dict: The result of the RPC call.

    Raises:
        Exception: If there is an error in the RPC response.
    """

    if not RPC_ENDPOINT:
        raise ValueError("RPC_ENDPOINT not found in environment file")

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }

    async with session.post(
        RPC_ENDPOINT, json=payload, headers={"x-api-key": API_KEY}
    ) as response:
        result = await response.json()
        if "error" in result:
            raise Exception(f"RPC Error ({method}>req:{params}): {result['error']}")
        return result.get("result")


async def get_block(block_number: str, session: ClientSession) -> dict:
    """
    Retrieve a block by its number.

    Args:
        block_number (str): The block number to retrieve (hexadecimal format).
        session (ClientSession): The aiohttp session to use for the request.

    Returns:
        dict: The block data.
    """
    return await call_rpc("eth_getBlockByNumber", [block_number, True], session)


async def get_transaction_trace(tx_hash: str, session: ClientSession) -> dict:
    """
    Trace a transaction by its hash.

    Args:
        tx_hash (str): The transaction hash to trace.
        session (ClientSession): The aiohttp session to use for the request.

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
    return await call_rpc("debug_traceTransaction", [tx_hash, {"tracer": tracer}], session)
