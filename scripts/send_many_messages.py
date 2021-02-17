import asyncio
import random

from scripts.send_message import *

n_updates = n_users * 10


async def _main(loop):
    async with make_producer(loop) as producer:
        update_sends = [send_update(producer, fake_update()) for i in range(n_updates)]
        await asyncio.gather(*update_sends)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
