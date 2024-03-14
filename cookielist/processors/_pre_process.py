import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Literal
from urllib import parse

from cookielist.environment import env
from cookielist.utils import BADGE_REDIRECT_SERVERS, JsonToken, Types


@dataclass(repr=False, eq=False, frozen=True)
class AniListMedia:
    __slots__ = (
        "mediaId",
        "mediaTitle",
        "coverImage",
        "listStatus",
        "mediaStatus",
        "mediaType",
        "mediaFormat",
        "mediaEpisodeCount",
        "mediaDuration",
        "userMediaProgress",
        "nextAiringAt",
        "nextAiringEpisode",
        "mediaAniListSiteUrl",
        "mediaMyAnimeListSiteUrl",
    )

    mediaId: Types.TUniqueIdentifier
    mediaTitle: str
    coverImage: Types.TUniversalResourceLocator
    listStatus: Types.TAniListListStatus
    mediaStatus: Types.TAniListMediaStatus
    mediaType: Types.TAniListMediaType
    mediaFormat: Types.TAniListMediaFormat
    mediaEpisodeCount: int | None
    mediaDuration: int | None
    userMediaProgress: int | None
    nextAiringAt: Types.TTimeStamp | None
    nextAiringEpisode: int | None
    mediaAniListSiteUrl: Types.TUniversalResourceLocator
    mediaMyAnimeListSiteUrl: Types.TUniversalResourceLocator


@dataclass(repr=False, eq=False, frozen=True)
class AniListUser:
    __slots__ = (
        "userId",
        "userHandle",
        "userAniListSiteUrl",
        "userAvatar",
        "profileColor",
        "animeCount",
        "animeMinutesWatched",
        "animeEpisodesWatched",
        "mangaCount",
        "mangaChaptersRead",
    )

    userId: Types.TUniqueIdentifier
    userHandle: str
    userAniListSiteUrl: Types.TUniversalResourceLocator
    userAvatar: Types.TUniversalResourceLocator
    profileColor: str
    animeCount: int
    animeMinutesWatched: int
    animeEpisodesWatched: int
    mangaCount: int
    mangaChaptersRead: int


@dataclass(repr=False, eq=False, frozen=False)
class CookieListOptions:
    __slots__ = (
        "timezoneName",
        "timeFormatString",
        "dateFormatString",
        "firstDayOfWeek",
        "mediaTitleLanguage",
        "badgeTemplate",
        "commentSection",
        "badgeServer",
        "badgeOptions",
        "isBadgeServerCustom",
        "userOptionFormatted"
    )
    timezoneName: str
    timeFormatString: str
    dateFormatString: str
    firstDayOfWeek: str
    mediaTitleLanguage: Literal["english", "romaji", "native"]
    badgeTemplate: str | None
    commentSection: int
    badgeServer: str
    isBadgeServerCustom: bool
    badgeOptions: dict[str, dict[str, str]]
    userOptionFormatted: None | dict[str, str]


@dataclass(repr=False, eq=False, frozen=True)
class MediaCollection:
    CURRENT: deque[AniListMedia] = field(default_factory=deque)
    PLANNING: deque[AniListMedia] = field(default_factory=deque)
    COMPLETED: deque[AniListMedia] = field(default_factory=deque)
    DROPPED: deque[AniListMedia] = field(default_factory=deque)
    PAUSED: deque[AniListMedia] = field(default_factory=deque)
    REPEATING: deque[AniListMedia] = field(default_factory=deque)
    Map: dict[Types.TUniqueIdentifier, AniListMedia] = field(default_factory=dict)
    Statuses: dict[Types.TUniqueIdentifier, Types.TAniListListStatus] = field(
        default_factory=dict
    )


def _format_user_settings(options: CookieListOptions, data: dict[str, dict]) -> dict:
    _formatted = {
        "-comment-activity": {
            "description": "Comment section URI",
            "placeholder": "https://anilist.co/activity/000000000",
            "value": (
                f"https://anilist.co/activity/{options.commentSection}"
                if options.commentSection is not None
                else ""
            ),
        },
        "-badge-server": {
            "description": "Custom badge's server",
            "placeholder": BADGE_REDIRECT_SERVERS.get(str(data["user"]["id"])[0], ""),
            "value": options.badgeServer if options.isBadgeServerCustom else "",
        },
        "--badge-template": {
            "description": "Preferred badge template",
            "placeholder": "(user-selected)",
            "value": options.badgeTemplate,
        },
    }

    formatted = []
    for id, values in _formatted.items():
        formatted.append({**values, "id": id})
    return formatted


