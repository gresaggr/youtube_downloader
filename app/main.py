from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router
from app.services.queue_service import init_queue, close_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection, channel = await init_queue()
    yield
    await close_queue(connection)


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Монтируем директорию downloads для раздачи файлов
app.mount("/downloads", StaticFiles(directory="/downloads"), name="downloads")
templates = Jinja2Templates(directory="app/templates")

app.include_router(router)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
