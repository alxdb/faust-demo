from typing import Any
import logging

import faust


class UserUpdate(faust.Record):
    user_id: int
    event_type: str
    event_data: Any


app = faust.App("faust-demo", broker="kafka://kafka:9092")
user_updates = app.topic("user_updates", value_type=UserUpdate, partitions=8)
users = app.Table("user", partitions=8)


@app.agent(user_updates)
async def process_user_updates(updates: faust.StreamT[UserUpdate]):
    async for update in updates:
        logging.info(f"recieved update: {update}")
        user = users.get(update.user_id)
        if user:
            user[update.event_type] = update.event_data
            users[update.user_id] = user
        else:
            users[update.user_id] = {update.event_type: update.event_data}


@app.page("/users")
async def get_users(self, request):
    return self.json(users)


