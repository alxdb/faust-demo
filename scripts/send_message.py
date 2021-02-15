import contextlib
import dataclasses
from typing import Any
import json

import asyncio
import aiokafka

@dataclasses.dataclass
class UserUpdate():
    user_id: int
    event_type: str
    event_data: Any


async def send_update(producer: aiokafka.AIOKafkaProducer, update: UserUpdate):
    msg_data = json.dumps(dataclasses.asdict(update)).encode("utf-8")
    await producer.send_and_wait("user_updates", msg_data)


@contextlib.asynccontextmanager
async def make_producer(loop):
    producer = aiokafka.AIOKafkaProducer(loop=loop, bootstrap_servers=["kafka"])
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


async def _main(loop):
    async with make_producer(loop) as producer:
        event = UserUpdate(user_id=0, event_type="name", event_data="phil")
        await send_update(producer, event)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
