import pypeln as pl  # type: ignore[import-untyped]

from tracer.config import ASYNC_WORKERS_LIMIT


async def schedule_task(task, stage) -> None:
    """
    Schedule asynchronous tasks for processing a given stage.

    Args:
        task (Callable[[int, AsyncWeb3], None]): A function to execute for each item in the stage.
            The function should take two arguments: an item from the stage and a session.
        stage (Iterable[int]): An iterable of items to process with the task function.

    This function uses an a AsyncWeb3 session to execute the provided task function
    for each item in the stage concurrently, with a specified number of workers.

    The number of concurrent workers is defined by `ASYNC_WORKERS_LIMIT`.
    """

    async def f(arg):
        await task(arg)

    await pl.task.each(
        f=f,
        stage=stage,
        workers=ASYNC_WORKERS_LIMIT,
    )
