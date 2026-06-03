from dotenv import load_dotenv
from fastapi import FastAPI

from internal.routes import init_routes

load_dotenv()

app = FastAPI()
init_routes(app)
