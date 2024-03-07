from typing import Literal, TypeAlias

TUniversalResourceLocator: TypeAlias = str
TUniqueIdentifier: TypeAlias = int
TAniListListStatus: TypeAlias = Literal[
    "CURRENT", "PLANNING", "COMPLETED", "DROPPED", "PAUSED", "REPEATING"
]
TAniListMediaStatus: TypeAlias = Literal[
    "FINISHED", "RELEASING", "NOT_YET_RELEASED", "CANCELLED", "HIATUS"
]
TAniListMediaType: TypeAlias = Literal["anime", "manga"]
TCookieListMediaType: TypeAlias = Literal["ANIME", "MANGA", "MUSIC", "NOVEL"]
TAniListMediaFormat: TypeAlias = Literal[
    "TV",
    "TV_SHORT",
    "MOVIE",
    "SPECIAL",
    "OVA",
    "ONA",
    "MUSIC",
    "MANGA",
    "NOVEL",
    "ONE_SHOT",
]
TTimeStamp: TypeAlias = int | float
