from internal.anilist import (
    description_of,
    episode_count,
    get_media,
    rating_of,
    title_of,
    year_of,
)

# Meta is only served for our own `anilist:` ids (list items with no IMDb
# mapping). IMDb (`tt`) items are rendered by Cinemeta.


async def get_meta(type: str, id: str):
    try:
        anilist_id = int(id.split(":")[1])
    except (IndexError, ValueError):
        return {"meta": None}

    media = await get_media(anilist_id)
    if media is None:
        return {"meta": None}

    cover = media.get("coverImage") or {}
    total = episode_count(media)

    videos = [
        {
            "id": f"anilist:{anilist_id}:{number}",
            "title": f"Episode {number}",
            "episode": number,
            "season": 1,
        }
        for number in range(1, total + 1)
    ]

    return {
        "meta": {
            "id": f"anilist:{anilist_id}",
            "type": "series",
            "name": title_of(media),
            "genres": media.get("genres") or [],
            "poster": cover.get("extraLarge") or cover.get("large"),
            "background": media.get("bannerImage"),
            "description": description_of(media),
            "releaseInfo": year_of(media),
            "imdbRating": rating_of(media),
            "videos": videos,
        }
    }
