from fastapi.responses import FileResponse


def manifest():
    return FileResponse("public/manifest.json")
