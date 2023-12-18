import arrow
import jmespath
from dotted_dict import DottedDict


class QueueProcessor:
    AIRING_ANIME = "[?media.nextAiringEpisode != `null` && media.status == 'RELEASING']"
    WATCHING_ANIME = "[?media.nextAiringEpisode == `null` && (media.status == 'FINISHED' || media.status == 'RELEASING') && media.format != 'MOVIE' && media.format != 'MUSIC']"
    WATCHING_MOVIE = "[?media.nextAiringEpisode == `null` && (media.status == 'FINISHED' || media.status == 'RELEASING') && media.format == 'MOVIE']"
    WATCHING_MUSIC = "[?media.nextAiringEpisode == `null` && (media.status == 'FINISHED' || media.status == 'RELEASING') && media.format == 'MUSIC']"
    READING_MANGA = "[?media.format != 'NOVEL']"
    READING_NOVEL = "[?media.format == 'NOVEL']"
    HIATUS_ANIME = "[?media.status == 'HIATUS']"
    UPCOMING_ANIME = "[?media.status == 'NOT_YET_RELEASED']"

    JMES_OPTIONS = jmespath.Options(dict_cls=DottedDict)

    def __init__(self):
        JMES_PREFIX = "data.MediaListCollection.lists[?isCustomList == `false` && status == 'CURRENT' ].entries[] | @"
        JMES_SUFFIX = ".{media: media, progress: progress}"

        self.queries = DottedDict(
            animeAiring=jmespath.compile(JMES_PREFIX + self.AIRING_ANIME + JMES_SUFFIX),
            animeWatching=jmespath.compile(
                JMES_PREFIX + self.WATCHING_ANIME + JMES_SUFFIX
            ),
            movieWatching=jmespath.compile(
                JMES_PREFIX + self.WATCHING_MOVIE + JMES_SUFFIX
            ),
            musicWatching=jmespath.compile(
                JMES_PREFIX + self.WATCHING_MUSIC + JMES_SUFFIX
            ),
            mangaReading=jmespath.compile(
                JMES_PREFIX + self.READING_MANGA + JMES_SUFFIX
            ),
            novelReading=jmespath.compile(
                JMES_PREFIX + self.READING_NOVEL + JMES_SUFFIX
            ),
            animeHiatus=jmespath.compile(JMES_PREFIX + self.HIATUS_ANIME + JMES_SUFFIX),
            animeUpcoming=jmespath.compile(
                JMES_PREFIX + self.UPCOMING_ANIME + JMES_SUFFIX
            ),
        )

    @staticmethod
    def __time_format(seconds: int) -> str:
        day = int(seconds // (3600 * 24))
        hour = int(seconds // 3600 % 24)
        minute = int(seconds % 3600 // 60)

        return (
            f"{day}d {hour + (1 if minute > 30 else 0)}h"
            if day > 0
            else f"{hour}h {minute}m"
            if hour > 0
            else f"{minute}m"
        )

    @staticmethod
    def __queue_sort(queue_item_group: DottedDict) -> list[DottedDict]:
        return sorted(
            queue_item_group,
            key=lambda queue_item: queue_item.media.nextAiringEpisode.airingAt
            if queue_item.media.nextAiringEpisode is not None
            else 0,
        )

    @staticmethod
    def __un_complete_filter(queue_item: DottedDict) -> bool:
        return (queue_item.episode == 0) or (
            (queue_item.progress + 1) < queue_item.episode
        )

    @staticmethod
    def __queue_item_format(queue_item: DottedDict) -> DottedDict:
        return DottedDict(
            id=queue_item.media.id,
            url=queue_item.media.siteUrl,
            duration=queue_item.media.duration if queue_item.media.duration else 0,
            progress=queue_item.progress,
            max_progress=(queue_item.media.nextAiringEpisode.episode - 1)
            if queue_item.media.nextAiringEpisode
            else queue_item.media.episodes
            if queue_item.media.episodes
            else "none",
            count=queue_item.media.episodes,
            name=queue_item.media.title.english or queue_item.media.title.romaji,
            cover=queue_item.media.coverImage.large,
            episode=queue_item.media.nextAiringEpisode.episode
            if queue_item.media.nextAiringEpisode
            else 0,
            next_airing=queue_item.media.nextAiringEpisode.airingAt
            if queue_item.media.nextAiringEpisode
            else None,
        )

    def __calculate(self, queue_item_group: DottedDict, options: DottedDict) -> dict:
        now_timestamp = arrow.utcnow().timestamp()

        formatted_queue_group = list(
            map(self.__queue_item_format, self.__queue_sort(queue_item_group))
        )

        for queue_item in formatted_queue_group:
            queue_item.time = (
                self.__time_format(queue_item.next_airing - now_timestamp)
                if queue_item.next_airing
                else None
            )

        un_complete_queue_items = list(
            filter(self.__un_complete_filter, formatted_queue_group)
        )

        un_complete_queue_items_count = sum(
            map(
                lambda queue_item: ((queue_item.episode - 1) - queue_item.progress)
                if queue_item.episode
                else (queue_item.count - queue_item.progress)
                if queue_item.count
                else 0,
                un_complete_queue_items,
            )
        )

        un_complete_queue_items_duration_minutes = sum(
            map(
                lambda queue_item: queue_item.duration
                * (
                    (
                        queue_item.max_progress
                        if queue_item.max_progress != "none"
                        else queue_item.progress
                    )
                    - queue_item.progress
                ),
                un_complete_queue_items,
            )
        )

        return {
            "lists": formatted_queue_group,
            "behind_count": un_complete_queue_items_count,
            "behind_duration_minutes": un_complete_queue_items_duration_minutes,
            "behind_duration_formatted": self.__time_format(
                un_complete_queue_items_duration_minutes * 60
            ),
        }

    def calculate(self, data) -> dict:
        return {
            "Airing Anime": self.__calculate(
                self.queries.animeAiring.search(data.anime, self.JMES_OPTIONS),
                data.options,
            ),
            "Anime in Progress": self.__calculate(
                self.queries.animeWatching.search(data.anime, self.JMES_OPTIONS),
                data.options,
            ),
            "Movie in Progress": self.__calculate(
                self.queries.movieWatching.search(data.anime, self.JMES_OPTIONS),
                data.options,
            ),
            "Music in Progress": self.__calculate(
                self.queries.musicWatching.search(data.anime, self.JMES_OPTIONS),
                data.options,
            ),
            "Upcoming Anime": self.__calculate(
                self.queries.animeUpcoming.search(data.anime, self.JMES_OPTIONS),
                data.options,
            ),
            "Anime on Hiatus": self.__calculate(
                self.queries.animeHiatus.search(data.anime, self.JMES_OPTIONS),
                data.options,
            ),
            "Manga in Progress": self.__calculate(
                self.queries.mangaReading.search(data.manga, self.JMES_OPTIONS),
                data.options,
            ),
            "Novel in Progress": self.__calculate(
                self.queries.novelReading.search(data.manga, self.JMES_OPTIONS),
                data.options,
            ),
        }
