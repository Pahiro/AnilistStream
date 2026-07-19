from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from internal.anilist import load_mapping
from internal.routes import init_routes

load_dotenv()


async def _refresh_mapping() -> None:
    try:
        await load_mapping()
    except Exception as e:  # keep serving even if the dataset is unreachable
        print(f"Error loading anime mapping: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    await _refresh_mapping()
    scheduler.add_job(_refresh_mapping, "interval", hours=24)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
init_routes(app, templates)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
