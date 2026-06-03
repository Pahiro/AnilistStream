"""
Current Provider: AnimeVerse
Subject to always change this submodule will keep getting updated

Will always implement three functions:
    search(query: str) -> list[Anime]
    get_anime(anime_id: int) -> Anime | None
    get_streams(anime_id: int, episode_id: int) -> list[Stream]
"""

import base64
import hashlib
import hmac
import time

import httpx

from internal.provider.model import Anime, Stream

CF_CLEARANCE = "6WDMjSrrOEQTNgRayFJ_oekpZVQVAYaXBQ0gwFdDoPk-1780445682-1.2.1.1-bwgbTjF20QAWTUHjrvs9g5SFc.dqwBxFerppbwHzWHUzAy59XB0ya0g.o0CU0dMFalUMu3qSUm.xTS3nsU9eBmS1ptZ0ziJDY_Ut4q670IvQLRVh1PKnIRupPVzUP5NNvvCwFsCu_PjzBtLHW_yavxUxzYOAI.Ob3pglzAx3u6cLAmQ.JM3QtPxeb3lvJwQtU2V8CKm7J9t9mGaCgt0F7iriNBPh3GKicplDLGCdLxSeSkGW4dbh_oweu4V_EJbNAdjucPFCPmfICECn6iB4Q43SYFC1OV_tugkO7U3yZbnpr3f7ZR21H2LiufdJ5DK7RIgt8O6zvEz8zgrjEu2CdQ"
SIG_BYTES = 16

COOKIES = {"cf_clearance": CF_CLEARANCE}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0",
    "Referer": "https://animeverse.to/",
    "Origin": "https://animeverse.to",
}
FINGERPRINT = {
    "ua": "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0",
    "language": "en-US",
    "timezone": "America/New_York",
    "hw": 8,
    "screen": "1920x1080x24",
    "canvas": "abc123",
    "webgl": "Intel|Mesa Intel UHD Graphics",
}


def b64url_decode(s: str) -> bytes:
    s = s.replace("-", "+").replace("_", "/")
    s += "=" * ((4 - len(s) % 4) % 4)
    return base64.b64decode(s)


def b64url_encode(b: bytes) -> str:
    return base64.b64encode(b).decode().replace("+", "-").replace("/", "_").rstrip("=")


def sign_request(method: str, path: str, auth_key: str) -> dict:
    ts = str(int(time.time() * 1000))
    message = f"{method}|{path}|{ts}".encode()
    key_bytes = b64url_decode(auth_key)
    sig = hmac.new(key_bytes, message, hashlib.sha256).digest()
    sig_truncated = b64url_encode(sig[:SIG_BYTES])
    return {"x-av-ts": ts, "x-av-sig": sig_truncated}


async def fetch(path: str) -> dict:
    async with httpx.AsyncClient(cookies=COOKIES, headers=HEADERS) as client:
        resp = await client.post(
            "https://animeverse.to/api/v1/session",
            json={"fp": FINGERPRINT},
        )
        resp.raise_for_status()
        auth_key = resp.json()["clientAuthKey"]

        sig_headers = sign_request("GET", path, auth_key)
        resp = await client.get(f"https://animeverse.to{path}", headers=sig_headers)
        resp.raise_for_status()
        return resp.json()


async def search(query: str) -> list[Anime]:
    return []


async def get_anime(anime_id: int) -> Anime | None:
    return None


async def get_streams(anime_id: int, episode_id: int) -> list[Stream]:
    return []
