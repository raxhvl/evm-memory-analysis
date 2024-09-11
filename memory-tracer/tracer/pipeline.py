import pypeln as pl  # type: ignore[import-untyped]
from aiohttp import ClientSession, TCPConnector

from tracer.config import ASYNC_WORKERS_LIMIT


async def schedule_rpc_tasks(task, stage):

    async with ClientSession(connector=TCPConnector(limit=0)) as session:

        async def f(arg):
            await task(arg, session)

        await pl.task.each(
            f=f,
            stage=stage,
            workers=ASYNC_WORKERS_LIMIT,
        )

    print("Closing session")
