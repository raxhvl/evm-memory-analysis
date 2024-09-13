import argparse
import asyncio
import logging

from web3 import AsyncWeb3

from tracer.chain import get_call_frames_from_transaction, get_transactions_from_block
from tracer.fs import CSVIterator, FileType, OutputHandler
from tracer.ipc import create_session
from tracer.pipeline import schedule_task

# Configure logging
logging.basicConfig(
    filename="trace.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",  # Append mode
)


async def save_transactions(start_block: int, end_block: int, session: AsyncWeb3) -> str:
    """
    Save transactions for a range of blocks.

    Args:
        start_block (int): The starting block number.
        end_block (int): The ending block number.
        session (AsyncWeb3): The IPC session to be used.

    Returns:
        str: The name of the compressed file containing transactions.
    """
    block_range = range(start_block, end_block + 1)

    # Initialize the output handler for transactions
    output = OutputHandler(start_block, end_block, FileType.TRANSACTION)

    async def task(block_number: int):
        """
        Task to fetch transactions for a given block and write to output.

        Args:
            block_number (int): The block number to fetch transactions for.
            session: The session object for RPC calls.
        """
        transactions = await get_transactions_from_block(block_number, session)
        output.write(transactions)

    # Schedule RPC tasks for each block in the range
    await schedule_task(task=task, stage=block_range)

    output.compress()

    return output.compressed_file_name


async def save_call_frames(
    start_block: int, end_block: int, transaction_iterator: CSVIterator, session: AsyncWeb3
) -> None:
    """
    Save call frames for transactions within a range of blocks.

    Args:
        start_block (int): The starting block number.
        end_block (int): The ending block number.
        transaction_iterator (CSVIterator): Iterator for transactions from the CSV file.
        session (AsyncWeb3): The IPC session to be used.
    """
    # Initialize the output handler for call frames
    output = OutputHandler(start_block, end_block, FileType.CALL_FRAME)

    async def task(transaction):
        """
        Task to fetch call frames for a given transaction and write to output.

        Args:
            transaction: The transaction to fetch call frames for.
            session: The session object for RPC calls.
        """
        call_frames = await get_call_frames_from_transaction(transaction, session)
        output.write(call_frames)

    # Schedule RPC tasks for each transaction in the iterator
    await schedule_task(task=task, stage=transaction_iterator)

    output.compress()


async def trace_memory(start_block: int, end_block: int) -> None:
    """
    Trace memory usage for a range of blocks by saving transactions and call frames.

    Args:
        start_block (int): The starting block number.
        end_block (int): The ending block number.
    """
    try:
        # Create a persistent IPC session to be used for the lifetime of the script.
        async with create_session() as session:
            # Save transactions to a compressed csv file and get its path.
            tx_file = await save_transactions(start_block, end_block, session)

            # Process the transactions to save call frames
            with CSVIterator(tx_file) as transaction_iterator:
                await save_call_frames(start_block, end_block, transaction_iterator, session)
    except Exception as e:
        logging.error(f"Error tracing memory for blocks {start_block}-{end_block}: {e}")
        raise


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

    # Run the tracing process
    asyncio.run(trace_memory(start_block, end_block))
