import os
from urllib.parse import quote


def proxy_image(url):
    return f"{os.getenv('BASE_URL')}/proxy/image?url={quote(url)}"
