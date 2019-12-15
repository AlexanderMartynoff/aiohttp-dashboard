"""
This example demonstrates most basic operations with single model
"""
from tortoise import Tortoise, fields, run_async
from tortoise.models import Model


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    datetime = fields.DatetimeField(null=True)
    json = fields.JSONField(null=True)

    class Meta:
        table = "event"

    def __str__(self):
        return self.name


async def run():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    event = await Event.create(name="Test", json={1: 2})
    event_2 = await Event.create(name="Test 2", json={2: 2})


    events = Event.filter()
    # >>> Updated name

    for _ in await events:
        print(_.json)

    events = events.filter(id__in=[1])

    for _ in await events.values():
        print(_)


if __name__ == "__main__":
    run_async(run())