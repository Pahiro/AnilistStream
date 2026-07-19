"""
AniList <-> IMDb id mapping, backed by the Fribb/anime-lists dataset.

The dataset maps every AniList entry to (among others) an IMDb id plus the
TVDB season/episode-offset for that entry. We use it two ways:

  * catalog:  anilist_id  -> imdb id (+ media type)  so items stream via
              the user's existing IMDb-keyed sources (Nuvio, Cinemeta, ...).
  * sync:     imdb id (+ Cinemeta season/episode) -> anilist_id + absolute
              episode, so playing an episode pushes progress back to AniList.
"""

import httpx

MAPPING_URL = (
    "https://raw.githubusercontent.com/Fribb/anime-lists/master/anime-list-full.json"
)

# anilist_id -> record
_ANILIST_REC: dict[int, dict] = {}
# imdb tt id -> list of {anilist_id, season, offset}
_IMDB_INDEX: dict[str, list[dict]] = {}


async def load_mapping() -> None:
    global _ANILIST_REC, _IMDB_INDEX
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.get(MAPPING_URL)
        resp.raise_for_status()
        records = resp.json()

    anilist_rec: dict[int, dict] = {}
    imdb_index: dict[str, list[dict]] = {}
    for rec in records:
        aid = rec.get("anilist_id")
        if aid is None:
            continue
        anilist_rec[aid] = rec

        imdb = rec.get("imdb_id")
        if not imdb:
            continue
        if isinstance(imdb, str):
            imdb = [imdb]
        season = (rec.get("season") or {}).get("tvdb")
        offset = (rec.get("episode_offset") or {}).get("tvdb", 0) or 0
        for tt in imdb:
            imdb_index.setdefault(tt, []).append(
                {"anilist_id": aid, "season": season, "offset": offset}
            )

    _ANILIST_REC = anilist_rec
    _IMDB_INDEX = imdb_index
    print(f"Loaded anime mapping: {len(anilist_rec)} anilist entries, "
          f"{len(imdb_index)} imdb ids")


def imdb_for_anilist(anilist_id: int) -> str | None:
    """Return the first IMDb id mapped to this AniList entry, or None."""
    rec = _ANILIST_REC.get(anilist_id)
    if not rec:
        return None
    imdb = rec.get("imdb_id")
    if not imdb:
        return None
    return imdb[0] if isinstance(imdb, list) else imdb


def resolve_imdb_episode(tt: str, season: int, episode: int) -> tuple[int, int] | None:
    """
    Given a Cinemeta-style (imdb, season, episode), return
    (anilist_id, absolute_progress) for the matching AniList entry, or None.

    Cinemeta episode numbering mirrors TVDB, so we use the dataset's per-entry
    TVDB season + episode_offset. This handles both layouts a shared IMDb id can
    take:

      * true seasons (e.g. Slime S1/S2/S3/S4): filter by matching season, then
        the offset splits multi-cour seasons.
      * one absolute season (e.g. Ascendance, all season 1 with offsets 0/14/
        26/36): every entry is season 1, so the offset alone selects the cour.

    In both cases the right entry is the one with the greatest offset strictly
    below the requested episode, and progress = episode - offset.
    """
    candidates = _IMDB_INDEX.get(tt)
    if not candidates:
        return None

    same_season = [c for c in candidates if c["season"] == season]
    pool = same_season or candidates

    # Entries with an offset below this episode; pick the closest one below.
    below = [c for c in pool if (c["offset"] or 0) < episode]
    if below:
        chosen = max(below, key=lambda c: c["offset"] or 0)
    else:
        chosen = min(pool, key=lambda c: c["offset"] or 0)

    progress = episode - (chosen["offset"] or 0)
    if progress < 1:
        progress = episode
    return chosen["anilist_id"], progress
