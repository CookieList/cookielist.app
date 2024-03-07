from dotted_dict import DottedDict
from flask import session

from cookielist.processors._pre_process import AniListUser, CookieListOptions
from cookielist.utils import JsonToken


def calculate(parsedUserList: dict, User: AniListUser, Options: CookieListOptions):
    data = DottedDict({})

    __title_count = lambda media: sum(
        map(
            lambda group: group["completedGroupMediaCount"],
            parsedUserList["listResults"][media.upper()]["groupEntries"],
        )
    )

    __series_count = lambda media: parsedUserList["listResults"][media.upper()][
        "categoryGroupCount"
    ]

    data.anilist_user_id = User.userId
    data.anilist_username = User.userHandle
    data.anilist_avatar_url = User.userAvatar
    data.anilist_profile_theme_color = User.profileColor

    data.watched_anime_title_count = __title_count("anime")
    data.watched_manga_title_count = __title_count("manga")
    data.watched_music_title_count = __title_count("music")
    data.watched_novel_title_count = __title_count("novel")

    data.watched_anime_duration_in_minutes = User.animeMinutesWatched

    data.watched_anime_episodes_count = User.animeEpisodesWatched
    data.watched_manga_chapters_count = User.mangaChaptersRead

    data.watched_anime_series_count = __series_count("anime")
    data.watched_music_series_count = __series_count("music")
    data.watched_manga_series_count = __series_count("manga")
    data.watched_novel_series_count = __series_count("novel")

    data.__template = Options.badgeTemplate
    data.__server = Options.badgeServer
    data.__token = JsonToken.encode({"__id": str(session.get("id"))})
    data.__options = Options.badgeOptions

    return data.to_dict()
