"""
This example demonstrates most basic operations with single model
"""
from __future__ import annotations

import asyncio
from motor import motor_asyncio as motor


loop = asyncio.get_event_loop()


client = motor.AsyncIOMotorClient('mongodb://localhost:27017')


database = client.aiohttp_dashboard


async def get():
    elemetns = await database.requests.find({}).to_list(None)

    print(elemetns)


loop.run_until_complete(get())
