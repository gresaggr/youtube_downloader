from pydantic import BaseModel
from typing import Optional

class DownloadTask(BaseModel):
    url: str
    format: str
    resolution: Optional[str] = None
    task_id: Optional[str] = None