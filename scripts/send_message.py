import contextlib
import dataclasses
from typing import Any
import json
import random
import argparse

import asyncio
import aiokafka

names = ["phil", "jess", "alex", "sam", "wendy", "arthur", "randy"]
colors = ["red", "blue", "green", "yellow", "orange", "purple"]
n_users = 100

fields = {
    "name": lambda: random.choice(names),
    "color": lambda: random.choice(colors),
    "age": lambda: random.randint(18, 80),
}


@dataclasses.dataclass
class UserUpdate:
    user_id: int
    event_type: str
    event_data: Any


def fake_update(user_id=None, field=None):
    user_id = user_id if user_id is not None else random.randint(0, n_users)
    field = field if field is not None else random.choice(list(fields.keys()))
    return UserUpdate(user_id, field, fields[field]())


async def send_update(producer: aiokafka.AIOKafkaProducer, update: UserUpdate):
    msg_data = json.dumps(dataclasses.asdict(update)).encode("utf-8")
    await producer.send_and_wait("user_updates", msg_data, bytes([update.user_id]))


@contextlib.asynccontextmanager
async def make_producer(loop):
    producer = aiokafka.AIOKafkaProducer(loop=loop, bootstrap_servers=["kafka"])
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


parser = argparse.ArgumentParser(description="send a fake user update")
parser.add_argument("-t", dest="event_type")
parser.add_argument("-u", dest="user_id", type=int, required=False)


async def _main(loop):
    args = parser.parse_args()
    async with make_producer(loop) as producer:
        await send_update(
            producer, fake_update(user_id=args.user_id, field=args.event_type)
        )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