def _sanitize_options(data: dict[str, dict]) -> dict:
    options: dict[str, str | int | list[int | str]] = JsonToken.find_and_decode(
        data["user"]["about"] or ""
    )
    sanitized = {}

    sanitized["badgeTemplate"] = options.get("-badge-template")
    try:
        sanitized["commentSection"] = int(
            options.get("-comment-activity")
            .replace("https://anilist.co/activity", "")
            .lstrip("/")
            .split("/")[0]
            .split("?")[0]
        )
    except:
        sanitized["commentSection"] = None

    sanitized["badgeServer"] = options.get("-badge-server")
    if sanitized["badgeServer"] is None:
        sanitized["badgeServer"] = BADGE_REDIRECT_SERVERS.get(
            str(data["user"]["id"])[0], ""
        )
        sanitized["isBadgeServerCustom"] = False
    else:
        sanitized["isBadgeServerCustom"] = True

    sanitized["badgeOptions"] = defaultdict(list)
    for query in re.findall(
        rf"https?://(?:{sanitized['badgeServer']})/(?:{data['user']['id']}).svg(?:\?|/\?)(.*?)[\)|\s]",
        data["user"]["about"] or "",
    ):
        query_parsed = parse.parse_qsl(query)
        query_dict = dict(query_parsed)
        sanitized["badgeOptions"][
            query_dict.get("template", env.string("COOKIELIST_DEFAULT_BADGE_TEMPLATE"))
        ].extend(query_parsed)
    sanitized["badgeOptions"] = {
        template: dict(arguments)
        for template, arguments in sanitized["badgeOptions"].items()
    }
    return sanitized


def process(
    data: dict[str, dict]
) -> tuple[MediaCollection, AniListUser, CookieListOptions]:
    Options = CookieListOptions(
        userOptionFormatted=None,
        timezoneName=data["options"]["timezoneName"],
        timeFormatString=data["options"]["timeFormatString"],
        dateFormatString=data["options"]["dateFormatString"],
        firstDayOfWeek=data["options"]["firstDayOfWeek"],
        mediaTitleLanguage=data["options"]["mediaTitleLanguage"],
        **_sanitize_options(data),
    )
    Options.userOptionFormatted = _format_user_settings(Options, data)

    Media: defaultdict[Types.TAniListListStatus, deque[AniListMedia]] = defaultdict(
        deque
    )

    User = AniListUser(
        userId=data["user"]["id"],
        userHandle=data["user"]["name"],
        userAniListSiteUrl=data["user"]["siteUrl"],
        userAvatar=data["user"]["avatar"]["large"],
        profileColor=data["user"]["options"]["profileColor"],
        animeCount=data["user"]["statistics"]["anime"]["count"],
        animeMinutesWatched=data["user"]["statistics"]["anime"]["minutesWatched"],
        animeEpisodesWatched=data["user"]["statistics"]["anime"]["episodesWatched"],
        mangaCount=data["user"]["statistics"]["manga"]["count"],
        mangaChaptersRead=data["user"]["statistics"]["manga"]["chaptersRead"],
    )

    getLanguageNameFunctionsMap = dict(
        english=lambda _: _["english"] or _["romaji"] or _["native"],
        romaji=lambda _: _["romaji"] or _["english"] or _["native"],
        native=lambda _: _["native"] or _["romaji"] or _["english"],
    )
    getLanguageNameFunction = getLanguageNameFunctionsMap.get(
        Options.mediaTitleLanguage.lower(), getLanguageNameFunctionsMap["english"]
    )

    for entry in sum(data["list"], []):
        media: dict[str, int | str | None | dict[str, str | int]] = entry["media"]
        type = "manga" if media["type"] == "MANGA" else "anime"

        if media["nextAiringEpisode"] is not None:
            nextAiringAt = media["nextAiringEpisode"]["airingAt"]
            nextAiringEpisode = media["nextAiringEpisode"]["episode"]
        else:
            nextAiringAt = None
            nextAiringEpisode = None

        Media[entry["status"]].append(
            AniListMedia(
                mediaId=media["id"],
                mediaTitle=getLanguageNameFunction(media["title"]),
                coverImage=media["coverImage"]["large"],
                listStatus=entry["status"],
                mediaStatus=media["status"],
                mediaType=type,
                mediaFormat=media["format"],
                mediaEpisodeCount=media["episodes"],
                mediaDuration=media["duration"],
                userMediaProgress=entry["progress"],
                nextAiringAt=nextAiringAt,
                nextAiringEpisode=nextAiringEpisode,
                mediaAniListSiteUrl=media["siteUrl"],
                mediaMyAnimeListSiteUrl=(
                    f"https://myanimelist.net/{type}/{media['idMal']}"
                    if media["idMal"]
                    else None
                ),
            )
        )

    mediaCollectionGroup = {
        media.mediaId: media for media in sum(Media.values(), deque())
    }
    statusMap = {
        mediaId: media.listStatus for mediaId, media in mediaCollectionGroup.items()
    }

    return (
        MediaCollection(**Media, Map=mediaCollectionGroup, Statuses=statusMap),
        User,
        Options,
    )
