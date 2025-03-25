import asyncio
import aio_pika
import redis.asyncio as redis
import json
import sys
import os
import yt_dlp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.downloader import download_video
from app.models.task import DownloadTask


async def connect_to_rabbitmq(retries=10, delay=5):
    for attempt in range(retries):
        try:
            connection = await aio_pika.connect_robust(
                f"amqp://guest:guest@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
            )
            print("Connected to RabbitMQ successfully")
            return connection
        except Exception as e:
            if attempt < retries - 1:
                print(f"Failed to connect to RabbitMQ, retrying in {delay} seconds... ({attempt + 1}/{retries})")
                await asyncio.sleep(delay)
            else:
                raise Exception("Could not connect to RabbitMQ after multiple attempts") from e


async def process_task(message: aio_pika.IncomingMessage):
    async with message.process():
        task_data = json.loads(message.body.decode())
        task = DownloadTask(**task_data)

        async with redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0) as redis_client:
            # Сразу устанавливаем статус с URL
            await redis_client.set(f"task:{task.task_id}", json.dumps({"status": "queued", "url": task.url}))

            try:
                print(f"Processing task: URL={task.url}, Format={task.format}")
                # Получаем название видео
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(task.url, download=False)
                    video_title = info.get('title', 'Unknown Title')

                # Обновляем статус с названием
                await redis_client.set(f"task:{task.task_id}",
                                       json.dumps({"status": "processing", "url": task.url, "title": video_title}))

                # Запускаем скачивание
                file_path = await asyncio.to_thread(download_video, task.url, task.format)
                if not isinstance(file_path, str):
                    raise ValueError(f"Expected string, got {type(file_path)}: {file_path}")

                # Завершаем с полным статусом
                status_data = {"status": "completed", "url": task.url, "title": video_title, "file_path": file_path}
                await redis_client.set(f"task:{task.task_id}", json.dumps(status_data))
                print(f"Task completed: {file_path}, Title: {video_title}")
            except Exception as e:
                error_msg = {"status": f"error: {str(e)}", "url": task.url}
                if 'video_title' in locals():
                    error_msg["title"] = video_title
                print(f"Task failed: {error_msg}")
                await redis_client.set(f"task:{task.task_id}", json.dumps(error_msg))


async def main():
    connection = await connect_to_rabbitmq()
    channel = await connection.channel()
    queue = await channel.declare_queue("download_queue")

    await channel.set_qos(prefetch_count=settings.MAX_PREFETCH_COUNT)
    await queue.consume(process_task)
    print("Worker started, waiting for tasks...")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
