from internal.provider import get_anime


async def get_meta(type: str, id: str):
    provider_id = id.split(":")[1]

    anime_data = await get_anime(provider_id)

    if anime_data is None:
        return {"meta": None}

    return {
        "meta": {
            "id": f"as:{provider_id}:{anime_data.anilist_id}:{anime_data.mal_id}",
            "type": "anime",
            "name": anime_data.title,
            "genres": anime_data.genres,
            "poster": anime_data.poster,
            "background": anime_data.banner,
            "description": anime_data.description,
            "releaseInfo": anime_data.start_date,
            "imdbRating": anime_data.rating,
            "videos": [
                {
                    "id": f"as:{provider_id}:{anime_data.anilist_id}:{anime_data.mal_id}:{episode.number}",
                    "title": episode.title,
                    "episode": episode.number,
                    "season": 1,
                }
                for episode in anime_data.episodes
            ],
        }
    }
