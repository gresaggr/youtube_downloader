import aio_pika
import redis.asyncio as redis
import uuid
import json
from app.core.config import settings


async def init_queue():
    connection = await aio_pika.connect_robust(f"amqp://guest:guest@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/")
    channel = await connection.channel()
    await channel.declare_queue("download_queue")
    return connection, channel


async def close_queue(connection):
    await connection.close()


async def add_task_to_queue(task):
    connection, channel = await init_queue()
    task.task_id = str(uuid.uuid4())
    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(task.dict()).encode()),
        routing_key="download_queue"
    )
    await connection.close()
    return task.task_id


async def get_task_status(task_id: str):
    redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    status = await redis_client.get(f"task:{task_id}")
    await redis_client.close()
    return status.decode() if status else "pending"
