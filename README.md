<p align="center">
  <img src="https://aniliststream.edmit.in/logo.png" alt="AnilistStream Logo" width="120" />
</p>

<h1 align="center">AnilistStream</h1>

<p align="center">
  A self-hostable Stremio addon for HTTP anime streaming with AniList watch progress syncing.
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/Saadiq8149/AnilistStream?style=for-the-badge&logo=github" alt="GitHub Stars" />
  <img src="https://img.shields.io/badge/Stremio-Addon-blue?style=for-the-badge&logo=stremio" alt="Stremio Addon" />
</p>

<p align="center">
  <a href="https://aniliststream.edmit.in">
    <img src="https://img.shields.io/badge/⚡%20Install%20Now-AnilistStream-6441A5?style=for-the-badge&logo=stremio&logoColor=white" alt="Install AnilistStream" />
  </a>
  <a href="https://hub.docker.com/r/12345saadiq/aniliststream">
    <img src="https://img.shields.io/badge/Docker%20Hub-12345saadiq%2Faniliststream-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Hub Repository" />
  </a>
</p>

---

## Self Hosting
```
docker run -d -p 7000:8000 --env ANILIST_CLIENT_ID={} --env BASE_URL={} 12345saadiq/aniliststream
```
---
### AniList OAuth Setup

To enable watch progress syncing, you need to register an AniList API application:

1. Go to [https://anilist.co/settings/developer](https://anilist.co/settings/developer)
2. Click **Create new client**
3. Set the **Redirect URL** to your instance's callback URL (`{BASE_URL}/configure`)
4. Copy the **Client ID** into your environment variables

Users can then log in from the web UI to authorize progress syncing.

---

## Disclaimer

AnilistStream is an independent open-source project and is **not affiliated with, endorsed by, or connected to Stremio, AniList, or any content provider** used as a stream source.

This addon indexes and links to streams hosted by third-party services. The developers of AnilistStream do not host, store, or distribute any video content. Users are responsible for ensuring that their use of this addon complies with the laws and regulations applicable in their jurisdiction.

The public instance is provided on a best-effort basis with no guarantees of uptime, availability, or continued operation.
