from scripts.send_message import *

import asyncio
import random

names = ["phil", "jess", "alex", "sam", "wendy", "arthur", "randy"]
colors = ["red", "blue", "green", "yellow", "orange", "purple"]
n_users = 100
n_updates = 10

fields = {
    "name": lambda: random.choice(names),
    "color": lambda: random.choice(colors),
    "age": lambda: random.randint(18, 80),
}

def fake_update(user_id = None):
    field = random.choice(list(fields.keys()))
    return UserUpdate(user_id if user_id is not None else random.randint(0, n_users), field, fields[field]())


async def _main(loop):
    async with make_producer(loop) as producer:
        fake_updates = [fake_update(i) for i in range(n_updates)]
        update_sends = [send_update(producer, fake_update) for fake_update in fake_updates]
        await asyncio.gather(
            *update_sends
        )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
