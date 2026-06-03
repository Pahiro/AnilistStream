from fastapi.responses import FileResponse


def get_manifest():
    return FileResponse("public/manifest.json")
