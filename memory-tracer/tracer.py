import argparse
import asyncio

from tracer.chain import get_transactions_from_block
from tracer.output import FileType
from tracer.output import Handler as OutputHandler
from tracer.pipeline import schedule_rpc_tasks


async def save_transactions(start_block, end_block):

    block_range = range(start_block, end_block + 1)

    output = OutputHandler(start_block, end_block, FileType.TRANSACTION)

    async def task(block_number, session):
        transactions = await get_transactions_from_block(block_number, session)
        output.write(transactions)

    await schedule_rpc_tasks(task=task, stage=block_range)

    output.compress()


# Trace memory trends for given range of blocks
async def trace_memory(start_block, end_block):

    await save_transactions(start_block, end_block)


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
