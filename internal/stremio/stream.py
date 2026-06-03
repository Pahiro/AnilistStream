from internal.provider.provider import get_streams


async def get_stream(type: str, id: str):
    provider_id = id.split(":")[1]
    episode_id = id.split(":")[-1]

    streams_list = await get_streams(provider_id, episode_id)

    streams = [
        {
            "url": stream.url,
            "name": stream.name,
            "behaviourHints": {"proxyHeaders": stream.headers}
            if stream.headers
            else {},
        }
        for stream in streams_list
    ]

    return {"streams": streams}
