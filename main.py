from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from internal.provider.provider import init_provider
from internal.routes import init_routes

load_dotenv()
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    await init_provider(scheduler)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
init_routes(app, templates)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
