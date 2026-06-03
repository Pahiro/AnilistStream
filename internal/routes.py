from fastapi import FastAPI

from internal.stremio.manifest import manifest


def init_routes(app: FastAPI):
    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/manifest.json")
    async def get_manifest():
        return manifest()
