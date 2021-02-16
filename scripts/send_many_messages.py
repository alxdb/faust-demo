import asyncio
import random

from scripts.send_message import *

names = ["phil", "jess", "alex", "sam", "wendy", "arthur", "randy"]
colors = ["red", "blue", "green", "yellow", "orange", "purple"]
n_users = 100
n_updates = n_users * 10

fields = {
    "name": lambda: random.choice(names),
    "color": lambda: random.choice(colors),
    "age": lambda: random.randint(18, 80),
}


def fake_update():
    user_id = random.randint(0, n_users)
    field = random.choice(list(fields.keys()))
    return UserUpdate(user_id, field, fields[field]())


async def _main(loop):
    async with make_producer(loop) as producer:
        update_sends = [
            send_update(producer, fake_update()) for i in range(n_updates)
        ]
        await asyncio.gather(*update_sends)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
