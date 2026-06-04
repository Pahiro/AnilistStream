import os
from urllib.parse import unquote

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates

import internal.stremio as stremio

headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
}


def init_routes(app: FastAPI, templates: Jinja2Templates):
    @app.middleware("http")
    async def add_cors_headers(request, call_next):
        response = await call_next(request)
        for key, value in headers.items():
            response.headers[key] = value
        return response

    @app.get("/", response_class=HTMLResponse)
    # @app.get("/{anilist_token}", response_class=HTMLResponse)
    async def root(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"server_url": os.getenv("BASE_URL")},
        )

    @app.get("/configure", response_class=HTMLResponse)
    @app.get("/{anilist_token}/configure", response_class=HTMLResponse)
    @app.get("/configure.json", response_class=HTMLResponse)
    @app.get("/{anilist_token}/configure.json", response_class=HTMLResponse)
    async def configure(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="configure.html",
            context={
                "client_id": os.getenv("ANILIST_CLIENT_ID"),
                "server_url": os.getenv("BASE_URL"),
            },
        )

    @app.get("/manifest.json")
    @app.get("/{anilist_token}/manifest.json")
    async def manifest():
        return stremio.get_manifest()

    @app.get("/logo.png")
    @app.get("/{anilist_token}/logo.png")
    async def logo():
        return FileResponse("public/logo.png")

    @app.get("/catalog/{type}/{id}/{extra}.json")
    @app.get("/{anilist_token}/catalog/{type}/{id}/{extra}.json")
    async def catalog(type: str, id: str, extra: str):
        if not type == "anime" or not id == "as-search":
            return Response(status_code=404)
        return await stremio.get_catalog(type, id, extra)

    @app.get("/meta/{type}/{id}.json")
    @app.get("/{anilist_token}/meta/{type}/{id}.json")
    async def meta(type: str, id: str):
        if not type == "anime" or not id.startswith("as:"):
            return Response(status_code=404)
        return await stremio.get_meta(type, id)

    @app.get("/stream/{type}/{id}.json")
    async def stream_without_token(type: str, id: str):
        if not type == "anime" or not id.startswith("as:"):
            return Response(status_code=404)
        return await stremio.get_stream(None, type, id)

    @app.get("/{anilist_token}/stream/{type}/{id}.json")
    async def stream(anilist_token: str | None, type: str, id: str):
        if not type == "anime" or not id.startswith("as:"):
            return Response(status_code=404)
        return await stremio.get_stream(anilist_token, type, id)

    @app.get("/proxy/image")
    @app.get("/{anilist_token}/proxy/image")
    async def proxy_image(url: str):
        async with httpx.AsyncClient() as client:
            r = await client.get(unquote(url))

        return Response(content=r.content, media_type=r.headers.get("content-type"))
