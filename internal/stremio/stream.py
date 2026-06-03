from internal.anilist import sync_anilist
from internal.provider.provider import get_streams


async def get_stream(type: str, id: str):
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
        "eyJpdiI6IllOMnRWdlR4U1JtMjltdHdFTThMZkE9PSIsInZhbHVlIjoiXC9LVWhWN08wbDI5MHNMUFE2M0RGQkdvVXUxNTAzWW43Y2RIcDlkUDdCNkphRWcrQ25HaWdGM0xRN1YzWDRnK0hLZ3lPKzVmRjBxRHU4WEhVQ0R4UnhSMlJObEhJZ1F4VCtmSllTTEFrWTRVNnNEUE5sT3ZqcElHQnhkcWFKQ3VLSG01WE1IWkI2a1NOTTQwbGc0a29NcjN4OThcL0xvVnhQK1h5N0FpMWFmVjF5blREZlkzQkEyUVB6M1wvR0t2M2tkIiwibWFjIjoiMmY1MTEyYjQ5Yzc2MGZjYmRmNTI0YWVlYmJmYTQzYTFmNDQxYjZhZmIyNDg5NzZmNzQ3NTM3ODAxNGI0NzI0NyJ9",
        anilist_id,
        mal_id,
        int(episode_id),
    )

    return {"streams": streams}
