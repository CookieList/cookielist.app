import calendar
import zoneinfo
from collections import defaultdict, deque

import arrow

from cookielist.processors._pre_process import (
    AniListMedia,
    AniListUser,
    CookieListOptions,
    MediaCollection,
)


class ScheduleProcessor:
    def __init__(self) -> None:

        self.weekDayMapping = dict(enumerate(calendar.day_name)) | dict(
            map(reversed, dict(enumerate(calendar.day_name)).items())
        )

    def calculate(
        self, Media: MediaCollection, User: AniListUser, Options: CookieListOptions
    ) -> dict:
        userMediaSchedule = defaultdict(lambda: defaultdict(deque))

        userTimezone = zoneinfo.ZoneInfo(Options.timezoneName)
        userCurrentDateTime = arrow.Arrow.now(userTimezone)
        userCurrentTimestamp = userCurrentDateTime.timestamp()
        oneWeekSpan = userCurrentDateTime.shift(days=-1), userCurrentDateTime.shift(
            weeks=1
        )

        airingMedia: list[AniListMedia] = sorted(
            filter(lambda _: _.nextAiringAt, Media.Map.values()),
            key=lambda _: _.nextAiringAt,
        )

        for media in airingMedia:
            mediaAiringTime = arrow.Arrow.fromtimestamp(
                media.nextAiringAt, tzinfo=userTimezone
            )
            weekDay = self.weekDayMapping[mediaAiringTime.weekday()]
            isMediaAiringThisWeek = mediaAiringTime.is_between(*oneWeekSpan)
            formattedAiringTime = mediaAiringTime.format(
                Options.timeFormatString
                if isMediaAiringThisWeek
                else Options.dateFormatString
            )

            userMediaSchedule[weekDay][formattedAiringTime].append(
                {
                    "mediaId": media.mediaId,
                    "mediaAniListSiteUrl": media.mediaAniListSiteUrl,
                    "mediaMyAnimeListSiteUrl": media.mediaMyAnimeListSiteUrl,
                    "mediaTitle": media.mediaTitle,
                    "coverImage": media.coverImage,
                    "nextAiringEpisode": media.nextAiringEpisode,
                    "isMediaAiringThisWeek": isMediaAiringThisWeek,
                    "timeUntilAiring": (
                        "airing"
                        if userCurrentTimestamp < media.nextAiringAt
                        else "aired"
                    )
                    + " "
                    + mediaAiringTime.humanize(locale="en-us"),
                }
            )

        todaysWeekDay = userCurrentDateTime.weekday()
        if Options.firstDayOfWeek == "Today":
            weekStart = todaysWeekDay
        elif Options.firstDayOfWeek == "Yesterday":
            weekStart = todaysWeekDay - 1 if todaysWeekDay != 0 else 6
        else:
            weekStart = self.weekDayMapping.get(Options.firstDayOfWeek, 0)
        weekOrder = map(
            lambda weekday: self.weekDayMapping[weekday],
            list(range(weekStart, 7)) + list(range(weekStart)),
        )
        sortedUserMediaSchedule = {
            weekDay: userMediaSchedule[weekDay] for weekDay in weekOrder
        }
        isScheduleEmpty = not bool(
            {
                _: userMediaSchedule[_]
                for _ in userMediaSchedule.keys()
                if userMediaSchedule[_]
            }
        )

        return {
            "userMediaSchedule": sortedUserMediaSchedule,
            "isScheduleEmpty": isScheduleEmpty,
            "todaysWeekDay": self.weekDayMapping[todaysWeekDay],
            "currentMediaIds": {media.mediaId for media in Media.CURRENT},
        }
