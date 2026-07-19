"""
We don't host video. This handler exists purely to catch the "user is watching
episode N" signal and push it back to AniList as watch progress.

Stremio queries every installed addon for streams, so for IMDb (`tt`) ids our
addon runs alongside the user's real stream sources (Nuvio, etc.): we recognise
the anime, sync progress, and return a single confirmation entry linking to
AniList. For anime not in the mapping we stay silent (return nothing).
"""

from internal.anilist import resolve_imdb_episode, save_progress


def _confirmation(anilist_id: int, progress: int) -> dict:
    return {
        "name": "AniList",
        "description": f"✓ Synced — progress set to episode {progress}",
        "externalUrl": f"https://anilist.co/anime/{anilist_id}",
    }


async def get_stream(anilist_token: str | None, type: str, id: str):
    # Our own ids for list items without an IMDb mapping: anilist:<id>:<episode>
    if id.startswith("anilist:"):
        parts = id.split(":")
        anilist_id = int(parts[1])
        episode = int(parts[2]) if len(parts) > 2 else 1
        await save_progress(anilist_token, anilist_id, episode)
        return {"streams": [_confirmation(anilist_id, episode)]}

    # IMDb ids from Cinemeta: "tt123" (movie) or "tt123:season:episode"
    if id.startswith("tt"):
        parts = id.split(":")
        tt = parts[0]
        if len(parts) >= 3:
            season, episode = int(parts[1]), int(parts[2])
        else:
            season, episode = 1, 1

        resolved = resolve_imdb_episode(tt, season, episode)
        if resolved is None:
            return {"streams": []}  # not an anime we track; stay out of the way

        anilist_id, progress = resolved
        await save_progress(anilist_token, anilist_id, progress)
        return {"streams": [_confirmation(anilist_id, progress)]}

    return {"streams": []}
