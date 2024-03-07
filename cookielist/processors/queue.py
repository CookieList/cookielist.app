from collections import deque
from typing import Iterator

import arrow

from cookielist.processors._pre_process import (
    AniListMedia,
    AniListUser,
    CookieListOptions,
    MediaCollection,
)


class QueueProcessor:

    @staticmethod
    def __time_format(seconds: int) -> str:
        day = int(seconds // (3600 * 24))
        hour = int(seconds // 3600 % 24)
        minute = int(seconds % 3600 // 60)

        return (
            f"{day}d {hour + (1 if minute > 30 else 0)}h"
            if day > 0
            else f"{hour}h {minute}m" if hour > 0 else f"{minute}m"
        )

    def __queue_sections(
        self, Media: MediaCollection
    ) -> list[tuple[str, Iterator[AniListMedia]]]:
        currentMedia: list[AniListMedia] = sorted(
            Media.CURRENT, key=lambda media: media.nextAiringAt or 0
        )

        sectionAiringAnime = filter(
            lambda media: media.nextAiringEpisode is not None
            and media.mediaStatus == "RELEASING"
            and media.mediaType == "anime",
            currentMedia,
        )
        sectionAnimeInProgress = filter(
            lambda media: media.nextAiringEpisode is None
            and (media.mediaStatus == "FINISHED" or media.mediaStatus == "RELEASING")
            and media.mediaFormat != "MUSIC"
            and media.mediaFormat != "MOVIE"
            and media.mediaType == "anime",
            currentMedia,
        )
        sectionMovieInProgress = filter(
            lambda media: media.nextAiringEpisode is None
            and (media.mediaStatus == "FINISHED" or media.mediaStatus == "RELEASING")
            and media.mediaFormat == "MOVIE"
            and media.mediaType == "anime",
            currentMedia,
        )
        sectionMusicInProgress = filter(
            lambda media: media.nextAiringEpisode is None
            and (media.mediaStatus == "FINISHED" or media.mediaStatus == "RELEASING")
            and media.mediaFormat == "MUSIC"
            and media.mediaType == "anime",
            currentMedia,
        )
        sectionUpcomingAnime = filter(
            lambda media: media.mediaStatus == "NOT_YET_RELEASED"
            and media.mediaType == "anime",
            currentMedia,
        )
        sectionAnimeOnHiatus = filter(
            lambda media: media.mediaStatus == "HIATUS" and media.mediaType == "anime",
            currentMedia,
        )
        sectionMangaInProgress = filter(
            lambda media: media.mediaFormat != "NOVEL" and media.mediaType == "manga",
            currentMedia,
        )
        sectionNovelInProgress = filter(
            lambda media: media.mediaFormat == "NOVEL" and media.mediaType == "manga",
            currentMedia,
        )

        return [
            ("Airing Anime", sectionAiringAnime),
            ("Anime in Progress", sectionAnimeInProgress),
            ("Movie in Progress", sectionMovieInProgress),
            ("Music in Progress", sectionMusicInProgress),
            ("Upcoming Anime", sectionUpcomingAnime),
            ("Anime on Hiatus", sectionAnimeOnHiatus),
            ("Manga in Progress", sectionMangaInProgress),
            ("Novel in Progress", sectionNovelInProgress),
        ]

    def calculate(
        self, Media: MediaCollection, User: AniListUser, Options: CookieListOptions
    ) -> dict:
        queueSections = self.__queue_sections(Media)
        currentUtcTimestamp = arrow.utcnow().timestamp()
        userQueue = dict()

        for queueSectionTitle, queueSectionMediaGroup in queueSections:
            queueSectionMediaCollection = deque([])

            for media in queueSectionMediaGroup:
                timeUntilAiring = (
                    self.__time_format(media.nextAiringAt - currentUtcTimestamp)
                    if media.nextAiringAt
                    else None
                )
                maxPossibleMediaProgress = (
                    (media.nextAiringEpisode - 1)
                    if media.nextAiringEpisode
                    else media.mediaEpisodeCount if media.mediaEpisodeCount else "none"
                )

                queueSectionMediaCollection.append(
                    {
                        "media": media,  # ***
                        "mediaDuration": media.mediaDuration or 0,  # duration
                        "nextAiringEpisode": media.nextAiringEpisode or 0,  # episode
                        "timeUntilAiring": timeUntilAiring,  # time
                        "maxPossibleMediaProgress": maxPossibleMediaProgress,  # max_progress
                    }
                )

            dueQueueSectionMediaCollection = list(
                filter(
                    lambda queueSectionMedia: (
                        queueSectionMedia["nextAiringEpisode"] == 0
                    )
                    or (
                        (queueSectionMedia["media"].userMediaProgress + 1)
                        < queueSectionMedia["nextAiringEpisode"]
                    ),
                    queueSectionMediaCollection,
                )
            )

            dueProgressCount = sum(
                map(
                    lambda queueSectionMedia: (
                        (
                            (queueSectionMedia["nextAiringEpisode"] - 1)
                            - queueSectionMedia["media"].userMediaProgress
                        )
                        if queueSectionMedia["nextAiringEpisode"]
                        else (
                            (
                                queueSectionMedia["media"].mediaEpisodeCount
                                - queueSectionMedia["media"].userMediaProgress
                            )
                            if queueSectionMedia["media"].mediaEpisodeCount
                            else 0
                        )
                    ),
                    dueQueueSectionMediaCollection,
                )
            )

            dueProgressDurationInMinutes = sum(
                map(
                    lambda queueSectionMedia: queueSectionMedia["mediaDuration"]
                    * (
                        (
                            queueSectionMedia["maxPossibleMediaProgress"]
                            if queueSectionMedia["maxPossibleMediaProgress"] != "none"
                            else queueSectionMedia["media"].userMediaProgress
                        )
                        - queueSectionMedia["media"].userMediaProgress
                    ),
                    dueQueueSectionMediaCollection,
                )
            )

            userQueue[queueSectionTitle] = {
                "queueSectionMediaCollection": queueSectionMediaCollection,  # list
                "dueProgressCount": dueProgressCount,  # behind_count
                "dueProgressDurationInMinutes": dueProgressDurationInMinutes,  # behind_duration_minutes
                "dueProgressDurationFormatted": self.__time_format(
                    dueProgressDurationInMinutes * 60
                ),  # behind_duration_formatted
            }

        return userQueue
