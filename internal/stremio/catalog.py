from urllib.parse import unquote

from internal.provider import search


def get_catalog(type: str, id: str, extra: str):
    extra = unquote(extra)
    query = extra.split("=")[-1]

    anime_list = search(query)

    metas = [
        {
            "id": f"as:{anime.id}:{anime.anilist_id or 'null'}:{anime.mal_id or 'null'}",
            "type": "anime",
            "name": anime.title,
            "genres": anime.genres,
            "poster": anime.poster,
            "background": anime.banner,
            "description": anime.description,
            # "releaseInfo" - later
            "imdbRating": anime.rating,
        }
        for anime in anime_list
    ]

    return {"metas": metas}
