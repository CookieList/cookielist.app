from collections import defaultdict

import jmespath
from dotted_dict import DottedDict

from cookielist.database import CookieListDatabase, dbconstants
from cookielist.database.database import ClDbItem


class ListProcessor:
    cookiedb = CookieListDatabase()

    def __init__(self) -> None:
        media_ids_jmes = "data.MediaListCollection.lists[?isCustomList == `false` && ({})].entries[].media.id"

        self.watched_media_query = jmespath.compile(
            media_ids_jmes.format(
                " || ".join(
                    f"status == '{status}'" for status in dbconstants.POSITIVE_STATUS
                )
            )
        )
        self.will_not_watch_media_query = jmespath.compile(
            media_ids_jmes.format(
                " || ".join(
                    f"status == '{status}'" for status in dbconstants.NEGATIVE_STATUS
                )
            )
        )
        self.parsed_media_query = jmespath.compile(
            "data.MediaListCollection.lists[?isCustomList == `false`].entries[] | {ids: @[*].media.id, entries: @[*].media}"
        )

    def __parse_media_map_id(self, data: DottedDict) -> dict:
        parsed_anime = self.parsed_media_query.search(data.anime)
        parsed_manga = self.parsed_media_query.search(data.manga)
        parsed_media = zip(
            parsed_anime["ids"] + parsed_manga["ids"],
            parsed_anime["entries"] + parsed_manga["entries"],
        )
        return dict(parsed_media)

    def __media_relation_group(self, media_ids: list[int]) -> list[list[ClDbItem]]:
        unique_relation_ids = {
            self.cookiedb.relation(media_id)
            for media_id in media_ids
            if media_id in self.cookiedb
        }
        relation_media_groups = [
            [self.cookiedb[media_id] for media_id in relation]
            for relation in [
                self.cookiedb(relation_id) for relation_id in unique_relation_ids
            ]
        ]
        return relation_media_groups

    def calculate(self, data: DottedDict) -> dict:
        watched_media_ids = set(
            self.watched_media_query.search(data.anime)
            + self.watched_media_query.search(data.manga)
        )
        dropped_media_ids = set(
            self.will_not_watch_media_query.search(data.anime)
            + self.will_not_watch_media_query.search(data.manga)
        )
        media_id_map = self.__parse_media_map_id(data)

        result = defaultdict(lambda: dict(entries=list(), duration=0, length=0))

        for related_media_group in self.__media_relation_group(watched_media_ids):
            __media_type = related_media_group[0].TYPE
            __media_duration = sum(item.DURATION for item in related_media_group)
            __media_length = len(related_media_group)

            __formatted_related_media = [
                dict(
                    id=media.ID,
                    name=media.NAME,
                    url=f"https://anilist.co/anime/{media.ID}"
                    if __media_type in dbconstants.WATCH_TYPES
                    else f"https://anilist.co/manga/{media.ID}",
                    cover=media.COVER,
                    format=media.FORMAT or "UNKNOWN",
                    completed=(_is_media_completed := media.ID in watched_media_ids),
                    available=(
                        _is_media_available_to_watch := media.STATUS
                        in dbconstants.AVAILABLE_STATUS
                    ),
                    plausible=False
                    if (_is_media_completed or media.ID in dropped_media_ids)
                    else _is_media_available_to_watch,
                )
                for media in related_media_group
            ]

            __total_completed_media_count = len(
                list(filter(lambda item: item["completed"], __formatted_related_media))
            )
            __is_media_group_finished = not any(
                item["plausible"] for item in __formatted_related_media
            )

            _completed_media_statuses = [
                media_item["format"]
                for media_item in __formatted_related_media
                if media_item["completed"]
            ]
            __media_completion_status = {
                dbconstants.FORMAT_ALIAS.get(
                    _media_format, _media_format
                ): _completed_media_statuses.count(_media_format)
                for _media_format in dbconstants.RELATION_PARSE_PRIORITY_ORDER
                if _completed_media_statuses.count(_media_format)
            }.items()

            result[__media_type]["length"] += 1
            result[__media_type]["duration"] += __media_duration
            result[__media_type]["entries"].append(
                dict(
                    group=__formatted_related_media,
                    id=__formatted_related_media[0]["id"],
                    name=self.cookiedb[
                        self.cookiedb.series(__formatted_related_media[0]["id"])
                    ].NAME,
                    total=__media_length,
                    completed=__total_completed_media_count,
                    duration=__media_duration,
                    watched=__is_media_group_finished,
                    status=__media_completion_status,
                )
            )

        for __media_type in result.keys():
            result[__media_type]["entries"].sort(key=lambda _: _["name"].upper())

        return dict(
            result=result,
            ignored=[
                media_id_map[media_id]
                for media_id in filter(
                    lambda id: id not in self.cookiedb, watched_media_ids
                )
            ],
        )
