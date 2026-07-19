from internal.anilist import (
    description_of,
    get_list,
    imdb_for_anilist,
    rating_of,
    title_of,
    year_of,
)

# Stremio catalog id -> AniList list status
STATUS_BY_CATALOG = {
    "anilist-current": "CURRENT",
    "anilist-planning": "PLANNING",
}


def _poster(media: dict) -> str | None:
    cover = media.get("coverImage") or {}
    return cover.get("extraLarge") or cover.get("large")


def _meta_type(media: dict) -> str:
    return "movie" if media.get("format") == "MOVIE" else "series"


def entries_to_metas(entries: list[dict]) -> list[dict]:
    metas = []
    for entry in entries:
        media = entry["media"]
        tt = imdb_for_anilist(media["id"])
        if tt:
            meta_id = tt
            meta_type = _meta_type(media)
        else:
            # No IMDb mapping: keep it browsable/syncable via our own id.
            meta_id = f"anilist:{media['id']}"
            meta_type = "series"

        metas.append(
            {
                "id": meta_id,
                "type": meta_type,
                "name": title_of(media),
                "poster": _poster(media),
                "background": media.get("bannerImage"),
                "description": description_of(media),
                "genres": media.get("genres") or [],
                "releaseInfo": year_of(media),
                "imdbRating": rating_of(media),
            }
        )

    return metas


async def get_catalog(anilist_token: str | None, type: str, id: str, extra: str = ""):
    status = STATUS_BY_CATALOG.get(id)
    if status is None or not anilist_token:
        return {"metas": []}

    entries = await get_list(status, anilist_token)
    return {"metas": entries_to_metas(entries)}
