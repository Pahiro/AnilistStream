from internal.anilist import sync_anilist
from internal.provider.provider import get_streams


async def get_stream(anilist_token: str | None, type: str, id: str):
    provider_id = id.split(":")[1]
    anilist_id = None if id.split(":")[2] == "None" else int(id.split(":")[2])
    mal_id = None if id.split(":")[3] == "None" else int(id.split(":")[3])
    episode_id = id.split(":")[-1]

    streams_list = await get_streams(provider_id, episode_id)

    streams = [
        {
            "url": stream.url,
            "name": "AnilistStream",
            "description": stream.name,
            "behaviourHints": {"proxyHeaders": stream.headers}
            if stream.headers
            else {},
        }
        for stream in streams_list
    ]

    await sync_anilist(
        anilist_token,
        anilist_id,
        mal_id,
        int(episode_id),
    )

    return {"streams": streams}
