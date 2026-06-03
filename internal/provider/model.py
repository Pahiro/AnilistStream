from pydantic import BaseModel


class EpisodeData(BaseModel):
    number: int
    title: str | None = None
    thumbnail: str | None = None
    release_date: str | None = None


class Anime(BaseModel):
    id: str
    anilist_id: int | None = None
    mal_id: int | None = None
    title: str
    description: str | None = None
    episodes: list[EpisodeData] | None = None
    start_date: str | None = None
    end_date: str | None = None
    genres: list[str] | None = None
    poster: str | None = None
    banner: str | None = None
    rating: float | None = None


class Stream(BaseModel):
    url: str
    name: str
    type: str
    headers: dict[str, str] | None = None
