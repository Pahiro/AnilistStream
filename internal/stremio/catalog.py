from urllib.parse import unquote

from internal.provider import search


async def get_catalog(type: str, id: str, extra: str):
    extra = unquote(extra)
    query = extra.split("=")[-1]

    anime_list = await search(query)

    metas = [
        {
            "id": f"as:{anime.id}:{anime.anilist_id}:{anime.mal_id}",
            "type": "anime",
            "name": anime.title,
            "genres": anime.genres,
            "poster": anime.poster,
            "background": anime.banner,
            "description": anime.description,
            "releaseInfo": anime.start_date,
            "imdbRating": anime.rating,
        }
        for anime in anime_list
    ]

    return {"metas": metas}
