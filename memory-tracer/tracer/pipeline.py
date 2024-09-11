import pypeln as pl  # type: ignore[import-untyped]
from aiohttp import ClientSession, TCPConnector

from tracer.config import ASYNC_WORKERS_LIMIT


async def schedule_rpc_tasks(task, stage) -> None:
    """
    Schedule asynchronous tasks for processing a given stage using RPC calls.

    Args:
        task (Callable[[int, ClientSession], None]): A function to execute for each item in the stage.
            The function should take two arguments: an item from the stage and an aiohttp ClientSession.
        stage (Iterable[int]): An iterable of items to process with the task function.

    This function uses an asynchronous HTTP session to execute the provided task function
    for each item in the stage concurrently, with a specified number of workers.

    The number of concurrent workers is defined by `ASYNC_WORKERS_LIMIT`.
    """
    async with ClientSession(connector=TCPConnector(limit=0)) as session:

        async def f(arg):
            await task(arg, session)

        await pl.task.each(
            f=f,
            stage=stage,
            workers=ASYNC_WORKERS_LIMIT,
        )
