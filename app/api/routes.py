from fastapi import APIRouter, HTTPException
from app.models.task import DownloadTask
from app.services.queue_service import add_task_to_queue, get_task_status
from app.core.config import settings
import re
import json

router = APIRouter()


def validate_youtube_url(url: str) -> bool:
    pattern = r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[A-Za-z0-9_-]{11}"
    short_pattern = r"^[A-Za-z0-9_-]{11}$" # если просто id (yQebXIkBAws)
    return bool(re.match(pattern, url) or re.match(short_pattern, url))


@router.post("/download")
async def start_download(task: DownloadTask):
    if not validate_youtube_url(task.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    if task.format not in settings.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Invalid format")
    task_id = await add_task_to_queue(task)
    return {
        "task_id": task_id,
        "status": "queued",
        "check_status_pause": settings.CHECK_STATUS_PAUSE  # Добавляем задержку
    }


@router.get("/status/{task_id}")
async def check_status(task_id: str):
    status_raw = await get_task_status(task_id)
    try:
        status_data = json.loads(status_raw)
        status = status_data.get("status", "unknown")
        url = status_data.get("url")
        title = status_data.get("title")
        file_path = status_data.get("file_path")
        if status == "completed" and file_path:
            file_name = file_path.split("/")[-1]
            download_url = f"/downloads/{file_name}"
            return {"task_id": task_id, "status": status, "url": url, "title": title, "download_url": download_url}
        return {"task_id": task_id, "status": status, "url": url, "title": title}
    except json.JSONDecodeError:
        return {"task_id": task_id, "status": status_raw}
