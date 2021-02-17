from typing import Any
import multiprocessing

import logging

import faust
import faust.web


class UserUpdate(faust.Record):
    user_id: int
    event_type: str
    event_data: Any


app = faust.App("faust-demo", broker="kafka://kafka:9092", store="rocksdb://")
user_updates_topic = app.topic("user_updates", value_type=UserUpdate)

users_table = app.Table("users", partitions=user_updates_topic.partitions, default=dict)
users_by_color_table = app.Table(
    "users_by_color", partitions=user_updates_topic.partitions, default=dict
)


@app.agent(user_updates_topic, concurrency=multiprocessing.cpu_count())
async def process_user_updates(updates: faust.StreamT[UserUpdate]):
    async for update in updates:
        logging.info(f"Recieved update: {update}")

        logging.info(f"Updating user: {update.user_id}")
        user = users_table[update.user_id]
        prev_event_data = user.get(update.event_type)
        user[update.event_type] = update.event_data
        users_table[update.user_id] = user

        if update.event_type == "color":
            logging.info(f"Recieved color update: {update}")
            user_id = str(update.user_id)
            old, new = prev_event_data, update.event_data

            if old != new:
                if old in users_by_color_table:
                    logging.info(f"Updating color: {old}")
                    users_by_color = users_by_color_table[old]
                    if user_id in users_by_color:
                        logging.info(f"Deleting {user_id} from {old}")
                        del users_by_color[user_id]
                        users_by_color_table[old] = users_by_color

                logging.info(f"Updating color: {new}")
                users_by_color = users_by_color_table[new]
                users_by_color[user_id] = users_table[int(user_id)]
                users_by_color_table[new] = users_by_color


@app.page("/users")
async def get_users(web, request):
    return web.json({k: v for k, v in users_table.items()})


@app.page("/users/{user_id}")
@app.table_route(users_table, match_info='user_id')
async def get_user_by_id(web: faust.web.View, request, **kwargs):
    user_id = int(kwargs["user_id"])
    if user_id in users_table:
        return web.json(users_table.get(user_id))
    else:
        raise web.NotFound()


@app.page("/users_by_color")
async def get_all_users_by_color(web, request, **kwargs):
    return web.json(({k: v for k, v in users_by_color_table.items()}))


@app.page("/users_by_color/{color}")
@app.table_route(users_by_color_table, match_info='color')
async def get_users_by_color(web, request, **kwargs):
    color = kwargs["color"]
    if color in users_by_color_table:
        return web.json(users_by_color_table.get(color))
    else:
        raise web.NotFound()
