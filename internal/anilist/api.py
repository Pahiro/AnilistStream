"""Thin AniList GraphQL client: read lists, read media, write progress/status."""

import re

import httpx

ANILIST_URL = "https://graphql.anilist.co"

_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str | None) -> str | None:
    if not text:
        return text
    return _TAG_RE.sub("", text).replace("&mdash;", "-").strip()


async def _query(query: str, variables: dict, token: str | None = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            ANILIST_URL,
            json={"query": query, "variables": variables},
            headers=headers,
        )
        resp.raise_for_status()
        payload = resp.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]


async def viewer_id(token: str) -> int | None:
    data = await _query("query { Viewer { id } }", {}, token=token)
    return (data.get("Viewer") or {}).get("id")


_LIST_QUERY = """
query ($userId: Int, $status: MediaListStatus) {
  MediaListCollection(userId: $userId, type: ANIME, status: $status) {
    lists {
      entries {
        progress
        media {
          id
          idMal
          format
          episodes
          genres
          averageScore
          siteUrl
          startDate { year }
          title { english romaji }
          description(asHtml: false)
          coverImage { extraLarge large }
          bannerImage
        }
      }
    }
  }
}
"""


async def get_list(status: str, token: str) -> list[dict]:
    """Return the authenticated user's anime list for a given status."""
    uid = await viewer_id(token)
    if uid is None:
        return []
    data = await _query(_LIST_QUERY, {"userId": uid, "status": status}, token=token)
    collection = (data.get("MediaListCollection") or {}).get("lists") or []
    entries: list[dict] = []
    for lst in collection:
        entries.extend(lst.get("entries") or [])
    return entries


_MEDIA_QUERY = """
query ($id: Int) {
  Media(id: $id, type: ANIME) {
    id
    idMal
    format
    episodes
    genres
    averageScore
    siteUrl
    startDate { year }
    title { english romaji }
    description(asHtml: false)
    coverImage { extraLarge large }
    bannerImage
    nextAiringEpisode { episode }
  }
}
"""


async def get_media(anilist_id: int) -> dict | None:
    data = await _query(_MEDIA_QUERY, {"id": anilist_id})
    return data.get("Media")


_ENTRY_QUERY = """
query ($id: Int) {
  Media(id: $id, type: ANIME) {
    episodes
    mediaListEntry { progress status }
  }
}
"""

_SAVE_MUTATION = """
mutation ($mediaId: Int, $progress: Int, $status: MediaListStatus) {
  SaveMediaListEntry(mediaId: $mediaId, progress: $progress, status: $status) {
    id progress status
  }
}
"""


async def save_progress(
    token: str, anilist_id: int, progress: int, status: str = "CURRENT"
) -> dict | None:
    """
    Set watch progress on AniList, never rewinding. Auto-completes when the
    final episode is reached. Returns the (unchanged or updated) entry.
    """
    if not token:
        return None

    data = await _query(_ENTRY_QUERY, {"id": anilist_id}, token=token)
    media = data.get("Media") or {}
    entry = media.get("mediaListEntry") or {}
    current = entry.get("progress") or 0

    # Never regress a further-along or already-completed entry.
    if entry.get("status") == "COMPLETED" or current >= progress:
        return entry or None

    total = media.get("episodes")
    if total and progress >= total:
        progress = total
        status = "COMPLETED"

    data = await _query(
        _SAVE_MUTATION,
        {"mediaId": anilist_id, "progress": progress, "status": status},
        token=token,
    )
    return data.get("SaveMediaListEntry")


# ---- presentation helpers --------------------------------------------------

def title_of(media: dict) -> str:
    t = media.get("title") or {}
    return t.get("english") or t.get("romaji") or "Unknown"


def description_of(media: dict) -> str | None:
    return _clean(media.get("description"))


def rating_of(media: dict) -> float | None:
    score = media.get("averageScore")
    return round(score / 10, 1) if score else None


def year_of(media: dict) -> str | None:
    y = (media.get("startDate") or {}).get("year")
    return str(y) if y else None


def episode_count(media: dict) -> int:
    eps = media.get("episodes")
    if eps:
        return eps
    nxt = (media.get("nextAiringEpisode") or {}).get("episode")
    if nxt:
        return max(nxt - 1, 1)
    return 1
