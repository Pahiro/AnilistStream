# AniList Lists (Stremio addon)

Fork of [Saadiq8149/AnilistStream](https://github.com/Saadiq8149/AnilistStream),
repurposed after its stream source (AnimeVerse) shut down.

This version does **not** host any streams. Instead it:

- Adds two browsable Stremio catalogs from your AniList account:
  **Currently Watching** and **Plan to Watch**.
- Emits each anime with its **IMDb id** (via the
  [Fribb/anime-lists](https://github.com/Fribb/anime-lists) dataset) so your
  *existing* IMDb-keyed stream sources (Nuvio, Torrentio, Cinemeta, …) provide
  the video. Titles with no IMDb mapping fall back to a browsable `anilist:` id.
- **Syncs your watch progress back to AniList** as you watch: it registers as a
  stream provider, so when you open an episode Stremio also calls this addon,
  which translates the Cinemeta season/episode into the correct AniList entry
  and updates your progress (never rewinding; auto-completing on the last
  episode).

## Configure & install

1. Deploy (see below), reachable at a public HTTPS `BASE_URL`.
2. Create an AniList API client at <https://anilist.co/settings/developer> with
   redirect URL `{BASE_URL}/configure`; set its Client ID as `ANILIST_CLIENT_ID`.
3. Open `{BASE_URL}/configure`, authorise with AniList, and install the
   generated `{BASE_URL}/<token>/manifest.json` into Stremio.

## Run

```
docker run -d -p 7000:8000 \
  --env ANILIST_CLIENT_ID=<your_client_id> \
  --env BASE_URL=<https://your.domain> \
  <image>
```

## Notes

- Watch-progress sync follows Cinemeta's TVDB-style numbering. For the common
  case (one AniList entry per IMDb season, or a single absolute season) it is
  exact; unusual franchise numbering may occasionally target the wrong entry.

## Disclaimer

Independent open-source project, not affiliated with Stremio or AniList. It
hosts no video content and links to no streams; it only reads/writes your own
AniList data and provides catalog metadata.
