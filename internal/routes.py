from fastapi import FastAPI

import internal.stremio as stremio

headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
}


def init_routes(app: FastAPI):
    @app.middleware("http")
    async def add_cors_headers(request, call_next):
        response = await call_next(request)
        for key, value in headers.items():
            response.headers[key] = value
        return response

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/manifest.json")
    async def manifest():
        return stremio.get_manifest()

    @app.get("/catalog/{type}/{id}/{extra}.json")
    async def catalog(type: str, id: str, extra: str):
        return stremio.get_catalog(type, id, extra)

    @app.get("/meta/{type}/{id}.json")
    async def meta(type: str, id: str):
        return stremio.get_meta(type, id)

    @app.get("/stream/{type}/{id}.json")
    async def stream(type: str, id: str):
        return stremio.get_stream(type, id)
