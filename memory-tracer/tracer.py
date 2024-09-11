import argparse
import asyncio

from tracer.chain import get_call_frames_from_transaction, get_transactions_from_block
from tracer.fs import CSVIterator, FileType, OutputHandler
from tracer.pipeline import schedule_rpc_tasks


async def save_transactions(start_block: int, end_block: int) -> str:

    block_range = range(start_block, end_block + 1)

    output = OutputHandler(start_block, end_block, FileType.TRANSACTION)

    async def task(block_number, session):
        transactions = await get_transactions_from_block(block_number, session)
        output.write(transactions)

    await schedule_rpc_tasks(task=task, stage=block_range)

    output.compress(False)

    return output.compressed_file_name


async def save_call_frames(
    start_block: int, end_block: int, transaction_iterator: CSVIterator
) -> None:

    output = OutputHandler(start_block, end_block, FileType.CALL_FRAME)

    async def task(transaction, session):
        call_frames = await get_call_frames_from_transaction(transaction, session)
        output.write(call_frames)

    await schedule_rpc_tasks(task=task, stage=transaction_iterator)

    # TODO: remove
    output.compress(False)


# Trace memory trends for given range of blocks
async def trace_memory(start_block, end_block):

    tx_file = await save_transactions(start_block, end_block)

    with CSVIterator(tx_file) as transaction_iterator:
        await save_call_frames(start_block, end_block, transaction_iterator)


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
