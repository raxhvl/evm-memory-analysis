import json

from aiohttp import ClientSession

from tracer.config import API_KEY, INSTRUCTIONS, MEMORY_ACCESS_SIZE, RPC_ENDPOINT


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
    # Failed transactions are ignored.

    tracer = f"""
    {{
        data: [],
        required_instructions: {json.dumps(INSTRUCTIONS)},
        fault: function (log) {{}},
        step: function (log) {{
            let name = log.op.toString();

            if (Object.keys(this.required_instructions).includes(name)) {{

                const instruction = this.required_instructions[name];

                post_memory_size =  pre_memory_size =  log.memory.length();
                is_fixed_size = instruction.access_size == "{MEMORY_ACCESS_SIZE.FIXED.value}"
                access_regions = []

                // post_memory_size is the highest offset accessed by the instruction.
                instruction.stack_input_positions.forEach( input =>{{
                    offset = log.stack.peek(input.offset);
                    size = is_fixed_size ? instruction.size :
                           log.stack.peek(input.size);

                    if(size>0){{
                        post_memory_size = Math.max(post_memory_size, offset + size);
                    }}
                    access_regions.push({{offset, size}});
                }});

                // Ensure post_memory_size is a multiple of 32 (rounded up)
                post_memory_size = Math.ceil(post_memory_size / 32) * 32;

                memory_expansion = post_memory_size - pre_memory_size;

                this.data.push({{
                    op: instruction.opcode,
                    depth: log.getDepth(),
                    access_regions,
                    gas_cost: log.getCost(),
                    pre_memory_size,
                    post_memory_size,
                    memory_expansion
                }});
            }}
        }},
        result: function (ctx, _) {{
            let error = !!ctx.error
            return {{
                error,
                data: error ? [] : this.data
            }};
        }}
    }}
    """
    return await call_rpc("debug_traceTransaction", [tx_hash, {"tracer": tracer}], session)
