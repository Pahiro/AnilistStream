from urllib.parse import unquote

import httpx
from fastapi import FastAPI
from fastapi.responses import Response

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
        return await stremio.get_catalog(type, id, extra)

    @app.get("/meta/{type}/{id}.json")
    async def meta(type: str, id: str):
        return await stremio.get_meta(type, id)

    @app.get("/stream/{type}/{id}.json")
    async def stream(type: str, id: str):
        return await stremio.get_stream(type, id)

    @app.get("/proxy/image")
    async def proxy_image(url: str):
        async with httpx.AsyncClient() as client:
            r = await client.get(unquote(url))

        return Response(content=r.content, media_type=r.headers.get("content-type"))
