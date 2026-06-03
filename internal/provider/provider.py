"""
Current Provider: AnimeVerse
Can change if this provider stops working

Will always implement three functions:
    init_provider() -> None // For any preproceesing needed for the api
    search(query: str) -> list[Anime]
    get_anime(anime_id: int) -> Anime | None
    get_streams(anime_id: int, episode_id: int) -> list[Stream]
"""

import base64
import hashlib
import hmac
import json
import re
import time
from datetime import datetime
from urllib.parse import quote

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from rapidfuzz import fuzz, process

from internal.provider.model import Anime, EpisodeData, Stream

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


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


async def init_provider(scheduler: AsyncIOScheduler) -> None:
    async def fetch_animeverse_catalog() -> None:
        # url = "/api/v1/catalog"
        # try:
        #     response = await fetch(url)
        #     global animeverse_catalog
        #     animeverse_catalog = {}

        #     for item in response["items"]:
        #         animeverse_catalog[item["id"]] = item["slug"]

        #     print(f"Animeverse catalog updated at {datetime.now()}")

        # except Exception as e:
        #     print(f"Error fetching animeverse catalog: {e}")

        # Test mode
        with open("public/animeverse_catalog.json", "r") as f:
            data = json.load(f)["items"]
            global SEARCH_INDEX, SEARCH_CHOICES
            SEARCH_INDEX = data
            SEARCH_CHOICES = [normalize(item.get("searchTitle", "")) for item in data]

    await fetch_animeverse_catalog()
    scheduler.add_job(fetch_animeverse_catalog, "interval", hours=6)


async def search(query: str) -> list[Anime]:
    query = normalize(query)

    matches = process.extract(
        query,
        SEARCH_CHOICES,
        scorer=fuzz.token_set_ratio,
        limit=20,
        score_cutoff=60,
    )

    results = []
    for match in matches:
        anime = SEARCH_INDEX[match[2]]
        poster_url = f"https://animeverse.to{anime.get('thumb', '')}"
        banner_url = f"https://animeverse.to{anime.get('cover', '')}"

        results.append(
            Anime(
                id=anime.get("slug", ""),
                title=anime.get("alternativeTitle", "") or anime.get("title", ""),
                poster=f"http://127.0.0.1:8000/proxy/image?url={quote(poster_url)}",
                banner=f"http://127.0.0.1:8000/proxy/image?url={quote(banner_url)}",
                genres=anime.get("genres", []),
                rating=anime.get("rating", 0.0),
                start_date=str(anime.get("year", "")),
                episodes=[],
            )
        )

    return results


async def get_anime(anime_id: str) -> Anime | None:
    url = f"/api/v1/anime/{anime_id}"
    try:
        response = await fetch(url)
        catalog_data = [item for item in SEARCH_INDEX if item["slug"] == anime_id][0]

        poster_url = f"https://animeverse.to{response.get('thumb', '')}"
        banner_url = f"https://animeverse.to{response.get('cover', '')}"

        episodes = []
        episodes_data = response.get("episodes", [])
        for episode in episodes_data:
            episodes.append(
                EpisodeData(
                    id=episode.get("id"),
                    number=episode.get("number"),
                    title=episode.get("title", f"Episode {episode.get('number')}"),
                )
            )

        return Anime(
            id=anime_id,
            mal_id=response.get("malId"),
            title=catalog_data.get("alternativeTitle")
            or response.get("title", "Unknown"),
            description=response.get("synopsis"),
            episodes=episodes,
            start_date=response.get("start_date"),
            genres=catalog_data.get("genres"),
            poster=f"http://127.0.0.1:8000/proxy/image?url={quote(poster_url)}",
            banner=f"http://127.0.0.1:8000/proxy/image?url={quote(banner_url)}",
            rating=response.get("rating"),
        )

    except httpx.HTTPStatusError:
        return None


async def get_streams(anime_id: str, episode_id: str) -> list[Stream]:
    url = f"/api/v1/anime/{anime_id}/stream/{episode_id}"
    try:
        response = await fetch(url)
        return [
            Stream(
                url=response.get("stream", ""),
                name="AnilistStream AnimeVerse Sub",
                type="sub",
                headers=None,
            )
        ]
    except httpx.HTTPStatusError:
        return []
