import httpx

ANILIST_URL = "https://graphql.anilist.co"


async def get_anilist_id(mal_id: int | None) -> int | None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            ANILIST_URL,
            json={
                "query": """
                    query ($idMal: Int) {
                        Media(idMal: $idMal, type: ANIME) {
                            id
                        }
                    }
                """,
                "variables": {"idMal": mal_id},
            },
        )
        if response.status_code == 200:
            data = response.json()
            return data["data"]["Media"]["id"]
        return None


async def sync_anilist(
    anilist_token: str | None,
    anilist_id: int | None,
    mal_id: int | None,
    episode_number: int,
):
    if anilist_token is None or (anilist_id is None and mal_id is None):
        return

    if anilist_id is None:
        anilist_id = await get_anilist_id(mal_id)
        if anilist_id is None:
            return

    async with httpx.AsyncClient() as client:
        await client.post(
            ANILIST_URL,
            json={
                "query": """
                    mutation ($mediaId: Int, $progress: Int) {
                        SaveMediaListEntry(mediaId: $mediaId, progress: $progress) {
                            id
                        }
                    }
                """,
                "variables": {"mediaId": anilist_id, "progress": episode_number},
            },
            headers={"Authorization": f"Bearer {anilist_token}"},
        )
